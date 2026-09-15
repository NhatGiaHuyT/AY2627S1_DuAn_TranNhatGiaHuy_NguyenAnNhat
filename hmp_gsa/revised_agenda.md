# AGENDA BÁO CÁO: HMP-SA VÀ ĐỊNH HƯỚNG MỞ RỘNG HMP-GSA TRÊN NỀN TẢNG MDL

---

# Phần 0 — Bài toán và Related Work

## 0.1. Bài toán Frequent Pattern Mining

Cho một cơ sở dữ liệu giao dịch:

```text
D = {t₁, t₂, ..., tₙ}
```

mỗi transaction chứa một tập item, ví dụ:

```text
t₁ = {A, B, C, D}
t₂ = {A, B, C, E}
t₃ = {A, B, D}
```

Ta muốn tìm một **Code Table** `C` gồm các pattern có khả năng mô tả và nén dữ liệu tốt.

Ví dụ:

```text
C = {{A,B}, {B}, ...}
```

Không phải mục tiêu là tìm tất cả pattern phổ biến.

Mục tiêu là tìm **một tập pattern đủ tốt để mô tả dữ liệu với tổng số bit nhỏ nhất**.

---

## 0.2. Vì sao bài toán khó?

Nếu có `n` item khác nhau, số itemset khác nhau có thể lên tới:

```text
2ⁿ - 1
```

Nếu xem mỗi itemset là một candidate có thể được chọn hoặc không chọn vào Code Table, số Code Table có thể tăng theo:

```text
2^(2ⁿ - 1)
```

Đây là một không gian tìm kiếm cực lớn.

Vì vậy, ta không thể đơn giản thử toàn bộ Code Table.

---

# Phần 1 — MDL: Tiêu chuẩn để đánh giá một Code Table

HMP sử dụng nguyên lý **Minimum Description Length (MDL)**.

Ý tưởng:

> Một model tốt phải mô tả được dữ liệu tốt nhưng bản thân model cũng không được quá phức tạp.

Ta tối thiểu hóa:

```text
L(C,D) = L(C|D) + L(D|C)
```

Trong đó:

* `L(C|D)`: số bit cần để mô tả Code Table.
* `L(D|C)`: số bit cần để mã hóa dữ liệu bằng Code Table.

Do đó:

```text
Code Table đơn giản
        ↕
khả năng nén dữ liệu
```

được cân bằng bởi cùng một objective MDL.

**Điểm quan trọng:** trong quá trình nghiên cứu HMP-GSA, MDL vẫn là objective function. GSA chỉ thay đổi **cách search**, không thay đổi nguyên lý MDL.

---

# Phần 2 — HMP-SA

HMP-SA đưa **Simulated Annealing (SA)** vào quá trình tìm kiếm Code Table.

Ý tưởng cơ bản:

```text
Candidate
   ↓
Evaluate MDL
   ↓
Generate Neighbor
   ↓
Evaluate Neighbor
   ↓
Accept / Reject
   ↓
Repeat
```

Neighbor được tạo bằng cách thay đổi pattern hiện tại thông qua mutation, chẳng hạn thêm hoặc bỏ một item trong pattern.

SA không chỉ chấp nhận bước tốt.

Đặt:

```text
ΔMDL = L(candidate) - L(current)
```

Vì MDL được cực tiểu hóa, candidate mới tốt hơn khi:

```text
ΔMDL < 0
```

thì chấp nhận.

Nếu candidate mới xấu hơn, nó vẫn có thể được chấp nhận với một xác suất phụ thuộc vào nhiệt độ:

```text
P(accept) = exp(-ΔMDL / T)
```

Trong mã Java gốc, biến tương đương được viết theo hướng tiết kiệm:
`improveCompressionSize - newCompressionSize`. Vì vậy cần giữ nhất quán
quy ước dấu khi trình bày hoặc triển khai Python.

Nhờ đó SA có khả năng đi qua những vùng có objective tạm thời xấu để tiếp tục khám phá không gian tìm kiếm.

Đây là lý do SA có lợi thế so với một search thuần greedy.

---

# Phần 3 — HMP và Binary Co-occurrence Matrix

Một đóng góp quan trọng của HMP là sử dụng **Binary Co-occurrence Matrix** để lưu thông tin support của các cặp item.

Ví dụ:

```text
       A   B   C   D
A      -   8   5   2
B          -   7   3
C              -   4
D                  -
```

Giá trị `(A,B)` cho biết mức độ đồng xuất hiện của `A` và `B`.

Ma trận này được xây dựng bằng một pass qua dataset và sau đó cho phép truy vấn support của một cặp item nhanh hơn thay vì liên tục quét lại toàn bộ database. Chi phí xây dựng vẫn phụ thuộc vào tổng số cặp trong các transaction; `O(1)` chỉ nên dùng cho một lần truy vấn một ô đã được lưu, không phải cho toàn bộ quá trình tìm cặp tốt nhất.

Điều này đặc biệt hữu ích cho heuristic dựa trên pairwise co-occurrence.

**Lưu ý:** Binary Co-occurrence Matrix là thông tin có sẵn từ dataset/HMP. Nó không phải là bộ nhớ học được từ các solution của SA.

---

# Phần 4 — Điểm mạnh và giới hạn mà ta quan tâm

## 4.1. Điểm mạnh của SA

SA không cần lưu toàn bộ không gian tìm kiếm.

Thay vì:

```text
generate everything
→ store everything
→ compare everything
```

nó có thể:

```text
generate
→ evaluate
→ keep current information
→ discard candidate
→ generate next candidate
```

Do đó search có thể hoạt động với bộ nhớ tương đối nhỏ so với việc lưu toàn bộ các solution đã khám phá.

---

## 4.2. Câu hỏi nghiên cứu của chúng ta

Từ đây xuất hiện câu hỏi:

> Nếu search đã từng tìm thấy nhiều solution tốt, liệu những solution đó có chứa thông tin cấu trúc có thể giúp ích cho những bước search tiếp theo hay không?

HMP-SA chủ yếu sử dụng trạng thái hiện tại và các heuristic có sẵn để quyết định bước tiếp theo.

Ý tưởng của chúng ta là bổ sung một dạng **compressed memory**:

```text
Good solutions
      ↓
Extract structural information
      ↓
Compress into a small representation
      ↓
Use representation to bias future search
```

Do đó:

```text
SEARCH
  ↓
GOOD SOLUTIONS
  ↓
LEARN STRUCTURE
  ↓
GUIDE SEARCH
  ↓
GOOD SOLUTIONS
  ↓
LEARN AGAIN
  ↓
...
```

Đây là ý tưởng trung tâm của **HMP-GSA**.

---

# Phần 5 — HMP-GSA

## 5.1. Ý tưởng

HMP-GSA giữ nguyên:

* MDL objective;
* candidate representation;
* neighborhood concept;
* Simulated Annealing;
* stochastic acceptance.

Thay đổi chính là:

> Search không chỉ sử dụng thông tin của database và trạng thái hiện tại, mà còn học một representation nhỏ từ những solution tốt đã tìm thấy.

Ta gọi representation này là:

**Feature Weight Vector**

```text
W = [w₁, w₂, ..., wₖ]
```

Mỗi weight thể hiện mức độ ưu tiên của một structural feature.

Thay vì lưu:

```text
solution₁
solution₂
solution₃
...
solutionₙ
```

ta chỉ giữ:

```text
W
```

Đây là ý tưởng **compressed search memory**.

**Trạng thái triển khai hiện tại:** Python đã có engine Guided-SA, các variant,
dataset scan và một MDL-like adapter. Tuy nhiên adapter này chưa phải là bản
dịch đầy đủ của toàn bộ code-table state trong HMP paper/Java. Vì vậy các slide
về kết quả HMP-GSA phải ghi rõ đây là prototype/MDL-like validation, không phải
claim tái tạo hoàn chỉnh.

---

# Phần 6 — Ba cách định nghĩa Feature Weight Vector

Đây là phần nghiên cứu chính mà chúng ta muốn thử nghiệm.

Ta chưa giả định trước variant nào tốt nhất.

Thay vào đó, thử ba hypothesis độc lập.

---

## Variant A — Successful Feature

### Ý tưởng

Một feature được reinforcement nếu nó xuất hiện trong một mutation dẫn tới cải thiện MDL.

Ví dụ:

```text
current
   ↓
add B
   ↓
new solution
   ↓
ΔMDL < 0
```

thì feature `B` nhận reinforcement.

Một dạng update đơn giản:

