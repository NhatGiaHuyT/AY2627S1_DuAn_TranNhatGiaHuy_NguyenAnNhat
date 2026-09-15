# HMP-GSA architecture and experiment flow

## 1) High-level idea

This repository separates the optimization engine from the problem definition:

- `HMPGSA` manages the simulated annealing loop, temperature, candidate sampling, and memory updates.
- `GSAAdapter` defines the concrete problem interface.
- A variant (`unguided`, `prior_only`, `successful_feature`, `good_solution_frequency`, `mutation_feature`) decides what the engine remembers.

This keeps the search algorithm constant while changing only the guidance mechanism.

## 2) Core components

### Search engine
- `hmp_gsa/modules/engine.py`
- `HMPGSA` owns:
  - current state
  - temperature schedule
  - candidate pool sampling
  - acceptance probability
  - learning weights
  - decay

### Adapter contract
- `hmp_gsa/modules/adapter.py`
- `GSAAdapter` requires:
  - `initial_state()`
  - `initial_prior()`
  - `sample_moves(...)`
  - `apply_move(...)`
  - `evaluate(...)`
  - `features_of(...)`

The adapter is the boundary between the generic guided-SA engine and the actual optimization problem.

### Preserved synthetic reference
- `hmp_gsa/experiments/landscapes.py`
- This implementation is retained for isolated regression/reference tests only.
- The experiment runner does not import or execute it.

### Real dataset prior pipeline
- `hmp_gsa/scripts/prior_scan.py`
- The scanner reads transactional data, ignores empty lines, counts transactions, item frequency, and pairwise co-occurrence.
- It writes deterministic outputs to:
  - `hmp_gsa/derived/<dataset>/statistics.json`
  - `hmp_gsa/derived/<dataset>/item_frequency.csv`
  - `hmp_gsa/derived/<dataset>/cooccurrence.csv`

### MDL-like objective
- `hmp_gsa/modules/mdl.py`
- This is not a fabricated research objective; it follows the project’s Java HMP-SA pattern-compression logic:
  - residual database after removing repeated patterns
  - code-table overhead for the selected patterns
  - lower total cost = better compression

## 3) Prior distinction

The repository explicitly separates:

1. Initial memory prior
   - `initial_prior()`
   - a static feature weight map used to initialize memory

2. Dynamic data prior
   - `prior_weight(state, move, prior)`
   - intended future dataset signal based on co-occurrence / transaction structure

The final candidate score is effectively:

`memory_weight * dynamic_prior_weight`

This preserves the intended distinction between learned search memory and dataset-derived prior information.

## 4) How the experiment run works

### Real-dataset experiment run
Command:

```powershell
cd d:/hmp_gsa_prototype/AY2627S1_DuAn_TranNhatGiaHuy_NguyenAnNhat
python -m unittest hmp_gsa.tests.test_gsa hmp_gsa.tests.test_variants -v
```

or via config:

```powershell
cd d:/hmp_gsa_prototype/AY2627S1_DuAn_TranNhatGiaHuy_NguyenAnNhat
python -m hmp_gsa.experiments.run --config hmp_gsa/configs/baseline.json
```

The experiment runner writes:

- `results/<timestamp>/config.json`
- `results/<timestamp>/runs.csv`
- `results/<timestamp>/summary.csv`

### Dataset scan run
```powershell
cd d:/hmp_gsa_prototype/AY2627S1_DuAn_TranNhatGiaHuy_NguyenAnNhat
python hmp_gsa/scripts/main.py
```

This writes the persisted dataset statistics and pairwise co-occurrence prior to the `hmp_gsa/derived` folder.

## 5) How to interpret the results

### For real-dataset experiments
Look at:

- `best_score` across runs
- variance across seeds
- acceptance rate over time
- learned weights per feature / feature-op pair

Interpretation:

- `unguided`: baseline SA behavior
- `prior_only`: static prior only, no online learning
- `successful_feature`: weights features that produce improving accepted moves
- `good_solution_frequency`: weights features that appear in strong solutions
- `mutation_feature`: distinguishes feature + operation pairs

### For dataset-based experiments
Interpretation should focus on:

- whether the MDL-like objective decreases as patterns are added
- whether the learned prior produces more useful candidate moves
- whether the dataset co-occurrence prior biases search toward strong pattern neighborhoods

In short, the main metric is objective reduction under a fixed evaluation budget, not raw weight magnitude alone.

## 6) Current status

The repo currently supports three layers cleanly:

1. dataset scan + persistence
2. configurable multi-dataset runner
3. generic GSA engine + guidance variants
4. MDL-like compression objective consistent with the Java HMP-SA runner

The real full paper-level MDL state representation is still the next research boundary if one wants to replicate every exact detail of the printed MDL formulation.
