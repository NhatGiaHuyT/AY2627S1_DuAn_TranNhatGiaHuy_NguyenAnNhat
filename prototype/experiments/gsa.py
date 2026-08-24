from hmp_gsa.core import (
    GoodSolutionFrequencyGSA,
    MutationFeatureGSA,
    PriorOnlyGSA,
    SearchResult,
    SuccessfulFeatureGSA,
    UnguidedGSA,
)
from hmp_gsa.settings import engine_kwargs


VARIANTS = {
    UnguidedGSA.name: UnguidedGSA,
    PriorOnlyGSA.name: PriorOnlyGSA,
    SuccessfulFeatureGSA.name: SuccessfulFeatureGSA,
    GoodSolutionFrequencyGSA.name: GoodSolutionFrequencyGSA,
    MutationFeatureGSA.name: MutationFeatureGSA,
}


def run_search(adapter, variant_cls, seed, search, guidance) -> SearchResult:
    return variant_cls(adapter, **engine_kwargs(search, guidance, seed)).run()
