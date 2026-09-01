from __future__ import annotations

try:
    from modules.subset import SubsetSelectionAdapter
except ModuleNotFoundError:  # pragma: no cover - legacy import mode
    from modules.subset import SubsetSelectionAdapter


class SyntheticLandscape(SubsetSelectionAdapter):
    """Controlled synthetic objectives, not MDL."""

    def __init__(self, name: str, n_features: int = 20, prior: float = 1.0):
        super().__init__(n_items=n_features, prior=prior)
        self.name = name

    @property
    def n_features(self) -> int:
        return self.n_items

    def evaluate(self, state) -> float:
        # Lower is better.
        s = state.selected
        score = 20.0

        if self.name == "success_sensitive":
            score -= 5 * len(s & {1, 2, 3})
            score += 0.4 * max(0, len(s) - 3)

        elif self.name == "frequency_sensitive":
            if {1, 2, 3}.issubset(s):
                score -= 15
            score += 0.3 * len(s)

        elif self.name == "operation_sensitive":
            score -= 4.5 * len(s & {1, 2, 3})
            score += 0.35 * max(0, len(s) - 3)

        elif self.name == "deceptive":
            score -= 3 * len(s & {4, 5})
            if {1, 2, 3}.issubset(s):
                score -= 12
            score += 0.5 * len(s)

        elif self.name == "sparse_optimum":
            if {7, 11, 13}.issubset(s):
                score -= 17
            score += 0.25 * len(s)

        else:
            raise ValueError(f"Unknown landscape: {self.name}")

        return score
