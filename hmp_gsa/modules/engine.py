from abc import ABC, abstractmethod
from collections.abc import Mapping
from random import Random
from typing import Generic, TypeVar

State = TypeVar("State")
Move = TypeVar("Move")
Feature = TypeVar("Feature")
GuidanceKey = TypeVar("GuidanceKey")


class HMPGSA(
    ABC,
    Generic[State, Move, Feature, GuidanceKey],
):
    def __init__(
        self,
        *,
        iterations: int = 10_000,
        temperature_start: float = 10.0,
        temperature_end: float = 0.1,
        candidate_pool_size: int = 5,
        alpha: float = 0.1,
        decay: float = 0.001,
        elite_fraction: float = 0.1,
        seed: int = 0,
        epsilon: float = 1e-9,
    ):
        self.iterations = iterations
        self.temperature_start = temperature_start
        self.temperature_end = temperature_end
        self.candidate_pool_size = candidate_pool_size

        self.alpha = alpha
        self.decay = decay
        self.elite_fraction = elite_fraction
        self.seed = seed
        self.epsilon = epsilon

        self.weights: dict[GuidanceKey, float] = {}
        self._seen_scores: list[float] = []

    # ------------------------------------------------------------------
    # SA
    # ------------------------------------------------------------------

    def temperature(
        self,
        iteration: int,
    ) -> float:
        if self.iterations <= 1:
            return self.temperature_end

        progress = iteration / (self.iterations - 1)

        return self.temperature_start + progress * (
            self.temperature_end - self.temperature_start
        )

    def accept(
        self,
        old_score: float,
        new_score: float,
        temperature: float,
        rng: Random,
    ) -> bool:
        if new_score < old_score:
            return True

        if temperature <= 0.0:
            return False

        import math

        probability = math.exp(-(new_score - old_score) / temperature)

        return rng.random() < probability

    # ------------------------------------------------------------------
    # Guidance key
    # ------------------------------------------------------------------

    @abstractmethod
    def key_for_move(
        self,
        state: State,
        move: Move,
    ) -> GuidanceKey:
        """
        Convert a move into the key used by the
        guidance memory.
        """
        raise NotImplementedError

    @abstractmethod
    def prior_feature_for_key(
        self,
        key: GuidanceKey,
    ) -> Feature:
        """
        Map a guidance key back to the feature used
        by the common HMP initial prior.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Initial memory
    # ------------------------------------------------------------------

    def _initial_weight(
        self,
        key: GuidanceKey,
        prior: Mapping[Feature, float],
    ) -> float:

        feature = self.prior_feature_for_key(key)

        return max(
            self.epsilon,
            float(
                prior.get(
                    feature,
                    self.epsilon,
                )
            ),
        )

    def _ensure_weight(
        self,
        key: GuidanceKey,
        prior: Mapping[Feature, float],
    ) -> float:

        if key not in self.weights:
            self.weights[key] = self._initial_weight(
                key,
                prior,
            )

        return self.weights[key]

    # ------------------------------------------------------------------
    # Reinforcement
    # ------------------------------------------------------------------

    def _reinforce(
        self,
        key: GuidanceKey,
        amount: float,
        prior: Mapping[Feature, float],
    ) -> None:

        self._ensure_weight(
            key,
            prior,
        )

        self.weights[key] += amount

    # ------------------------------------------------------------------
    # Candidate weighting
    # ------------------------------------------------------------------

    def _candidate_weight(
        self,
        state: State,
        move: Move,
        prior: Mapping[Feature, float],
    ) -> tuple[GuidanceKey, float]:

        key = self.key_for_move(
            state,
            move,
        )

        weight = self._ensure_weight(
            key,
            prior,
        )

        return key, weight

    def sample_weighted_move(
        self,
        state: State,
        candidates: list[Move],
        prior: Mapping[Feature, float],
        rng: Random,
    ) -> Move:

        if not candidates:
            raise ValueError("Candidate pool cannot be empty.")

        weighted_candidates = []

        for move in candidates:
            key, weight = self._candidate_weight(
                state,
                move,
                prior,
            )

            weighted_candidates.append((move, weight))

        total = sum(weight for _, weight in weighted_candidates)

        if total <= 0.0:
            return rng.choice(candidates)

        moves = [move for move, _ in weighted_candidates]

        weights = [weight for _, weight in weighted_candidates]

        return rng.choices(
            moves,
            weights=weights,
            k=1,
        )[0]

    # ------------------------------------------------------------------
    # Forgetting
    # ------------------------------------------------------------------

    def decay_weights(self) -> None:

        for key in self.weights:
            self.weights[key] *= 1.0 - self.decay

            # Keep the key alive.
            #
            # If we deleted it, encountering it again would
            # reinitialize it from W0 and therefore undo forgetting.
            self.weights[key] = max(
                self.epsilon,
                self.weights[key],
            )

    # ------------------------------------------------------------------
    # Learning hooks
    # ------------------------------------------------------------------

    @abstractmethod
    def update_memory(
        self,
        *,
        state_before: State,
        state_after: State,
        move: Move,
        old_score: float,
        new_score: float,
        accepted: bool,
        prior: Mapping[Feature, float],
    ) -> None:
        raise NotImplementedError

    def update_good_solution_memory(
        self,
        *,
        state: State,
        score: float,
        threshold: float | None,
        prior: Mapping[Feature, float],
        adapter,
    ) -> None:
        pass

    # ------------------------------------------------------------------
    # Elite threshold
    # ------------------------------------------------------------------

    def _elite_threshold(self) -> float | None:

        if not self._seen_scores:
            return None

        ordered = sorted(self._seen_scores)

        index = int(len(ordered) * self.elite_fraction)

        index = min(
            index,
            len(ordered) - 1,
        )

        return ordered[index]
    
    def run(
        self,
        adapter,
    ):

        rng = Random(self.seed)

        prior = adapter.initial_prior()

        self.weights.clear()
        self._seen_scores.clear()

        state = adapter.initial_state()
        score = adapter.evaluate(state)

        best_state = state
        best_score = score

        for iteration in range(self.iterations):
            temperature = self.temperature(iteration)

            candidates = list(
                adapter.sample_moves(
                    state,
                    rng,
                    self.candidate_pool_size,
                )
            )

            if not candidates:
                raise RuntimeError("Adapter returned an empty candidate pool.")

            move = self.sample_weighted_move(
                state,
                candidates,
                prior,
                rng,
            )

            state_before = state
            old_score = score

            state_after = adapter.apply_move(
                state_before,
                move,
            )

            new_score = adapter.evaluate(state_after)

            accepted = self.accept(
                old_score,
                new_score,
                temperature,
                rng,
            )

            if accepted:
                state = state_after
                score = new_score

            if score < best_score:
                best_state = state
                best_score = score

            # Record the score of the actual current state.
            self._seen_scores.append(score)

            self.update_memory(
                state_before=state_before,
                state_after=state_after,
                move=move,
                old_score=old_score,
                new_score=new_score,
                accepted=accepted,
                prior=prior,
            )

            self.update_good_solution_memory(
                state=state,
                score=score,
                threshold=self._elite_threshold(),
                prior=prior,
                adapter=adapter,
            )

            self.decay_weights()

        return best_state, best_score
