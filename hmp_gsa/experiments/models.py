try:
    from modules.subset import SubsetState as ToyState
except ModuleNotFoundError:  # pragma: no cover - legacy import mode
    from hmp_gsa.modules.subset import SubsetState as ToyState

__all__ = ["ToyState"]
