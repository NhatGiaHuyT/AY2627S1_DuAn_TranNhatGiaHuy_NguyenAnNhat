from __future__ import annotations

from .core import (
    GoodSolutionFrequencyGSA,
    MutationFeatureGSA,
    PriorOnlyGSA,
    SuccessfulFeatureGSA,
    UnguidedGSA,
)
from .settings import engine_kwargs
from .subset import SubsetSelectionAdapter


class ToyMDLAdapter(SubsetSelectionAdapter):
    """Tiny toy problem for verifying the architecture.

    It is NOT the HMP MDL objective.

    The hidden low-cost structure is {1, 2, 3}; the adapter lets GSA exercise
    add/remove mutations and the three memory hypotheses.
    """

    def __init__(self, n_items: int = 20):
        # Pretend this came from HMP's binary co-occurrence matrix.
        super().__init__(n_items=n_items, prior={1: 2.0, 2: 2.0, 3: 2.0})

    def evaluate(self, state):
        useful = len(state.selected & {1, 2, 3})
        noise = len(state.selected - {1, 2, 3})
        return 20.0 - 6.0 * useful + 2.0 * noise


def main():
    adapter = ToyMDLAdapter()

    for cls in (
        UnguidedGSA,
        PriorOnlyGSA,
        SuccessfulFeatureGSA,
        GoodSolutionFrequencyGSA,
        MutationFeatureGSA,
    ):
        algorithm = cls(adapter, **engine_kwargs(seed=42))
        result = algorithm.run()

        print(f"\n{cls.__name__}")
        print("best score:", result.best_score)
        print("best state:", result.best_state)
        print("top weights:", sorted(
            result.weights.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])
        print("evaluations:", result.evaluations)


if __name__ == "__main__":
    main()
