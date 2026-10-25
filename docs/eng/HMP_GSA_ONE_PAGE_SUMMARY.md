# Tóm tắt kết quả nghiên cứu HMP-GSA

## Mục tiêu

HMP-GSA được đề xuất như một mở rộng của HMP-SA. Mục tiêu là giữ nguyên nguyên lý tối ưu hóa MDL và cơ chế Simulated Annealing, đồng thời bổ sung một bộ nhớ nén `Feature Weight Vector` để học từ các bước tìm kiếm có triển vọng. Bộ nhớ này chỉ làm thay đổi xác suất chọn candidate, không thay thế hàm đánh giá MDL và không biến thuật toán thành greedy search.

## Những gì đã triển khai

- Xây dựng Guided-SA engine dùng chung cho toàn bộ các variant.
- Cài đặt hai nhóm đối chứng: `unguided` và `prior_only`.
- Cài đặt ba giả thuyết học:
  - **Variant A - Successful Feature:** tăng trọng số cho feature trong mutation cải thiện objective.
  - **Variant B - Good-Solution Frequency:** tăng trọng số cho feature xuất hiện trong solution tốt.
  - **Variant C - Mutation + Feature:** ghi nhớ cặp `(operation, feature)`, ví dụ `(add, item)` hoặc `(remove, item)`.
- Thêm cơ chế initial prior, multinomial sampling và decay.
- Quét dataset thật `accident.txt`, lưu item frequency và pairwise co-occurrence.
- Xây dựng MDL-like adapter dựa trên residual database và code-table cost, tham chiếu từ chương trình Java HMP-SA.
- Bổ sung test và experiment runner để so sánh các variant với cùng seed, budget, temperature và candidate pool.

## Kết quả pilot trên dữ liệu thật

Runner hiện tại dùng trực tiếp hai dataset crawling, 5 variant, 3 random seed, 30 iteration mỗi run và candidate pool size bằng 5. Synthetic landscapes vẫn được giữ trong source để regression/reference nhưng không còn được runner thực thi. Objective được minimize, nên điểm thấp hơn là tốt hơn.

| Dataset | Unguided | Variant A | Variant B | Variant C |
|---|---:|---:|---:|---:|
| `requirements` | 1,143,091.33 | 1,125,641.00 | 1,125,641.00 | 1,125,641.00 |
| `themealdb` | 233,516.00 | 229,647.33 | 229,647.33 | 229,647.33 |

Sau khi sửa prior theo đúng pattern key, các phương pháp dùng prior đạt điểm tốt hơn `unguided` trên cả hai dataset. Tuy nhiên ba variant online vẫn có cùng điểm với `prior_only` trong pilot 30 iteration. Điều này cho thấy static co-occurrence prior đang có tác dụng, nhưng budget ngắn chưa tạo đủ reinforcement khác biệt giữa A/B/C. Kết quả và metrics chi tiết nằm trong `results/20260915_133339/summary.csv` và `run_metrics.csv`.

## Dữ liệu thật và giới hạn hiện tại

Dataset `accident.txt` đã được quét thành công với:

```text
340,183 transactions
468 distinct items
Average transaction length: 33.8079
Density: 7.2239%
46,815 observed item pairs
```

Chương trình Java HMP-SA cũng đã sinh code table cho `iris.txt`, với một run ghi nhận compression size từ `24,000` bit xuống `3,690` bit và code table gồm `44` pattern.

Pilot hiện tại đã chạy trên dữ liệu thật, nhưng objective vẫn là MDL-like adapter chứ chưa phải code-table state paper-exact. Vì vậy chưa thể tuyên bố HMP-GSA đã thắng HMP-SA trên dữ liệu thật hoặc đã tái tạo đầy đủ MDL theo paper.

## Kết luận và hướng tiếp theo

Prototype đã chứng minh được rằng Guided-SA, ba cơ chế memory và pipeline quét dataset có thể hoạt động độc lập và được kiểm thử. Kết quả ban đầu ủng hộ giả thuyết rằng search experience có thể được nén thành trọng số để bias exploration, nhưng hiệu quả phụ thuộc vào cấu trúc landscape.

Bước tiếp theo là xây dựng candidate generation tương thích với HMP và sparse co-occurrence structure, sau đó chạy so sánh công bằng `HMP-SA`, `prior-only`, `HMP-GSA-A`, `HMP-GSA-B` và `HMP-GSA-C` trên cùng dataset, cùng code-table state, cùng MDL evaluator, cùng evaluation budget và cùng random seeds.
