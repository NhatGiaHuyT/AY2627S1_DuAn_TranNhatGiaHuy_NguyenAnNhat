# Experiment protocol

## Question

What representation of search experience is useful for guiding stochastic
MDL-like search under a fixed evaluation budget?

## A
Remember features involved in improving moves.

## B
Remember features that occur in good solutions.

## C
Remember operation-feature pairs.

## Controlled variables

For A/B/C comparisons keep identical:
- seed
- initial state
- objective
- candidate-pool size
- iterations/evaluation budget
- temperature schedule
- prior
- alpha and decay

Controls, also run through `HMPGSA`:
- `unguided`: uniform sampling, no memory
- `prior_only`: static adapter prior, no online updates

The experiment runner uses `DatasetMDLAdapter` and indexed dataset candidates.
Synthetic landscapes remain available as reference code but are not executed by
the runner. Engine kwargs come from `hmp_gsa.settings`.

## Primary measurements

- best objective
- objective versus evaluation count
- evaluations to reach a target
- variance across seeds
- guidance-memory size

## Important

Raw weight magnitudes are not directly comparable across A/B/C because the
update semantics differ.

The configured experiments use real transaction datasets and the repository's
MDL-like adapter. They are not yet a paper-exact HMP implementation: candidate
sizes, candidate cap, and residual/code-table cost must be reported with every
result. Synthetic landscapes are retained only for isolated regression tests.

## Transition to HMP

For paper-faithful comparison:
1. replace the MDL-like adapter with the exact HMP code-table state;
2. keep A/B/C unchanged;
3. compare against HMP-SA under identical budgets;
4. then measure runtime and memory.
