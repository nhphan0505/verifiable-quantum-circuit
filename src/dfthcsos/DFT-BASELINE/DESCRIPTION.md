# [DFT-BASELINE] Tải góc Givens theo batch 8 word bằng QROM và XOR delta

Loại: kế thừa baseline ban tổ chức; không thay đổi thuật toán gốc. Các file nguồn được liên kết ở cuối mô tả.

Mục tiêu của phần mạch này là tải các word góc dùng cho phép quay Givens trong block encoding DFTHC SOS. Baseline dùng factorization có sẵn của ban tổ chức, không tối ưu lại các factor hay rank. Với N=76 orbital, mỗi vector được biểu diễn bằng 75 góc. Bảng baseline có `76 + R·B = 3.976` địa chỉ, với R=65 và B=60: 76 hàng đầu dành cho thành phần một hạt, các hàng còn lại dành cho các vector hai hạt.

Baseline dùng cây Givens trong submission mẫu và word góc 12 bit. Một word w biểu diễn góc `θ = π·w/2^(12−1)`. Mỗi batch gồm J=8 góc; vì có 75 góc nên cần `ceil(75/8)=10` mạch ANGLE_k. Các vị trí dư của batch cuối được đệm bằng 0. Mỗi mạch dùng chung thanh ghi địa chỉ selection và tám thanh ghi word.

Điểm chính của cách tải là không xóa batch cũ rồi tính batch mới từ 0. Gọi batch k của địa chỉ a là B[k,a], bảng mà mạch tải là `delta[0,a]=B[0,a]` và `delta[k,a]=B[k,a] XOR B[k−1,a]` khi k>0. Mỗi ANGLE_k thực hiện oracle XOR `|a>|z> → |a>|z XOR delta[k,a]>`. Vì vậy khi z đang chứa batch trước, một lần gọi mạch biến nó trực tiếp thành batch hiện tại.

Mỗi bảng delta được triển khai bằng QROM thông thường. Unary iteration theo cây phân đoạn tạo các điều kiện khớp địa chỉ; các bit 1 của dữ liệu cổ điển điều khiển việc XOR vào thanh ghi word bằng CNOT. Những nhánh đủ điều kiện có dữ liệu đồng nhất có thể kết thúc sớm. Các ancilla điều khiển được uncompute bằng đo và sửa pha; địa chỉ phải được giữ nguyên và workspace phải sạch sau mỗi mạch.

Họ mạch chạy theo thứ tự thuận để đưa từng batch góc tới phần phép quay, rồi theo thứ tự ngược để xóa các word. Mỗi oracle XOR tự nghịch đảo, nhưng vẫn phải kiểm tra cả hai chiều để xác nhận thứ tự batch, phần đệm và việc dọn dữ liệu. Baseline chỉ tải góc; các thành phần state preparation và Givens còn lại được verifier tính chi phí theo mô hình quy định.

Giá trị vector được chấm được giải mã từ các góc mà mạch thực sự tải lên cây Givens. Chỉ thay U trong NPZ mà giữ nguyên mạch không thay đổi vector được verifier khôi phục. Các trọng số factorization kết hợp với vector này quyết định sai số tái dựng, normalization và hệ số λ_eff. Vì vậy tối ưu lượng tử hóa góc hay factorization phải kiểm tra lại các chỉ số Hamiltonian, không chỉ chi phí QROM.

Các đánh đổi chính là J, số bit góc và cấu trúc bảng tra. J lớn giảm số batch nhưng tăng số qubit word; độ chính xác góc thấp giảm tài nguyên nhưng có thể làm sai số vượt ngưỡng. Mỗi ANGLE_k bị giới hạn 128 qubit; tổng qubit dùng tính điểm còn bao gồm tài nguyên được mô hình hóa ở các phần khác. Mục tiêu cuối là giảm `λ_eff·T_total·Q_total` trong khi vẫn qua toàn bộ điều kiện chấp nhận.

Mã triển khai: [baseline.py](solution.py). Nguồn: [angle_k_reference_circuit.py](../../../verifiers/dfthcsos/example_submission/angle_k_reference_circuit.py). Điểm full và dev_5min được lưu tại [SCORES.md](../SCORES.md).

Phiên bản nguồn gốc được đối chiếu bằng SHA-256 trong [data_manifest.json](../../../data_manifest.json); chưa có Git commit/Issue để gắn permalink.

Cấu hình dựng baseline: [configs/baseline.json](configs/baseline.json). CLI mới đọc JSON và tự đặt tên artifact theo tên config; thuật toán tạo mạch được giữ nguyên.
