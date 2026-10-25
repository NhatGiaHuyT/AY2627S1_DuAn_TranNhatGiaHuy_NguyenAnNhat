# Báo cáo nghiên cứu HMP-GSA

## 1. Câu hỏi nghiên cứu

Liệu một bộ nhớ nhỏ gọn được học từ kinh nghiệm tìm kiếm có cải thiện tìm kiếm đặc trưng ngẫu nhiên giống MDL vượt qua một dataset được quét một bước qua các đôi nhãn cùng nhau xuất hiện trên một hay không?

So sánh:

```text
Simulated Annealing không có quét
Simulated Annealing + có quét bộ dữ liệu
Simulated Annealing + có quét + tính trọng số đặc trưng nén 
SA + prior + bộ nhớ Good-Solution Frequency
SA + prior + bộ nhớ Mutation + Feature
```

So sánh khoa học quan trọng do đó không chỉ là so với `unguided`. Mà là liệu bộ nhớ online có cải thiện so với `prior_only` hay không.

## 2. Dữ liệu và cài đặt

Runner hiện tại dùng các dataset giao dịch thật được cấu hình trong JSON. Config dataset mở rộng đang hoạt động là [real_data_500.json](../hmp_gsa/configs/real_data_500.json).

Dataset hiện tại:

- `datasets/crawling/requirements.txt`: requirements thu thập từ 2,436 repository.
- `datasets/crawling/themealdb.txt`: nguyên liệu thu thập từ 790 món ăn.

Runner hỗ trợ bất kỳ số lượng tệp giao dịch phân tách bằng khoảng trắng bổ sung nào bằng cách thêm mục vào mảng `datasets`.

Cài đặt landscape synthetic vẫn nằm trong `hmp_gsa/experiments/landscapes.py` để dùng hồi quy/tham chiếu đơn lập, nhưng runner dữ liệu thật không thực thi nó.

## 3. Thiết kế tìm kiếm

Tất cả điều kiện chia sẻ:

- cùng dataset;
- cùng trạng thái ban đầu;
- cùng evaluator giống MDL;
- cùng candidate pool size;
- cùng lịch trình nhiệt độ;
- cùng seed;
- cùng ngân sách đánh giá; và
- cùng quy tắc chấp nhận simulated annealing.

Dataset adapter hiện hỗ trợ các operation có cấu hình:

```text
add(pattern)
remove(pattern)
replace(old_pattern, new_pattern)
```

Điều này quan trọng vì Variant C học `(operation, feature)`. Trong thiết kế trước đó chỉ có add, C không thể phân biệt thêm với bớt và do đó không phải là kiểm định hợp lệ cho giả thuyết.

## 4. Các variant bộ nhớ

### Unguided

Bộ nhớ move đồng đều. Đo lường tìm kiếm không có hướng dẫn dataset.

### Prior-only

Dùng hỗ trợ item/cặp từ dataset làm prior pattern tĩnh. Nó không học online.

### Successful Feature, A

Củng cố feature liên quan đến một move cải thiện được chấp nhận.

### Good-Solution Frequency, B

Củng cố các feature xuất hiện trong các trạng thái code-table elite.

### Mutation + Feature, C

Củng cố tổ hợp operation-feature chính xác, chẳng hạn:

```text
(add, pattern)
(remove, pattern)
(replace, pattern)
```

## 5. Phát hiện pilot đã kiểm chứng

Run 1,000 iteration hoàn thành trước khi bật lân cận remove/replace mới tạo ra:

| Dataset | Unguided | Prior-only | A/B/C |
|---|---:|---:|---:|
| `requirements` | 593,936.0 | 574,620.4 | 568,447.0 |
| `themealdb` | 119,686.3 | 109,179.3 | 108,814.1 |

Diễn giải:

1. Prior dataset thật rõ ràng cải thiện tìm kiếm so với `unguided`.
2. Hướng dẫn online mang lại cải thiện thêm so với `prior_only` ở điểm tổng hợp.
3. A, B và C đi theo các vết move giống hệt trong run đó.
4. Do đó cải thiện tổng hợp chưa thể quy cho khác biệt giữa A, B và C.
5. Giải thích khả dĩ nhất là lân cận chỉ-add cộng với prior tĩnh mạnh.

Đây là một phát hiện hợp lệ về thiết kế trước đó, không phải bằng chứng rằng ba giả thuyết tương đương một cách tổng quát.

## 6. Thiết kế lại đã cài đặt

Config mở rộng hiện bật:

```json
"move_operations": ["add", "remove", "replace"]
```

Adapter tính lại residual mask từ code table đã đột biến, nên việc xóa hoặc thay thế một pattern không để lại trạng thái residual lỗi thời.

Hành vi operation mới được kiểm thử hồi quy. Kiểm định tập trung hiện tại:

```text
Ran 22 tests ... OK
```

## 7. Thí nghiệm tiếp theo phải đo gì

Với mỗi dataset, variant và seed, báo cáo:

- điểm giống MDL tốt nhất;
- điểm ở 10%, 25%, 50%, 75% và 100% ngân sách;
- số đánh giá để đạt mục tiêu cố định;
- tỷ lệ chấp nhận;
- runtime;
- kích thước bộ nhớ đã học;
- số và loại move add/remove/replace; và
- độ đa dạng code table đã khám phá.

So sánh quyết định là:

```text
prior_only vs Successful Feature
prior_only vs Good-Solution Frequency
prior_only vs Mutation + Feature
```

## 8. Khẳng định và giới hạn

Có thể khẳng định bây giờ:

- dataset thật được runner có cấu hình sử dụng;
- prior hỗ trợ cấp pattern ảnh hưởng đến tìm kiếm;
- prior cải thiện pilot đã hoàn thành so với tìm kiếm đồng đều;
- engine có các variant bộ nhớ online riêng biệt;
- lân cận có hỗ trợ operation đã được cài đặt và kiểm thử.

Chưa thể khẳng định:

- A, B hay C là chiến lược bộ nhớ tốt nhất;
- HMP-GSA thắng HMP-SA đúng paper;
- evaluator Python tái tạo chính xác chi phí code-table MDL của paper;
- run mở rộng có hỗ trợ operation mới cải thiện hội tụ cho đến khi kết quả đầy đủ của nó được tạo.

Objective Python hiện tại vẫn giống MDL. Khẳng định HMP cuối cùng đòi hỏi khớp trạng thái code-table Java, mã hóa residual, mã hóa usage và giao thức đánh giá.

## 9. Khả năng tái tạo

Chạy thí nghiệm mở rộng bằng:

```powershell
python -m hmp_gsa.experiments.run --config hmp_gsa/configs/real_data_500.json
```

Tiến trình được in trước và sau mỗi run dataset/variant/seed. Mỗi run hoàn thành ghi:

- `runs.csv`: vết cấp iteration;
- `run_metrics.csv`: một hàng mỗi run;
- `summary.csv`: kết quả tổng hợp; và
- `config.json`: cấu hình chính xác đã dùng.
