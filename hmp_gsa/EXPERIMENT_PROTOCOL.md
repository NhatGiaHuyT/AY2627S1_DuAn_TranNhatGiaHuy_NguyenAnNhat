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

Neighborhood sampling is `SubsetSelectionAdapter` for both `hmp_gsa.demo`
and `experiments`. Engine kwargs come from `hmp_gsa.settings`.

## Primary measurements

- best objective
- objective versus evaluation count
- evaluations to reach a target
- variance across seeds
- guidance-memory size

## Important

Raw weight magnitudes are not directly comparable across A/B/C because the
update semantics differ.

The synthetic landscapes are deliberately controlled thought experiments.
They do not establish an HMP/MDL result.

## Transition to HMP

After the hypotheses are understood:
1. wrap the real HMP code behind the same interface;
2. keep A/B/C unchanged;
3. compare against HMP-SA under identical budgets;
4. then measure runtime and memory.
