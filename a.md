# AGENDA BÁO CÁO: KHUNG THUẬT TOÁN HMP-SA & ĐỊNH HƯỚNG MỞ RỘNG HMP-GSA TRÊN NỀN TẢNG MDL

---

## Phần 0: Bối cảnh & So sánh nền tảng (Related Work)

**Vấn đề của Frequent Pattern Mining truyền thống:**
- Các thuật toán như Apriori, FP-Growth sinh ra hàng triệu pattern dư thừa (pattern explosion), đặc biệt khi ngưỡng support thấp, khiến kết quả khó diễn giải.
- Redundancy cao: nhiều pattern chỉ là biến thể của nhau, mang cùng một lượng thông tin.

**Krimp (Vreeken et al.):**
- Áp dụng MDL để chọn Code Table từ tập ứng viên sinh sẵn (thường bằng FP-Growth ở support thấp), duyệt theo *standard candidate order*, thêm vào nếu giúp giảm $L(C,D)$.
- **Hạn chế:** phụ thuộc nặng vào thứ tự duyệt ứng viên và chất lượng tập ứng viên đầu vào — giải thuật greedy, không có khả năng quay lui.

**SLIM (Smets & Vreeken):**
- Không cần sinh ứng viên trước; xây dựng Code Table bằng cách hợp nhất (union) hai mã đã có, chọn cặp hợp nhất giúp nén tốt nhất.
- **Hạn chế:** vẫn là giải thuật tham lam — không gian tìm kiếm giới hạn ở các pattern hình thành từ hợp nhất trực tiếp, dễ bỏ sót tối ưu toàn cục.

**→ Khoảng trống mà HMP-SA lấp vào:**
- Cả Krimp lẫn SLIM đều là giải thuật tham lam đơn hướng, không có cơ chế thoát tối ưu cục bộ.
- HMP-SA đưa Simulated Annealing vào, dùng Metropolis criterion để chấp nhận có xác suất bước đi "tệ hơn tạm thời", giúp khám phá không gian pattern rộng hơn.

---

## Phần 1: Nền tảng Lý thuyết & Mô hình hóa MDL (Minimum Description Length)

- **Triết lý nén dữ liệu:** thay vì tìm tất cả tổ hợp mẫu phổ biến (dễ bùng nổ tổ hợp), HMP tìm một Bảng mã (Code Table – $C$) chứa các mẫu đại diện giúp nén cơ sở dữ liệu $D$ tốt nhất.
- **Hàm mục tiêu MDL:** cực tiểu hóa tổng độ dài mô tả theo bit:
$$L(C, D) = L(C|D) + L(D|C)$$
  - $L(C|D)$: dung lượng lưu trữ bản thân bảng mã $C$.
  - $L(D|C)$: dung lượng cơ sở dữ liệu sau khi mã hóa bằng các mã trong $C$.
- **Tính toán ban đầu:**
  - Ước tính kích thước gốc thô: $S = 32 \times \text{Tổng số mục}$.
  - Tính mảng Trọng số tần suất động $I_w$ của từng mục dữ liệu đơn lẻ: $w_k = \dfrac{\text{usage}(i_k)}{|D|}$.
- **(Bổ sung) Cơ chế Cover Algorithm:** cần làm rõ cách một pattern "phủ" (cover) một giao dịch — quy tắc thứ tự ưu tiên mã theo *standard cover order* (length giảm dần, rồi đến usage giảm dần) — đây là cơ sở để usage() thực sự được tính trong công thức trên.

---

## Phần 2: Trái tim giải thuật — Vòng lặp HMP-SA (Giai đoạn Heuristic)

- **Cấu trúc hai tầng:** Outer Loop & Inner Loop.
- **Điều kiện dừng Vòng lặp ngoài:** chạy đến khi $|C| < \dfrac{1}{3} \times \text{maxCodeTableSize}$.
- **Khởi tạo mỗi lượt lặp ngoài:**
  - Sinh mẫu ngẫu nhiên ban đầu $p$ dựa trên phân phối trọng số $I_w$, độ dài từ 3 đến 6 mục.
  - Thiết lập nhiệt độ ban đầu $T = T_{init} = 100$.
