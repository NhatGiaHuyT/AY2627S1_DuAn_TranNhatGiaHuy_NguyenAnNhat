import csv
import tempfile
import unittest
from pathlib import Path

from hmp_gsa.modules.models import Move
from hmp_gsa.modules.subset import SubsetSelectionAdapter
from hmp_gsa.modules.variants import SuccessfulFeatureGSA
from hmp_gsa.scripts.prior_scan import process_dataset, scan_dataset


class DynamicPriorAdapter(SubsetSelectionAdapter):
    def __init__(self):
        super().__init__(n_items=3, prior={1: 2.0, 2: 1.0, 3: 1.0})

    def evaluate(self, state):
        return 0.0

    def prior_weight(self, state, move, prior=None):
        return 3.0 if move.feature == 1 else 0.5


class TestDatasetPriorAndPersistence(unittest.TestCase):
    def test_scan_dataset_reports_expected_stats(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            dataset_path = Path(tmp_dir) / "toy.txt"
            dataset_path.write_text("1 2\n1 3\n2 3\n", encoding="utf-8")

            result = scan_dataset(str(dataset_path))

            self.assertEqual(result["size_D"], 3)
            self.assertEqual(result["distinct_I"], 3)
            self.assertAlmostEqual(result["atl"], 2.0)
            self.assertAlmostEqual(result["density"], 66.666666666666666)
            self.assertEqual(result["item_frequency"]["1"], 2)
            self.assertEqual(result["item_frequency"]["2"], 2)
            self.assertEqual(result["item_frequency"]["3"], 2)
            self.assertEqual(result["pair_cooccurrence"][("1", "2")], 1)
            self.assertEqual(result["pair_cooccurrence"][("1", "3")], 1)
            self.assertEqual(result["pair_cooccurrence"][("2", "3")], 1)

    def test_process_dataset_persists_deterministic_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            dataset_path = Path(tmp_dir) / "toy.txt"
            dataset_path.write_text("1 2\n1 3\n2 3\n", encoding="utf-8")
            output_root = Path(tmp_dir) / "derived"

            first = process_dataset("toy", str(dataset_path), output_root=str(output_root))
            second = process_dataset("toy", str(dataset_path), output_root=str(output_root))

            self.assertTrue(Path(first, "statistics.json").exists())
            self.assertTrue(Path(first, "item_frequency.csv").exists())
            self.assertTrue(Path(first, "cooccurrence.csv").exists())
            self.assertEqual(
                Path(first, "statistics.json").read_text(encoding="utf-8"),
                Path(second, "statistics.json").read_text(encoding="utf-8"),
            )

            with open(Path(first, "cooccurrence.csv"), newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 3)
            lookup = {(row["item_i"], row["item_j"]): int(row["cooccurrence"]) for row in rows}
            self.assertEqual(lookup[("1", "2")], 1)
            self.assertEqual(lookup[("1", "3")], 1)
            self.assertEqual(lookup[("2", "3")], 1)

    def test_prior_integration_uses_initial_prior_and_dynamic_multiplier(self):
        adapter = DynamicPriorAdapter()
        algorithm = SuccessfulFeatureGSA(adapter, iterations=1, alpha=1.0, decay=0.0)

        self.assertEqual(
            algorithm._ensure_weight(1, adapter.initial_prior()),
            2.0,
        )
        self.assertEqual(
            algorithm._ensure_weight(99, adapter.initial_prior()),
            1.0,
        )

        state = adapter.initial_state()
        move = Move("add", 1)
        self.assertAlmostEqual(
            algorithm._candidate_weight(move, state, adapter.initial_prior()),
            6.0,
        )

        move_missing = Move("add", 2)
        self.assertAlmostEqual(
            algorithm._candidate_weight(move_missing, state, adapter.initial_prior()),
            0.5,
        )


if __name__ == "__main__":
    unittest.main()
