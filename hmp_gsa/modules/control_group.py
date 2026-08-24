from typing import Mapping

from .engine import HMPGSA
from .models import Feature, GuidanceKey, Move

class UnguidedGSA(HMPGSA):
    """Control: same SA loop and candidate pool, uniform sampling, no memory."""

    name = "unguided"

    def key_for_move(self, move: Move) -> GuidanceKey:
        return self.adapter.feature_of_move(move)

    def initial_weight(self, key: GuidanceKey, prior: Mapping[Feature, float]) -> float:
        return 1.0

    def decay_weights(self) -> None:
        return None


class PriorOnlyGSA(HMPGSA):
    """Control: sample from the static adapter prior, with no online updates."""

    name = "prior_only"

    def key_for_move(self, move: Move) -> GuidanceKey:
        return self.adapter.feature_of_move(move)

    def initial_weight(self, key: GuidanceKey, prior: Mapping[Feature, float]) -> float:
        return float(prior.get(key, 1.0))

    def decay_weights(self) -> None:
        return None