```text
wᵢ ← wᵢ + α · |ΔMDL|
```

Feature càng liên quan tới những bước tạo ra compression tốt, weight càng tăng.

### Hypothesis

> Những feature thường xuất hiện trong mutation làm giảm MDL có khả năng hữu ích cho những mutation tiếp theo.

---

# Variant B — Good-Solution Frequency

### Ý tưởng

Không quan tâm trực tiếp mutation nào tạo ra improvement.

Thay vào đó, khi tìm được một solution đủ tốt:

```text
L(C,D) thấp
```

ta xem những feature nào xuất hiện trong solution đó.

Ví dụ:

```text
Good solution 1: A B C
Good solution 2: A B
Good solution 3: A C
```

ta có:

```text
A → xuất hiện nhiều
B → xuất hiện nhiều
C → xuất hiện nhiều
```

và reinforcement weight dựa trên frequency.

Một dạng đơn giản:

```text
wᵢ ← wᵢ + α
```

mỗi khi feature `i` xuất hiện trong một good solution.

### Hypothesis

> Những feature thường xuất hiện trong các solution có MDL thấp có khả năng là thành phần của những vùng tốt trong search space.

---

# Variant C — Mutation + Feature

Variant này giữ nhiều thông tin hơn A.

Thay vì chỉ nhớ:

```text
B tốt
```

ta nhớ:

```text
ADD(B) tốt
REMOVE(B) tốt
```

hoặc tổng quát hơn:

```text
(operation, feature)
```

Ví dụ:

```text
(add, A)
(add, B)
(remove, C)
```

có những weight riêng.

Nếu:

```text
ADD(B)
```

thường tạo ra improvement thì weight của `(add,B)` tăng.

Nếu:

```text
REMOVE(B)
```

thường có lợi thì weight của `(remove,B)` tăng.

### Hypothesis

> Không chỉ feature quan trọng, mà **cách feature được sử dụng** cũng chứa thông tin về hướng search.

Variant C vì vậy có representation giàu thông tin hơn A/B nhưng cũng có nhiều state cần lưu hơn.

---

# Phần 7 — Ba tầng hình thành Weight

Ba variant trên trả lời câu hỏi **search học cái gì**.

Ngoài ra, chúng ta có một cơ chế chung để hình thành weight theo thời gian.

## Layer 1 — Initial Prior

Search không bắt đầu hoàn toàn từ số 0.

HMP đã có thông tin structural từ database, đặc biệt là pairwise co-occurrence.

Do đó ta có thể khởi tạo:

```text
W₀
```

từ prior này.

Ví dụ:

```text
co-occurrence(A,B) cao
        ↓
A-B có initial weight cao hơn
```

Đây chỉ là **prior từ dữ liệu**, chưa phải bằng chứng rằng feature đó thực sự tốt theo MDL.

---

## Layer 2 — Reinforcement

Trong quá trình search, weight được cập nhật dựa trên variant đang thử.

Ví dụ với Successful Feature:

```text
ΔMDL < 0
      ↓
reinforce feature
```

Với Good-Solution Frequency:

```text
good solution found
      ↓
reinforce features appearing in it
```

Với Mutation + Feature:

```text
successful mutation
      ↓
reinforce (operation, feature)
```

---

## Layer 3 — Decay

Một feature tốt ở giai đoạn trước không nhất thiết tốt mãi mãi.

Do đó weight có thể giảm theo thời gian:

```text
wᵢ ← wᵢ(1 - γ)
```

Mục đích:

```text
old information
      ↓
gradually forgotten
```

Trong khi feature tiếp tục được reinforcement sẽ giữ weight cao.

Như vậy memory không phải một archive vô hạn.

Nó là một **adaptive compressed memory**.

---

# Phần 8 — Multinomial Sampling

Feature Weight Vector chỉ hữu ích nếu nó có thể ảnh hưởng đến search.

Ta chuyển weight thành xác suất:

```text
P(i) = wᵢ / Σⱼ wⱼ
```

Sau đó sử dụng **multinomial sampling** để chọn feature.

Ví dụ:

```text
A: 0.50
B: 0.30
C: 0.15
D: 0.05
```

thì một lần sampling có thể cho:

```text
A
```

nhưng không phải lúc nào cũng là `A`.

Điều này rất quan trọng.

