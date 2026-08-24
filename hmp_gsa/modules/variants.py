from typing import Mapping, Any, Optional

from .engine import HMPGSA
from .models import Feature, GuidanceKey, Move

class SuccessfulFeatureGSA(HMPGSA):
    """Hypothesis A.

    Memory key:
        feature

    Reinforcement:
        improving accepted mutation => feature weight += alpha * improvement

    This is intentionally strict: only an accepted move with negative delta
    reinforces the feature.
    """
    name = "successful_feature"

    def key_for_move(self, move: Move) -> GuidanceKey:
        return self.adapter.feature_of_move(move)

    def initial_weight(self, key: GuidanceKey, prior: Mapping[Feature, float]) -> float:
        return float(prior.get(key, 1.0))

    def update_memory(
        self,
        *,
        move: Move,
        old_score: float,
        new_score: float,
        accepted: bool,
        state_before: Any,
        state_after: Any,
    ) -> None:
        delta = new_score - old_score
        if accepted and delta < 0:
            key = self.key_for_move(move)
            self.weights[key] = self.weights.get(key, 1.0) + self.alpha * abs(delta)

class GoodSolutionFrequencyGSA(HMPGSA):
    """Hypothesis B.

    Memory key:
        feature

    Reinforcement:
        when a candidate is in the elite/good set, every feature present in
        that candidate receives a small reinforcement.

    The prototype uses a quantile-like threshold over observed scores.
    """
    name = "good_solution_frequency"
    def key_for_move(self, move: Move) -> GuidanceKey:
        return self.adapter.feature_of_move(move)

    def initial_weight(self, key: GuidanceKey, prior: Mapping[Feature, float]) -> float:
        return float(prior.get(key, 1.0))

    def update_good_solution_memory(
        self,
        *,
        state: Any,
        score: float,
        elite_threshold: Optional[float],
    ) -> None:
        if elite_threshold is None or score > elite_threshold:
            return

        for feature in self.adapter.features_of(state):
            self.weights[feature] = self.weights.get(feature, 1.0) + self.alpha

class MutationFeatureGSA(HMPGSA):
    """Hypothesis C.

    Memory key:
        (operation, feature)

    Reinforcement:
        accepted improving mutation => reinforce the exact operation-feature
        combination.

    This distinguishes:
        ADD X
    from:
        REMOVE X
    """
    name = "mutation_feature"

    def key_for_move(self, move: Move) -> GuidanceKey:
        return (
            self.adapter.operation_of_move(move),
            self.adapter.feature_of_move(move),
        )

    def initial_weight(self, key: GuidanceKey, prior: Mapping[Feature, float]) -> float:
        _, feature = key
        return float(prior.get(feature, 1.0))

    def update_memory(
        self,
        *,
        move: Move,
        old_score: float,
        new_score: float,
        accepted: bool,
        state_before: Any,
        state_after: Any,
    ) -> None:
        delta = new_score - old_score
        if accepted and delta < 0:
            key = self.key_for_move(move)
            self.weights[key] = self.weights.get(key, 1.0) + self.alpha * abs(delta)