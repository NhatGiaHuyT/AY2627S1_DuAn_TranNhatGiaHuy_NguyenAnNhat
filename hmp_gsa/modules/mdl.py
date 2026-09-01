from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from math import ceil, log2
from random import Random
from typing import Iterable, Mapping

from .adapter import GSAAdapter
from .models import Feature, Move


@dataclass(frozen=True)
class MDLState:
    code_table: frozenset[tuple[int, ...]]
    residual: tuple[tuple[int, ...], ...] = ()

    def with_pattern(self, pattern: tuple[int, ...]) -> "MDLState":
        code_table = set(self.code_table)
        code_table.add(tuple(pattern))
        residual = tuple(
            tuple(item for item in transaction if item not in set(pattern))
            for transaction in self.residual or ()
        )
        return MDLState(frozenset(code_table), residual)


class DatasetMDLAdapter(GSAAdapter):
    """MDL-style adapter aligned with the Java HMP-SA implementation.

    The Java runner measures compression as the residual database size after
    removing the current pattern set, plus a code-table cost for pattern usage.
    This is a faithful first approximation of the MDL-like objective described in
    the project notes without inventing a radically different search space.
    """

    def __init__(
        self,
        transactions,
        *,
        max_pattern_size: int = 3,
        prior_multiplier: float = 1.0,
    ):
        self.transactions = tuple(tuple(sorted(set(t))) for t in transactions)
        self.max_pattern_size = max_pattern_size
        self.prior_multiplier = prior_multiplier
        self._all_items = tuple(sorted({item for tx in self.transactions for item in tx}))
        self._support = Counter()
        for tx in self.transactions:
            for i in range(len(tx)):
                self._support[tx[i]] += 1
            for j in range(len(tx)):
                for k in range(j + 1, len(tx)):
                    pattern = (tx[j], tx[k])
                    self._support[pattern] += 1
        self._item_prior = {
            item: float(self._support.get(item, 0) + 1.0) * prior_multiplier
            for item in self._all_items
        }

    def initial_state(self) -> MDLState:
        return MDLState(code_table=frozenset(), residual=self.transactions)

    def initial_prior(self) -> Mapping[Feature, float]:
        return dict(self._item_prior)

    def sample_moves(self, state: MDLState, rng: Random, pool_size: int):
        candidates = []
        pool_seen = set()
        all_patterns = self._candidate_patterns(state)
        rng.shuffle(all_patterns)
        for pattern in all_patterns[: max(1, pool_size)]:
            key = tuple(sorted(pattern))
            if key in pool_seen:
                continue
            pool_seen.add(key)
            candidates.append(Move("add", key))
        return candidates

    def _candidate_patterns(self, state: MDLState):
        patterns = []
        for tx in state.residual or self.transactions:
            for size in range(1, min(self.max_pattern_size, len(tx)) + 1):
                from itertools import combinations

                for combo in combinations(tx, size):
                    combo = tuple(sorted(combo))
                    if len(combo) == 0:
                        continue
                    if self._pattern_support(combo, state.residual or self.transactions) > 0:
                        patterns.append(combo)
        seen = set()
        unique = []
        for pattern in patterns:
            if pattern not in seen:
                seen.add(pattern)
                unique.append(pattern)
        return unique

    def _pattern_support(self, pattern: tuple[int, ...], transactions) -> int:
        count = 0
        for tx in transactions:
            if all(item in tx for item in pattern):
                count += 1
        return count

    def apply_move(self, state: MDLState, move: Move) -> MDLState:
        if move.operation != "add":
            raise ValueError(f"Unsupported move operation: {move.operation}")
        pattern = tuple(sorted(move.feature))
        if not pattern:
            return state
        if pattern in state.code_table:
            return state
        residual = tuple(
            tuple(item for item in transaction if item not in set(pattern))
            for transaction in state.residual if state.residual
        )
        if not residual:
            residual = ()
        new_table = set(state.code_table)
        new_table.add(pattern)
        return MDLState(frozenset(new_table), residual)

    def evaluate(self, state: MDLState) -> float:
        return self._mdl_cost(state.code_table, state.residual or self.transactions)

    def features_of(self, state: MDLState):
        for pattern in state.code_table:
            yield pattern

    def feature_of_move(self, move: Move):
        return move.feature

    def operation_of_move(self, move: Move) -> str:
        return move.operation

    def _mdl_cost(self, code_table, residual_transactions) -> float:
        residual_bits = 0
        for tx in residual_transactions:
            residual_bits += len(tx) * 32

        code_bits = 0
        for pattern in code_table:
            count = self._pattern_support(pattern, self.transactions)
            if count <= 0:
                continue
            value_bits = int(ceil(log2(count + 1)))
            code_bits += value_bits + len(pattern) * 32

        return float(residual_bits + code_bits)