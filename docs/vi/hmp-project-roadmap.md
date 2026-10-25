# Planing & Phân Chia Nhiệm Vụ: Dự Án HMP (Hybrid Metaheuristics & MDL)




```
[Khởi tạo & Tiền xử lý] ──> [Phát triển thuật toán chính] ──> [Đánh giá & Phân tích] ──> [Cải tiến nghiên cứu mới]
     (DB & Preprocess)                 (Mine Data)                    (Analyze)                (Future Work)
```

---

##  Check list

### PHẦN 1: KHỞI TẠO & TIỀN XỬ LÝ (DB & PREPROCESS)
*Mục tiêu: Đọc dữ liệu thô, chuẩn hóa và tính toán các thông số nền tảng trước khi chạy thuật toán.*

- **1.1. Bộ đọc dữ liệu (Parser):**
  - Viết module đọc các định dạng tệp dữ liệu giao dịch chuẩn (FIMI, SPMF) dưới dạng tệp văn bản (`.txt`), phân tách bằng khoảng trắng.
  - Hỗ trợ nạp nhãn phân lớp (labels) ở cuối mỗi giao dịch phục vụ cho tác vụ phân loại sau này.
- **1.2. Ánh xạ số nguyên (Integer Encoding):**
  - Ánh xạ toàn bộ các mục dữ liệu dạng chữ (items) thành các số nguyên (`integer`) đại diện.
  - Thiết lập quy ước tính toán dung lượng: mỗi số nguyên chiếm mặc định **32 bit** để làm cơ sở tính kích thước ban đầu.
- **1.3. Tính toán trọng số mục dữ liệu (`CalculateItemWeights`):**
  - Cài đặt hàm tính tần suất xuất hiện tương đối của từng mục dữ liệu $i_k$ trong cơ sở dữ liệu $D$:
    $$w_k = \frac{\text{usage}(i_k)}{|D|}$$
- **1.4. Tính dung lượng gốc (`CalculateDatabaseSize`):**
  - Cài đặt hàm đo lường kích thước ban đầu $S$ của cơ sở dữ liệu $D$ khi chưa nén (tính bằng bit):
    $$S = 32 \times \text{Tổng số lượng mục trong các giao dịch}$$

---

### PHẦN 2: PHÁT TRIỂN THUẬT TOÁN CHÍNH (MINE DATA)
*Mục tiêu: Xây dựng các cấu trúc dữ liệu động, cơ chế sinh mẫu lân cận và vòng lặp tối ưu hóa siêu heuristic.*

- **2.1. Quản lý Trạng thái Cơ sở dữ liệu (Matrix & Hashmap):**
  - Cài đặt cấu trúc dữ liệu Hashmap hoặc Ma trận động $\mathbb{M}$ để theo dõi tần suất xuất hiện đồng thời của các cặp mục dữ liệu.
  - Cài đặt hàm cập nhật ma trận khi quét qua giao dịch và hàm xóa mẫu khỏi cơ sở dữ liệu (`D <- D \ p`).
- **2.2. Hàm sinh mẫu lân cận (`GetNeighbor`):**
  - Cài đặt cơ chế sinh mẫu ngẫu nhiên có độ dài tối đa là `Max = 6` dựa trên trọng số $w_i$.
  - Cài đặt thuật toán thêm/bớt ngẫu nhiên 1 mục dữ liệu dựa trên ràng buộc kích thước:
    - Nếu kích thước đạt tối thiểu: bắt buộc thêm mục mới với xác suất tỉ lệ thuận với trọng số $w_i$.
    - Nếu kích thước đạt tối đa (`Max = 6`): bắt buộc bớt mục hiện có.
    - Trường hợp còn lại: chọn ngẫu nhiên thêm hoặc bớt mục.
- **2.3. Bộ tính toán độ nén theo nguyên lý MDL (`CalculateCompression`):**
  - Cài đặt hàm tính tổng độ dài mã hóa $S' = L(C|D) + L(D|C)$.
  - Tính độ dài mã hóa của các mục trong bảng mã $C$ dựa trên tần suất sử dụng thực tế:
    $$L(\text{code}(X|C)) = -\log_2\left(\frac{\text{usage}(X)}{\sum \text{usage}}\right)$$
