# HMP-GSA presentation review and extension

## Purpose

This document is a corrected, slide-ready extension for the supplied HMP-GSA presentation. It records claims that need qualification and adds findings from the current repository so the presentation distinguishes:

- the original Java HMP-SA implementation;
- the Python Guided-SA research prototype;
- the dataset preprocessing layer;
- the current MDL-like adapter; and
- results that are genuinely measured versus results that remain hypotheses.

The supplied deck is available as a PDF attachment, but no editable `.pptx`/`.odp` source is present in the workspace. These sections can therefore be copied into the presentation manually or used as the content specification for an editable rebuild.

## Corrections to existing slides

### 1. MDL delta and Metropolis sign

The presentation must use one convention consistently. Recommended convention:

```text
Delta_MDL = L(candidate, D) - L(current, D)
```

Because MDL is minimized:

```text
Delta_MDL < 0  -> candidate improves compression -> accept
Delta_MDL = 0  -> equal objective -> accept
Delta_MDL > 0  -> candidate is worse -> accept with exp(-Delta_MDL / T)
```

The Java implementation uses the equivalent savings convention:

```text
savings = currentCompressionSize - newCompressionSize
```

Therefore, a slide that says `L(current) - L(candidate) < 0` for an improvement is incorrect. The sign should be reversed, or the variable should be renamed to `savings`.

### 2. Co-occurrence matrix complexity

The sparse triangular matrix supports direct lookup of a stored pair. That is an `O(1)` lookup claim under the implementation assumptions. It is not correct to present the complete greedy selection process as `O(1)`:

- building the matrix scans transactions and their item pairs;
- clearing and rebuilding it after residual reduction scans the current database again;
- finding the maximum pair may scan stored entries unless an additional priority structure is maintained.

Safer wording:

> The sparse matrix avoids rescanning the whole database for every pair-support query. It reduces memory use for sparse pair structure and accelerates individual support lookup; total mining cost still depends on the number of transactions, pairs, and rebuilds.

### 3. “Binary co-occurrence matrix” versus learned memory

The matrix is a dataset-derived prior or heuristic signal. It is not the learned GSA memory. The learned memory is the weight map updated from search events. The presentation should show two separate arrows:

```text
Dataset -> co-occurrence prior W_prior
Search trajectory -> learned memory W_learned
```

They may both affect sampling, but they have different meanings and must not be called the same memory.

### 4. HMP-SA versus the Python prototype

The original Java runner is not identical to the Python engine. The Java runner has:

- an outer loop adding accepted patterns to `codetable`;
- an inner SA loop over a candidate pattern;
- dynamic residual-database reduction after accepting a useful pattern;
- a later pair-pattern filling phase using the sparse matrix.

The Python engine has a generic one-candidate-per-iteration Guided-SA loop. It is designed as an adapter boundary and does not yet reproduce every Java state transition.

### 5. HMP-GSA slides containing placeholder text

The supplied pages for the HMP-GSA, Feature Weight Vector, three-layer weight, and Multinomial Sampling sections contain Lorem Ipsum rather than technical content. These pages should be replaced with the extension sections below. The placeholder text is not merely a style issue: it leaves the central contribution, update equations, controls, and evidence undefined.

### 6. Claims about experimental proof

The current synthetic results do not prove that HMP-GSA improves HMP/MDL mining. They test whether the three memory hypotheses behave differently on controlled objectives. The deck should explicitly label them:

> Synthetic hypothesis-validation results; not real-dataset MDL results.

The real Java output on `iris.txt` is evidence that the legacy HMP-SA pipeline runs and produces a code table. It is not a comparison against Python HMP-GSA because the two pipelines do not yet share the same adapter, state, budget, or evaluator implementation.

## Replacement and extension slides

### Slide A — What has actually been implemented

**Title:** Current implementation boundary

```text
Implemented and tested
----------------------
1. Generic Guided-SA engine
2. Unguided and prior-only controls
3. Successful-feature, good-solution, and mutation-feature variants
4. Dataset scan with item frequency and pair co-occurrence persistence
5. MDL-like pattern/residual adapter
6. Regression tests and reproducible synthetic runner

Still required for paper-faithful HMP-GSA
-----------------------------------------
1. Exact HMP code-table state and usage coding
2. Exact Java-compatible neighborhood and residual semantics
3. Real adapter wiring from dataset files to the GSA loop
4. Matched HMP-SA versus HMP-GSA experiments
```

