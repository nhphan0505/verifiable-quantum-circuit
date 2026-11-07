# invsqrt

Mục tiêu: giảm **Q × (Toffoli + T/4)**, với các điều kiện của verifier gốc.

## Bài làm hiện tại

- `INV-BASELINE/solution.py`: bản sao thuật toán ban tổ chức, chưa tối ưu.
- Nguồn: `verifiers/invsqrt/nr_reference_circuit.py`.
- **Baseline full: PASS — score 2076774.233715282, 200.540.928 shot.**
- [Mục lục và tiêu đề Issue](EXPERIMENTS.md).
- [Bảng điểm](SCORES.md).

## Solution baseline

Chuẩn hóa x theo cặp bit; chọn một trong bốn đa thức bậc ba và đánh giá bằng Horner; thực hiện một bước Newton–Raphson; dịch kết quả, áp pha theo bit, rồi uncompute toàn bộ.

Giữ nguyên x; scratch về 0; sai số pha theo verifier, đồng thời phải còn dung sai cho tổng hợp phép quay.

## Chạy

Dùng `.venv` và pip kickmix trên Windows để dựng mạch; upload submission lên notebook Colab để chấm.
Xem [lệnh dựng baseline và hướng dẫn chấm](../../docs/COLAB_GRADING.md).
Mạch đã dựng nằm trong `artifacts/invsqrt/INV-BASELINE/`. Lưu JSON chấm vào `results/invsqrt/`.
SCORES.md ghi cả FULL / PASS và DEV_5MIN / PASS; chỉ so điểm trong cùng chế độ và cấu hình.

## Bắt đầu hướng mới

Nhận Issue trước khi code. Tạo `<ID>/solution.py`, `<ID>/DESCRIPTION.md` và `<ID>/configs/<config>.json` theo mẫu trong `templates/`.
Thêm ID/title/link mô tả vào EXPERIMENTS.md. Artifact có cùng stem config; một hướng có nhiều config, không sao chép code cho mỗi setting.
