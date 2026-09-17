try:
    from modules.models import SearchResult
    from modules.variants import SuccessfulFeatureGSA, GoodSolutionFrequencyGSA, MutationFeatureGSA, UnguidedGSA, PriorOnlyGSA
    from configs.settings import engine_kwargs
except ModuleNotFoundError:  # pragma: no cover - legacy import mode
    from modules.models import SearchResult
    from modules.variants import SuccessfulFeatureGSA, GoodSolutionFrequencyGSA, MutationFeatureGSA, UnguidedGSA, PriorOnlyGSA
    from configs.settings import engine_kwargs


VARIANTS = {
    UnguidedGSA.name: UnguidedGSA,
    PriorOnlyGSA.name: PriorOnlyGSA,
    SuccessfulFeatureGSA.name: SuccessfulFeatureGSA,
    GoodSolutionFrequencyGSA.name: GoodSolutionFrequencyGSA,
    MutationFeatureGSA.name: MutationFeatureGSA,
}