**Speaker note:** This is a prototype with a clear research boundary, not a claim that all paper details have already been reproduced.

### Slide B — Actual architecture

**Title:** Repository architecture and data flow

```text
transaction file D
      |
      v
prior_scan.py
      |
      +--> statistics.json
      +--> item_frequency.csv
      +--> cooccurrence.csv
      |
      v
Dataset-derived prior
      |
      v
GSAAdapter <-----------------------------+
      |                                  |
      +--> initial_state()               |
      +--> sample_moves()                |
      +--> apply_move()                  |
      +--> evaluate()                    |
      +--> features_of()                 |
                                         |
                                         v
                                  HMPGSA engine
                                  - sample one move
                                  - evaluate candidate
                                  - SA acceptance
                                  - update W
                                  - decay W
```

**Important:** the current experiment runner uses synthetic landscapes. The dataset scanner and MDL-like adapter exist, but they are not yet the default end-to-end experiment command. A live probe on the full `accident.txt` dataset was stopped because the current adapter enumerates combinations from every residual transaction at each move; this candidate generation is not yet practical for the dataset's 340,183 transactions and 468 items.

### Slide C — What the GSA memory learns

**Title:** Three hypotheses, one search loop

All variants share the same:

- candidate pool;
- objective and lower-is-better convention;
- temperature schedule;
- Metropolis acceptance;
- evaluation budget;
- prior interface; and
- decay mechanism.

Only the learned key and update rule change:

| Variant | Learned key | Evidence used |
|---|---|---|
| A: Successful Feature | feature | improving mutation event |
| B: Good-Solution Frequency | feature | feature occurrence in an elite candidate |
| C: Mutation + Feature | `(operation, feature)` | improving operation-feature event |

Controls:

- `unguided`: no online learning, uniform memory weights;
- `prior_only`: static prior, no online learning.

Raw weight magnitudes are not directly comparable across A, B, and C because their update semantics differ.

### Slide D — Correct sampling equation

**Title:** Guided multinomial sampling

For each move `m` in the sampled candidate pool:

```text
score(m) = memory_weight(key(m)) * prior_weight(state, m)
P(m) = score(m) / sum(score(x) for x in pool)
```

The engine samples one move from the pool and evaluates only that selected candidate. It does not enumerate and evaluate the full neighborhood.

This is the GSA contribution: it changes which candidates are explored more often. It does not replace the MDL evaluator or the SA acceptance rule.

### Slide E — Correct SA loop

**Title:** Search, evaluate, accept, learn

```text
1. Generate a small candidate pool
2. Sample one move using W and the prior
3. Apply the move to obtain a candidate state
4. Evaluate the candidate objective
5. Accept or reject using SA
6. Update the variant-specific memory
7. Apply decay
8. Continue until the evaluation budget is exhausted
```

Use:

```text
Delta_MDL = candidate_score - current_score
```

The candidate is better when `Delta_MDL < 0`.

### Slide F — Findings from the real-dataset pilot

**Title:** Real-dataset pilot findings

Configuration from the fresh run on 2026-09-15:

- 2 crawled transaction datasets;
- 5 variants including two controls;
- 3 seeds per variant;
- 30 iterations;
- candidate pool size 5;
- temperature from 2.0 to 0.01.

Selected mean best-score results, where lower is better:

| Dataset | Unguided | Successful Feature | Good-Solution Frequency | Mutation + Feature |
|---|---:|---:|---:|---:|
| `requirements` | 1,143,091.33 | 1,125,641.00 | 1,125,641.00 | 1,125,641.00 |
| `themealdb` | 233,516.00 | 229,647.33 | 229,647.33 | 229,647.33 |

Interpretation:

- Prior-guided methods improved on `unguided` for both real datasets.
- `prior_only` and A/B/C tied in this short pilot, so static prior is active but online reinforcement has not yet separated the variants.
- This is a real-data result, but it is not evidence that the variants are universally equivalent.
- The short budget and current MDL-like evaluator may not expose differences in online guidance.
- Fair per-run telemetry is available in `run_metrics.csv`: evaluations, acceptance rate, runtime, and weight count are recorded without sharing adapter caches between runs.
- The next comparison must include convergence curves, evaluations-to-target, acceptance rate, runtime, and larger budgets.

