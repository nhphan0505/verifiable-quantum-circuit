# [DQI-BASELINE] Giải mã Reed–Solomon bằng EEA đồng bộ kết hợp Chien search và Forney

Loại: kế thừa baseline ban tổ chức; không thay đổi thuật toán gốc. Các file nguồn được liên kết ở cuối mô tả.

Bài toán dùng mã Reed–Solomon trên `GF(2^12)`, có 4.095 vị trí và 70 syndrome, tương ứng tối đa 35 lỗi ký hiệu. Mạch nhận các syndrome lượng tử S và các thanh ghi cổ điển M chứa kết quả đo MBUC. Nó phải áp pha `(-1)^(Σⱼ popcount(eⱼ & Mⱼ))`, trong đó e là vector lỗi được giải mã từ S, rồi khôi phục toàn bộ syndrome và đưa qubit phụ về 0. Vector lỗi không được cung cấp trực tiếp cho mạch.

Ý tưởng baseline là tính các đa thức cần cho giải mã, dùng chúng để áp pha theo từng vị trí, rồi đảo quá trình tính đa thức. Cách này không cần giữ toàn bộ vector lỗi như một đầu ra lượng tử thường trực.

Giai đoạn đầu dùng thuật toán Euclid mở rộng đồng bộ (EEA) để tính đa thức định vị lỗi σ và đa thức đánh giá lỗi ω. Hai mảng thanh ghi lưu trạng thái đa thức; các thanh ghi con trỏ lưu bậc, vị trí hoạt động, thương và thông tin dừng. Unary iteration điều khiển việc truy cập, dịch và cập nhật phần mảng đang hoạt động. Baseline phát ra `3·(70+1)+9 = 222` bước EEA; bộ đếm dừng quản lý trạng thái thuật toán để có thể đảo lại quá trình sau đó.

Các phép cộng trong GF(2^12) là XOR. Bình phương và nhân với hằng số trường được biểu diễn bằng mạng tuyến tính CNOT. Nhân hai giá trị lượng tử dùng phép nhân trường; phép nghịch đảo dùng chuỗi Itoh–Tsujii cùng các thanh ghi scaffold. Những tích tạm phù hợp được xóa bằng measurement-based uncomputation, có sửa pha, để giảm chi phí uncompute.

Giai đoạn tiếp theo thực hiện Chien search trên các vị trí của codeword: cập nhật và đánh giá σ, đạo hàm σ′ và ω tại các điểm trường tương ứng. Điều kiện `σ=0` xác định vị trí lỗi; công thức Forney cung cấp giá trị lỗi thông qua ω và nghịch đảo σ′. Mạch kết hợp giá trị này với M của vị trí đang xét để áp pha MBUC. Các hệ số trường cố định được gộp vào bước cập nhật để tận dụng phép nhân hằng tuyến tính.

Sau khi áp pha, mạch xóa dữ liệu tạm của bước tìm lỗi và chạy đảo EEA. Kết quả cuối chỉ giữ pha mong muốn trên syndrome ban đầu. Tính đúng phải bao gồm pha và workspace sạch, không chỉ giá trị giải mã cổ điển.

Những thành phần cần cân nhắc khi phát triển từ baseline là số bước EEA, cách lưu hai mảng đa thức, con trỏ và các khối nhân/nghịch đảo trường. Điểm phụ thuộc `R(ε₊)·Q²·T`, nên giảm qubit có thể đáng giá ngay cả khi phải tính lại một phần. Ngược lại, giảm số vòng lặp có thể tăng lỗi giải mã và hệ số phạt R; không thể chỉ nhìn số cổng để kết luận phương án tốt hơn.

Mã triển khai: [baseline.py](solution.py). Nguồn: [dqi_reference_circuit.py](../../../verifiers/dqi/dqi_reference_circuit.py). Điểm full và dev_5min được lưu tại [SCORES.md](../SCORES.md).

Phiên bản nguồn gốc được đối chiếu bằng SHA-256 trong [data_manifest.json](../../../data_manifest.json); chưa có Git commit/Issue để gắn permalink.

Cấu hình dựng baseline: [configs/baseline.json](configs/baseline.json). CLI mới đọc JSON và tự đặt tên artifact theo tên config; thuật toán tạo mạch được giữ nguyên.

## Kết luận và mốc đối chiếu local

Run dev_5min mới xác nhận lại baseline trên 4.096 shots với seed 20261106:
không phát hiện lỗi giá trị/pha, kết quả trùng mốc dev trước. Đây là bằng chứng
trên profile dev. Dùng run mới làm mốc đối chiếu cho ứng viên
cùng môi trường và hash verifier/harness; score nằm trong SCORES.md.

Config tham chiếu: [baseline.json](configs/baseline.json).
Run: [verifier.json](../../../results/dqi/DQI-BASELINE/baseline/dev_5min/20261107T092603Z-local-dev_5min-f901a5/verifier.json).
Nguồn gốc: [provenance.json](../../../results/dqi/DQI-BASELINE/baseline/dev_5min/20261107T092603Z-local-dev_5min-f901a5/provenance.json).
Artifact được dựng trước Git; chỉ xác định được hash nguồn lịch sử và hash artifact
qua biên bản build, không có SHA commit nguồn. Không coi HEAD hiện tại là phiên bản
tạo artifact này. Source/config hiện tại dùng để tham khảo/tái dựng, không thay thế
bằng chứng lịch sử.

Run [full local](../../../results/dqi/DQI-BASELINE/baseline/full/20261107T094931Z-local-full-5ed1c6/verifier.json)
đã PASS với 102.400 shots, không phát hiện lỗi giá trị hoặc pha, dùng tham số
mặc định chính thức của verifier DQI. Đây là mốc full để so với ứng viên cùng
môi trường và phiên bản verifier; chưa phải điểm nộp trên hệ thống cuộc thi.
Không so trực tiếp score full với dev vì hệ số phạt phụ thuộc số mẫu.

Hash artifact của full khớp run dev và biên bản build baseline trước Git;
[provenance full](../../../results/dqi/DQI-BASELINE/baseline/full/20261107T094931Z-local-full-5ed1c6/provenance.json)
giữ hash nguồn lịch sử, không gán SHA commit hiện tại cho artifact cũ.
Config hiện tại chỉ là tham chiếu như đã nêu trên. Kết quả full/dev và hệ số
baseline `1.00×` được ghi riêng trong SCORES.md.
