# Rà soát và mở rộng bài thuyết trình HMP-GSA

## Mục đích

Tài liệu này là phần mở rộng đã hiệu chỉnh, sẵn sàng cho slide, dành cho bài thuyết trình HMP-GSA được cung cấp. Nó ghi nhận các khẳng định cần được giới hạn điều kiện và bổ sung các phát hiện từ repository hiện tại để bài thuyết trình phân biệt được:

- cài đặt Java HMP-SA gốc;
- prototype nghiên cứu Guided-SA bằng Python;
- tầng tiền xử lý dataset;
- adapter giống MDL hiện tại; và
- các kết quả thực sự được đo lường so với các kết quả vẫn chỉ là giả thuyết.

Deck được cung cấp dưới dạng tệp PDF đính kèm, nhưng không có mã nguồn `.pptx`/`.odp` chỉnh sửa được trong workspace. Do đó các phần này có thể được sao chép thủ công vào bài thuyết trình hoặc dùng làm đặc tả nội dung để dựng lại phiên bản chỉnh sửa được.

## Hiệu chỉnh các slide hiện có

### 1. Delta MDL và dấu của Metropolis

Bài thuyết trình phải dùng nhất quán một quy ước. Quy ước khuyến nghị:

```text
Delta_MDL = L(candidate, D) - L(current, D)
```

Vì MDL được tối thiểu hóa:

```text
Delta_MDL < 0  -> candidate cải thiện nén -> chấp nhận
Delta_MDL = 0  -> objective bằng nhau -> chấp nhận
Delta_MDL > 0  -> candidate tệ hơn -> chấp nhận với exp(-Delta_MDL / T)
```

Cài đặt Java dùng quy ước savings tương đương:

```text
savings = currentCompressionSize - newCompressionSize
```

Do đó, một slide nói `L(current) - L(candidate) < 0` biểu thị sự cải thiện là sai. Dấu phải được đảo lại, hoặc biến nên được đổi tên thành `savings`.

### 2. Độ phức tạp của ma trận đồng xuất hiện

Ma trận tam giác thưa hỗ trợ tra cứu trực tiếp một cặp đã lưu. Đó là khẳng định tra cứu `O(1)` dưới các giả định cài đặt. Không đúng khi trình bày toàn bộ quá trình chọn greedy là `O(1)`:

- xây dựng ma trận quét các giao dịch và các cặp item của chúng;
- xóa và dựng lại nó sau khi giảm residual quét lại database hiện tại;
- tìm cặp cực đại có thể quét các mục đã lưu trừ khi duy trì thêm cấu trúc ưu tiên.

Cách diễn đạt an toàn hơn:

> Ma trận thưa tránh việc quét lại toàn bộ database cho mỗi truy vấn hỗ trợ cặp. Nó giảm sử dụng bộ nhớ cho cấu trúc cặp thưa và tăng tốc tra cứu hỗ trợ đơn lẻ; tổng chi phí khai phá vẫn phụ thuộc vào số lượng giao dịch, cặp và lần dựng lại.

### 3. “Ma trận đồng xuất hiện nhị phân” so với bộ nhớ đã học

Ma trận là prior có nguồn gốc từ dataset hoặc tín hiệu heuristic. Nó không phải bộ nhớ GSA đã học. Bộ nhớ đã học là bản đồ trọng số được cập nhật từ các sự kiện tìm kiếm. Bài thuyết trình nên thể hiện hai mũi tên riêng biệt:

```text
Dataset -> prior đồng xuất hiện W_prior
Hành trình tìm kiếm -> bộ nhớ đã học W_learned
```

Cả hai đều có thể ảnh hưởng đến việc lấy mẫu, nhưng chúng có ý nghĩa khác nhau và không được gọi là cùng một bộ nhớ.

### 4. HMP-SA so với prototype Python

Runner Java gốc không giống hệt engine Python. Runner Java có:

- vòng lặp ngoài thêm các pattern được chấp nhận vào `codetable`;
- vòng lặp SA trong trên một candidate pattern;
- giảm residual database động sau khi chấp nhận một pattern hữu ích;
- giai đoạn điền pattern cặp sau đó sử dụng ma trận thưa.

Engine Python có vòng lặp Guided-SA tổng quát một candidate mỗi iteration. Nó được thiết kế như một ranh giới adapter và chưa tái tạo mọi chuyển trạng thái Java.

### 5. Các slide HMP-GSA chứa placeholder

