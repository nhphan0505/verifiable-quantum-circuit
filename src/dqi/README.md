# dqi

Mục tiêu: giảm **R(epsilon_plus) × Q² × T**, với các điều kiện của verifier gốc.

## Bài làm hiện tại

- `DQI-BASELINE/solution.py`: bản sao thuật toán ban tổ chức, chưa tối ưu.
- Nguồn: `verifiers/dqi/dqi_reference_circuit.py`.
- **Best đã kiểm tra đầy đủ của nhóm: chưa có.**
- [Mục lục và tiêu đề Issue](EXPERIMENTS.md).
- [Bảng điểm](SCORES.md).

## Solution baseline

Chạy EEA đồng bộ để tính đa thức định vị và đánh giá lỗi; Chien search và Forney áp pha MBUC; đảo EEA để khôi phục syndrome và xóa workspace.

Khôi phục syndrome, workspace sạch và pha MBUC đúng. Sai số được chấm bằng cận trên thống kê; số shot ảnh hưởng điểm.

## Chạy

Dùng `.venv` và pip kickmix trên Windows để dựng mạch; upload submission lên notebook Colab để chấm.
Xem [lệnh dựng baseline và hướng dẫn chấm](../../docs/COLAB_GRADING.md).
Mạch đã dựng nằm trong `artifacts/dqi/DQI-BASELINE/`. Lưu JSON chấm vào `results/dqi/`.
SCORES.md ghi cả FULL / PASS và DEV_5MIN / PASS; chỉ so điểm trong cùng chế độ và cấu hình.

## Bắt đầu hướng mới

Nhận Issue trước khi code. Tạo `<ID>/solution.py`, `<ID>/DESCRIPTION.md` và `<ID>/configs/<config>.json` theo mẫu trong `templates/`.
Thêm ID/title/link mô tả vào EXPERIMENTS.md. Artifact có cùng stem config; một hướng có nhiều config, không sao chép code cho mỗi setting.
