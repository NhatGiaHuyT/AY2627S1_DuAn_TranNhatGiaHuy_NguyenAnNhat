import csv
import json
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, stdev
from typing import Any

from tqdm import tqdm

from .prior_scan import process_dataset

from .gsa import (
    UnguidedGSA,
    PriorOnlyGSA,
    SuccessfulFeatureGSA,
    GoodSolutionFrequencyGSA,
    MutationFeatureGSA,
)

from ..modules.adapter import GSAAdapter
from ..modules.mdl import DatasetMDLAdapter


VARIANTS = {
    "unguided": UnguidedGSA,
    "prior_only": PriorOnlyGSA,
    "successful_feature": SuccessfulFeatureGSA,
    "good_solution_frequency": GoodSolutionFrequencyGSA,
    "mutation_feature": MutationFeatureGSA,
}


def load_config(
    path: str,
) -> dict:

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def prepare_dataset(
    dataset: dict,
) -> str:
    """
    Generate the dataset-derived prior artifacts.

    This runs once per dataset, before any
    variant/seed experiments.

    Returns the derived dataset directory.
    """

    return process_dataset(
        name=dataset["name"],
        file_path=dataset["path"],
        output_root="derived",
    )


def build_engine(
    variant_name: str,
    config: dict,
    seed: int,
):
    try:
        engine_class = VARIANTS[
            variant_name
        ]

    except KeyError:
        raise ValueError(
            f"Unknown variant: {variant_name}"
        ) from None

    search = config["search"]
    guidance = config["guidance"]

    return engine_class(
        iterations=search["iterations"],
        candidate_pool_size=search[
            "candidate_pool_size"
        ],
        temperature_start=search[
            "temperature_start"
        ],
        temperature_end=search[
            "temperature_end"
        ],
        elite_fraction=search[
            "elite_fraction"
        ],
        alpha=guidance["alpha"],
        decay=guidance["decay"],
        epsilon=guidance["epsilon"],
        seed=seed,
    )


def build_adapter(
    dataset: dict,
    derived_path: str,
) -> GSAAdapter:

    with open(
        dataset["path"],
        "r",
        encoding="utf-8",
    ) as file:
        transactions = [
            tuple(
                int(item)
                for item in line.split()
            )
            for line in file
            if line.strip()
        ]

    return DatasetMDLAdapter(
        transactions=transactions,
        max_pattern_size=dataset[
            "max_pattern_size"
        ],
        candidate_sizes=tuple(
            dataset["candidate_sizes"]
        ),
        max_candidates=dataset[
            "max_candidates"
        ],
        move_operations=tuple(
            dataset["move_operations"]
        ),
        cooccurrence_path=(
            f"{derived_path}/cooccurrence.csv"
        ),
    )


def run_variant(
    dataset: dict,
    derived_path: str,
    variant_name: str,
    config: dict,
    seed: int,
) -> dict[str, Any]:

    engine = build_engine(
        variant_name=variant_name,
        config=config,
        seed=seed,
    )

    adapter = build_adapter(
        dataset=dataset,
        derived_path=derived_path,
    )

    best_state, best_score = engine.run(
        adapter
    )

    return {
        "dataset": dataset["name"],
        "variant": variant_name,
        "seed": seed,
        "best_score": best_score,
        "best_state": best_state,
    }


def save_results(
    dataset_name: str,
    results: list[dict[str, Any]],
) -> None:
    """
    Save raw experiment results and an aggregated
    summary for one dataset.
    """

    output_dir = os.path.join(
        "results",
        dataset_name.lower(),
    )

    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    # --------------------------------------------------------------
    # Raw results
    # --------------------------------------------------------------

    runs_path = os.path.join(
        output_dir,
        "runs.csv",
    )

    with open(
        runs_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "dataset",
            "variant",
            "seed",
            "best_score",
        ])

        for result in results:
            writer.writerow([
                result["dataset"],
                result["variant"],
                result["seed"],
                result["best_score"],
            ])

    # --------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------

    scores_by_variant = defaultdict(list)

    for result in results:
        scores_by_variant[
            result["variant"]
        ].append(
            result["best_score"]
        )

    summary_path = os.path.join(
        output_dir,
        "summary.csv",
    )

    with open(
        summary_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "dataset",
            "variant",
            "runs",
            "mean",
            "std",
            "best",
            "worst",
        ])

        for variant in scores_by_variant:
            scores = scores_by_variant[
                variant
            ]

            writer.writerow([
                dataset_name,
                variant,
                len(scores),
                mean(scores),
                (
                    stdev(scores)
                    if len(scores) > 1
                    else 0.0
                ),
                min(scores),
                max(scores),
            ])

    print(
        f"Results saved → {output_dir}"
    )


def run_dataset(
    dataset: dict,
    config: dict,
    max_workers: int | None = None,
) -> list[dict[str, Any]]:

    name = dataset["name"]

    variants = config["variants"]
    seeds = config["seeds"]

    print(
        f"\n{'=' * 60}"
    )
    print(
        f"DATASET: {name}"
    )
    print(
        f"{'=' * 60}"
    )

    # --------------------------------------------------------------
    # Dataset preprocessing
    # --------------------------------------------------------------

    derived_path = prepare_dataset(
        dataset
    )

    # --------------------------------------------------------------
    # Experiment jobs
    # --------------------------------------------------------------

    jobs = [
        (
            variant_name,
            seed,
        )
        for variant_name in variants
        for seed in seeds
    ]

    results = []

    with ThreadPoolExecutor(
        max_workers=max_workers,
    ) as executor:

        futures = {
            executor.submit(
                run_variant,
                dataset,
                derived_path,
                variant_name,
                config,
                seed,
            ): (
                variant_name,
                seed,
            )
            for variant_name, seed in jobs
        }

        progress_enabled = config.get(
            "progress",
            True,
        )

        if progress_enabled:

            with tqdm(
                total=len(futures),
                desc=f"{name}",
                unit="run",
                dynamic_ncols=True,
            ) as progress:

                for future in as_completed(
                    futures
                ):

                    variant_name, seed = futures[
                        future
                    ]

                    result = future.result()

                    results.append(result)

                    progress.set_postfix_str(
                        f"{variant_name} | "
                        f"seed={seed} | "
                        f"best={result['best_score']:.0f}"
                    )

                    progress.update(1)

        else:

            for future in as_completed(
                futures
            ):

                result = future.result()

                results.append(result)

    # --------------------------------------------------------------
    # Deterministic result ordering
    # --------------------------------------------------------------

    variant_order = {
        variant: index
        for index, variant in enumerate(
            variants
        )
    }

    seed_order = {
        seed: index
        for index, seed in enumerate(
            seeds
        )
    }

    results.sort(
        key=lambda result: (
            variant_order[
                result["variant"]
            ],
            seed_order[
                result["seed"]
            ],
        )
    )

    # --------------------------------------------------------------
    # Persist results
    # --------------------------------------------------------------

    save_results(
        dataset_name=name,
        results=results,
    )

    return results


def run(
    config: dict,
    max_workers: int | None = None,
) -> list[dict[str, Any]]:

    all_results = []

    configured_workers = config.get(
        "parallel",
        {},
    ).get(
        "max_workers"
    )

    workers = (
        max_workers
        if max_workers is not None
        else configured_workers
    )

    for dataset in config[
        "datasets"
    ]:

        all_results.extend(
            run_dataset(
                dataset=dataset,
                config=config,
                max_workers=workers,
            )
        )

    print(
        f"\n{'=' * 60}"
    )
    print(
        "EXPERIMENT COMPLETE"
    )
    print(
        f"{'=' * 60}"
    )

    return all_results