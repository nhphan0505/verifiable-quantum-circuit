# Chấm bằng notebook local

Cài Python 3.13 và môi trường từ root:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
```

Mở `notebooks/GQA_Grade_Submission.ipynb` trong VS Code với Python/Jupyter
extensions, chọn kernel `.venv` của project. Tên file notebook được giữ để các link
cũ vẫn mở được; nội dung hiện chạy local. Không cần server Colab hoặc upload ZIP.

Điền TRACK (`invsqrt`, `dqi`, `dfthcsos`), MODE (`smoke`, `dev_5min`, `full`),
EXPERIMENT_ID, OWNER và CONFIG_NAME trong form: chạy cell setup và cell form
trước, chọn dropdown rồi chạy cell chấm. Đổi track sẽ xóa ID/config đang chọn;
đổi ID sẽ xóa config. Nút Làm mới lấy lại danh sách sau khi compile config mới.
ID lấy từ src theo track; config chỉ hiện khi có JSON và artifact đúng tên. Notebook tìm file đúng tên trong
`artifacts/<TRACK>/<ID>/<CONFIG_NAME>.kmb` hoặc `.zip` (task 3), đồng thời yêu cầu
`src/<TRACK>/<ID>/configs/<CONFIG_NAME>.json` tồn tại. Không tự chọn config khác.
Task 3 cần hai file dữ liệu FeMoCo trong verifiers/dfthcsos theo DATA.md.

Seed/mẫu dev giữ nguyên profile v1, timeout 300 giây, một worker. Full không có
timeout, dùng verifier gốc/default chính thức. Dừng cell sẽ dừng process chấm và
lưu trạng thái INTERRUPTED. TIMEOUT/INTERRUPTED không có điểm hợp lệ.

Kết quả tự lưu vào `results/<TRACK>/<ID>/<CONFIG_NAME>/<MODE>/<run_id>/`,
gồm config chấm, metadata/môi trường/hash, stdout/stderr, verifier.json nếu có
JSON gốc. Trường `upload_artifact` giữ tên cũ để tương thích checker nhưng chứa
hash artifact local thực tế. Task 3 được giải nén tạm dưới artifacts rồi dọn sau chấm.

Đúng một provenance build_only khớp hash sẽ được nối vào run. Nếu thiếu/mơ hồ,
review.json nêu phần agent cần đối chiếu; không suy đoán commit từ HEAD. Notebook
không cập nhật SCORES hay tự commit; báo agent thư mục Saved để phân tích ở prompt 04.
Không sửa log/JSON gốc. Kết quả lịch sử vẫn giữ nguyên.

Dev PASS không thay full PASS. So cải thiện với baseline cùng môi trường local,
mode/profile/seed và phiên bản verifier/harness; thiếu baseline tương thích thì
để hệ số cải thiện trống. Không dùng baseline Colab khác dependency để so trực tiếp.
