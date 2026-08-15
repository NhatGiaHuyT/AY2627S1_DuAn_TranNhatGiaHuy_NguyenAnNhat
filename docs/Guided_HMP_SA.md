(MDL-GSA)

Tổng quan ý tưởng:
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

chúng ta sẽ nói sơ về tiền bối HMP-SA ban đầu để hiểu được hướng đi và câu hỏi nghiên cứu của MDL-GSA, luồng tổng quan:
CSDL -> làm sạch code table XYZ -> lập tập candidate -> đánh giá tập nén -> giữ/bỏ -> SẼ có candidate cho C -> lặp tiếp

nó sẽ ngẫu nhiên generate ra các tập candidate rồi chỉnh nó bằng cách lấy Neighbor, cơ chế lấy như sau: neighbor khác bởi MỘT yếu tố trong tập, HMP-SA sẽ chọn ngẫu nhiên có xác suất phụ thuộc vào weight yếu tố nén, với cỡ đặc trưng min < cỡ < max, đây là một local neighborhood, để thoát local thì con đường stochastic sẽ là điểm nóng và tại sao chúng ta ưu tiên HMP-SA thay vì HMP-HC.

Vậy thì ta có giả thuyết và giải thuật tiền bối, giả thuyết thì phải vững chắc và có cơ sở để thay đổi trước, và điểm đầu có ý nghĩa là ta sẽ soi mói điểm mạnh VÀ điểm yếu của HMP-SA:
ĐIỂM MẠNH:
SA CÓ THỂ tiết kiệm chi phí bộ nhớ rất hiệu quả(đánh giá xong vứt, không cần search hết)

ĐIỂM YẾU(giả thuyết):
Cách tìm không thể NHỚ được các vùng giải pháp tốt của nó như thế nào, thuật toán không thể nhớ là một điểm yếu thực của các thuật toán trong khoa học máy tính

Các thực nghiệm của HMP-SA có tiến triển bất cân xứng; có thể qua nhiều iteration mà không có tiến triển nhưng rồi vọt lên khi tìm được một đặc trưng tốt, bài báo cho rằng sự ngẫu nhiên trong cách search và vẫn bị giữ lại ở local tạm thời, đây chính là điểm yếu chúng ta muốn phong tỏa.

Giờ chúng ta sẽ sang giải thuật ta đưa ra đề xuất, HMP-GSA, trước tiên, ta hãy đặt một câu hỏi để định hướng: Làm cách nào để quá trình SEARCH học ra được từ các sưu tập giải pháp tốt nó đã phát hiện ra?
Giải pháp tốt -> trích xuất đặc trưng -> học được sự phân bổ -> dẫn dắt hướng đi tương lai

Đơn giản hóa: một giải pháp tốt không phải là giải pháp tổng, nó chính là sự chứng mình được của cấu trúc của các vùng có triển vọng.

VD: A + B, A + C, A + B + C

Ta có thể đề ra cấu trúc mối quan hệ giữa A, B, C là thực dụng

Thuật toán GSA thực chất lấy cảm hứng từ lí thuyết Mean-Field, ta không cần biết chi tiết, ngắn gọn, chúng ta có ORDER PARAMETER, là một biến nắm được một đặc điểm cấu trúc quan trọng của hệ thống. GSA dùng thông tin từ cấu hình tốt (hoặc gọi low energy trong ý của Simmulated Annealing) để xây dựng một đại diện của các cấu hình tốt sẽ nhìn như thế nào.

Chính đại diện đó ảnh hưởng tới khai phá trong tương lai, các bước mới: cấu hình tốt -> cấu trúc theo xác suất -> đại diện(ORDER PARAM) -> Guiding Function -> Bias Search -> chọn 1 candidate -> đánh giá

Trong chi phí bộ nhớ, ta sẽ đơn giản hóa hơn nữa bằng cách không giữ tất cả lịch sử khai phá, ta sẽ giữ một đại diện được nén được học, còn lại thông tin không quan trọng, ta vứt, nhưng vẫn NHỚ được thông tin hữu ích

Tất nhiên ta sẽ vẫn xài nhiều ý tưởng của tiền bối HMP-SA về cách tìm bức tranh tổng thể, các giải pháp tốt sẽ được thiên vị nhưng vẫn là xác suất, có thể cho model đi dạo.

Ta sẽ chọn "cấu trúc" nào để học?
Đây là câu hỏi quan trọng nhất trong MDL-GSA hiện tại, ta có thể nhìn vào itemsets với các solution khác nhau:
Cách 1: Nhìn vào itemset - Những itemset nào thường xuất hiện trong các solution có MDL thấp?
Cách 2: Nhìn vào từng item - Những item nào thường tham gia vào solution tốt?
Cách 3: Nhìn vào quan hệ giữa các item - Có những cặp hoặc nhóm item nào thường xuất hiện cùng nhau?

Một cách tiếp cận đơn giản đầu tiên: Feature Weight Vector, Thay vì lưu solution 1-n, ta chỉ lưu một vector trọng số, đây chính là compressed memory của search, nhưng trọng số không phải tự nhiên xuất hiện, ta hiện có ít nhất ba giả thuyết độc lập:
A - Successful Feature: Nếu một feature tham gia vào một mutation làm giảm MDL, feature đó nhận được reinforcement.
B - Good-Solution Frequency: Một hướng khác không quan tâm trực tiếp feature đã tạo ra bao nhiêu improvement.
C - Mutation + Feature: "Hành động nào trên feature nào thường tốt?"



Hệ thống các bước 1 pass:
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
W_{t+1}(I)
=
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

> Feature hữu ích liên tục sẽ giữ weight cao; thông tin cũ hoặc chỉ tình cờ hữu ích sẽ dần mất ảnh hưởng.