Các trang được cung cấp cho các phần HMP-GSA, Feature Weight Vector, trọng số ba tầng và Multinomial Sampling chứa Lorem Ipsum thay vì nội dung kỹ thuật. Các trang này nên được thay thế bằng các phần mở rộng bên dưới. Văn bản placeholder không chỉ là vấn đề phong cách: nó để trống đóng góp trung tâm, các phương trình cập nhật, các điều khiển và bằng chứng.

### 6. Các khẳng định về bằng chứng thực nghiệm

Kết quả synthetic hiện tại không chứng minh rằng HMP-GSA cải thiện khai phá HMP/MDL. Chúng kiểm tra xem ba giả thuyết bộ nhớ có hành xử khác nhau trên các objective được kiểm soát hay không. Deck nên ghi nhãn chúng một cách tường minh:

> Kết quả kiểm định giả thuyết synthetic; không phải kết quả MDL trên dataset thật.

Đầu ra Java thật trên `iris.txt` là bằng chứng rằng pipeline HMP-SA legacy chạy được và tạo ra code table. Nó không phải so sánh với HMP-GSA Python vì hai pipeline chưa chia sẻ cùng adapter, trạng thái, ngân sách hay cài đặt evaluator.

## Các slide thay thế và mở rộng

### Slide A — Điều gì thực sự đã được cài đặt

**Tiêu đề:** Ranh giới cài đặt hiện tại

```text
Đã cài đặt và kiểm thử
----------------------
1. Engine Guided-SA tổng quát
2. Nhóm đối chứng unguided và prior-only
3. Các variant successful-feature, good-solution và mutation-feature
4. Quét dataset với persistence tần suất item và đồng xuất hiện cặp
5. Adapter pattern/residual giống MDL
6. Kiểm thử hồi quy và runner synthetic có thể tái tạo

Vẫn cần cho HMP-GSA đúng paper
--------------------------------
1. Trạng thái code-table HMP và mã hóa usage chính xác
2. Lân cận và ngữ nghĩa residual tương thích Java chính xác
3. Adapter wiring thực từ tệp dataset vào vòng lặp GSA
4. Thí nghiệm so sánh HMP-SA với HMP-GSA đã khớp
```

**Ghi chú diễn giả:** Đây là một prototype với ranh giới nghiên cứu rõ ràng, không phải khẳng định rằng mọi chi tiết paper đã được tái tạo.

### Slide B — Kiến trúc thực tế

**Tiêu đề:** Kiến trúc repository và luồng dữ liệu

```text
tệp giao dịch D
      |
      v
prior_scan.py
      |
      +--> statistics.json
      +--> item_frequency.csv
      +--> cooccurrence.csv
      |
      v
Prior có nguồn gốc từ dataset
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
                                   - lấy mẫu một move
                                   - đánh giá candidate
                                   - chấp nhận SA
                                   - cập nhật W
                                   - decay W
```

**Quan trọng:** experiment runner hiện tại dùng landscape synthetic. Dataset scanner và adapter giống MDL tồn tại, nhưng chúng chưa là lệnh thí nghiệm end-to-end mặc định. Một lần probe trực tiếp trên toàn bộ dataset `accident.txt` đã bị dừng vì adapter hiện tại liệt kê tổ hợp từ mọi residual transaction tại mỗi move; việc sinh candidate này chưa khả thi với 340,183 giao dịch và 468 item của dataset.

### Slide C — Bộ nhớ GSA học được gì

**Tiêu đề:** Ba giả thuyết, một vòng lặp tìm kiếm

Tất cả variant chia sẻ:

- candidate pool;
- objective và quy ước thấp hơn là tốt hơn;
- lịch trình nhiệt độ;
- chấp nhận Metropolis;
- ngân sách đánh giá;
- interface prior; và
- cơ chế decay.

Chỉ key đã học và quy tắc cập nhật thay đổi:

| Variant | Key đã học | Bằng chứng sử dụng |
|---|---|---|
| A: Successful Feature | feature | sự kiện mutation cải thiện |
| B: Good-Solution Frequency | feature | sự xuất hiện feature trong một candidate elite |
| C: Mutation + Feature | `(operation, feature)` | sự kiện operation-feature cải thiện |

Nhóm đối chứng:

- `unguided`: không học online, trọng số bộ nhớ đồng đều;
- `prior_only`: prior tĩnh, không học online.

