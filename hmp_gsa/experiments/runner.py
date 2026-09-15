import csv
import json
from time import perf_counter
from datetime import datetime
from pathlib import Path

from .gsa import VARIANTS, run_search
from .datasets import load_transactions, resolve_dataset_path
from modules.mdl import DatasetMDLAdapter

def _trace_row(step):
    return {
        "iteration": step.iteration,
        "current_score": step.current_score,
        "candidate_score": step.candidate_score,
        "best_score": step.best_score,
        "temperature": step.temperature,
        "operation": step.move.operation,
        "feature": step.move.feature,
        "accepted": step.accepted,
        "sampled_probability": step.sampled_probability,
        "guidance_key": str(step.guidance_key),
    }


def run(config, output_root="results"):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(output_root) / stamp
    out.mkdir(parents=True)

    (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    runs = []
    search = config["search"]
    guidance = config["guidance"]
    repo_root = Path(__file__).resolve().parents[2]
    progress_enabled = config.get("progress", True)
    total_runs = (
        len(config["datasets"])
        * len(config["variants"])
        * len(config["seeds"])
    )
    completed_runs = 0
    experiment_started = perf_counter()

    def show_progress(message):
        if progress_enabled:
            print(message, end="\r", flush=True)

    for dataset in config["datasets"]:
        dataset_name = dataset["name"]
        dataset_path = resolve_dataset_path(repo_root, dataset["path"])
        transactions = load_transactions(dataset_path)
        for variant_name in config["variants"]:
            cls = VARIANTS[variant_name]
            for seed in config["seeds"]:
                show_progress(
                    f"Starting {completed_runs}/{total_runs}: "
                    f"{dataset_name}/{variant_name}/seed={seed}"
                )
                # Each run gets a fresh adapter so score caches cannot leak
                # between variants or seeds and distort runtime comparisons.
                adapter = DatasetMDLAdapter(
                    transactions,
                    max_pattern_size=dataset.get("max_pattern_size", 2),
                    candidate_sizes=tuple(dataset.get("candidate_sizes", [1, 2])),
                    max_candidates=dataset.get("max_candidates", 10000),
                    move_operations=tuple(
                        dataset.get("move_operations", ["add"])
                    ),
                    prior_multiplier=guidance.get("prior", 1.0),
                )
                initial_score = adapter.evaluate(adapter.initial_state())
                started = perf_counter()
                result = run_search(adapter, cls, seed, search, guidance)
                runtime_seconds = perf_counter() - started
                accepted = sum(step.accepted for step in result.history)
                final_score = (
                    result.history[-1].current_score
                    if result.history
                    else initial_score
                )
                runs.append(
                    {
                        "dataset": dataset_name,
                        "variant": variant_name,
                        "seed": seed,
                        "result": result,
                        "initial_score": initial_score,
                        "final_score": final_score,
                        "accepted_moves": accepted,
                        "acceptance_rate": accepted / len(result.history)
                        if result.history
                        else 0.0,
                        "runtime_seconds": runtime_seconds,
                        "weight_count": len(result.weights),
                    }
                )
                completed_runs += 1
                elapsed = perf_counter() - experiment_started
                average = elapsed / completed_runs
                eta_seconds = average * (total_runs - completed_runs)
                show_progress(
                    f"Progress: {completed_runs}/{total_runs} "
                    f"({completed_runs / total_runs:.0%}) | "
                    f"last={dataset_name}/{variant_name}/seed={seed} | "
                    f"elapsed={elapsed:.1f}s | ETA={eta_seconds:.1f}s"
                )

    if progress_enabled:
        print()

    fields = [
        "dataset",
        "variant",
        "seed",
        "iteration",
        "current_score",
        "candidate_score",
        "best_score",
        "temperature",
        "operation",
        "feature",
        "accepted",
        "sampled_probability",
        "guidance_key",
        "evaluations",
        "runtime_seconds",
    ]
    with open(out / "runs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for run_record in runs:
            result = run_record["result"]
            for step in result.history:
                writer.writerow(
                    {
                        "dataset": run_record["dataset"],
                        "variant": run_record["variant"],
                        "seed": run_record["seed"],
                        **_trace_row(step),
                        "evaluations": result.evaluations,
                        "runtime_seconds": run_record["runtime_seconds"],
                    }
                )

    metric_fields = [
        "dataset",
        "variant",
        "seed",
        "initial_score",
        "best_score",
        "final_score",
        "evaluations",
        "accepted_moves",
        "acceptance_rate",
        "runtime_seconds",
        "weight_count",
    ]
    with open(out / "run_metrics.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metric_fields)
        writer.writeheader()
        for run_record in runs:
            result = run_record["result"]
            writer.writerow(
                {
                    "dataset": run_record["dataset"],
                    "variant": run_record["variant"],
                    "seed": run_record["seed"],
                    "initial_score": run_record["initial_score"],
                    "best_score": result.best_score,
                    "final_score": run_record["final_score"],
                    "evaluations": result.evaluations,
                    "accepted_moves": run_record["accepted_moves"],
                    "acceptance_rate": run_record["acceptance_rate"],
                    "runtime_seconds": run_record["runtime_seconds"],
                    "weight_count": run_record["weight_count"],
                }
            )

    groups = {}
    for run_record in runs:
        groups.setdefault(
            (run_record["dataset"], run_record["variant"]), []
        ).append(run_record)

    with open(out / "summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "dataset",
                "variant",
                "runs",
                "mean_best_score",
                "min_best_score",
                "max_best_score",
                "mean_final_score",
                "mean_evaluations",
                "mean_acceptance_rate",
                "mean_runtime_seconds",
                "mean_weight_count",
            ],
        )
        writer.writeheader()
        for (dataset, variant), group_runs in groups.items():
            best_scores = [run["result"].best_score for run in group_runs]
            writer.writerow(
                {
                    "dataset": dataset,
                    "variant": variant,
                    "runs": len(group_runs),
                    "mean_best_score": sum(best_scores) / len(best_scores),
                    "min_best_score": min(best_scores),
                    "max_best_score": max(best_scores),
                    "mean_final_score": sum(
                        run["final_score"] for run in group_runs
                    ) / len(group_runs),
                    "mean_evaluations": sum(
                        run["result"].evaluations for run in group_runs
                    ) / len(group_runs),
                    "mean_acceptance_rate": sum(
                        run["acceptance_rate"] for run in group_runs
                    ) / len(group_runs),
                    "mean_runtime_seconds": sum(
                        run["runtime_seconds"] for run in group_runs
                    ) / len(group_runs),
                    "mean_weight_count": sum(
                        run["weight_count"] for run in group_runs
                    ) / len(group_runs),
                }
            )

    return out
