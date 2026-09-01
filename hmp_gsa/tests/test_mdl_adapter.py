import unittest

from hmp_gsa.modules.mdl import DatasetMDLAdapter
from hmp_gsa.modules.models import Move


class TestMDLAdapter(unittest.TestCase):
    def test_mdl_objective_prefers_useful_pattern(self):
        adapter = DatasetMDLAdapter(
            transactions=[(1, 2), (1, 2), (1, 3)],
            max_pattern_size=2,
        )
        empty_state = adapter.initial_state()
        useful_state = adapter.apply_move(empty_state, Move("add", (1, 2)))

        self.assertLess(adapter.evaluate(useful_state), adapter.evaluate(empty_state))

    def test_initial_prior_is_based_on_dataset_support(self):
        adapter = DatasetMDLAdapter(
            transactions=[(1, 2), (1, 2), (1, 3)],
            max_pattern_size=2,
        )
        prior = adapter.initial_prior()
        self.assertGreater(prior[1], 0)
        self.assertGreater(prior[2], 0)
        self.assertGreater(prior[3], 0)

    def test_sample_moves_produces_valid_pattern_neighbors(self):
        adapter = DatasetMDLAdapter(
            transactions=[(1, 2), (1, 2), (1, 3)],
            max_pattern_size=2,
        )
        moves = list(adapter.sample_moves(adapter.initial_state(), __import__("random").Random(0), 5))
        self.assertGreater(len(moves), 0)
        self.assertTrue(all(move.feature for move in moves))


if __name__ == "__main__":
    unittest.main()
