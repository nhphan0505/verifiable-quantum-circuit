# [INV-BASELINE] Tính pha 1/√x bằng đa thức bậc ba và một bước Newton–Raphson

Loại: kế thừa baseline ban tổ chức; không thay đổi thuật toán gốc. Các file nguồn được liên kết ở cuối mô tả.

Mục tiêu của mạch là thực hiện phép biến đổi `|x>|0> → exp(2πi/√x)|x>|0>` với x nguyên từ 1 đến 3.133.452. Thanh ghi x có 22 qubit; phép tính phải giữ nguyên x và đưa mọi qubit phụ về 0. Đây là cách triển khai tham khảo của ban tổ chức, dùng làm mốc để so sánh các phương án tối ưu.

Mạch đầu tiên đếm các cặp bit 0 ở đầu x và dịch trái theo bội số của hai bit. Gọi số lần dịch cặp là s, giá trị chuẩn hóa là `M = x·2^(2s)/2^20`, thuộc `[1,4)`. Khi đó `1/√x = 2^(s−10)/√M`. Chuẩn hóa giúp phần tính đa thức và Newton dùng độ rộng cố định thay vì phải xử lý trực tiếp mọi độ lớn của x.

Để tạo ước lượng đầu y₀ cho `1/√M`, mạch chia miền chuẩn hóa thành bốn khoảng `[1,1.5)`, `[1.5,2)`, `[2,3)` và `[3,4)`. Hai bộ đa thức bậc ba cho hai khoảng đầu được tái sử dụng với hệ số điều chỉnh để phủ hai khoảng sau. Các bit cao của M chọn hệ số; mạch đánh giá đa thức bằng Horner trên độ lệch so với đầu khoảng. Hệ số có dấu luân phiên nên phép tính được tổ chức thành các phép nhân và trừ liên tiếp.

Sau đó mạch thực hiện một bước Newton–Raphson theo công thức `y₁ = y₀(3 − M·y₀²)/2`. Các đại lượng trong mạch được biểu diễn bằng số nguyên fixed-point, nên hệ số 1/2 và hệ số chuẩn hóa được thể hiện qua vị trí dấu phẩy và phép dịch. Đầu ra được dịch theo s để trở về giá trị tương ứng với x ban đầu. Mỗi bit đầu ra điều khiển một cổng Z_POW; tổng pha của các bit biểu diễn giá trị xấp xỉ `1/√x`.

Cấu hình mặc định dùng 14 bit cho độ lệch trong Horner, 17 bit cho hệ số và trung gian Horner, 28 bit cho bình phương và tích hiệu chỉnh, 29 bit cho kết quả Newton. Phép nhân bỏ các tích riêng nằm dưới bit thấp nhất được giữ lại. Vì việc cắt từng tích riêng khác với chỉ làm tròn tích cuối, mô hình `fixed_point_model()` mô phỏng chính xác quy tắc cắt cụt của mạch. `relative_error()` dùng mô hình này để khảo sát sai số số học.

Cuối cùng mạch đảo các bước tính toán, khôi phục x và xóa workspace. Các temporary AND phù hợp được uncompute bằng đo X và sửa pha có điều kiện. Không thể bỏ bước sửa pha chỉ vì các bit đầu ra trông đúng trên dữ liệu cổ điển.

Hướng này đánh đổi độ rộng thanh ghi và số tích riêng với sai số. Khi cải tiến cần tính cả chi phí compute/uncompute, số qubit cực đại và chi phí tổng hợp phép quay. Giảm bit quá nhiều có thể làm sai số vượt ngưỡng hoặc làm phần dung sai còn lại cho tổng hợp phép quay quá nhỏ, khiến tổng điểm tăng.

Mã triển khai: [baseline.py](solution.py). Nguồn: [nr_reference_circuit.py](../../../verifiers/invsqrt/nr_reference_circuit.py). Điểm full và dev_5min được lưu tại [SCORES.md](../SCORES.md).

Phiên bản nguồn gốc được đối chiếu bằng SHA-256 trong [data_manifest.json](../../../data_manifest.json); chưa có Git commit/Issue để gắn permalink.

Cấu hình dựng baseline: [configs/baseline.json](configs/baseline.json). CLI mới đọc JSON và tự đặt tên artifact theo tên config; thuật toán tạo mạch được giữ nguyên.


## Kết luận và mốc đối chiếu local

Run dev_5min mới xác nhận lại baseline trên 4.096 mẫu (8.192 shots) với seed 20261106:
không phát hiện lỗi giá trị/pha, kết quả trùng mốc dev trước (score 2076443.1049173493).
Đây là bằng chứng trên profile dev, chưa xác nhận full. Dùng run mới làm mốc đối chiếu
cho ứng viên cùng môi trường và hash verifier/harness; score nằm trong SCORES.md.

Config tham chiếu: [baseline.json](configs/baseline.json).
Run: [verifier.json](../../../results/invsqrt/INV-BASELINE/baseline/dev_5min/20261107T180810Z-local-dev_5min-eb9c85/verifier.json).
Nguồn gốc: [provenance.json](../../../results/invsqrt/INV-BASELINE/baseline/dev_5min/20261107T180810Z-local-dev_5min-eb9c85/provenance.json).
Artifact được dựng trước Git; chỉ xác định được hash nguồn lịch sử và hash artifact
qua biên bản build, không có SHA commit nguồn. Không coi HEAD hiện tại là phiên bản
tạo artifact này. Source/config hiện tại dùng để tham khảo/tái dựng, không thay thế
bằng chứng lịch sử.