### Slide G — Evidence from the Java reference

**Title:** Legacy HMP-SA reference run

The checked-in `HMP_SA/result_SAMP_iris.txt` shows the Java runner processing `iris.txt` with:

- initial raw size: `24000` bits;
- one recorded run: final code table size `44`;
- patterns found by SA: `13`;
- final compression size: `3690` bits;
- reported compression ratio: `15.375%`;
- reported runtime: `0.02` seconds;
- reported memory: approximately `5.23 MB`.

This confirms that the legacy Java HMP-SA implementation produces code-table output. It does not yet establish a fair HMP-SA versus HMP-GSA comparison because the Python side has not been wired to the same complete state and protocol.

### Slide H — Dataset preprocessing finding

**Title:** Real data is scanned, but not yet the full GSA experiment

The Python scanner reads transaction files and persists:

- transaction count;
- distinct item count;
- average transaction length;
- density;
- item frequency; and
- pairwise co-occurrence.

This is real dataset preprocessing. The current limitation is integration: the persisted prior is not yet the complete runtime path for a paper-faithful HMP-GSA search that returns a comparable code table.
The current scan of `accident.txt` reports:

```text
|D| = 340,183 transactions
|I| = 468 distinct items
ATL = 33.8079
density = 7.2239%
observed pairs = 46,815
```

The current limitation is evaluator fidelity: the real-data pilot runs through
the MDL-like adapter, but it is not yet the paper-exact HMP code-table state.
The accurate claim is **real-dataset pilot through a bounded MDL-like adapter**,
not a completed paper-faithful HMP-GSA benchmark.

### Slide I — Research conclusion at this stage

**Title:** What can be claimed now?

```text
Can claim
---------
- The GSA engine and three learning hypotheses are implemented.
- Controls use the same search machinery.
- Dataset priors are computed and persisted.
- A conservative MDL-like adapter exists.
- Synthetic tests show guidance can help on some landscapes and hurt on others.
- The Java reference produces real HMP-SA code tables.

Cannot claim yet
----------------
- HMP-GSA beats HMP-SA on a real dataset.
- The Python objective is an exact paper-level MDL implementation.
- The sparse matrix makes the complete greedy phase O(1).
- Synthetic benchmark results validate real mining quality.
```

### Slide J — Next experiment

**Title:** The decisive next step

Implement one real adapter around the Java-compatible HMP state, then run:

```text
same dataset
same initial state
same evaluator
same move budget
same temperature schedule
same seeds

HMP-SA / unguided
vs prior-only
vs HMP-GSA-A
vs HMP-GSA-B
vs HMP-GSA-C
```

Report:

- best MDL score;
- MDL versus evaluation count;
- evaluations to reach a target score;
- runtime;
- peak memory;
- variance across seeds;
- explored-solution diversity; and
- learned-memory size.

Only after this matched experiment should the presentation make a performance claim about HMP-GSA.

## Verified repository evidence

The focused regression command passes:

```powershell
python -m unittest hmp_gsa.tests.test_gsa hmp_gsa.tests.test_variants hmp_gsa.tests.test_dataset_scan hmp_gsa.tests.test_mdl_adapter -v
```

Result: `Ran 19 tests ... OK`.

The fresh synthetic run was generated with:

```powershell
python -m hmp_gsa.experiments.run --config hmp_gsa/configs/baseline.json
```

Output directory:

```text
results/20260907_181724/
```

The most important supporting implementation files are:

- `hmp_gsa/modules/engine.py` — shared Guided-SA loop;
- `hmp_gsa/modules/adapter.py` — adapter contract and prior hook;
- `hmp_gsa/modules/mdl.py` — current MDL-like adapter;
- `hmp_gsa/scripts/prior_scan.py` — real dataset scan and persistence;
- `hmp_gsa/experiments/landscapes.py` — explicitly synthetic objectives;
- `HMP_SA/HMP_SA_Runner.java` — legacy Java reference implementation; and
- `HMP_SA/result_SAMP_iris.txt` — recorded Java output.
