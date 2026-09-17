from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from math import ceil, log2
from random import Random
from itertools import combinations
from pathlib import Path
from typing import Mapping

from .adapter import GSAAdapter
from .models import Feature, Move


@dataclass(frozen=True)
class MDLState:
    code_table: frozenset[tuple[int, ...]]
    residual: tuple[tuple[int, ...], ...] = ()
    residual_masks: tuple[int, ...] = ()

    def with_pattern(
        self,
        pattern: tuple[int, ...],
    ) -> "MDLState":
        code_table = set(self.code_table)
        code_table.add(tuple(pattern))

        residual = tuple(
            tuple(
                item
                for item in transaction
                if item not in set(pattern)
            )
            for transaction in self.residual or ()
        )

        return MDLState(
            frozenset(code_table),
            residual,
        )


class DatasetMDLAdapter(GSAAdapter):
    """
    MDL-style adapter for the HMP-GSA experiments.

    Dataset-derived prior:
        - singleton feature  -> item frequency
        - pair feature       -> pairwise co-occurrence

    The resulting prior is the SAME W₀ supplied to every guided variant.

    GSA variants differ only in how they subsequently update W during
    the search trajectory.
    """

    def __init__(
        self,
        transactions,
        *,
        cooccurrence_path: str | Path,
        max_pattern_size: int = 3,
        prior_multiplier: float = 1.0,
        candidate_sizes: tuple[int, ...] = (1, 2),
        max_candidates: int = 10000,
        move_operations: tuple[str, ...] = ("add",),
    ):
        self.transactions = tuple(
            tuple(sorted(set(t)))
            for t in transactions
        )

        self._transaction_sets = tuple(
            frozenset(tx)
            for tx in self.transactions
        )

        self.max_pattern_size = max_pattern_size
        self.prior_multiplier = prior_multiplier
        self.candidate_sizes = tuple(
            sorted(set(candidate_sizes))
        )
        self.max_candidates = max_candidates
        self.move_operations = tuple(
            dict.fromkeys(move_operations)
        )

        self._all_items = tuple(
            sorted(
                {
                    item
                    for tx in self.transactions
                    for item in tx
                }
            )
        )

        self._item_bits = {
            item: 1 << index
            for index, item in enumerate(
                self._all_items
            )
        }

        self._transaction_masks = tuple(
            sum(
                self._item_bits[item]
                for item in transaction
            )
            for transaction in self.transactions
        )

        # ----------------------------------------------------------
        # Candidate/support statistics
        # ----------------------------------------------------------

        self._support = Counter()

        for tx in self.transactions:
            for size in self.candidate_sizes:
                if (
                    size > self.max_pattern_size
                    or size > len(tx)
                ):
                    continue

                for pattern in combinations(tx, size):
                    self._support[
                        tuple(sorted(pattern))
                    ] += 1

        # ----------------------------------------------------------
        # Dataset prior
        #
        # This is W₀.
        #
        # It comes from the preprocessing artifacts rather than
        # from the MDL search trajectory.
        # ----------------------------------------------------------

        (
            self._item_frequency,
            self._pair_cooccurrence,
        ) = self._load_cooccurrence_prior(
            cooccurrence_path
        )

        self._pattern_prior = (
            self._build_pattern_prior()
        )

        self._score_cache: dict[
            frozenset[tuple[int, ...]],
            float,
        ] = {}

    # ==============================================================
    # PRIOR
    # ==============================================================

    def _load_cooccurrence_prior(
        self,
        path: str | Path,
    ) -> tuple[
        dict[int, float],
        dict[tuple[int, int], float],
    ]:
        """
        Load the dataset-derived prior artifacts.

        The preprocessing step produces:
            item_frequency.csv
            cooccurrence.csv

        Both are converted to the integer representation used by
        DatasetMDLAdapter.
        """

        base_path = Path(path)

        if base_path.is_dir():
            item_frequency_path = (
                base_path / "item_frequency.csv"
            )
            cooccurrence_path = (
                base_path / "cooccurrence.csv"
            )
        else:
            cooccurrence_path = base_path
            item_frequency_path = (
                base_path.parent / "item_frequency.csv"
            )

        item_frequency: dict[int, float] = {}

        with item_frequency_path.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                item = int(row["item"])
                frequency = float(
                    row["frequency"]
                )

                item_frequency[item] = frequency

        pair_cooccurrence: dict[
            tuple[int, int],
            float,
        ] = {}

        with cooccurrence_path.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                i = int(row["item_i"])
                j = int(row["item_j"])

                pair = tuple(
                    sorted((i, j))
                )

                pair_cooccurrence[pair] = float(
                    row["cooccurrence"]
                )

        return (
            item_frequency,
            pair_cooccurrence,
        )

    def _build_pattern_prior(
        self,
    ) -> dict[Feature, float]:
        """
        Convert the dataset-level prior representation into the
        Feature -> weight representation required by GSA.

        Important:
            This is only the INITIAL prior W₀.

            It is not the online GSA memory.
        """

        prior: dict[Feature, float] = {}

        for pattern in self._support:
            pattern = tuple(sorted(pattern))

            if len(pattern) == 1:
                item = pattern[0]

                value = self._item_frequency.get(
                    item,
                    0.0,
                )

            elif len(pattern) == 2:
                pair = (
                    pattern[0],
                    pattern[1],
                )

                value = self._pair_cooccurrence.get(
                    pair,
                    0.0,
                )

            else:
                # The preprocessing artifact is pairwise.
                #
                # Therefore there is no dataset-derived
                # co-occurrence value for larger patterns.
                #
                # Do NOT manufacture one by summing/averaging
                # pairwise values.
                continue

            prior[pattern] = (
                float(value)
                * self.prior_multiplier
            )

        return prior

    def initial_prior(
        self,
    ) -> Mapping[Feature, float]:
        """
        Return W₀.

        Every guided GSA variant receives this exact mapping.
        """

        return dict(self._pattern_prior)

    # ==============================================================
    # INITIAL STATE
    # ==============================================================

    def initial_state(self) -> MDLState:
        return MDLState(
            code_table=frozenset(),
            residual=self.transactions,
            residual_masks=self._transaction_masks,
        )

    # ==============================================================
    # MOVE GENERATION
    # ==============================================================

    def sample_moves(
        self,
        state: MDLState,
        rng: Random,
        pool_size: int,
    ):
        all_addable = [
            pattern
            for pattern in self._support
            if pattern not in state.code_table
        ]

        if len(all_addable) > self.max_candidates:
            available_adds = rng.sample(
                all_addable,
                self.max_candidates,
            )
        else:
            available_adds = all_addable

        candidates = []

        if "add" in self.move_operations:
            candidates.extend(
                Move("add", pattern)
                for pattern in available_adds
            )

        if "remove" in self.move_operations:
            candidates.extend(
                Move("remove", pattern)
                for pattern in state.code_table
            )

        if (
            "replace" in self.move_operations
            and state.code_table
        ):
            for new_pattern in available_adds:
                candidates.append(
                    Move(
                        "replace",
                        new_pattern,
                        payload=tuple(
                            state.code_table
                        ),
                    )
                )

        if not candidates:
            return []

        if len(candidates) > pool_size:
            candidates = rng.sample(
                candidates,
                pool_size,
            )

        return candidates

    # ==============================================================
    # SUPPORT
    # ==============================================================

    def _candidate_patterns(
        self,
        state: MDLState,
    ):
        return [
            pattern
            for pattern, support in self._support.items()
            if support > 0
        ]

    def _pattern_support(
        self,
        pattern: tuple[int, ...],
        transactions,
    ) -> int:
        indexed = self._support.get(
            tuple(sorted(pattern))
        )

        if (
            transactions is self.transactions
            and indexed is not None
        ):
            return indexed

        count = 0

        for tx in transactions:
            if all(
                item in tx
                for item in pattern
            ):
                count += 1

        return count

    # ==============================================================
    # STATE TRANSITIONS
    # ==============================================================

    def apply_move(
        self,
        state: MDLState,
        move: Move,
    ) -> MDLState:
        pattern = tuple(
            sorted(move.feature)
        )

        new_table = set(
            state.code_table
        )

        if move.operation == "add":
            if (
                not pattern
                or pattern in new_table
            ):
                return state

            new_table.add(pattern)

        elif move.operation == "remove":
            if pattern not in new_table:
                return state

            new_table.remove(pattern)

        elif move.operation == "replace":
            old_patterns = tuple(
                move.payload or ()
            )

            if (
                pattern in new_table
                or not old_patterns
            ):
                return state

            new_table.remove(
                old_patterns[0]
            )
            new_table.add(pattern)

        else:
            raise ValueError(
                f"Unsupported move operation: "
                f"{move.operation}"
            )

        residual_masks = (
            self._residual_masks_for_table(
                frozenset(new_table)
            )
        )

        return MDLState(
            frozenset(new_table),
            residual_masks=residual_masks,
        )

    # ==============================================================
    # RESIDUAL
    # ==============================================================

    def _residual_masks_for_table(
        self,
        code_table: frozenset[
            tuple[int, ...]
        ],
    ) -> tuple[int, ...]:

        encoded_patterns = []

        for pattern in sorted(
            code_table,
            key=len,
            reverse=True,
        ):
            pattern_mask = 0

            for item in pattern:
                pattern_mask |= (
                    self._item_bits[item]
                )

            encoded_patterns.append(
                pattern_mask
            )

        residual_masks = []

        for transaction_mask in (
            self._transaction_masks
        ):
            residual_mask = transaction_mask

            for pattern_mask in encoded_patterns:
                if (
                    pattern_mask
                    & residual_mask
                    == pattern_mask
                ):
                    residual_mask &= ~pattern_mask

            residual_masks.append(
                residual_mask
            )

        return tuple(
            residual_masks
        )

    # ==============================================================
    # OBJECTIVE
    # ==============================================================

    def evaluate(
        self,
        state: MDLState,
    ) -> float:

        if state.code_table not in self._score_cache:
            self._score_cache[
                state.code_table
            ] = self._mdl_cost(
                state.code_table,
                state.residual_masks,
            )

        return self._score_cache[
            state.code_table
        ]

    # ==============================================================
    # FEATURE EXTRACTION
    # ==============================================================

    def features_of(
        self,
        state: MDLState,
    ):
        for pattern in state.code_table:
            yield pattern

    def feature_of_move(
        self,
        move: Move,
    ):
        return move.feature

    def operation_of_move(
        self,
        move: Move,
    ) -> str:
        return move.operation

    # ==============================================================
    # MDL COST
    # ==============================================================

    def _mdl_cost(
        self,
        code_table,
        residual_masks,
    ) -> float:

        residual_bits = (
            sum(
                mask.bit_count()
                for mask in residual_masks
            )
            * 32
        )

        code_bits = 0

        for pattern in code_table:
            count = self._support.get(
                pattern,
                0,
            )

            if count <= 0:
                continue

            value_bits = int(
                ceil(
                    log2(
                        count + 1
                    )
                )
            )

            code_bits += (
                value_bits
                + len(pattern) * 32
            )

        return float(
            residual_bits
            + code_bits
        )