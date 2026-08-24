from modules.models import SearchResult
from modules.control_group import UnguidedGSA, PriorOnlyGSA
from modules.variants import SuccessfulFeatureGSA, GoodSolutionFrequencyGSA, MutationFeatureGSA
from configs.settings import engine_kwargs


VARIANTS = {
    UnguidedGSA.name: UnguidedGSA,
    PriorOnlyGSA.name: PriorOnlyGSA,
    SuccessfulFeatureGSA.name: SuccessfulFeatureGSA,
    GoodSolutionFrequencyGSA.name: GoodSolutionFrequencyGSA,
    MutationFeatureGSA.name: MutationFeatureGSA,
}


def run_search(adapter, variant_cls, seed, search, guidance) -> SearchResult:
    return variant_cls(adapter, **engine_kwargs(search, guidance, seed)).run()
