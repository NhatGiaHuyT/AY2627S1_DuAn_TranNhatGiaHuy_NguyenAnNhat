# MDL-GSA (Guided HMP-SA)

## Tổng quan ý tưởng

- Sau khi tìm hiểu cách tìm của HMP-SA (là một thuật toán SA bình thường trên nguyên lý MDL), mình tự hỏi: thay vì cho thuật toán HMP-SA khai phá không gian MDL mà không hướng dẫn, liệu ta có thể cho search "học" (learn) những vùng lời giải tốt và sử dụng kiến thức đó để hướng dẫn các bước tìm tiếp theo?

Một bước cơ bản tổng: Tìm -> Tìm các giải pháp tốt -> Học đặc trưng cấu trúc -> lại tìm -> lại học

---

### Bối cảnh vấn đề HMP đang giải quyết

Chúng ta có một CSDL = {t1, t2, ...}

Ví dụ: 
- t1 = {A, B, C, D}
- t2 = {A, B, C, E}
- t3 = {A, B, D}

Mục tiêu: tìm các tập đặc trưng / tập vật phẩm có thể nén được các thông tin hữu ích, có thể tổng quan được cả CSDL, ví dụ:

y = {{A, B}, {B}}

---

### Nhắc lại về MDL

Một model tốt sẽ cho ta lời giải thích tốt về tổng quan CSDL mà không quá phức tạp.

Total Description Length = Model Cost + Encoded Data Cost

Chúng ta muốn tối thiểu hóa Total Description Length — nghĩa là cân bằng giữa Model Cost và Encoded Data Cost. Nếu không dùng MDL thì search space sẽ lên tới 2^(2^n - 1), cực kỳ lớn.

---

### Tóm tắt HMP-SA (tiền bối)

Luồng tổng quan của HMP-SA:

- CSDL -> làm sạch code table XYZ -> lập tập candidate -> đánh giá tập nén -> giữ/bỏ -> SẼ có candidate cho C -> lặp tiếp

HMP-SA sẽ ngẫu nhiên generate các tập candidate rồi chỉnh nó bằng cách lấy neighbor. Neighbor khác bởi MỘT yếu tố trong tập — HMP-SA sẽ chọn neighbor theo cơ chế nào đó (SA).

---

### Điểm mạnh & điểm yếu của HMP-SA

- ĐIỂM MẠNH:
  - SA có thể tiết kiệm chi phí bộ nhớ rất hiệu quả (đánh giá xong vứt, không cần search hết).

- ĐIỂM YẾU (giả thuyết):
  - Cách tìm không thể nhớ được các vùng giải pháp tốt đã đi qua; thuật toán không có bộ nhớ lâu dài về vùng lời giải tốt là một điểm yếu thực.
  - Các thực nghiệm của HMP-SA có tiến triển bất cân xứng: có thể qua nhiều iteration mà không có tiến triển, nhưng rồi bất ngờ vọt lên khi tìm được một đặc trưng tốt.

---

## HMP-GSA (đề xuất)

Mục tiêu: Làm cách nào để quá trình SEARCH học được những cấu trúc/hệ quy mẫu từ các giải pháp tốt và sử dụng chúng để dẫn dắt tìm kiếm trong tương lai?

Luồng ý tưởng: Giải pháp tốt -> trích xuất đặc trưng -> học được sự phân bố -> dẫn dắt hướng đi tương lai.

Đơn giản: một giải pháp tốt không phải giải pháp tổng quát, mà là bằng chứng cho một cấu trúc (structure) của vùng có triển vọng.

Ví dụ: A + B, A + C, A + B + C → ta có thể suy ra mối quan hệ giữa A, B, C.

Thuật toán GSA lấy cảm hứng từ lý thuyết Mean-Field: chúng ta có một ORDER PARAMETER (đại diện) nắm một số thông tin cấu trúc; đại diện này ảnh hưởng tới quá trình khai phá trong tương lai.

Các bước mới (khái quát):
- Cấu hình tốt -> học cấu trúc theo xác suất -> lưu đại diện (ORDER PARAM) -> Guiding Function -> Bias search hướng theo đại diện đó.

Trong chi phí bộ nhớ, ta đơn giản hóa bằng cách không giữ tất cả lịch sử khai phá; thay vào đó giữ một đại diện nén (compressed memory) được học.

Tất nhiên vẫn dùng nhiều ý tưởng của HMP-SA: các giải pháp tốt được thiên vị nhưng vẫn duy trì tính ngẫu nhiên (xác suất) để tránh bị kẹt local.

---

### Câu hỏi then chốt

TA NÊN CHỌN CẤU TRÚC GÌ LÀM ĐẠI DIỆN? CÁC GIẢI PHÁP MÀ MDL ÍT THÌ NÓ NHƯ THẾ NÀO, CÓ TỐT HƠN HMP-SA KHÔNG?

---

## Một cách tiếp cận: Feature Weight Vector

Thay vì lưu toàn bộ lịch sử solution 1..n, ta chỉ lưu một vector trọng số (feature weight vector) — đây là compressed memory của quá trình search.

Ý tưởng cơ bản:

- A - Successful Feature: nếu một feature tham gia vào một mutation làm giảm MDL, feature đó nhận reinforcement.
- B - Good-Solution Frequency: xem tần suất feature xuất hiện trong các solution tốt.
- C - Mutation + Feature: hành động nào trên feature nào thường dẫn đến cải thiện?

### Hệ thống các bước (1 pass)

DATABASE
   │
   ↓
Layer 1: Prior
   │
   ↓
SEARCH
   │
   ↓
Layer 2: Reinforcement
   │
   ↓
Layer 3: Decay
   │
   ↓
Updated Weight Vector
   │
   ↓
Multinomial Sampling
   │
   ↓
Guided Search
   └──────────────→ repeat

---

### 3 tầng hình thành Weight

Ta không muốn lưu toàn bộ lịch sử solution. Thay vào đó, search giữ một **Feature Weight Vector** nhỏ gọn, và weight được hình thành từ 3 nguồn:

#### Layer 1 — Initial Prior

Trước khi search, dùng structural information có sẵn từ HMP, đặc biệt là **Binary Co-occurrence Matrix**, để khởi tạo:

W_0(I)

Ý tưởng: Những cấu trúc có quan hệ mạnh trong CSDL được xem là có triển vọng ngay từ đầu. Đây là prior, chưa phải bằng chứng rằng feature thực sự tốt cho MDL.

#### Layer 2 — Trajectory Reinforcement

Trong quá trình search, nếu một feature tham gia vào một mutation làm giảm MDL:

ΔMDL < 0

thì tăng weight của nó, ví dụ:

W_{t+1}(I) = W_t(I) + α |ΔMDL|

Ý tưởng: Search không chỉ học từ CSDL, mà còn học từ chính kinh nghiệm optimization của nó.

#### Layer 3 — Decay / Forgetting

Một feature từng tốt có thể không còn tốt ở vùng search khác. Vì vậy weight được giảm dần nếu không tiếp tục được reinforcement:

W_{t+1}(I) = W_t(I) (1 - γ)

Ý tưởng: Feature hữu ích liên tục sẽ giữ weight cao; thông tin cũ hoặc chỉ tình cờ hữu ích sẽ dần mất ảnh hưởng.

---