Độ lớn trọng số thô không so sánh trực tiếp được giữa A, B và C vì ngữ nghĩa cập nhật của chúng khác nhau.

### Slide D — Phương trình lấy mẫu đúng

**Tiêu đề:** Lấy mẫu multinomial có hướng dẫn

Với mỗi move `m` trong candidate pool được lấy mẫu:

```text
score(m) = memory_weight(key(m)) * prior_weight(state, m)
P(m) = score(m) / sum(score(x) for x in pool)
```

Engine lấy mẫu một move từ pool và chỉ đánh giá candidate đã chọn đó. Nó không liệt kê và đánh giá toàn bộ lân cận.

Đây là đóng góp của GSA: nó thay đổi candidate nào được khám phá thường xuyên hơn. Nó không thay thế evaluator MDL hay quy tắc chấp nhận SA.

### Slide E — Vòng lặp SA đúng

**Tiêu đề:** Tìm kiếm, đánh giá, chấp nhận, học

```text
1. Sinh một candidate pool nhỏ
2. Lấy mẫu một move bằng W và prior
3. Áp dụng move để có trạng thái candidate
4. Đánh giá objective candidate
5. Chấp nhận hoặc từ chối bằng SA
6. Cập nhật bộ nhớ riêng của variant
7. Áp dụng decay
8. Tiếp tục cho đến khi ngân sách đánh giá cạn
```

Dùng:

```text
Delta_MDL = candidate_score - current_score
```

Candidate tốt hơn khi `Delta_MDL < 0`.

### Slide F — Phát hiện từ pilot trên dataset thật

**Tiêu đề:** Phát hiện pilot trên dataset thật

Cấu hình từ run mới ngày 2026-09-15:

- 2 dataset giao dịch đã crawl;
- 5 variant bao gồm hai nhóm đối chứng;
- 3 seed mỗi variant;
- 30 iteration;
- candidate pool size 5;
- nhiệt độ từ 2.0 đến 0.01.

Kết quả mean best-score chọn lọc, thấp hơn là tốt hơn:

| Dataset | Unguided | Successful Feature | Good-Solution Frequency | Mutation + Feature |
|---|---:|---:|---:|---:|
| `requirements` | 1,143,091.33 | 1,125,641.00 | 1,125,641.00 | 1,125,641.00 |
| `themealdb` | 233,516.00 | 229,647.33 | 229,647.33 | 229,647.33 |

Diễn giải:

- Các phương pháp có prior cải thiện so với `unguided` trên cả hai dataset thật.
- `prior_only` và A/B/C hòa trong pilot ngắn này, nên prior tĩnh đang hoạt động nhưng reinforcement online chưa tách biệt các variant.
- Đây là kết quả trên dữ liệu thật, nhưng không phải bằng chứng rằng các variant tương đương một cách phổ quát.
- Ngân sách ngắn và evaluator giống MDL hiện tại có thể không bộc lộ khác biệt trong hướng dẫn online.
- Telemetry công bằng mỗi run có trong `run_metrics.csv`: đánh giá, tỷ lệ chấp nhận, runtime và số lượng trọng số được ghi mà không chia sẻ adapter cache giữa các run.
- So sánh tiếp theo phải bao gồm đường hội tụ, số đánh giá để đạt mục tiêu, tỷ lệ chấp nhận, runtime và ngân sách lớn hơn.

### Slide G — Bằng chứng từ tham chiếu Java

**Tiêu đề:** Run tham chiếu HMP-SA legacy

Tệp `HMP_SA/result_SAMP_iris.txt` đã lưu trong repo cho thấy runner Java xử lý `iris.txt` với:

- kích thước thô ban đầu: `24000` bit;
- một run ghi nhận: kích thước code table cuối `44`;
- pattern tìm được bởi SA: `13`;
- kích thước nén cuối: `3690` bit;
- tỷ lệ nén báo cáo: `15.375%`;
- runtime báo cáo: `0.02` giây;
- bộ nhớ báo cáo: xấp xỉ `5.23 MB`.

Điều này xác nhận rằng cài đặt Java HMP-SA legacy tạo ra đầu ra code table. Nó chưa thiết lập so sánh HMP-SA với HMP-GSA công bằng vì phía Python chưa được wiring vào cùng trạng thái và giao thức hoàn chỉnh.

### Slide H — Phát hiện tiền xử lý dataset

