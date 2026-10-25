# Kiến trúc HMP-GSA và quy trình thí nghiệm

## 1) Ý tưởng tổng quan

Repository này tách biệt engine tối ưu hóa khỏi phần định nghĩa bài toán:

- `HMPGSA` quản lý vòng lặp simulated annealing, nhiệt độ, lấy mẫu candidate và cập nhật bộ nhớ.
- `GSAAdapter` định nghĩa interface bài toán cụ thể.
- Một variant (`unguided`, `prior_only`, `successful_feature`, `good_solution_frequency`, `mutation_feature`) quyết định engine nhớ những gì.

Điều này giữ cho thuật toán tìm kiếm không đổi, chỉ thay đổi cơ chế hướng dẫn.

## 2) Các thành phần chính

### Search engine
- `hmp_gsa/modules/engine.py`
- `HMPGSA` sở hữu:
  - trạng thái hiện tại
  - lịch trình nhiệt độ
  - lấy mẫu candidate pool
  - xác suất chấp nhận
  - trọng số học
  - decay

### Adapter contract
- `hmp_gsa/modules/adapter.py`
- `GSAAdapter` yêu cầu:
  - `initial_state()`
  - `initial_prior()`
  - `sample_moves(...)`
  - `apply_move(...)`
  - `evaluate(...)`
  - `features_of(...)`

Adapter là ranh giới giữa engine guided-SA tổng quát và bài toán tối ưu hóa thực tế.

### Tham chiếu synthetic được bảo lưu
- `hmp_gsa/experiments/landscapes.py`
- Cài đặt này chỉ được giữ lại để kiểm thử hồi quy/tham chiếu đơn lập.
- Experiment runner không import hay thực thi nó.

### Pipeline prior cho dataset thật
- `hmp_gsa/scripts/prior_scan.py`
- Scanner đọc dữ liệu giao dịch, bỏ qua các dòng trống, đếm số giao dịch, tần suất item và đồng xuất hiện từng cặp.
- Nó ghi các đầu ra tất định vào:
  - `hmp_gsa/derived/<dataset>/statistics.json`
  - `hmp_gsa/derived/<dataset>/item_frequency.csv`
  - `hmp_gsa/derived/<dataset>/cooccurrence.csv`

### Hàm mục tiêu giống MDL
- `hmp_gsa/modules/mdl.py`
- Đây không phải một mục tiêu nghiên cứu bịa ra; nó tuân theo logic nén pattern code-table của chương trình Java HMP-SA:
  - residual database sau khi bỏ các pattern lặp lại
  - chi phí overhead bảng mã cho các pattern đã chọn
  - tổng chi phí thấp hơn = nén tốt hơn

## 3) Phân biệt prior

Repository tách biệt rõ ràng:

1. Initial memory prior
   - `initial_prior()`
   - một bản đồ trọng số feature tĩnh dùng để khởi tạo bộ nhớ

2. Dynamic data prior
   - `prior_weight(state, move, prior)`
   - tín hiệu dataset tương lai dự kiến dựa trên đồng xuất hiện / cấu trúc giao dịch

Điểm candidate cuối cùng về bản chất là:

`memory_weight * dynamic_prior_weight`

Điều này bảo toàn sự phân biệt dự kiến giữa bộ nhớ tìm kiếm đã học và thông tin prior có nguồn gốc từ dataset.

## 4) Cách chạy thí nghiệm

### Chạy thí nghiệm trên dataset thật
Lệnh:

```powershell
cd d:/hmp_gsa_prototype/AY2627S1_DuAn_TranNhatGiaHuy_NguyenAnNhat
python -m unittest hmp_gsa.tests.test_gsa hmp_gsa.tests.test_variants -v
```

hoặc qua config:

```powershell
cd d:/hmp_gsa_prototype/AY2627S1_DuAn_TranNhatGiaHuy_NguyenAnNhat
python -m hmp_gsa.experiments.run --config hmp_gsa/configs/baseline.json
```

Experiment runner ghi:

- `results/<timestamp>/config.json`
- `results/<timestamp>/runs.csv`
- `results/<timestamp>/summary.csv`

### Chạy quét dataset
```powershell
cd d:/hmp_gsa_prototype/AY2627S1_DuAn_TranNhatGiaHuy_NguyenAnNhat
python hmp_gsa/scripts/main.py
```

Lệnh này ghi thống kê dataset đã lưu và prior đồng xuất hiện từng cặp vào thư mục `hmp_gsa/derived`.

## 5) Cách đọc kết quả

### Cho thí nghiệm trên dataset thật
Xem:

- `best_score` qua các run
- phương sai qua các seed
- tỷ lệ chấp nhận theo thời gian
- trọng số đã học theo feature / cặp feature-op

Diễn giải:

- `unguided`: hành vi SA cơ sở
- `prior_only`: chỉ prior tĩnh, không học online
- `successful_feature`: trọng số cho các feature tạo ra các move được chấp nhận và cải thiện
- `good_solution_frequency`: trọng số cho các feature xuất hiện trong các solution mạnh
- `mutation_feature`: phân biệt các cặp feature + operation

### Cho thí nghiệm dựa trên dataset
Diễn giải nên tập trung vào:

- liệu hàm mục tiêu giống MDL có giảm khi thêm pattern hay không
- liệu prior đã học có tạo ra các move candidate hữu ích hơn không
- liệu prior đồng xuất hiện từ dataset có bias tìm kiếm về các lân cận pattern mạnh không

Tóm lại, metric chính là mức giảm objective dưới ngân sách đánh giá cố định, chứ không phải đơn thuần độ lớn trọng số.

## 6) Trạng thái hiện tại

Repo hiện hỗ trợ sạch sẽ bốn tầng:

1. quét dataset + persistence
2. runner đa dataset có cấu hình
3. engine GSA tổng quát + các variant hướng dẫn
4. hàm mục tiêu nén giống MDL nhất quán với runner Java HMP-SA

Biểu diễn trạng thái MDL đầy đủ đúng paper vẫn là ranh giới nghiên cứu tiếp theo nếu muốn tái tạo mọi chi tiết chính xác của công thức MDL trong bài báo.
