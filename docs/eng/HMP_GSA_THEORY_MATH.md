# HMP-GSA: Theory & Mathematics

A detailed mathematical treatment of the HMP-GSA framework: the MDL objective, the simulated-annealing engine, the guidance-memory model, its theoretical interpretation, complexity, a fully worked numerical example, and the explicit deviations from the HMP-SA paper.

Notation matches the codebase (`hmp_gsa/modules/`). Default experimental parameters come from `hmp_gsa/configs/real_data_500.json`.

---

## 0. Notation

| Symbol | Meaning | Code |
|---|---|---|
| $D = \{t_1,\dots,t_n\}$ | transaction database | `transactions` |
| $I$, $m=\|I\|$ | item universe | `_all_items` |
| $C$ | code table (set of patterns) | `MDLState.code_table` |
| $X \subseteq I$ | pattern / itemset | `Feature` (a tuple) |
| $\mathrm{sup}(X)$ | support: $\#\{t : X \subseteq t\}$ | `_support` |
| $W_0$ | dataset prior, $F \to \mathbb{R}_{\ge 0}$ | `initial_prior()` |
| $W$ | guidance memory, $K \to \mathbb{R}_{\ge 0}$ | `self.weights` |
| $K$ | guidance key space | `GuidanceKey` |
| $\varphi: K \to F$ | key → prior-feature map | `prior_feature_for_key` |
| $\alpha$ | reinforcement rate (default 0.1) | `alpha` |
| $\lambda_d$ | decay rate (default 0.01) | `decay` |
| $\lambda$ | elite fraction (default 0.25) | `elite_fraction` |
| $\varepsilon$ | weight floor (default $10^{-9}$) | `epsilon` |
| $T(i)$ | temperature at iteration $i$ | `temperature()` |
| $s$ | MDL cost (objective, **lower = better**) | `evaluate()` |

---

## 1. MDL foundations

### 1.1 Description length

The MDL principle selects the model minimizing the total description length:

$$L(D, C) = L(D \mid C) + L(C \mid D)$$

- $L(D \mid C)$: cost of encoding the data using the model (the **residual**).
- $L(C \mid D)$: cost of describing the model itself (the **code table**).

### 1.2 Heuristic partial-coverage MDL

Following the Grimp-style formulation used by HMP, coverage is *partial*: a pattern need not explain every transaction, and uncovered items are encoded individually at a fixed width of 32 bits:

$$L_H(D, C) = \underbrace{\sum_{t \in D} 32 \cdot \bigl| t \setminus \textstyle\bigcup_{X \in \mathrm{cover}_C(t)} X \bigr|}_{\text{residual bits}} \;+\; \underbrace{\sum_{X \in C,\; u(X) > 0} \Bigl( 32\,|X| + L(\mathrm{code}(X)) \Bigr)}_{\text{code-table bits}}$$

where $\mathrm{cover}_C(t) = \{X \in C : X \subseteq t\}$ and usage $u(X) = \#\{t : X \in \mathrm{cover}_C(t)\}$.

The Shannon-optimal code length in the paper is fractional:

$$L(\mathrm{code}(X)) = -\log_2 \frac{u(X)}{n}$$

**Implementation approximation** (`mdl.py:_mdl_cost`): the code length is discretized and computed from the *original-dataset* support rather than residual usage:

$$L(\mathrm{code}(X)) \;\approx\; \lceil \log_2(\mathrm{sup}(X) + 1) \rceil$$

This is a deliberate heuristic: it avoids recomputing usage per candidate evaluation, at the cost of not being the exact MDL objective. See §7.

### 1.3 Compression ratio

$$CR(D, C) = 100 \cdot \frac{L_H(D, C)}{L(D)}, \qquad L(D) = 32 \cdot \sum_{t}|t|$$

Lower CR is better. Our engine directly minimizes $L_H(D,C)$, which is equivalent.

### 1.4 Why the search is hard

With $m$ items there are $2^m - 1$ nonempty itemsets, hence

$$2^{\,2^m - 1}$$

possible code tables. Exact optimization is intractable for realistic $m$, which is why a heuristic search (SA) is used at all.

---

## 2. Simulated annealing

### 2.1 Metropolis acceptance

Let $s$ be the current objective and $s'$ the objective after a candidate move, $\Delta = s' - s$. The engine (`engine.py:accept`) uses:

$$P_{\mathrm{accept}} = \begin{cases} 1 & \Delta < 0 \quad \text{(improvement)}\\ \exp(-\Delta / T) & \Delta \ge 0 \end{cases}$$

The paper writes the same rule with the opposite sign convention $\Delta S = S - S'$:

$$P_{\mathrm{accept}} = 1 \text{ if } \Delta S \ge 0, \quad \exp(\Delta S / T) \text{ if } \Delta S < 0$$

These are identical: $\exp(\Delta S / T) = \exp(-(s'-s)/T)$. **Never mix the two conventions** — mixing silently inverts the SA behavior. Note the edge case $\Delta = 0$: the code falls through to $\exp(0/T) = 1$, so a neutral move is accepted with probability $\approx 1$ (`rng.random() < 1` holds a.s.).

### 2.2 Cooling schedule

The paper uses geometric cooling $T_{r+1} = \alpha T_r$, giving after $k$ steps $T_k = T_{\mathrm{init}}\alpha^k$ and a step count to reach $T_{\min}$:

$$k = \left\lceil \frac{\ln(T_{\min}/T_{\mathrm{init}})}{\ln \alpha} \right\rceil$$

(e.g. $T_{\mathrm{init}}=100$, $T_{\min}=0.1$, $\alpha=0.9 \Rightarrow k = 66$).

**Our engine uses a linear schedule** (`engine.py:temperature`):

$$T(i) = T_{\mathrm{start}} + \frac{i}{N-1}\,(T_{\mathrm{end}} - T_{\mathrm{start}}), \qquad i = 0,\dots,N-1$$

with $N$ = `iterations` (default 1000), $T_{\mathrm{start}}=2.0$, $T_{\mathrm{end}}=0.01$. Linear cooling reaches $T_{\min}$ exactly at the final iteration and is simple to reason about, but see §7 and §8 for the theoretical caveat.

### 2.3 Convergence theory (background)

Classical SA theory (Hajek 1988) guarantees convergence to the global optimum only under *logarithmic* cooling $T(i) \ge c/\log(i)$. Neither geometric nor linear cooling satisfies this; both are standard engineering practice that trade the guarantee for a fixed budget. This is acceptable here because the objective is heuristic MDL anyway (§1.2).

### 2.4 Ergodicity

The move set (add/remove/replace patterns) makes the state space connected: any code table can be reached from any other by a sequence of add/remove moves. Combined with the positive acceptance probability of worsening moves at $T > 0$, the chain is ergodic for fixed $W$ — this is what makes the Boltzmann intuition of §4.4 valid.

---

## 3. The guidance-memory model (the HMP-GSA contribution)

### 3.1 Formal structure

The guidance memory is a map $W: K \to \mathbb{R}_{\ge 0}$ from guidance keys to weights. A key is derived from a move:

$$k = \kappa(\text{state}, \text{move}) \quad \text{(`key_for_move`)}$$

The variants instantiate $K$ and $\kappa$ differently:

| Variant | $K$ | $\kappa$ |
|---|---|---|
| `unguided` | $\{*\}$ (trivial) | $\kappa \equiv *$ |
| `prior_only` | $F$ | $\kappa = X$ (the pattern) |
| `successful_feature` | $F$ | $\kappa = X$ |
| `good_solution_frequency` | $F$ | $\kappa = X$ |
| `mutation_feature` | $\{\mathrm{op}\} \times F$ | $\kappa = (\mathrm{op}, X)$ |

### 3.2 Initialization from the dataset prior

The dataset prior $W_0: F \to \mathbb{R}_{\ge 0}$ is produced once by preprocessing (`prior_scan.py`):

$$W_0(\{i\}) = \mathrm{sup}(\{i\}), \qquad W_0(\{i,j\}) = \mathrm{sup}(\{i,j\})$$

i.e. **raw support counts** (not normalized frequencies). Patterns of size $\ge 3$ receive no prior value — the artifact is pairwise only, and the code deliberately refuses to manufacture one by summing pairs (`mdl.py:_build_pattern_prior`).

A key's weight is lazily initialized on first encounter (`engine.py:_initial_weight`):

$$W(k) \;\leftarrow\; \max\bigl(\varepsilon,\; W_0(\varphi(k))\bigr)$$

Every guided variant receives the *same* $W_0$; variants differ only in how $W$ evolves afterwards.

### 3.3 Proposal distribution

Given a candidate pool $C = \{m_1,\dots,m_c\}$, a move is sampled by multinomial selection proportional to weight (`engine.py:sample_weighted_move`):

$$P(m_j \mid C) = \frac{W(\kappa(m_j))}{\sum_{j'} W(\kappa(m_{j'}))}$$

