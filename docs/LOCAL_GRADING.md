# Chấm smoke/full bằng kickmix-engine

Cài Python 3.13, tạo `.venv` và cài `requirements-notebook.txt` để mở
`notebooks/GQA_Grade_Submission.ipynb` bằng VS Code/Jupyter. Giữ `kickmix==1.0.0`
trong requirements để compile KMB và cung cấp import cho verifier chính thức.

Notebook dùng **kickmix-engine 0.6.0** với hai chế độ smoke và full. Chọn TRACK, MODE,
EXPERIMENT_ID, CONFIG_NAME và điền OWNER. Không còn lựa chọn dev hoặc
backend chấm cũ. Full không giới hạn thời gian; dừng cell lưu INTERRUPTED,
không có điểm hợp lệ.

Artifact vẫn là `artifacts/<TRACK>/<ID>/<CONFIG_NAME>.kmb` (bài 1–2) hoặc `.zip`
(bài 3). ZIP chứa submission.npz và angle_k_*.kmb liên tục từ 0 tại gốc.
Cần config JSON tương ứng và dữ liệu FeMoCo của bài 3 theo DATA.md.

Results vẫn lưu ở `results/<TRACK>/<ID>/<CONFIG_NAME>/<MODE>/<run_id>/`, gồm
config.json, metadata.json, stdout/stderr, verifier.json khi có JSON và provenance
khi tìm được đúng một build khớp hash. Thiếu/mơ hồ provenance thì review.json ghi
phần cần đối chiếu; không suy ra commit nguồn từ HEAD. Notebook không tự sửa
SCORES hoặc commit. Các run dev lịch sử vẫn được giữ và checker vẫn đọc để bảo toàn bằng chứng.
Smoke chỉ kiểm tra nhanh, không thay thế full và không ghi điểm vào SCORES.

Có thể so điểm giữa các phiên bản/môi trường theo chính sách repo; cần ghi rõ
điều kiện chấm và giới hạn. Đợt chấm lại này dùng cùng engine cho baseline và ứng viên.

## Engine chấm mặc định

Notebook tự nhận diện OS. Linux và macOS dùng Python của kernel; Windows dùng
Ubuntu mặc định trong WSL và `<project>/.venv-engine/bin/python`. KMB/ZIP và thư mục
results vẫn theo quy ước trên. Không dùng engine cũ làm fallback khi cài đặt thiếu.

Windows chưa có WSL: mở PowerShell Administrator, chạy `wsl --install -d Ubuntu`,
khởi động lại nếu được yêu cầu, rồi mở Ubuntu để tạo tài khoản. Chọn Ubuntu làm
distro mặc định bằng `wsl --set-default Ubuntu`. Xem [hướng dẫn Microsoft](https://learn.microsoft.com/windows/wsl/install).

Trong Linux/macOS hoặc terminal Ubuntu (Windows), chuẩn bị Python 3.13 và tạo
môi trường riêng. Trên WSL, cd tới project bằng đường dẫn `/mnt/d/...`:

```bash
python3.13 -m venv .venv-engine
.venv-engine/bin/python -m pip install -r requirements.txt
```

Cài wheel **0.6.0** phù hợp OS/CPU từ
[release upstream](https://github.com/manwithacat/kickmix-engine/releases/tag/v0.6.0),
đối chiếu SHA-256 với `SHA256SUMS.txt` và `release-manifest.json` trước khi cài:

```bash
.venv-engine/bin/python -m pip install /path/to/kickmix_engine-0.6.0-PLATFORM.whl
.venv-engine/bin/python -m kickmix_engine doctor --json
```

Linux/macOS chạy notebook bằng `.venv` như trước: cài cùng wheel vào `.venv`.
Windows giữ notebook trong `.venv` Windows; chỉ engine chấm dùng `.venv-engine`
Linux. Không dùng `.venv` Windows trong WSL. Wheel phải hỗ trợ kiến trúc hiện tại;
macOS Intel chưa có wheel được xác nhận, cần build upstream và kiểm thử riêng.
Không tự tải binary hoặc tự cài WSL từ notebook.

Metadata mới có `engine` (version, platform, kernel) và packages của runtime thực
sự chấm. Metadata cho phép người đọc đối chiếu điều kiện baseline và ứng viên. Kết quả lịch sử giữ nguyên bytes.
Full dùng CLI engine với đầy đủ tham số mặc định chính thức. Smoke dùng
invsqrt max-x=4096, shots-per-x=1; DQI num-shots=4096; DFTHC shots-per-address=1.
Trước nghiệm thu trên mỗi nền tảng, chạy `verify ... --cross-check` với artifact
thật và verifier repository. Việc tests orchestration đạt không thay bằng chứng
đối chiếu mạch hay full verification.
