from typing import Any, Hashable
from dataclasses import dataclass

Feature = Hashable
GuidanceKey = Hashable

@dataclass(frozen=True)
class Move:
    operation: str
    feature: Feature
    payload: Any = None

@dataclass
class StepRecord:
    iteration: int
    current_score: float
    candidate_score: float
    best_score: float
    accepted: bool
    temperature: float
    move: Move
    sampled_probability: float
    guidance_key: GuidanceKey


@dataclass
class SearchResult:
    best_state: Any
    best_score: float
    history: list[StepRecord]
    weights: dict[GuidanceKey, float]
    evaluations: int