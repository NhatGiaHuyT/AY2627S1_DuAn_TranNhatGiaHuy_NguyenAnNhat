from abc import ABC, abstractmethod
from random import Random
from math import exp
from typing import Any, Mapping, Optional

from .adapter import GSAAdapter
from .models import Feature, GuidanceKey, Move, StepRecord, SearchResult

class HMPGSA(ABC):
    """Shared Guided-SA engine.

    Variants only define:
      - what key represents memory
      - how a key is initialized from the HMP prior
      - how a successful search event updates memory
      - how a good solution updates memory

    The SA acceptance rule and stochastic candidate selection are identical
    across variants.
    """

    def __init__(
        self,
        adapter: GSAAdapter,
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
        self.adapter = adapter
        self.iterations = iterations
        self.temperature_start = temperature_start
        self.temperature_end = temperature_end
        self.candidate_pool_size = candidate_pool_size
        self.alpha = alpha
        self.decay = decay
        self.elite_fraction = elite_fraction
        self.rng = Random(seed)
        self.epsilon = epsilon

        self.weights: dict[GuidanceKey, float] = {}
        self._seen_scores: list[float] = []

    # ---------- temperature / SA ----------

    def temperature(self, iteration: int) -> float:
        if self.iterations <= 1:
            return self.temperature_end
        ratio = iteration / (self.iterations - 1)
        # Log-linear cooling avoids negative temperatures and gives both
        # endpoints exactly.
        return self.temperature_start * (
            self.temperature_end / self.temperature_start
        ) ** ratio

    def accept(self, delta: float, temperature: float) -> bool:
        if delta <= 0:
            return True
        return self.rng.random() < exp(-delta / max(temperature, self.epsilon))

    # ---------- guidance ----------

    @abstractmethod
    def key_for_move(self, move: Move) -> GuidanceKey:
        raise NotImplementedError

    @abstractmethod
    def initial_weight(self, key: GuidanceKey, prior: Mapping[Feature, float]) -> float:
        raise NotImplementedError

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
        """Variant hook. Base implementation does nothing."""
        return None

    def update_good_solution_memory(
        self,
        *,
        state: Any,
        score: float,
        elite_threshold: Optional[float],
    ) -> None:
        """Variant hook. Base implementation does nothing."""
        return None

    def decay_weights(self) -> None:
        if self.decay <= 0:
            return
        factor = max(0.0, 1.0 - self.decay)
        for key in list(self.weights):
            self.weights[key] *= factor
            if self.weights[key] < self.epsilon:
                del self.weights[key]

    def _ensure_weight(self, key: GuidanceKey, prior: Mapping[Feature, float]) -> float:
        if key not in self.weights:
            self.weights[key] = max(
                self.epsilon, float(self.initial_weight(key, prior))
            )
        return self.weights[key]

    def sample_weighted_move(
        self, moves: list[Move], prior: Mapping[Feature, float]
    ) -> tuple[Move, float, GuidanceKey]:
        if not moves:
            raise ValueError("Adapter returned an empty candidate pool.")

        keys = [self.key_for_move(m) for m in moves]
        weights = [self._ensure_weight(k, prior) for k in keys]
        total = sum(weights)

        if total <= 0:
            # Defensive fallback. This should only occur with malformed priors.
            index = self.rng.randrange(len(moves))
            return moves[index], 1.0 / len(moves), keys[index]

        r = self.rng.random() * total
        cumulative = 0.0
        for move, key, weight in zip(moves, keys, weights):
            cumulative += weight
            if r <= cumulative:
                return move, weight / total, key

        return moves[-1], weights[-1] / total, keys[-1]


    def run(self) -> SearchResult:
        state = self.adapter.initial_state()
        current_score = self.adapter.evaluate(state)
        evaluations = 1

        best_state = state
        best_score = current_score
        history: list[StepRecord] = []
        prior = self.adapter.initial_prior()

        # Used only for the "good solution" threshold. We do not store states.
        self._seen_scores = [current_score]

        for iteration in range(self.iterations):
            temperature = self.temperature(iteration)

            moves = list(
                self.adapter.sample_moves(
                    state, self.rng, self.candidate_pool_size
                )
            )
            if not moves:
                continue

            move, sampled_probability, key = self.sample_weighted_move(moves, prior)
            candidate = self.adapter.apply_move(state, move)
            candidate_score = self.adapter.evaluate(candidate)
            evaluations += 1

            delta = candidate_score - current_score
            accepted = self.accept(delta, temperature)

            old_state = state
            if accepted:
                state = candidate
                current_score = candidate_score

            if candidate_score < best_score:
                best_score = candidate_score
                best_state = candidate

            # Store scores, not states. This keeps historical memory small.
            self._seen_scores.append(candidate_score)

            elite_threshold = self._elite_threshold()
            self.update_memory(
                move=move,
                old_score=current_score if not accepted else current_score - delta,
                new_score=candidate_score,
                accepted=accepted,
                state_before=old_state,
                state_after=candidate,
            )
            self.update_good_solution_memory(
                state=candidate if candidate_score <= current_score else state,
                score=candidate_score,
                elite_threshold=elite_threshold,
            )
            self.decay_weights()

            history.append(
                StepRecord(
                    iteration=iteration,
                    current_score=current_score,
                    candidate_score=candidate_score,
                    best_score=best_score,
                    accepted=accepted,
                    temperature=temperature,
                    move=move,
                    sampled_probability=sampled_probability,
                    guidance_key=key,
                )
            )

        return SearchResult(
            best_state=best_state,
            best_score=best_score,
            history=history,
            weights=dict(self.weights),
            evaluations=evaluations,
        )

    def _elite_threshold(self) -> Optional[float]:
        if not self._seen_scores:
            return None
        values = sorted(self._seen_scores)
        index = min(
            len(values) - 1,
            max(0, int(len(values) * self.elite_fraction)),
        )
        return values[index]