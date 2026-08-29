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

Nếu candidate mới tốt hơn:

```text
Δ = L(current) - L(candidate) > 0
```

thì chấp nhận.

Nếu candidate mới xấu hơn, nó vẫn có thể được chấp nhận với một xác suất phụ thuộc vào nhiệt độ:

```text
P(accept) = exp(Δ / T)
```

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

Ma trận này được xây dựng bằng một pass qua dataset và sau đó cho phép truy vấn support của một cặp item nhanh hơn thay vì liên tục quét lại toàn bộ database.

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

# Phần 15 — Câu hỏi nghiên cứu mở

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

# Phần 16 — Định hướng nghiên cứu

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
