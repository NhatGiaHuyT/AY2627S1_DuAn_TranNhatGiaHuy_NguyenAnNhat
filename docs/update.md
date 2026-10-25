# Cập nhật: max_pattern_size = 5 đã an toàn cho thí nghiệm MDL

Thầy/cô ạ, dưới đây là phần giải thích đơn giản về thay đổi tôi đã làm và lý do chọn max_pattern_size = 5.

---

## 1. Vấn đề xảy ra

Thầy/cô tăng `max_pattern_size` từ 2 lên 5 trong file `real_data_500.json`. Sau đó chương trình bị treo và tiêu thụ rất nhiều RAM.

**Nguyên nhân:** `DatasetMDLAdapter` trong `hmp_gsa/modules/mdl.py` đã đi qua từng giao dịch và sinh ra **tất cả các bộ patterns có độ dài từ 1 đến 5**. Với file `requirements.txt`, một giao dịch có thể có tới 99 mục. Số lượng bộ patterns có thể sinh ra từ 99 mục là cực kỳ lớn (hàng tỷ bộ). Máy tính đã cố gắng đếm tất cả và hết RAM.

## 2. Tôi đã làm gì

### 2.1 Chỉ đếm chính xác các pattern đơn lẻ và cặp

Bây giờ adapter chỉ lưu support (số lần xuất hiện) chính xác cho các pattern có độ dài 1 và 2. Các pattern dài hơn không được lưu ngay lúc khởi tạo.

### 2.2 Sinh candidate một cách linh hoạt

Thay vì đi qua toàn bộ `_support` mỗi lần tìm kiếm, `sample_moves` sẽ lấy ngẫu nhiên một số giao dịch giới hạn và sinh ra candidate từ chúng. Số lượng candidate được giới hạn ở `max_candidates` (5000). Do đó RAM luôn ở mức thấp.

## 3. max_pattern_size = 5 có đúng không?

### Có, vì lý do sau:

- Dữ liệu thật như `requirements.txt` (trung bình 16 mục, tối đa 99) và `themealdb.txt` (trung bình 10, tối đa 20) rõ ràng có các khái niệm lớn hơn cặp 2 mục.
- Nếu chỉ cho phép pattern tối đa 2, bạn đang tạo ra một **thiên kiến cấu trúc**. Bạn đang vô hiệu hóa khả năng tìm thấy các pattern lớn hơn, dù đó có là kết quả thực tế hay không.
- Thiên kiến này ảnh hưởng như nhau đến tất cả các biến thể (unguided, prior_only, các biến thể có bộ nhớ). Do đó nó làm méo mó kết quả so sánh.

### Tại sao nó vẫn công bằng?

- Ban đầu, **tất cả các biến thể đều nhận được cùng một prior W₀** (được tính từ các item đơn lẻ và cặp xuất hiện nhiều trong dataset).
- Prior này không thay đổi khi tìm kiếm.
- Nếu một biến thể có bộ nhớ online làm tốt hơn, đó là do cơ chế học, không phải do adapter ưu tiên nó.

## 4. So sánh với max_pattern_size = 2

| Khía cạnh | max_pattern_size = 2 | max_pattern_size = 5 (đã sửa) |
|---|---|---|
| RAM khi khởi tạo | Thấp | Thấp |
| RAM khi chạy | Thấp | Thấp |
| Khả năng tìm pattern lớn | Không | Có |
| Thiên kiến cấu trúc | Cao | Thấp |
| Kết quả có ý nghĩa với dữ liệu thật | Không hoàn toàn | Có hơn |

## 5. Kết luận

- `max_pattern_size = 5` là lựa chọn phù hợp cho các dataset giao dịch thật như của bạn.
- Sau khi sửa, chương trình chạy được mà không bị hết RAM.
- `prior_only` vẫn là cơ sở so sánh công bằng.
- Nếu dataset mới có giao dịch rất dài (>200 mục), hãy điều chỉnh `max_pattern_size` tương ứng để tránh tràn RAM.