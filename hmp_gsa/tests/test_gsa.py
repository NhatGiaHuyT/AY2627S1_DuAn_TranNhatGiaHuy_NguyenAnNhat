import json
import sys
import unittest
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from .. import VARIANTS, run_search
from experiments.landscapes import SyntheticLandscape
from modules.models import Move
from modules.control_group import PriorOnlyGSA, UnguidedGSA
from modules.variants import SuccessfulFeatureGSA, GoodSolutionFrequencyGSA, MutationFeatureGSA
from modules.subset import SubsetSelectionAdapter
from scripts.demo import ToyMDLAdapter
from configs.settings import DEFAULT_GUIDANCE, DEFAULT_SEARCH, engine_kwargs


REPO = Path(__file__).resolve().parents[1]


class TestGSAArchitecture(unittest.TestCase):
    def setUp(self):
        self.adapter = ToyMDLAdapter()

    def test_all_variants_run(self):
        for cls in (
            UnguidedGSA,
            PriorOnlyGSA,
            SuccessfulFeatureGSA,
            GoodSolutionFrequencyGSA,
            MutationFeatureGSA,
        ):
            with self.subTest(variant=cls.__name__):
                result = cls(
                    self.adapter,
                    iterations=100,
                    candidate_pool_size=3,
                    seed=123,
                ).run()

                self.assertIsNotNone(result.best_state)
                self.assertTrue(result.evaluations > 0)

    def test_variant_a_reinforces_improving_feature(self):
        alg = SuccessfulFeatureGSA(
            self.adapter,
            iterations=1,
            alpha=1.0,
            decay=0.0,
        )

        alg.weights[1] = 1.0

        alg.update_memory(
            move=Move("add", 1),
            old_score=10,
            new_score=7,
            accepted=True,
            state_before=None,
            state_after=None,
        )

        self.assertEqual(alg.weights[1], 4.0)

    def test_variant_c_separates_operation(self):
        alg = MutationFeatureGSA(
            self.adapter,
            iterations=1,
            alpha=1.0,
            decay=0.0,
        )

        add_key = alg.key_for_move(Move("add", 1))
        remove_key = alg.key_for_move(Move("remove", 1))

        self.assertNotEqual(add_key, remove_key)

    def test_candidate_pool_is_not_full_neighborhood(self):
        moves = list(self.adapter.sample_moves(
            self.adapter.initial_state(),
            Random(1),
            pool_size=2,
        ))
        self.assertLessEqual(len(moves), 4)

    def test_unguided_does_not_learn(self):
        result = UnguidedGSA(
            self.adapter,
            iterations=80,
            alpha=10.0,
            decay=0.5,
            seed=0,
        ).run()
        self.assertTrue(result.weights)
        self.assertTrue(all(weight == 1.0 for weight in result.weights.values()))


class TestSharedExperimentSurface(unittest.TestCase):
    def test_neighborhood_code_is_shared(self):
        self.assertIs(
            ToyMDLAdapter.sample_moves,
            SubsetSelectionAdapter.sample_moves,
        )
        self.assertIs(
            SyntheticLandscape.sample_moves,
            SubsetSelectionAdapter.sample_moves,
        )
        self.assertIs(ToyMDLAdapter.apply_move, SubsetSelectionAdapter.apply_move)
        self.assertIs(SyntheticLandscape.apply_move, SubsetSelectionAdapter.apply_move)

    def test_experiment_variants_are_core_classes(self):
        self.assertIs(VARIANTS["unguided"], UnguidedGSA)
        self.assertIs(VARIANTS["prior_only"], PriorOnlyGSA)
        self.assertIs(VARIANTS["successful_feature"], SuccessfulFeatureGSA)
        self.assertIs(VARIANTS["good_solution_frequency"], GoodSolutionFrequencyGSA)
        self.assertIs(VARIANTS["mutation_feature"], MutationFeatureGSA)

    def test_baseline_config_matches_engine_schema(self):
        config = json.loads((REPO / "configs" / "baseline.json").read_text(encoding="utf-8"))
        self.assertEqual(config["search"], DEFAULT_SEARCH)
        self.assertEqual(config["guidance"], DEFAULT_GUIDANCE)

    def test_experiment_run_search_uses_engine_kwargs(self):
        adapter = SyntheticLandscape("success_sensitive", n_features=8)
        result = run_search(
            adapter,
            UnguidedGSA,
            seed=1,
            search={"iterations": 15, "candidate_pool_size": 3},
            guidance={},
        )
        self.assertEqual(len(result.history), 15)
        expected = engine_kwargs(
            {"iterations": 15, "candidate_pool_size": 3}, {}, seed=1
        )
        self.assertEqual(expected["epsilon"], DEFAULT_GUIDANCE["epsilon"])


if __name__ == "__main__":
    unittest.main()
