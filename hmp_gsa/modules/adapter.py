from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping
from random import Random

from .models import Feature, Move


class GSAAdapter(ABC):
    @abstractmethod
    def initial_state(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def initial_prior(self) -> Mapping[Feature, float]:
        raise NotImplementedError

    @abstractmethod
    def sample_moves(
        self, state: Any, rng: Random, pool_size: int
    ) -> Iterable[Move]:
        raise NotImplementedError

    @abstractmethod
    def apply_move(self, state: Any, move: Move) -> Any:
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, state: Any) -> float:
        raise NotImplementedError

    @abstractmethod
    def features_of(self, state: Any) -> Iterable[Feature]:
        raise NotImplementedError

    def feature_of_move(self, move: Move) -> Feature:
        return move.feature

    def operation_of_move(self, move: Move) -> str:
        return move.operation

    def prior_weight(
        self,
        state: Any,
        move: Move,
        prior: Mapping[Feature, float] | None = None,
    ) -> float:
        """Optional dynamic prior contribution for a candidate move.

        The initial memory prior is still represented by `initial_prior()` and
        `_ensure_weight(...)`. This hook is reserved for future dataset-derived
        guidance such as a co-occurrence prior `P(move | state, dataset)`.
        """
        if prior is None:
            return 1.0
        key = self.feature_of_move(move)
        value = prior.get(key, 1.0)
        return float(value) if value is not None else 1.0