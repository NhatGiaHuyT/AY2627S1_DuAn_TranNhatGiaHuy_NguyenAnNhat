import csv
import json
from datetime import datetime
from pathlib import Path

from .gsa import VARIANTS, run_search
from .landscapes import SyntheticLandscape


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
    landscape_cfg = config["landscape"]

    for landscape_name in config["landscapes"]:
        adapter = SyntheticLandscape(
            landscape_name,
            landscape_cfg["n_features"],
            prior=guidance.get("prior", 1.0),
        )
        for variant_name in config["variants"]:
            cls = VARIANTS[variant_name]
            for seed in config["seeds"]:
                result = run_search(adapter, cls, seed, search, guidance)
                runs.append((landscape_name, variant_name, seed, result))

    fields = [
        "landscape",
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
    ]
    with open(out / "runs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for landscape, variant, seed, result in runs:
            for step in result.history:
                writer.writerow(
                    {
                        "landscape": landscape,
                        "variant": variant,
                        "seed": seed,
                        **_trace_row(step),
                    }
                )

    groups = {}
    for landscape, variant, seed, result in runs:
        groups.setdefault((landscape, variant), []).append(result.best_score)

    with open(out / "summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "landscape",
                "variant",
                "runs",
                "mean_best_score",
                "min_best_score",
                "max_best_score",
            ],
        )
        writer.writeheader()
        for (landscape, variant), scores in groups.items():
            writer.writerow(
                {
                    "landscape": landscape,
                    "variant": variant,
                    "runs": len(scores),
                    "mean_best_score": sum(scores) / len(scores),
                    "min_best_score": min(scores),
                    "max_best_score": max(scores),
                }
            )

    return out