**Tiêu đề:** Dữ liệu thật đã được quét, nhưng chưa là thí nghiệm GSA đầy đủ

Scanner Python đọc các tệp giao dịch và lưu:

- số lượng giao dịch;
- số lượng item phân biệt;
- độ dài giao dịch trung bình;
- mật độ;
- tần suất item; và
- đồng xuất hiện từng cặp.

Đây là tiền xử lý dataset thật. Hạn chế hiện tại là tích hợp: prior đã lưu chưa là đường chạy runtime hoàn chỉnh cho tìm kiếm HMP-GSA đúng paper trả về code table có thể so sánh.
Quét hiện tại của `accident.txt` báo cáo:

```text
|D| = 340,183 giao dịch
|I| = 468 item phân biệt
ATL = 33.8079
mật độ = 7.2239%
số cặp quan sát được = 46,815
```

Hạn chế hiện tại là độ trung thực của evaluator: pilot dữ liệu thật chạy qua adapter giống MDL, nhưng nó chưa là trạng thái code-table HMP đúng paper. Khẳng định chính xác là **pilot dataset thật qua một adapter giống MDL có giới hạn**, chứ không phải benchmark HMP-GSA đúng paper đã hoàn thành.

### Slide I — Kết luận nghiên cứu ở giai đoạn này

**Tiêu đề:** Điều gì có thể khẳng định bây giờ?

```text
Có thể khẳng định
-----------------
- Engine GSA và ba giả thuyết học đã được cài đặt.
- Nhóm đối chứng dùng chung máy móc tìm kiếm.
- Prior dataset được tính và lưu.
- Tồn tại adapter giống MDL thận trọng.
- Kiểm thử synthetic cho thấy hướng dẫn có thể giúp trên một số landscape và gây hại trên những landscape khác.
- Tham chiếu Java tạo code table HMP-SA thật.

Chưa thể khẳng định
-------------------
- HMP-GSA thắng HMP-SA trên dataset thật.
- Objective Python là cài đặt MDL đúng paper.
- Ma trận thưa làm cho toàn bộ giai đoạn greedy là O(1).
- Kết quả benchmark synthetic xác thực chất lượng khai phá thật.
```

### Slide J — Thí nghiệm tiếp theo

**Tiêu đề:** Bước quyết định tiếp theo

Cài đặt một adapter thật duy nhất quanh trạng thái HMP tương thích Java, rồi chạy:

```text
cùng dataset
cùng trạng thái ban đầu
cùng evaluator
cùng ngân sách move
cùng lịch trình nhiệt độ
cùng seed

HMP-SA / unguided
vs prior-only
vs HMP-GSA-A
vs HMP-GSA-B
vs HMP-GSA-C
```

Báo cáo:

- điểm MDL tốt nhất;
- MDL theo số lần đánh giá;
- số đánh giá để đạt điểm mục tiêu;
- runtime;
- bộ nhớ đỉnh;
- phương sai qua các seed;
- độ đa dạng solution đã khám phá; và
- kích thước bộ nhớ đã học.

Chỉ sau thí nghiệm khớp này, bài thuyết trình mới nên đưa khẳng định hiệu năng về HMP-GSA.

## Bằng chứng repository đã kiểm chứng

Lệnh hồi quy tập trung chạy thành công:

```powershell
python -m unittest hmp_gsa.tests.test_gsa hmp_gsa.tests.test_variants hmp_gsa.tests.test_dataset_scan hmp_gsa.tests.test_mdl_adapter -v
```

Kết quả: `Ran 19 tests ... OK`.

Run synthetic mới được tạo bằng:

```powershell
python -m hmp_gsa.experiments.run --config hmp_gsa/configs/baseline.json
```

Thư mục đầu ra:

```text
results/20260907_181724/
```

Các tệp cài đặt hỗ trợ quan trọng nhất:

- `hmp_gsa/modules/engine.py` — vòng lặp Guided-SA dùng chung;
- `hmp_gsa/modules/adapter.py` — adapter contract và hook prior;
- `hmp_gsa/modules/mdl.py` — adapter giống MDL hiện tại;
- `hmp_gsa/scripts/prior_scan.py` — quét dataset thật và persistence;
- `hmp_gsa/experiments/landscapes.py` — objective synthetic tường minh;
- `HMP_SA/HMP_SA_Runner.java` — cài đặt tham chiếu Java legacy; và
- `HMP_SA/result_SAMP_iris.txt` — đầu ra Java đã ghi.
