# HMP-GSA Research Report

## 1. Research question

Does a compact memory learned from search experience improve stochastic MDL-like pattern search beyond a static dataset prior?

The comparison is:

```text
SA without prior
SA + dataset prior
SA + prior + Successful Feature memory
SA + prior + Good-Solution Frequency memory
SA + prior + Mutation + Feature memory
```

The important scientific comparison is therefore not only against `unguided`. It is whether online memory improves over `prior_only`.

## 2. Data and implementation

The current runner uses real transaction datasets configured in JSON. The active extended dataset config is [real_data_500.json](../hmp_gsa/configs/real_data_500.json).

Current datasets:

- `datasets/crawling/requirements.txt`: requirements collected from 2,436 repositories.
- `datasets/crawling/themealdb.txt`: ingredients collected from 790 meals.

The runner supports any number of additional whitespace-separated transaction files by adding entries to the `datasets` array.

The synthetic landscape implementation remains in `hmp_gsa/experiments/landscapes.py` for isolated regression/reference use, but the real-data runner does not execute it.

## 3. Search design

All conditions share:

- the same dataset;
- the same initial state;
- the same MDL-like evaluator;
- the same candidate pool size;
- the same temperature schedule;
- the same seed;
- the same evaluation budget; and
- the same simulated-annealing acceptance rule.

The dataset adapter now supports configurable operations:

```text
add(pattern)
remove(pattern)
replace(old_pattern, new_pattern)
```

This matters because Variant C learns `(operation, feature)`. In the earlier add-only design, C could not distinguish adding from removing and was therefore not a valid test of the hypothesis.

## 4. Memory variants

### Unguided

Uniform move memory. This measures the search without dataset guidance.

### Prior-only

Uses item/pair support from the dataset as a static pattern prior. It does not learn online.

### Successful Feature, A

Reinforces the feature involved in an accepted improving move.

### Good-Solution Frequency, B

Reinforces features appearing in elite code-table states.

### Mutation + Feature, C

Reinforces the exact operation-feature combination, such as:

```text
(add, pattern)
(remove, pattern)
(replace, pattern)
```

## 5. Verified pilot finding

The completed 1,000-iteration run before enabling the new remove/replace neighborhood produced:

| Dataset | Unguided | Prior-only | A/B/C |
|---|---:|---:|---:|
| `requirements` | 593,936.0 | 574,620.4 | 568,447.0 |
| `themealdb` | 119,686.3 | 109,179.3 | 108,814.1 |

Interpretation:

1. The real dataset prior clearly improved search over `unguided`.
2. Online guidance provided a further improvement over `prior_only` in the aggregate score.
3. A, B, and C followed identical move traces in that run.
4. Therefore the aggregate improvement cannot yet be attributed to a difference between A, B, and C.
5. The most likely explanation was the add-only neighborhood plus the strong static prior.

This is a valid finding about the previous design, not evidence that the three hypotheses are equivalent in general.

## 6. Redesign now implemented

The extended config now enables:

```json
"move_operations": ["add", "remove", "replace"]
```

The adapter recomputes residual masks from the mutated code table, so removing or replacing a pattern does not leave stale residual state.

The new operation behavior is covered by regression tests. Current focused validation:

```text
Ran 22 tests ... OK
```

## 7. What the next experiment must measure

For each dataset, variant, and seed, report:

- best MDL-like score;
- score at 10%, 25%, 50%, 75%, and 100% of the budget;
- evaluations to reach a fixed target;
- acceptance rate;
- runtime;
- learned-memory size;
- number and type of add/remove/replace moves; and
- diversity of explored code tables.

The decisive comparison is:

```text
prior_only vs Successful Feature
prior_only vs Good-Solution Frequency
prior_only vs Mutation + Feature
```

## 8. Claims and limitations

Can claim now:

- real datasets are used by the configurable runner;
- pattern-level support prior affects search;
- the prior improves the completed pilot over uniform search;
- the engine has separate online-memory variants;
- the operation-enabled neighborhood is implemented and tested.

Cannot claim yet:

- A, B, or C is the best memory strategy;
- HMP-GSA beats HMP-SA paper-faithfully;
- the Python evaluator exactly reproduces the HMP paper code-table cost;
- the new operation-enabled extended run improves convergence until its complete results are generated.

The current Python objective remains MDL-like. A final HMP claim requires matching the Java code-table state, residual encoding, usage coding, and evaluation protocol.

## 9. Reproducibility

Run the extended experiment with:

```powershell
python -m hmp_gsa.experiments.run --config hmp_gsa/configs/real_data_500.json
```

Progress is printed before and after every dataset/variant/seed run. Each completed run writes:

- `runs.csv`: iteration-level trace;
- `run_metrics.csv`: one row per run;
- `summary.csv`: aggregate results; and
- `config.json`: exact configuration used.
