# Local build → Colab verify

## Dựng mạch theo config

Python local dùng `.venv` với `pip install -r requirements.txt`. Từ root project:

```powershell
.\.venv\Scripts\python.exe src/invsqrt/INV-BASELINE/solution.py --config src/invsqrt/INV-BASELINE/configs/baseline.json
.\.venv\Scripts\python.exe src/dqi/DQI-BASELINE/solution.py --config src/dqi/DQI-BASELINE/configs/baseline.json
.\.venv\Scripts\python.exe src/dfthcsos/DFT-BASELINE/solution.py --config src/dfthcsos/DFT-BASELINE/configs/baseline.json
```

Đầu ra tự động: `artifacts/<TRACK>/<ID>/<config-name>.kmb` (task 1–2), `.zip` (task 3). Baseline hiện có tên config `baseline`. Nếu artifact đã tồn tại, code báo lỗi; chỉ thêm `--overwrite` khi muốn dựng lại. Có thể dùng `--output <đường-dẫn>/<config-name>.kmb` hoặc `.zip` để đổi thư mục đích.

Task 3 tự đóng gói `submission.npz` và `angle_k_0.kmb`, ... ở gốc ZIP. Không cần giữ thư mục mạch rời để chấm.

## Chuẩn bị ZIP sau khi clone

Sau khi khôi phục dữ liệu theo [DATA.md](../DATA.md), chạy từ root project:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_colab.py
```

Lệnh tạo lại `artifacts/colab/gqa_verifiers.zip`, `dfthcsos_reference.zip` và
`manifest.json` chứa SHA-256 các đầu vào/hai ZIP. Script kiểm tra đủ file và
hash verifier/dữ liệu gốc theo `data_manifest.json`; thiếu hoặc sai thì dừng
trước khi ghi ZIP. Dev harness được đóng gói từ source hiện tại của repo.
Các output không commit; teammate clone mới chạy lại lệnh này.

## Chấm bằng tay

Mở `notebooks/GQA_Grade_Submission.ipynb` trong Colab, chọn CPU và chạy tuần tự:

1. Dùng runtime Python 3.13; cell cài kickmix 1.0.0, NumPy 2.4.6 và SciPy 1.16.3 theo requirements-colab.txt.
2. Notebook tự kiểm tra các file verifier/harness cần thiết trong runtime; nếu đủ thì bỏ qua upload. Nếu thiếu, upload đúng một `artifacts/colab/gqa_verifiers.zip`; notebook kiểm tra lại sau giải nén.
3. Chọn TRACK, EXPERIMENT_ID, MODE và OWNER. Không có ô CONFIG_NAME.
4. Task 1–2 bắt buộc đúng một `.kmb`; task 3 bắt buộc đúng một ZIP submission. Sai số lượng/định dạng/cấu trúc ZIP thì code báo lỗi và chặn verify, không dùng lại submission cũ.
5. Riêng task 3, upload `artifacts/colab/dfthcsos_reference.zip` ở cell dữ liệu nếu runtime chưa có dữ liệu tham chiếu.
6. Chạy Verify, đợi kết thúc rồi chạy Tải results. Giải nén ZIP vào root project.

Tên config lấy từ stem artifact: `balanced.kmb` hoặc `balanced.zip` → `balanced`. Ký tự ngoài chữ/số/gạch ngang/gạch dưới được thay bằng `_`. Bên trong ZIP task 3 vẫn phải giữ tên `submission.npz`, `angle_k_*.kmb` liên tục từ 0. Không nhận file rời.

Kết quả: `results/<TRACK>/<ID>/<CONFIG_NAME>/<MODE>/<run_id>/`. Metadata ghi tên config và `upload_artifact` (name, sha256, size_bytes) của đúng file `.kmb`/`.zip` đã upload; `submission_sha256` giữ hash từng file mạch/NPZ sau giải nén. Đối chiếu `upload_artifact.sha256` với hash artifact trong record build_only; config.json là tham số chấm, không phải JSON dựng mạch. Không cần upload JSON build; phiên bản dựng nằm trong source/config Git hoặc record build_only. Mỗi lần chấm có run-id mới nên không ghi đè.

## Các chế độ

| Mode | Invsqrt | DQI | DFTHC |
| --- | --- | --- | --- |
| smoke | x=1..4096, 1 shot/x | 1024 shot | Mọi địa chỉ, 1 shot/địa chỉ |
| dev_5min v1 | 4096 x trải toàn miền, lặp 2 lần | 4096 shot, giữ kích thước bài | Mọi địa chỉ, 4 shot/địa chỉ, đầy đủ metrics Hamiltonian |
| full | x=1..3.133.452, 64 shot/x, tổng 200.540.928 shot | 102400 shot | Mọi địa chỉ, 64 shot/địa chỉ |

Dev dùng seed 20261106, độc lập với circuit, và một worker. Dùng cùng profile, seed và số mẫu để so sánh. Invsqrt lưu hash tập mẫu; tập này gồm biên chuẩn hóa/đa thức, đầu vào nhỏ/lớn, mẫu đều và ngẫu nhiên. Không bảo đảm bắt được worst-case; mô hình số học của mỗi hướng cần được kiểm tra riêng.

Timeout dev mặc định 300 giây gồm thời gian process nạp circuit/chấm, không gồm pip/upload/hash trước chạy. TIMEOUT không phải lỗi mạch và không có điểm hợp lệ; vẫn tải được metadata/log. Chưa tự hiệu chỉnh số mẫu theo máy; đo baseline trước, điều chỉnh cấu hình rồi so tất cả ứng viên cùng cấu hình. Điểm DQI phụ thuộc cận lỗi theo số mẫu; JSON có thêm Q²T để phân tích tài nguyên.

Full/dev PASS đều ghi vào SCORES.md với hai cột riêng; smoke/FAIL/TIMEOUT chỉ lưu results. Không so trực tiếp điểm dev với full. Mô tả ý tưởng và kết luận kỹ thuật đặt ở src/<TRACK>/<ID>/DESCRIPTION.md; EXPERIMENTS.md chỉ là mục lục.

## Bảo trì

Sau khi cập nhật `src/common/dev_verify.py`, chạy lại `scripts/prepare_colab.py`. Verifier gốc phải giữ đúng hash manifest; script từ chối verifier bị sửa. Notebook không nhúng source/circuit bằng base64. Thay file notebook local không tác động đến phiên Colab đang chạy.

Artifact notebook smoke cũ được giữ tại `artifacts/colab/archive/` để lưu lịch sử, không dùng cho lần chấm mới.

Phiên bản Python/dependency và cách kiểm tra records: [REPOSITORY_CHECKS.md](REPOSITORY_CHECKS.md).
