from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import ceil, log2
from random import Random
from itertools import combinations
from typing import Mapping

from .adapter import GSAAdapter
from .models import Feature, Move


@dataclass(frozen=True)
class MDLState:
    code_table: frozenset[tuple[int, ...]]
    residual: tuple[tuple[int, ...], ...] = ()
    residual_masks: tuple[int, ...] = ()

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
        candidate_sizes: tuple[int, ...] = (1, 2),
        max_candidates: int = 10000,
        move_operations: tuple[str, ...] = ("add",),
    ):
        self.transactions = tuple(tuple(sorted(set(t))) for t in transactions)
        self._transaction_sets = tuple(frozenset(tx) for tx in self.transactions)
        self.max_pattern_size = max_pattern_size
        self.prior_multiplier = prior_multiplier
        self.candidate_sizes = tuple(sorted(set(candidate_sizes)))
        self.max_candidates = max_candidates
        self.move_operations = tuple(dict.fromkeys(move_operations))
        self._all_items = tuple(sorted({item for tx in self.transactions for item in tx}))
        self._item_bits = {item: 1 << index for index, item in enumerate(self._all_items)}
        self._transaction_masks = tuple(
            sum(self._item_bits[item] for item in transaction)
            for transaction in self.transactions
        )
        self._support = Counter()
        for tx in self.transactions:
            for size in self.candidate_sizes:
                if size > self.max_pattern_size or size > len(tx):
                    continue
                for pattern in combinations(tx, size):
                    self._support[tuple(sorted(pattern))] += 1
        self._candidate_order = sorted(
            self._support,
            key=lambda pattern: self._support[pattern],
            reverse=True,
        )
        self._pattern_prior = {
            pattern: float(support + 1.0) * prior_multiplier
            for pattern, support in self._support.items()
        }
        self._score_cache: dict[frozenset[tuple[int, ...]], float] = {}

    def initial_state(self) -> MDLState:
        return MDLState(
            code_table=frozenset(),
            residual=self.transactions,
            residual_masks=self._transaction_masks,
        )

    def initial_prior(self) -> Mapping[Feature, float]:
        return dict(self._pattern_prior)

    def sample_moves(self, state: MDLState, rng: Random, pool_size: int):
        available_adds = [
            pattern
            for pattern in self._candidate_order[: self.max_candidates]
            if pattern not in state.code_table
        ]
        candidates = []
        if "add" in self.move_operations:
            candidates.extend(Move("add", pattern) for pattern in available_adds)
        if "remove" in self.move_operations:
            candidates.extend(Move("remove", pattern) for pattern in state.code_table)
        if "replace" in self.move_operations and state.code_table:
            candidates.extend(
                Move("replace", pattern, payload=tuple(state.code_table))
                for pattern in available_adds
            )
        if not candidates:
            return []
        if len(candidates) > pool_size:
            candidates = rng.sample(candidates, pool_size)
        return candidates

    def _candidate_patterns(self, state: MDLState):
        return [pattern for pattern, support in self._support.items() if support > 0]

    def _pattern_support(self, pattern: tuple[int, ...], transactions) -> int:
        indexed = self._support.get(tuple(sorted(pattern)))
        if transactions is self.transactions and indexed is not None:
            return indexed
        count = 0
        for tx in transactions:
            if all(item in tx for item in pattern):
                count += 1
        return count

    def apply_move(self, state: MDLState, move: Move) -> MDLState:
        pattern = tuple(sorted(move.feature))
        new_table = set(state.code_table)
        if move.operation == "add":
            if not pattern or pattern in new_table:
                return state
            new_table.add(pattern)
        elif move.operation == "remove":
            if pattern not in new_table:
                return state
            new_table.remove(pattern)
        elif move.operation == "replace":
            old_patterns = tuple(move.payload or ())
            if pattern in new_table or not old_patterns:
                return state
            new_table.remove(old_patterns[0])
            new_table.add(pattern)
        else:
            raise ValueError(f"Unsupported move operation: {move.operation}")

        residual_masks = self._residual_masks_for_table(frozenset(new_table))
        return MDLState(frozenset(new_table), residual_masks=residual_masks)

    def _residual_masks_for_table(
        self, code_table: frozenset[tuple[int, ...]]
    ) -> tuple[int, ...]:
        encoded_patterns = []
        for pattern in sorted(code_table, key=len, reverse=True):
            pattern_mask = 0
            for item in pattern:
                pattern_mask |= self._item_bits[item]
            encoded_patterns.append(pattern_mask)

        residual_masks = []
        for transaction_mask in self._transaction_masks:
            residual_mask = transaction_mask
            for pattern_mask in encoded_patterns:
                if pattern_mask & residual_mask == pattern_mask:
                    residual_mask &= ~pattern_mask
            residual_masks.append(residual_mask)
        return tuple(residual_masks)

    def evaluate(self, state: MDLState) -> float:
        if state.code_table not in self._score_cache:
            self._score_cache[state.code_table] = self._mdl_cost(
                state.code_table,
                state.residual_masks,
            )
        return self._score_cache[state.code_table]

    def features_of(self, state: MDLState):
        for pattern in state.code_table:
            yield pattern

    def feature_of_move(self, move: Move):
        return move.feature

    def operation_of_move(self, move: Move) -> str:
        return move.operation

    def _mdl_cost(self, code_table, residual_masks) -> float:
        residual_bits = sum(mask.bit_count() for mask in residual_masks) * 32

        code_bits = 0
        for pattern in code_table:
            count = self._support.get(pattern, 0)
            if count <= 0:
                continue
            value_bits = int(ceil(log2(count + 1)))
            code_bits += value_bits + len(pattern) * 32

        return float(residual_bits + code_bits)