from __future__ import annotations

from typing import Mapping

# Canonical engine settings. `configs/baseline.json` must use these keys.
DEFAULT_SEARCH = {
    "iterations": 30,
    "candidate_pool_size": 5,
    "temperature_start": 2.0,
    "temperature_end": 0.01,
    "elite_fraction": 0.25,
}

DEFAULT_GUIDANCE = {
    "alpha": 0.10,
    "decay": 0.01,
    "prior": 1.0,
    "epsilon": 1e-9,
}


def engine_kwargs(
    search: Mapping | None = None,
    guidance: Mapping | None = None,
    seed: int = 0,
) -> dict:
    search = {**DEFAULT_SEARCH, **dict(search or {})}
    guidance = {**DEFAULT_GUIDANCE, **dict(guidance or {})}
    return {
        "iterations": search["iterations"],
        "temperature_start": search["temperature_start"],
        "temperature_end": search["temperature_end"],
        "candidate_pool_size": search["candidate_pool_size"],
        "alpha": guidance["alpha"],
        "decay": guidance["decay"],
        "elite_fraction": search["elite_fraction"],
        "seed": seed,
        "epsilon": guidance["epsilon"],
    }