- **Vòng lặp trong (Simulated Annealing):** hạ nhiệt từ 100 xuống $T_{min} = 0.1$ theo $T \leftarrow \alpha \cdot T$.
  - **Sinh lân cận (GetNeighbor):** đột biến $p$ thành $p'$ bằng cách thêm/bớt đúng 1 mục, điều phối theo $I_w$, kiểm soát độ dài ($m_{min}=3$, $m_{max}=6$).
  - **Đo đạc độ nén bit:** tính $S'$ khi đưa $p'$ vào bảng mã, tính $\Delta S = S - S'$.
  - **Điều kiện Metropolis:** chấp nhận $p'$ nếu $\Delta S > 0$, hoặc chấp nhận có xác suất nếu $e^{\Delta S / T} > \text{Random}(0,1)$.
- **Cơ chế co rút cơ sở dữ liệu động:** nếu sau vòng lặp trong, $S_{init} > S$:
  - Đưa $p$ vào $C$; xóa $p$ khỏi $D$ ($D \leftarrow D \setminus p$).
  - Cập nhật lại $I_w$ dựa trên $D$ đã co rút.
- **Cơ chế dừng sớm:** bộ đếm thử nghiệm thất bại `maxTry`.
- **(Bổ sung) Phân tích độ nhạy tham số:** giải thích căn cứ chọn $T_{init}=100$, $T_{min}=0.1$, hệ số làm nguội $\alpha$, `maxTry`, khoảng độ dài mẫu [3,6] — và ảnh hưởng của chúng lên tốc độ hội tụ / chất lượng nén.

---

## Phần 3: Giai đoạn 2 — Lựa chọn tham lam & Tăng tốc bằng Ma trận

- **Vì sao cần Giai đoạn 2:** SA chỉ tìm pattern chất lượng cao độ dài 3–6; cần `GreedyPatternSelection` để quét, tìm cặp 2 mục phổ biến, lấp đầy $C$ đến `maxCodeTableSize`.
- **Cơ chế GreedyPatternSelection:**
  - Khởi tạo Ma trận Tam giác Thưa (Sparse Triangular Matrix) từ $D$ động còn lại.
  - Tìm cặp $\{i, j\}$ có tần suất đồng xuất hiện cao nhất.
  - Đưa cặp vào $C$, xóa khỏi $D$, lặp lại đến khi đủ `maxCodeTableSize`.
    
---

Cấu Trúc Ma Trận Tam Giác Thưa (Sparse Triangular Matrix)
1. Bối cảnh

Trong Giai đoạn 2 của HMP-SA (GreedyPatternSelection), thuật toán cần liên tục tìm cặp mục dữ liệu {i, j} có tần suất đồng xuất hiện cao nhất trong cơ sở dữ liệu động còn lại, để lấp đầy bảng mã C cho đến khi đạt maxCodeTableSize.

Nếu quét tuần tự toàn bộ D mỗi lần cần tìm một cặp như vậy, chi phí là O(|D|) cho mỗi lần tìm — rất tốn kém khi phải lặp lại nhiều lần. Ma trận Tam giác Thưa được dùng để đưa chi phí tra cứu này xuống O(1).

2. Cấu trúc lưu trữ
Tam giác: tần suất đồng xuất hiện có tính đối xứng — count(i,j) = count(j,i) — nên chỉ cần lưu nửa trên của ma trận (i < j). Giảm ngay khoảng 50% bộ nhớ so với ma trận đầy đủ.
Thưa (Sparse): trong nửa tam giác đó, phần lớn cặp (i,j) có count = 0 (không bao giờ đồng xuất hiện trong bất kỳ giao dịch nào). Thay vì cấp phát mảng cố định n × n, chỉ lưu các cặp có count > 0, thường dùng cấu trúc dạng hash map: {(i, j): count}.

4. Quy trình xây dựng (Build phase)
Duyệt qua từng giao dịch t ∈ D.
Với mỗi cặp mục {i, j} ⊆ t (tổ hợp chập 2 trong giao dịch): tăng count(i,j) += 1.
Lặp lại cho toàn bộ D.

Độ phức tạp xây dựng: O(|D| × k̄²), với k̄ là độ dài trung bình của một giao dịch. Đây là chi phí một lần duy nhất (upfront cost), đổi lại các lần tra cứu sau đó chỉ mất O(1).