- **2.4. Thuật toán HMP-SA & HMP-HC:**


---

### PHẦN 3: ĐÁNH GIÁ & PHÂN TÍCH HIỆU NĂNG (ANALYZE)
*Mục tiêu: Thu thập chỉ số đo lường hiệu năng của các thuật toán và ứng dụng vào bài toán phân loại học máy.*

- **3.1. Thu thập số liệu đo lường (Metrics Logging):**
  - Đo lường và xuất ra Thời gian thực thi (Runtime) tính bằng giây.
  - Tính toán Tỷ lệ nén (Compression Ratio - CR %):
    $$\text{CR} = \frac{\text{Kích thước cơ sở dữ liệu sau nén } S}{\text{Kích thước cơ sở dữ liệu gốc } S_{init}} \times 100\%$$
- **3.2. Đánh giá chéo phân loại (10-fold Cross-Validation):**
  - Phân chia dữ liệu có nhãn thành 10 phần (10 folds).
  - Sử dụng bảng mã tối ưu $C$ của từng lớp để nén bản ghi thử nghiệm. Gán nhãn cho bản ghi dựa trên lớp nào mang lại độ dài mã hóa ngắn nhất (MDL).
  - Tính toán độ chính xác trung bình (Classification Accuracy %) để so sánh trực tiếp với kết quả trong bài báo (mục tiêu đạt mức trung bình ~80.50%).

---

### PHẦN 4: HƯỚNG PHÁT TRIỂN & CẢI TIẾN MỚI (FUTURE RESEARCH)
*Mục tiêu: Đưa ra các chỉnh sửa khoa học để viết một bài báo nghiên cứu hoàn toàn mới.*
- **4.1. Kết hợp HMP-SA và HMP-HC:** Chạy tuần tự SA và HC gây ra sự dư thừa và lãng phí không cần thiết nhưng kết hợp chúng một cách khoa học ở các khía cạnh như mô hình lai 2 giai đoạn hoặc Memetic Search (HC lồng SA), hoặc mô hình lai song song có thể phát huy tác dụng. 
- **4.2. Thuật toán tiến hóa bầy đàn:** Thay thế SA bằng thuật toán Di truyền (Genetic Algorithm) để tìm kiếm mẫu tối ưu thông qua các phép lai ghép (Crossover) và đột biến (Mutation).
- **4.3. Tự động hóa tham số (Adaptive Parameters):** Nghiên cứu cơ chế tự động điều chỉnh nhiệt độ $T_{init}$ và hệ số nguội $\alpha$ dựa vào độ dày đặc (Density) và kích thước của bộ dữ liệu đầu vào.
- **4.4. Cải tiến bộ nhớ:** Thay thế Matrix động $\mathbb{M}$ bằng cấu trúc Trie hoặc FP-Tree nhằm giảm dung lượng bộ nhớ tiêu thụ khi chạy dữ liệu siêu khổng lồ.
- **4.5. Nhận diện hành vi bất thường (Anomaly Detection):** Viết mô hình ứng dụng HMP để phát hiện các giao dịch gian lận tài chính hoặc tấn công mạng dựa trên việc đo lường độ dài mã hóa bất thường.

---



| Vai trò  | Nhiệm vụ chính |
| :---  | :--- |
| **Nhật** <br>*(Data)*  | - Lập trình Phần 1 (Parser, Integer Encoding, Weight & Size calculation).<br>- Quản lý lưu trữ datasets thô lấy từ UCI, SPMF. |
| **Huy** <br>*(Algorithm )*  | - Lập trình Phần 2  |
| **Hợp tác chung** <br>*(R&D & Writing)*  | - Phát triển Phần 3.2 (Ứng dụng phân loại, kiểm thử chéo 10-fold).<br>- Thực hiện các thử nghiệm cải tiến ở Phần 4 để chuẩn bị viết paper mới. |
