from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Iterable, Mapping, Union


from .engine import GSAAdapter
from .models import Move

PriorSpec = Union[float, Mapping[int, float]]

@dataclass(frozen=True)
class SubsetState:
    selected: frozenset[int]

    def add(self, feature: int) -> SubsetState:
        return SubsetState(self.selected | {feature})

    def remove(self, feature: int) -> SubsetState:
        return SubsetState(self.selected - {feature})


class SubsetSelectionAdapter(GSAAdapter):
    """Shared add/remove neighborhood for subset-selection prototypes.

    Demo and synthetic experiments must use this class so candidate generation
    cannot drift between studies.
    """

    def __init__(self, n_items: int = 20, prior: PriorSpec = 1.0):
        self.n_items = n_items
        if isinstance(prior, Mapping):
            self._prior = dict(prior)
        else:
            value = float(prior)
            self._prior = {i: value for i in range(1, n_items + 1)}

    def initial_state(self) -> SubsetState:
        return SubsetState(frozenset())

    def initial_prior(self) -> Mapping[int, float]:
        return dict(self._prior)

    def sample_moves(
        self, state: SubsetState, rng: Random, pool_size: int
    ) -> Iterable[Move]:
        available = [
            i for i in range(1, self.n_items + 1) if i not in state.selected
        ]
        selected = list(state.selected)
        rng.shuffle(available)
        rng.shuffle(selected)
        candidates = [Move("add", item) for item in available[:pool_size]]
        candidates.extend(Move("remove", item) for item in selected[:pool_size])
        return candidates

    def apply_move(self, state: SubsetState, move: Move) -> SubsetState:
        if move.operation == "add":
            return state.add(move.feature)
        if move.operation == "remove":
            return state.remove(move.feature)
        raise ValueError(move.operation)

    def features_of(self, state: SubsetState) -> Iterable[int]:
        return state.selected