HMP-GSA không biến thành greedy search:

```text
always choose A
```

mà là:

```text
A: rất có khả năng
B: có khả năng
C: vẫn có khả năng
D: ít khả năng
```

Do đó guidance tạo ra **biased stochastic exploration**.

---

# Phần 9 — Guiding Search

Luồng hoàn chỉnh:

```text
                 DATABASE
                     │
                     ↓
             Initial Prior
                     │
                     ↓
              Feature Weights
                     │
                     ↓
              Multinomial
                Sampling
                     │
                     ↓
              Generate Move
                     │
                     ↓
               Evaluate MDL
                     │
             ┌───────┴───────┐
             ↓               ↓
        Good/Useful       Not useful
             │
             ↓
        Reinforcement
             │
             ↓
            Decay
             │
             ↓
       Updated Weights
             │
             └──────────────→ next search
```

Điểm quan trọng:

**Feature Weight Vector không thay thế MDL evaluation.**

Nó chỉ giúp quyết định:

> "Nên thử cái gì trước / với xác suất bao nhiêu?"

Còn:

> "Cái này thực sự tốt hay không?"

vẫn phải được quyết định bởi MDL objective.

---

# Phần 10 — Vì sao cách này có thể tiết kiệm memory?

HMP-GSA không lưu toàn bộ history.

Ví dụ search đã khám phá:

```text
M₁, M₂, M₃, ..., M₁₀₀₀₀
```

thay vì giữ tất cả, ta có thể nén thông tin thành:

```text
W = [w₁, w₂, ..., wₖ]
```

Search chỉ cần giữ representation này cùng với trạng thái hiện tại và những dữ liệu cần thiết cho evaluation.

Vì vậy, mục tiêu của HMP-GSA không phải:

> "nhớ mọi solution."

Mà là:

> **"nhớ những thông tin hữu ích từ nhiều solution bằng một representation nhỏ."**

Đây là trade-off quan trọng:

```text
Memory ↓
    ↕
Information retained ↓
    ↕
Guidance quality
```

Một representation quá đơn giản có thể không học đủ thông tin.

Một representation quá lớn có thể làm mất lợi thế memory.

---

# Phần 11 — Guidance không được biến thành Greedy Search

Đây là điều kiện quan trọng của hypothesis.

Nếu guidance quá mạnh:

```text
high weight
   ↓
always select
   ↓
same region
   ↓
local optimum
```

thì HMP-GSA có thể mất lợi thế của SA.

Vì vậy guidance chỉ nên **bias probability**, không quyết định tuyệt đối.

Conceptually:

```text
Ordinary SA:

exploration
████████████████████

GSA:

exploration ████████████
guidance    ███████
```

thay vì:

```text
guidance = 100%
exploration = 0%
```

SA vẫn phải có khả năng thử những feature có weight thấp.

---

# Phần 12 — Research Hypotheses

Ta không giả định rằng HMP-GSA chắc chắn tốt hơn HMP-SA.

Ta kiểm tra ba hypothesis:

### H1 — Successful Feature

Feature xuất hiện trong những mutation làm giảm MDL có thể dùng để dự đoán hướng search hữu ích.

### H2 — Good-Solution Frequency

Feature xuất hiện thường xuyên trong good solutions có thể dùng để xác định những vùng có triển vọng trong search space.

### H3 — Mutation + Feature

Thông tin về `(operation, feature)` có thể cung cấp guidance chính xác hơn chỉ sử dụng feature đơn thuần.

---

# Phần 13 — Những gì cần chứng minh bằng thực nghiệm

Không cần chứng minh bằng toán học rằng một variant luôn thắng.

Ta cần kiểm tra:

```text
HMP-SA
   vs
HMP-GSA-A
HMP-GSA-B
HMP-GSA-C
```

trên cùng điều kiện.

Các chỉ số chính:

* Best MDL score
* Mean best MDL score
* Runtime
* Number of MDL evaluations
* Stability giữa các random seed
* Memory usage
* Convergence behavior

Vì MDL là objective cần **minimize**:

```text
lower MDL = better compression
```

---

# Phần 14 — Thí nghiệm Prototype đầu tiên

Để tránh thay đổi quá nhiều thứ cùng lúc, ba variant phải dùng chung:

