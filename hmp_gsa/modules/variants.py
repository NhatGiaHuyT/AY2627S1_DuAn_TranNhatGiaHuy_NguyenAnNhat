from .engine import HMPGSA


def _quality(score, threshold):
    """Quality factor: 0.0 to 1.0.

    1.0 = best possible (score much below threshold).
    0.0 = barely elite (score at threshold) or not elite.
    """
    if threshold is None:
        return 1.0
    if score > threshold:
        return 0.0
    delta = threshold - score
    scale = max(abs(threshold), 1.0)
    return min(1.0, delta / scale)


class UnguidedGSA(HMPGSA):

    name = "unguided"

    def key_for_move(self, state, move):
        return None

    def prior_feature_for_key(self, key):
        return None

    def _candidate_weight(self, state, move, prior):
        return None, 1.0

    def update_memory(self, *, state_before, state_after, move, old_score, new_score, accepted, prior):
        pass

    def update_good_solution_memory(self, *, state, score, threshold, prior, adapter):
        pass

    def decay_weights(self):
        pass


class PriorOnlyGSA(HMPGSA):
    name = "prior_only"

    def key_for_move(self, state, move):
        return move.feature

    def prior_feature_for_key(self, key):
        return key

    def update_memory(self, *, state_before, state_after, move, old_score, new_score, accepted, prior):
        pass

    def update_good_solution_memory(self, *, state, score, threshold, prior, adapter):
        pass

    def decay_weights(self):
        pass


class SuccessfulFeatureGSA(HMPGSA):
    name = "successful_feature"

    def key_for_move(self, state, move):
        return move.feature

    def prior_feature_for_key(self, key):
        return key

    def update_memory(
        self,
        *,
        state_before,
        state_after,
        move,
        old_score,
        new_score,
        accepted,
        prior,
    ):
        if not accepted:
            return

        delta = new_score - old_score

        if delta >= 0:
            return

        key = self.key_for_move(
            state_before,
            move,
        )

        self._reinforce(
            key,
            self.alpha * abs(delta),
            prior,
        )

    def update_good_solution_memory(
        self,
        *,
        state,
        score,
        threshold,
        prior,
        adapter,
    ):
        pass


class GoodSolutionFrequencyGSA(HMPGSA):
    name = "good_solution_frequency"

    def key_for_move(self, state, move):
        return move.feature

    def prior_feature_for_key(self, key):
        return key

    def update_memory(self, *, state_before, state_after, move, old_score, new_score, accepted, prior):
        pass

    def update_good_solution_memory(self, *, state, score, threshold, prior, adapter):
        q = _quality(score, threshold)
        if q <= 0.0:
            return
        for feature in adapter.features_of(state):
            self._reinforce(feature, self.alpha * q, prior)

    def decay_weights(self):
        for key in self.weights:
            self.weights[key] *= (1.0 - self.decay)
            self.weights[key] = max(self.epsilon, self.weights[key])


class MutationFeatureGSA(HMPGSA):

    name = "mutation_feature"

    def key_for_move(self, state, move):
        return (
            move.operation,
            move.feature,
        )

    def prior_feature_for_key(self, key):
        _, feature = key
        return feature

    def update_memory(
        self,
        *,
        state_before,
        state_after,
        move,
        old_score,
        new_score,
        accepted,
        prior,
    ):
        if not accepted:
            return

        delta = new_score - old_score

        if delta >= 0:
            return

        key = self.key_for_move(
            state_before,
            move,
        )

        self._reinforce(
            key,
            self.alpha * abs(delta),
            prior,
        )

    def update_good_solution_memory(
        self,
        *,
        state,
        score,
        threshold,
        prior,
        adapter,
    ):
        pass