4. Cập nhật động (Update phase)

Sau mỗi lượt Greedy chọn ra cặp {i, j} tối ưu:

Cặp này được đưa vào bảng mã C và xóa khỏi D.
Ma trận không cần xây dựng lại từ đầu — chỉ cần cập nhật (giảm) count của các cặp liên quan đến i và j trong những giao dịch bị ảnh hưởng.
Đây là điểm mấu chốt để giữ được lợi ích tốc độ: nếu phải rebuild O(|D|) sau mỗi lượt chọn, ưu thế tra cứu O(1) sẽ bị triệt tiêu.

---

## Phần 5: Hạn chế của HMP-SA & Định hướng mở rộng sang HMP-GSA (Guided Simulated Annealing)

**5.1 Hạn chế cốt lõi của HMP-SA:**
- Bước `GetNeighbor` hiện chỉ được điều phối bởi trọng số tần suất tĩnh $I_w$ (usage/|D|) — một tín hiệu toàn cục, không phụ thuộc ngữ cảnh, không biết mục nào *kết hợp* với các mục đã có trong $p$ sẽ giúp nén tốt hơn.
- Nhiều bước lân cận sinh ra chỉ là nhiễu (không cải thiện $\Delta S$), gây lãng phí số lượt thử — đặc biệt ở vùng $T$ gần $T_{min}$, nơi cần khai thác chính xác hơn là khám phá ngẫu nhiên.
- Chất lượng nghiệm cuối phụ thuộc nhiều vào random seed → thiếu ổn định giữa các lần chạy.

**5.2 Ý tưởng cốt lõi của Guided SA:**
- Bổ sung một **hàm dẫn đường $G(i, p)$** — ước lượng "mức độ hứa hẹn" của việc thêm mục $i$ vào pattern $p$ hiện tại — để định hướng `GetNeighbor` thay vì chọn ngẫu nhiên thuần theo $I_w$.
- Xác suất chọn mục $i$ để thêm vào $p'$ chuyển từ tỉ lệ với $w_i$ đơn thuần sang tỉ lệ với hàm kết hợp, ví dụ $w_i \times G(i, p)$.

**5.3 Các thành phần cần thiết kế cụ thể:**
- **Định nghĩa hàm $G$:**
  - Dựa trên Sparse Triangular Matrix đã xây ở Phần 3 (tái sử dụng, dùng sớm hơn trong pipeline thay vì chỉ ở Giai đoạn 2).
  - Hoặc dựa trên ước lượng nén cận biên (marginal gain estimate) — xấp xỉ nhanh $\Delta S$ mà không cần mã hóa lại toàn bộ $D$.
- **Điểm tích hợp $G$ vào vòng lặp:**
  - (a) Ở bước sinh lân cận (đổi phân phối xác suất chọn mục), hoặc
  - (b) Ở bước chấp nhận Metropolis (điều chỉnh $\Delta S$ hiệu dụng), hoặc
  - (c) Cả hai — cần thực nghiệm so sánh.
- **Cân bằng guide vs. explore:** nếu $G$ quá mạnh, SA có thể mất khả năng thoát local optimum (quay lại vấn đề tham lam của Krimp/SLIM). Đề xuất hệ số trộn $\beta$ giảm dần theo $T$ — early stage ưu tiên khám phá, late stage ưu tiên khai thác.
- **Chi phí tính toán của $G$:** đánh giá độ phức tạp của $G$ so với chi phí tính $\Delta S$ hiện tại, tránh lợi ích bị triệt tiêu bởi overhead.
- **Kế hoạch benchmark HMP-GSA vs. HMP-SA:**
  - Số vòng lặp trong trung bình để hội tụ.
  - Chất lượng nén cuối cùng $L(C,D)$.
  - Độ ổn định qua nhiều lần chạy với random seed khác nhau.
  - Độ chính xác phân loại (đối chiếu với Phần 4).

---

**Ghi chú trình bày:** Phần 0 nên đặt ngay đầu để định vị vấn đề trước khi đi vào chi tiết kỹ thuật; Phần 5 đặt cuối cùng, đóng vai trò cầu nối logic từ "HMP-SA hiện có" sang "HMP-GSA sắp phát triển" — tránh để phần kết luận rời rạc với nội dung chính.