```text
Dataset
Initial state
Neighborhood
MDL evaluator
Temperature schedule
SA acceptance rule
Iteration/evaluation budget
Random seeds
```

Chỉ thay đổi:

```text
HOW WEIGHTS ARE LEARNED
```

tức:

```text
A: Successful Feature

B: Good-Solution Frequency

C: Mutation + Feature
```

Điều này giúp nếu kết quả khác nhau, ta có cơ sở nói rằng sự khác biệt đến từ **cơ chế memory/guidance**, thay vì một thay đổi khác trong algorithm.

---

# Phần 15 — Kết quả thí nghiệm Prototype

## 15.1. Mục tiêu

Pilot hiện tại chạy trực tiếp trên dataset crawling thật. Nó chưa nhằm khẳng
định HMP-GSA tối ưu MDL tốt hơn HMP-SA paper-exact. Mục tiêu là kiểm tra pipeline
dataset và xem guidance có tạo khác biệt ban đầu hay không:

> Kiểm tra xem ba cách học memory A/B/C có tạo ra hành vi tìm kiếm khác nhau
> khi cùng chạy trên một Guided-SA engine hay không.

Vì vậy, runner dùng hai transaction database thật: `requirements.txt` và
`themealdb.txt`. Synthetic landscapes vẫn được giữ trong source để regression,
nhưng không còn được runner thực thi.

## 15.2. Thiết lập thí nghiệm

Các variant dùng chung:

```text
Số dataset         = 2
Số variant          = 5
Số random seed      = 3 (0 đến 2)
Số iteration/run    = 30
Candidate pool      = 5
Temperature         = 2.0 giảm dần đến 0.01
Objective           = lower score is better
```

Các variant được so sánh:

```text
unguided                 baseline, không học online
prior_only               chỉ dùng prior tĩnh
successful_feature       Variant A
good_solution_frequency  Variant B
mutation_feature         Variant C
```

Output được sinh bằng:

```powershell
python -m hmp_gsa.experiments.run --config hmp_gsa/configs/baseline.json
```

Kết quả chạy gần nhất nằm trong:

```text
results/20260915_132336/summary.csv
```

Mỗi ô trong bảng dưới đây là **mean best score** qua 10 seed. Vì objective cần
minimize, số nhỏ hơn là tốt hơn.

## 15.3. Kết quả chính

| Dataset | Unguided | Prior-only | Variant A | Variant B | Variant C |
|---|---:|---:|---:|---:|---:|
| requirements | 1,143,091.33 | 1,125,641.00 | 1,125,641.00 | 1,125,641.00 | 1,125,641.00 |
| themealdb | 233,516.00 | 229,647.33 | 229,647.33 | 229,647.33 | 229,647.33 |

## 15.4. Giải thích kết quả

### Kết quả 1 — Pilot thật đã chạy qua cả hai dataset

Runner đã đọc hai file crawling, tạo adapter riêng cho từng dataset và ghi kết
quả theo khóa `dataset`. Đây là khác biệt quan trọng so với experiment runner
cũ vốn luôn tạo `SyntheticLandscape`.

### Kết quả 2 — Chưa thấy khác biệt giữa các variant

Sau khi sửa prior theo đúng pattern key, các phương pháp dùng prior tốt hơn
`unguided` trên cả hai dataset. Tuy nhiên `prior_only` và ba variant online có
cùng mean best score trong pilot 3 seed và 30 iteration.

Điều này cho thấy static co-occurrence prior đang có tác dụng, nhưng budget
ngắn chưa tạo đủ reinforcement để phân biệt A/B/C.

### Kết quả 3 — Không được kết luận các variant tương đương nói chung

Điểm cuối giống nhau không chứng minh rằng đường hội tụ, acceptance rate,
runtime hoặc memory giống nhau. Các thí nghiệm tiếp theo cần đo:

```text
best score theo evaluation count
số evaluation để đạt target
acceptance rate
variance giữa các seed
```

## 15.5. Kết luận được phép rút ra

Từ thí nghiệm này, ta có thể kết luận:

```text
1. Engine có thực sự chạy được cả control và ba variant.
2. Các variant tạo ra hành vi khác nhau trên objective phù hợp.
3. Variant A có tín hiệu tích cực trên hai landscape.
4. Guidance có thể gây hại trên landscape đánh lừa local signal.
5. Việc giữ lại tính stochastic của SA vẫn cần thiết.
```

