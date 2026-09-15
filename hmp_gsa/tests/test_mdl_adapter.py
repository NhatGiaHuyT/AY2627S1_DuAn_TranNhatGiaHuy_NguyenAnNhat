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
        self.assertGreater(prior[(1,)], 0)
        self.assertGreater(prior[(2,)], 0)
        self.assertGreater(prior[(3,)], 0)

    def test_initial_prior_uses_pattern_keys_for_moves(self):
        adapter = DatasetMDLAdapter(
            transactions=[("a", "b"), ("a", "b"), ("a", "c")],
            max_pattern_size=2,
        )
        prior = adapter.initial_prior()

        self.assertEqual(prior[("a",)], 4.0)
        self.assertEqual(prior[("a", "b")], 3.0)
        self.assertNotIn("a", prior)

    def test_sample_moves_produces_valid_pattern_neighbors(self):
        adapter = DatasetMDLAdapter(
            transactions=[(1, 2), (1, 2), (1, 3)],
            max_pattern_size=2,
        )
        moves = list(adapter.sample_moves(adapter.initial_state(), __import__("random").Random(0), 5))
        self.assertGreater(len(moves), 0)
        self.assertTrue(all(move.feature for move in moves))

    def test_operation_neighborhood_supports_remove_and_replace(self):
        adapter = DatasetMDLAdapter(
            transactions=[("a", "b"), ("a", "b"), ("a", "c")],
            max_pattern_size=2,
            move_operations=("add", "remove", "replace"),
        )
        initial = adapter.initial_state()
        added = adapter.apply_move(initial, Move("add", ("a", "b")))
        moves = list(adapter.sample_moves(added, __import__("random").Random(1), 50))

        self.assertTrue(any(move.operation == "remove" for move in moves))
        self.assertTrue(any(move.operation == "replace" for move in moves))
        removed = adapter.apply_move(added, Move("remove", ("a", "b")))
        self.assertEqual(removed.code_table, frozenset())


if __name__ == "__main__":
    unittest.main()
