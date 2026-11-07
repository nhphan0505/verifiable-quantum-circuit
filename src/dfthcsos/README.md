# dfthcsos

Mục tiêu: giảm **lambda_eff × T_total × Q_total**, với các điều kiện của verifier gốc.

## Bài làm hiện tại

- `DFT-BASELINE/solution.py`: bản sao thuật toán ban tổ chức, chưa tối ưu.
- Nguồn: `verifiers/dfthcsos/example_submission/angle_k_reference_circuit.py`.
- **Best đã kiểm tra đầy đủ của nhóm: chưa có.**
- [Mục lục và tiêu đề Issue](EXPERIMENTS.md).
- [Bảng điểm](SCORES.md).

## Solution baseline

Chia bảng góc thành batch J word; tính XOR delta giữa batch hiện tại và trước; dựng QROM bằng cây unary iteration và uncompute ancilla bằng đo; xuất một mạch ANGLE_k cho mỗi batch.

Mỗi ANGLE_k tối đa 128 qubit; giữ selection, workspace sạch, không pha dư; tải đúng góc ở cả lượt thuận và ngược. Phải chấm lại sai số Hamiltonian và toàn bộ chi phí mô hình.

## Chạy

Dùng `.venv` và pip kickmix trên Windows để dựng mạch; upload submission lên notebook Colab để chấm.
Xem [lệnh dựng baseline và hướng dẫn chấm](../../docs/COLAB_GRADING.md).
Mạch đã dựng nằm trong `artifacts/dfthcsos/DFT-BASELINE/`. Lưu JSON chấm vào `results/dfthcsos/`.
SCORES.md ghi cả FULL / PASS và DEV_5MIN / PASS; chỉ so điểm trong cùng chế độ và cấu hình.

## Bắt đầu hướng mới

Nhận Issue trước khi code. Tạo `<ID>/solution.py`, `<ID>/DESCRIPTION.md` và `<ID>/configs/<config>.json` theo mẫu trong `templates/`.
Thêm ID/title/link mô tả vào EXPERIMENTS.md. Artifact có cùng stem config; một hướng có nhiều config, không sao chép code cho mỗi setting.
