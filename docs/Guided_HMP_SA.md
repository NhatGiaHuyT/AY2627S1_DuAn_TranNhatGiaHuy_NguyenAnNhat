###Tổng quan ý tưởng:
- sau khi tìm hiểu cách tìm của HMP-SA (là một thuật toán SA bình thường trên nguyên lý MDL), mình hỏi, thay vì cho thuật toán HMP-SA khai phá không gian MDL mà không học từ các solution trước đó (chọn, evaluate và vứt), chúng ta sẽ tìm hiểu cấu trúc của các giải pháp tốt có thể học được và để dẫn dắt/thiên vị để khai phá các lựa chọn có tính ngẫu nhiên có tính toán. (Từ bài báo khác (Guided Simulated Annealing Method for Optimization Problems et. C.I. Chou, R.S. Han, S.P. Li, T.K. Lee)[https://arxiv.org/pdf/cond-mat/0302137])

Một bước cơ bản tổng: Tìm -> Tìm các giải pháp tốt -> học đặc trưng cấu trúc -> lại tìm -> lại học

Trước khi đi sâu hơn, ta nên nhai lại vấn đề HMP đang giải quyết để ta có thể infer được một chút logic trong lập luận:
Chúng ta có một CSDL = {t1, t2, .....}
từng yếu tố có vật phẩm: t1 = {A, B, C, D}; t2 = {A, B, C, E}; t3 = {A, B, D}
chúng ta muốn tìm các tập đặc trưng / tập vật phẩm có thể nén được các thông tin hữu ích có thể tổng quan được cả CSDL như: y = { {A, B}, { B } } ; đây chính là model của chúng ta hoặc là "code table"

đi qua nhanh về MDL: Một model tốt sẽ cho ta lời giải thích tốt về tổng quan CSDL mà không quá phức tạp
-> Total Description Length = Model Cost + Encoded Data Cost

chúng ta muốn chi phí của Total Description Length tối thiểu, có nghĩa là phải cân bằng giữa Model Cost + Encoded Data Cost tối thiểu
nếu không xài MDL thì search space sẽ lên 2^(2^n - 1), một con số vô dụng

chúng ta sẽ nói sơ về tiền bối HMP-SA ban đầu để hiểu được hướng đi và câu hỏi nghiên cứu của GHMP-SA (Guided HMP-SA), luồng tổng quan:
CSDL -> làm sạch code table XYZ -> lập tập candidate -> đánh giá tập nén -> giữ/bỏ -> SẼ có candidate cho C -> lặp tiếp

nó sẽ ngẫu nhiên generate ra các tập candidate rồi chỉnh nó bằng cách lấy Neighbor, cơ chế lấy như sau: neighbor khác bởi MỘT yếu tố trong tập, HMP-SA sẽ chọn ngẫu nhiên có xác suất phụ thuộc vào weight yếu tố nén, với cỡ đặc trưng min < cỡ < max, đây là một local neighborhood, để thoát local thì con đường stochastic sẽ là điểm nóng và tại sao chúng ta ưu tiên HMP-SA thay vì HMP-HC.

Vậy thì ta có giả thuyết và giải thuật tiền bối, giả thuyết thì phải vững chắc và có cơ sở để thay đổi trước, và điểm đầu có ý nghĩa là ta sẽ soi mói điểm mạnh VÀ điểm yếu của HMP-SA:
ĐIỂM MẠNH:
SA CÓ THỂ tiết kiệm chi phí bộ nhớ rất hiệu quả(đánh giá xong vứt, không cần search hết)

ĐIỂM YẾU(giả thuyết):
Cách tìm không thể NHỚ được các vùng giải pháp tốt của nó như thế nào, thuật toán không thể nhớ là một điểm yếu thực của các thuật toán trong khoa học máy tính
