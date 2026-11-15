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

Dùng `.venv` và pip kickmix trên Windows để dựng mạch; chạy notebook local để chấm artifact trực tiếp.
Xem [lệnh dựng baseline và hướng dẫn chấm](../../docs/LOCAL_GRADING.md).
Mạch đã dựng nằm trong `artifacts/dfthcsos/DFT-BASELINE/`. Lưu JSON chấm vào `results/dfthcsos/`.
SCORES.md ghi cả FULL / PASS và DEV_5MIN / PASS; chỉ so điểm trong cùng chế độ và cấu hình.

## Tách compile, tối ưu và đóng gói

- `solution.py` của mỗi hướng dựng loader từ config và dữ liệu đã khai báo.
- `postprocessing.py` của hướng dành cho tối ưu/refit dữ liệu hóa học, nếu có.
  Phải khai báo input/output, tham số, seed và dependency; giữ dữ liệu đầu vào
  bất biến, xuất ứng viên mới và ghi provenance riêng. Nếu thay `angle_words`,
  phải dựng lại loader phù hợp. Không chạy ngầm trong đường build tái dựng exact;
  ứng viên đã tối ưu cần được chấm lại. Mã nghiên cứu thiếu đầu vào chưa được gọi
  là postprocessing tái lập được, không thay bằng hàm no-op hoặc chép dữ liệu cuối.
- Đóng gói dùng chung [package_submission.py](../common/package_submission.py),
  không chép logic ZIP vào từng hướng hoặc đặt vào `postprocessing.py`.

Chuẩn bị thư mục components chỉ chứa `submission.npz` và `angle_k_0.kmb`,
`angle_k_1.kmb`, ... liên tục. Từ root repo chạy bằng venv Windows:

```powershell
.venv/Scripts/python.exe src/common/package_submission.py --input-dir artifacts/dfthcsos/<ID>/components --output artifacts/dfthcsos/<ID>/<config>.zip
```

Thay `<ID>`/`<config>` bằng hướng và tên config thực tế. Có thể import hàm
`package_dfthcsos(input_dir, output)` trong solution để giữ một lệnh build end-to-end.
Khi chạy từ cwd khác, dùng đường dẫn tuyệt đối tới script/input/output. Tiện ích
chỉ cần Python chuẩn, từ chối file thừa, symlink, chỉ số thiếu và output đã tồn tại.
ZIP chứa components ở gốc, giữ nguyên bytes, dùng ZIP_STORED và metadata cố định
để cùng đầu vào cho cùng hash. Record in ra gồm hash ZIP và từng component để
solution nối với provenance build. Đây không phải verification hoặc tối ưu, cũng
không cam kết hash container gốc nếu không có ZIP gốc để đối chiếu.

## Bắt đầu hướng mới

Nhận Issue trước khi code. Tạo `<ID>/solution.py`, `<ID>/DESCRIPTION.md` và `<ID>/configs/<config>.json` theo mẫu trong `templates/`.
Thêm ID/title/link mô tả vào EXPERIMENTS.md. Artifact có cùng stem config; một hướng có nhiều config, không sao chép code cho mỗi setting.
