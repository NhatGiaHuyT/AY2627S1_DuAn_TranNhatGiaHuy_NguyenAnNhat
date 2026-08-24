import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.landscapes import SyntheticLandscape
from experiments.models import ToyState
from modules.control_group import UnguidedGSA
from modules.variants import (
    GoodSolutionFrequencyGSA,
    Move,
    MutationFeatureGSA,
    SuccessfulFeatureGSA,
)

class TestGSAVariants(unittest.TestCase):
    def test_a(self):
        adapter = SyntheticLandscape("success_sensitive")
        g = SuccessfulFeatureGSA(adapter, iterations=1, alpha=1.0, decay=0.0)
        g.weights[3] = 1.0
        g.update_memory(
            move=Move("add", 3),
            old_score=10,
            new_score=8,
            accepted=True,
            state_before=None,
            state_after=None,
        )
        assert g.weights[3] > 1.0


    def test_b(self):
        adapter = SyntheticLandscape("frequency_sensitive")
        g = GoodSolutionFrequencyGSA(adapter, iterations=1, alpha=0.1, decay=0.0)
        g.update_good_solution_memory(
            state=ToyState(frozenset({1, 3})),
            score=0.0,
            elite_threshold=1.0,
        )
        assert g.weights[1] > 0 and g.weights[3] > 0


    def test_c(self):
        adapter = SyntheticLandscape("operation_sensitive")
        g = MutationFeatureGSA(adapter, iterations=1, alpha=1.0, decay=0.0)
        add_move = Move("add", 3)
        remove_move = Move("remove", 3)
        assert g.key_for_move(add_move) != g.key_for_move(remove_move)

        g.weights[g.key_for_move(add_move)] = 1.0
        g.update_memory(
            move=add_move,
            old_score=10,
            new_score=8,
            accepted=True,
            state_before=None,
            state_after=None,
        )
        assert g.weights[g.key_for_move(add_move)] > 1.0
        assert g.key_for_move(remove_move) not in g.weights


    def test_unguided_ignores_improvement(self):
        adapter = SyntheticLandscape("success_sensitive")
        g = UnguidedGSA(adapter, iterations=1, alpha=10.0, decay=0.5)
        g.weights[3] = 1.0
        g.update_memory(
            move=Move("add", 3),
            old_score=10,
            new_score=1,
            accepted=True,
            state_before=None,
            state_after=None,
        )
        g.decay_weights()
        assert g.weights[3] == 1.0

if __name__ == "__main__":
    unittest.main()