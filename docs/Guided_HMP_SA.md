# MDL-GSA

## Tổng quan ý tưởng

Sau khi tìm hiểu cách tìm của HMP-SA (là một thuật toán SA bình thường trên nguyên lý MDL), mình hỏi:

> Thay vì cho thuật toán HMP-SA khai phá không gian MDL mà không học từ các solution trước đó (chọn, evaluate và vứt), chúng ta sẽ tìm hiểu cấu trúc của các giải pháp tốt có thể học được và để dẫn dắt/thiên vị để khai phá các lựa chọn có tính ngẫu nhiên có tính toán.

*(Từ bài báo khác: [Guided Simulated Annealing Method for Optimization Problems](https://arxiv.org/pdf/cond-mat/0302137), C. I. Chou, R. S. Han, S. P. Li, T. K. Lee)*

### Một bước cơ bản tổng

**Tìm → Tìm các giải pháp tốt → Học đặc trưng cấu trúc → Lại tìm → Lại học**

---

## 1. Nhắc lại vấn đề HMP đang giải quyết

Trước khi đi sâu hơn, ta nên nhai lại vấn đề HMP đang giải quyết để ta có thể infer được một chút logic trong lập luận.

Chúng ta có một CSDL:

$$
CSDL = \{t_1, t_2, \ldots\}
$$

Từng yếu tố có vật phẩm:

$$
t_1 = \{A, B, C, D\}
$$

$$
t_2 = \{A, B, C, E\}
$$

$$
t_3 = \{A, B, D\}
$$

Chúng ta muốn tìm các **tập đặc trưng / tập vật phẩm** có thể nén được các thông tin hữu ích có thể tổng quan được cả CSDL, như:

$$
y = \{\{A,B\}, \{B\}\}
$$

Đây chính là **model** của chúng ta, hoặc là **"code table"**.

---

## 2. Đi qua nhanh về MDL

Một model tốt sẽ cho ta lời giải thích tốt về tổng quan CSDL mà không quá phức tạp.

$$
\text{Total Description Length}
=
\text{Model Cost}
+
\text{Encoded Data Cost}
$$

Chúng ta muốn chi phí của **Total Description Length** tối thiểu, có nghĩa là phải cân bằng giữa:

- **Model Cost**
- **Encoded Data Cost**

Nếu không xài MDL thì search space sẽ lên:

$$
2^{(2^n-1)}
$$

Một con số vô dụng.

---

# 3. Tiền bối HMP-SA

Chúng ta sẽ nói sơ về tiền bối HMP-SA ban đầu để hiểu được hướng đi và câu hỏi nghiên cứu của MDL-GSA.

### Luồng tổng quan

```text
CSDL
  ↓
Làm sạch Code Table XYZ
  ↓
Lập tập Candidate
  ↓
Đánh giá tập nén
  ↓
Giữ / Bỏ
  ↓
Sẽ có Candidate cho C
  ↓
Lặp tiếp

## 3 tầng hình thành Weight

Ta không muốn lưu toàn bộ lịch sử solution. Thay vào đó, search giữ một **Feature Weight Vector** nhỏ gọn, và weight được hình thành từ 3 nguồn:

### Layer 1 — Initial Prior

Trước khi search, dùng structural information có sẵn từ HMP, đặc biệt là **Binary Co-occurrence Matrix**, để khởi tạo:

$$
W_0(I)
$$

Ý tưởng:

> Những cấu trúc có quan hệ mạnh trong CSDL được xem là có triển vọng ngay từ đầu.

Đây là **prior**, chưa phải bằng chứng rằng feature thực sự tốt cho MDL.

### Layer 2 — Trajectory Reinforcement

Trong quá trình search, nếu một feature tham gia vào một mutation làm giảm MDL:

$$
\Delta MDL < 0
$$

thì tăng weight của nó, ví dụ:

$$
W_{t+1}(I)=
W_t(I)+\alpha|\Delta MDL|
$$

Ý tưởng:

> Search không chỉ học từ CSDL, mà còn học từ chính kinh nghiệm optimization của nó.

### Layer 3 — Decay / Forgetting

Một feature từng tốt có thể không còn tốt ở vùng search khác. Vì vậy weight được giảm dần nếu không tiếp tục được reinforcement:

$$
W_{t+1}(I)=W_t(I)(1-\gamma)
$$

Ý tưởng:

> Feature hữu ích liên tục sẽ giữ weight cao; thông tin cũ hoặc chỉ tình cờ hữu ích sẽ dần mất ảnh hưởng..