Nhưng chưa được kết luận:

```text
1. HMP-GSA tốt hơn HMP-SA trên dataset thật.
2. Variant A là variant tốt nhất nói chung.
3. Feature frequency luôn dự đoán được pattern MDL tốt.
4. Kết quả synthetic là kết quả MDL.
5. Python adapter hiện tại là bản tái tạo đầy đủ của HMP paper.
```

## 15.6. Liên hệ với pipeline HMP thật

Repository còn có hai bằng chứng riêng biệt:

### Java HMP-SA trên `iris.txt`

Java reference đã sinh code table thật. Một run được ghi nhận có:

```text
Initial compression size = 24000 bits
Final code table size    = 44
Patterns from SA         = 13
Final compression size  = 3690 bits
Compression ratio        = 15.375%
```

Đây là kết quả của HMP-SA Java, không phải kết quả của các variant Python
HMP-GSA.

### Python dataset scan

Python đã đọc dataset transaction và sinh:

```text
statistics.json
item_frequency.csv
cooccurrence.csv
```

Đây là preprocessing thật và pilot runner hiện đã chạy trên hai dataset
crawling. Tuy nhiên nó chưa phải benchmark đối chứng Java paper-exact. Bản scan
`accident.txt` hiện ghi nhận:

```text
Transactions (|D|) = 340,183
Distinct items     = 468
Average length     = 33.8079
Density            = 7.2239%
Observed pairs     = 46,815
```

Một kiểm tra runtime trực tiếp với `DatasetMDLAdapter` trên toàn bộ
`accident.txt` cũng cho thấy giới hạn hiện tại: `_candidate_patterns()` đang
sinh các tổ hợp từ từng transaction cho mỗi bước. Với dataset lớn như trên,
việc này tăng rất nhanh và chưa trở thành một pipeline thực nghiệm thực dụng.
Vì vậy hiện tại chỉ có thể khẳng định **real dataset scan + adapter prototype**,
chưa thể khẳng định **real-dataset HMP-GSA search đã chạy hoàn chỉnh**.

Bước tiếp theo là thay candidate generation bằng cơ chế tương thích với HMP,
dùng sparse co-occurrence structure để giới hạn candidate, sau đó mới chạy
cùng dataset, cùng state, cùng evaluator và cùng evaluation budget cho HMP-SA,
prior-only và A/B/C.

---

# Phần 16 — Câu hỏi nghiên cứu mở

Sau prototype, các câu hỏi quan trọng hơn mới được đặt ra:

1. Feature nào thực sự đại diện tốt cho cấu trúc của good solutions?
2. Frequency có thực sự tương quan với MDL improvement không?
3. Successful Feature có tốt hơn chỉ nhìn frequency không?
4. Mutation + Feature có đáng với lượng memory bổ sung không?
5. Prior từ co-occurrence có giúp search tốt hơn không?
6. Decay có giúp tránh stale information không?
7. Guidance có giảm số MDL evaluations cần thiết không?
8. Guidance có làm mất exploration của SA không?
9. HMP-GSA có cải thiện best MDL trong cùng evaluation budget không?
10. Memory overhead của GSA có thực sự nhỏ so với lợi ích đạt được không?

---

# Phần 17 — Định hướng nghiên cứu

Do đó, HMP-GSA chưa nên được xem là một thuật toán hoàn chỉnh.

Ở giai đoạn hiện tại, nó là một **research hypothesis**:

> **Nếu các solution tốt trong MDL search chứa những structural patterns có thể học được, thì một compressed Feature Weight Vector có thể dùng để bias Simulated Annealing toward promising regions mà không cần lưu toàn bộ search history.**

Ta sẽ kiểm tra hypothesis này từng bước:

```text
Define representation
        ↓
Implement A / B / C
        ↓
Controlled experiments
        ↓
Observe behavior
        ↓
Compare with HMP-SA
        ↓
Keep / reject / modify hypothesis
        ↓
Develop stronger model
```

Mục tiêu trước mắt không phải chứng minh HMP-GSA "chắc chắn tốt hơn".

Mục tiêu là xác định:

> **Search có thực sự học được thông tin hữu ích từ good solutions hay không, và nếu có thì representation nào mang lại trade-off tốt nhất giữa compression quality, search time và memory?**
