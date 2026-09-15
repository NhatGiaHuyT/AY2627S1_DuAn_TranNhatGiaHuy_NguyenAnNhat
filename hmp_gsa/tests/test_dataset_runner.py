import json
import tempfile
import unittest
from pathlib import Path

from hmp_gsa.experiments.runner import run


class TestDatasetExperimentRunner(unittest.TestCase):
    def test_runner_uses_configured_dataset_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            dataset = root / "transactions.txt"
            dataset.write_text("a b\na b\na c\n", encoding="utf-8")
            config = {
                "datasets": [{"name": "fixture", "path": str(dataset), "max_pattern_size": 2}],
                "variants": ["unguided"],
                "seeds": [0],
                "search": {
                    "iterations": 2,
                    "candidate_pool_size": 2,
                    "temperature_start": 1.0,
                    "temperature_end": 0.1,
                    "elite_fraction": 0.5,
                },
                "guidance": {"alpha": 0.1, "decay": 0.01, "prior": 1.0, "epsilon": 1e-9},
            }
            output = run(config, output_root=str(root / "results"))
            summary = (output / "summary.csv").read_text(encoding="utf-8")
            self.assertIn("dataset,variant", summary)
            self.assertIn("fixture,unguided", summary)
            self.assertNotIn("landscape", summary)
            metrics = (output / "run_metrics.csv").read_text(encoding="utf-8")
            self.assertIn("evaluations", metrics.splitlines()[0])
            self.assertIn(",3,", metrics)


if __name__ == "__main__":
    unittest.main()