with a uniform fallback if the total weight is $\le 0$. Note this is *linear* weighting, not softmax: doubling a weight doubles its relative probability. For `unguided`, $\_candidate\_weight$ is overridden to return the constant $1.0$, i.e. a uniform proposal — the pure-SA control.

### 3.4 Memory update rules

Let $\Delta = s' - s$ for the evaluated move, $\mathbb{1}[\cdot]$ the indicator, and $F(S_t)$ the set of patterns in the current code table.

**Variant A — SuccessfulFeature** (`variants.py:SuccessfulFeatureGSA`):

$$W(\kappa) \;\mathrel{+}=\; \alpha \cdot |\Delta| \cdot \mathbb{1}[\text{accepted} \wedge \Delta < 0]$$

**Variant C — MutationFeature** (`variants.py:MutationFeatureGSA`): identical, but the key includes the operation:

$$W\bigl((\mathrm{op}, X)\bigr) \;\mathrel{+}=\; \alpha \cdot |\Delta| \cdot \mathbb{1}[\text{accepted} \wedge \Delta < 0]$$

**Variant B — GoodSolutionFrequency** (`variants.py:GoodSolutionFrequencyGSA`): reinforcement is driven by *state quality*, not move deltas:

$$W(X) \;\mathrel{+}=\; \alpha \cdot q(s_t, \tau_t) \quad \text{for every } X \in F(S_t)$$

where the quality factor is

$$q(s, \tau) = \begin{cases} 0 & s > \tau\\[2pt] \min\!\Bigl(1,\; \dfrac{\tau - s}{\max(|\tau|, 1)}\Bigr) & s \le \tau \end{cases}$$

and the elite threshold $\tau_t$ is the lower $\lambda$-quantile of the seen score history $\{s_1,\dots,s_t\}$ (`engine.py:_elite_threshold`): sort ascending, take index $\min\bigl(\lfloor \lambda \cdot t \rfloor,\, t-1\bigr)$. Since lower scores are better, "elite" means "among the best $\lambda$ fraction of scores seen so far".

**Decay / forgetting** (`engine.py:decay_weights`, active for B and the base engine):

$$W(k) \;\leftarrow\; \max\bigl(\varepsilon,\; (1 - \lambda_d)\, W(k)\bigr)$$

The $\varepsilon$-floor is deliberate: *deleting* a key would cause it to be re-initialized from $W_0$ on its next encounter, which would undo forgetting. The floor keeps the key alive with a tiny weight instead.

**Important asymmetry**: variants A and C implement *no* decay — their weights are monotonically non-decreasing. Only B forgets. This is a design difference, not an oversight, and it is part of what the experiments compare.

### 3.5 Per-iteration pseudocode

```
prior = adapter.initial_prior()            # W₀
state = adapter.initial_state();  s = evaluate(state)
for i in 0..N-1:
    T = T(i)                               # linear schedule
    C = adapter.sample_moves(state, rng, pool_size)
    m  ~ Multinomial({W(κ(m)) : m ∈ C})    # guided proposal
    state' = adapter.apply_move(state, m)
    s' = evaluate(state')
    accept = (s' < s) or (rng() < exp(-(s'-s)/T))
    if accept: state, s = state', s'
    track best (state, s)
    update_memory(...)                      # variant-specific, §3.4
    update_good_solution_memory(...)        # variant B only
    decay_weights()                         # §3.4
return best_state, best_score
```

---

## 4. Theoretical interpretation

### 4.1 Guidance only biases the *proposal*, never the *acceptance*

The acceptance rule depends only on $(s, s', T)$ — never on $W$. Therefore:

> **An improving move is always accepted, regardless of its weight.** Guidance changes only how often a move is *proposed*.

This is the central soundness argument of HMP-GSA: the memory cannot veto an improvement; it can only make good regions more likely to be sampled. The objective remains the sole gatekeeper.

### 4.2 Relation to estimation-of-distribution algorithms (EDAs)

Because keys are (essentially) features, the proposal distribution factorizes approximately as a *univariate* distribution over patterns — the same structure as a UMDA/PBIL. The update rule for B,

$$W \leftarrow (1-\lambda_d)W + \alpha\cdot(\text{quality signal}),$$

is structurally identical to the PBIL update $p_i \leftarrow (1-\eta)p_i + \eta x_i$: decay is the learning-rate term, reinforcement is the sample signal. A/C can be read as a "reward-weighted" PBIL where the signal is the improvement magnitude of a single move.

### 4.3 Relation to reinforcement learning

$W$ is a (non-normalized) policy over moves. The variants are Monte-Carlo policy updates with no value function and no bootstrapping:

- A/C: 1-step eligibility, reward $= |\Delta|$ on accepted improving moves.
- B: state-based eligibility (all patterns in elite states), reward $= q(s_t, \tau_t)$.

### 4.4 Relation to frequency memory in local search

The memory resembles the frequency/quality memory of tabu search and scatter search, but instead of forbidding or attracting moves, it *warps the proposal distribution* smoothly. Unlike tabu lists, it never forbids anything.

### 4.5 Bias–variance view of the five variants

| Variant | Guidance source | Bias | Variance |
|---|---|---|---|
| `unguided` | none | none | high |
| `prior_only` | static $W_0$ | high (fixed) | low |
| `successful_feature` | reactive, per-move | adaptive | medium |
| `mutation_feature` | reactive, operation-aware | adaptive | medium |
| `good_solution_frequency` | selective, per-state | adaptive | low (but slow warm-up) |

This is the formal version of the *phase-transition* hypothesis observed empirically: reactive methods (A/C) learn fast but saturate; selective methods (B) warm up slowly (their first iterations have $q \approx 0$ because $\tau_t$ has not yet separated from $s_t$) but produce a cleaner signal at long horizons.

### 4.6 Why B does nothing on iteration 1

With one seen score, $\tau_1 = s_1$, so $q(s_1, \tau_1) = 0$. Variant B needs a non-degenerate score history before its threshold separates from the current score — a concrete reason its advantage only appears at longer budgets.

---

## 5. Complexity

Per iteration, with $n$ transactions, $m$ items, pool size $c$, code table size $|C|$, memory size $|W|$:

| Step | Cost |
|---|---|
| `sample_moves` | $O\bigl(\min(n, 2\cdot\text{max\_candidates}) \cdot \text{combinations per tx} + |C|\bigr)$, capped at `max_candidates` |
| weighted sampling | $O(c)$ |
| `apply_move` + residual masks | $O(n \cdot m / 64)$ bitmask operations (patterns sorted by length desc) |
| `evaluate` | $O(1)$ amortized via `_score_cache` keyed on `code_table` |
| `update_memory` | $O(1)$ for A/C; $O(|C|)$ for B |
| `decay_weights` | $O(|W|)$ |

Total: $O\bigl(N \cdot (n \cdot m/64 + |C| + |W|)\bigr)$. The support counter is built once at construction and is bounded to patterns of size $\le 2$ (`MAX_EXACT_SIZE = 2`) with a min-support filter of $\lceil 0.005 \cdot n \rceil$, keeping construction memory tractable on large datasets.

---

## 6. Worked example (end to end, one iteration)

Dataset (the paper's 5-transaction example):

```
t1 = {a,c,d,e,f}   t2 = {d,e,f}   t3 = {a,c,e}   t4 = {a,f}   t5 = {b,f}
```

**Initial state** $S_0$: empty table, residual = $D$.

$$L_H(D, \varnothing) = 32 \cdot (5+3+3+2+2) = 480 \text{ bits}$$

**Prior $W_0$** (raw counts from a one-pass scan):

- Singletons: $a{=}3,\; b{=}1,\; c{=}2,\; d{=}2,\; e{=}3,\; f{=}4$
- Pairs: $\{a,c\}{=}2,\; \{a,e\}{=}2,\; \{a,f\}{=}2,\; \{c,e\}{=}2,\; \{d,e\}{=}2,\; \{d,f\}{=}2,\; \{e,f\}{=}2$, others $=1$

**Iteration 0** ($T = 2.0$). Suppose the pool is $\{ \text{add }\{a,c,e\},\; \text{add }\{f\},\; \text{add }\{d,e\} \}$ with weights $2, 4, 2$:

$$P(\{a,c,e\}) = \tfrac{2}{8} = 0.25,\quad P(\{f\}) = 0.5,\quad P(\{d,e\}) = 0.25$$

Say $\{a,c,e\}$ is sampled. Applying `add`:

- Residual: $t_1 \to \{d,f\}$, $t_2 \to \{d,e,f\}$ (unchanged), $t_3 \to \varnothing$, $t_4 \to \{a,f\}$ (unchanged), $t_5 \to \{b,f\}$ (unchanged)
- Residual bits $= 32 \cdot (2+3+0+2+2) = 288$
- Code bits $= \lceil\log_2(2+1)\rceil + 3\cdot 32 = 2 + 96 = 98$
- $s' = 288 + 98 = 386$, $\Delta = -94 < 0$ → **always accepted**

(Under the paper's Shannon formula the same table costs $\approx 387.97$ bits — the discretization difference is visible but small.)

**Memory after the move** ($\alpha = 0.1$):

| Variant | Update | New weight |
|---|---|---|
| `unguided` | none (constant 1.0) | — |
| `prior_only` | none | $W(\{a,c,e\}) = 2$ |
| `successful_feature` | $2 + 0.1 \cdot 94$ | $11.4$ |
| `mutation_feature` | $W((\text{add},\{a,c,e\})) = 11.4$ | $11.4$ |
| `good_solution_frequency` | $\tau_0 = s_0 = 386 \Rightarrow q = 0$ | $2$ (unchanged; decay applies: $2 \cdot 0.99$) |

**Iteration 1 feedback loop** (variants A/C): if the next pool is again $\{\{a,c,e\}, \{f\}, \{d,e\}\}$ with weights $11.4, 4, 2$:

$$P(\{a,c,e\}) = \tfrac{11.4}{17.4} \approx 0.655$$

A single improving move raised the pattern's proposal probability from 0.25 to 0.655 — this is the mechanism by which search experience is compressed into the weight vector.

---

## 7. Explicit deviations from the HMP-SA paper

HMP-GSA is a *distinct framework inspired by* HMP-SA, not a reimplementation:

| Aspect | HMP-SA paper | This implementation |
|---|---|---|
| Cooling | geometric $T \leftarrow \alpha T$ | linear interpolation (§2.2) |
| Code length | $-\log_2(u/n)$, fractional | $\lceil \log_2(\mathrm{sup}+1)\rceil$, integer bits |
| Support for code length | residual usage $u(X)$ | original-dataset support (precomputed) |
| Pattern sizes | 3–6 | $1..\text{max\_pattern\_size}$ (config: 1–2) |
| Search space | itemset lattice of *one* candidate | code-table state space |
| Neighbor | $\pm 1$ item within $[3,6]$ | add / remove / replace of whole patterns |
| Completion stage | greedy 2-itemsets fill $z/3 \to z$ | none |
| Residual | delete covered occurrences | bitmask partial coverage (equivalent semantics) |
| Cover order | unsorted, insertion order | frozenset (unordered) |
| Guidance | static item weights | pluggable memory $W$ (§3) |

Consequences: results are **not directly comparable** to the paper's published compression ratios. The framework's contribution is the guidance-memory abstraction and the controlled ablation it enables (§4.1).

Two implementation quirks to be aware of:

1. `replace` carries `payload = tuple(state.code_table)` and removes `old_patterns[0]` — the *first element of a frozenset's tuple conversion*, i.e. an arbitrary existing pattern. Replacement is therefore non-deterministic in which pattern it evicts.
2. The `_score_cache` is keyed on `code_table` alone, so residual masks must be a pure function of the table — which they are (`_residual_masks_for_table` recomputes from scratch each time).

---

## 8. Complete end-to-end flow

This section traces the exact computational path from raw input file to final experimental output, with file/line references.

### 8.1 Input preprocessing (one-time, per dataset)

**Input**: `datasets/crawling/{requirements,themealdb}.txt` — one transaction per line, items are space-separated integers.

```text
1067 1190 1232 1233 1807 1808 1813 2061 2076
142 444 1085 1264 1335 1453 1595 2031 2107
...
```

**Step 1 — `prior_scan.py:scan_dataset()`** (`prior_scan.py:31`):
- Single pass over the file.
- Builds `item_frequency: Counter[item → count]` and `pair_cooccurrence: Counter[(item_i, item_j) → count]`.
- Computes statistics: `|D|`, `|I|`, average transaction length, density.

**Step 2 — `prior_scan.py:save_results()`** (`prior_scan.py:121`):
Writes three artifacts to `derived/<dataset>/`:
- `statistics.json` — metadata
- `item_frequency.csv` — `item,frequency` (raw counts)
- `cooccurrence.csv` — `item_i,item_j,cooccurrence` (raw counts, `i < j`)

These artifacts are the **dataset prior** $W_0$ in support-count space.

### 8.2 Experiment configuration

**Config**: `hmp_gsa/configs/real_data_500.json` (`real_data_500.json:1`):
```json
{
  "datasets": [{ "name": "requirements", "path": "...", "max_pattern_size": 2, "candidate_sizes": [1,2], "max_candidates": 5000, "move_operations": ["add","remove","replace"] }, ...],
  "variants": ["unguided","prior_only","successful_feature","good_solution_frequency","mutation_feature"],
  "seeds": [0,1,2],
  "search": { "iterations": 1000, "candidate_pool_size": 5, "temperature_start": 2.0, "temperature_end": 0.01, "elite_fraction": 0.25 },
  "guidance": { "alpha": 0.1, "decay": 0.01, "prior": 1.0, "epsilon": 1e-9 }
}
```

### 8.3 Experiment runner pipeline

Entry point: `hmp_gsa/experiments/runner.py:run()` (`runner.py:436`).

For each dataset in config:
1. **`prepare_dataset()`** (`runner.py:46`): calls `process_dataset()` → runs `scan_dataset()` if derived artifacts don't exist, returns `derived_path`.
2. **Build engine** (`runner.py:65`): instantiates the variant class with hyperparameters from config:
   - `alpha`, `decay`, `epsilon` from `guidance`
   - `iterations`, `candidate_pool_size`, `temperature_start/end`, `elite_fraction` from `search`
   - `seed` for this run
3. **Build adapter** (`runner.py:104`): constructs `DatasetMDLAdapter`:
   - Reads transactions from `dataset["path"]` → list of `tuple[int, ...]` (deduped, sorted)
   - Loads prior CSVs from `derived_path/cooccurrence.csv` and `derived_path/item_frequency.csv`
   - Builds `MAX_EXACT_SIZE = 2` support counter (`mdl.py:80`) with min-support = `max(1, 0.005 * n_transactions)` (`mdl.py:78`)
   - Builds `W_0 = _pattern_prior` (`mdl.py:149`): singleton → item frequency, pair → co-occurrence, larger patterns → omitted
4. **Run variant** (`runner.py:143`): `engine.run(adapter)` → returns `(best_state, best_score)`.
5. **Collect** result dict: `{dataset, variant, seed, best_score, best_state}`.

Parallelization: `ThreadPoolExecutor` over `(variant, seed)` pairs (`runner.py:332`).

### 8.4 SA engine execution (the core loop)

**Engine class** (`engine.py:12`): `HMPGSA` with variant-specific hooks.

**`run(adapter)`** (`engine.py:320`):

```
1. rng = Random(seed)
2. prior = adapter.initial_prior()        # W₀: Feature → float
3. weights.clear(), _seen_scores.clear()
4. state = adapter.initial_state()        # empty code_table, residual = full transactions
5. score = adapter.evaluate(state)        # MDL cost of empty table (residual bits = 32 * sum |t|)
6. best_state, best_score = state, score

7. for iteration in 0 .. N-1:
   a. T = temperature(iteration)           # linear: T_start + i/(N-1)*(T_end - T_start)
   b. candidates = adapter.sample_moves(state, rng, pool_size)
      - For "add": sample transactions, extract all sub-patterns of allowed sizes not in code_table, cap at max_candidates
      - For "remove": all patterns in current code_table
      - For "replace": cross product of addable × one existing pattern (payload)
      - Trim to pool_size via rng.sample
   c. move = sample_weighted_move(state, candidates, prior, rng)
      - For each m: key = key_for_move(state, m)
      - weight = weights.get(key) or max(epsilon, prior.get(prior_feature_for_key(key), epsilon))
      - Multinomial sample via rng.choices
   d. state_after = adapter.apply_move(state, move)
      - Adds/removes/replaces pattern in code_table
      - Recomputes residual_masks: for each transaction mask, clear bits of each pattern (largest patterns first)
   e. new_score = adapter.evaluate(state_after)
      - Cache keyed by code_table frozenset
      - MDL cost: residual_bits = sum(popcount(mask))*32 + sum_over_patterns( ceil(log2(sup+1)) + 32*|pattern| )
   f. accept = (new_score < old_score) or (rng.random() < exp(-(new_score - old_score)/T))
   g. if accept: state, score = state_after, new_score
   h. track best: if score < best_score: best_state, best_score = state, score
   i. _seen_scores.append(score)
   j. update_memory(...)                   # variant-specific (§3.4)
   k. update_good_solution_memory(...)     # only GoodSolutionFrequencyGSA
   l. decay_weights()                      # (1-decay) * weight, floor epsilon

8. return best_state, best_score
```

### 8.5 Output artifacts

Per dataset, two CSV files under `results/<dataset>/`:

**`runs.csv`** (`runner.py:197`):
```csv
dataset,variant,seed,best_score
requirements,unguided,0,967273.0
requirements,unguided,1,976746.0
...
```

**`summary.csv`** (`runner.py:245`): aggregated statistics
```csv
dataset,variant,runs,mean,std,best,worst
requirements,unguided,3,971541.33,4805.41,967273.0,976746.0
requirements,prior_only,3,823174.0,22898.96,798943.0,844455.0
...
```

### 8.6 What `best_state` contains

`MDLState` (`mdl.py:16`):
- `code_table: frozenset[tuple[int, ...]]` — the selected patterns (e.g., `{(1190, 1813), (1067,), (1724, 1808)}`)
- `residual_masks: tuple[int, ...]` — bitmask per transaction after covering
- `residual: tuple[tuple[int, ...], ...]` — unused (always empty tuple in current code)

To reconstruct the human-readable code table:
```python
for pattern in best_state.code_table:
    print(pattern, "support:", adapter._support.get(pattern))
```

### 8.7 Visual pipeline summary

```
┌─────────────────────┐
│  requirements.txt   │  (raw transactions: space-separated ints per line)
└─────────┬───────────┘
          │ prior_scan.py (one-time)
          ▼
┌─────────────────────┐
│ derived/requirements/│
│  item_frequency.csv │──┐
│  cooccurrence.csv   │  │  (W₀ = raw support counts)
└─────────────────────┘  │
                         │
┌─────────────────────┐  │
│ real_data_500.json  │──┼──▶ runner.py:run()
│ (config)            │  │
└─────────────────────┘  │
                         ▼
              ┌─────────────────────┐
              │ DatasetMDLAdapter   │
              │  - loads W₀         │
              │  - builds support   │
              │  - builds bitmasks  │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ HMPGSA (variant)    │
              │  - weights ← W₀     │
              │  - SA loop (N=1000) │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ (best_state,        │
              │  best_score)        │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ results/requirements/│
              │  runs.csv           │
              │  summary.csv        │
              └─────────────────────┘
```

---

## 9. Open theoretical questions

1. **Non-stationarity.** Because $W$ evolves during the run, the chain is not time-homogeneous; classical SA convergence theory does not directly apply. Does the guidance preserve convergence to the Boltzmann distribution in an appropriate limit? Under what conditions on $\alpha, \lambda_d$?
2. **Optimal decay.** The PBIL analogy (§4.2) suggests $\lambda_d$ interacts with $\alpha$ as a learning rate. Is there an optimal $\lambda_d(\alpha, N)$?
3. **Phase transition.** Empirically, B overtakes A/C at long horizons (and on large datasets) but trails at short horizons. Can this be formalized — e.g., a bound on the warm-up time of $\tau_t$ versus the saturation time of reactive weights?
4. **Prior normalization.** $W_0$ is in raw counts. Since proposal probabilities are relative, the *scale* of $W_0$ interacts with $\alpha$ (a large prior value makes $\alpha|\Delta|$ reinforcements relatively smaller). Should $W_0$ be normalized to $[0,1]$?
5. **Usage-based code length.** Replacing $\mathrm{sup}(X)$ with true residual usage $u(X)$ in `_mdl_cost` would make the objective exact MDL at the cost of recomputation — is the speed/quality tradeoff worth it?

---

*Derived from `hmp_gsa/modules/` (adapter.py, engine.py, mdl.py, models.py, prior.py, variants.py), `hmp_gsa/experiments/prior_scan.py`, and `hmp_gsa/configs/real_data_500.json`. The HMP-SA paper reference is: E. Chen, M. Z. Nawaz, M. S. Nawaz, P. Fournier-Viger, "HMP: Efficient heuristic algorithms for MDL-based itemset mining," Applied Soft Computing 187 (2026) 114314.*
