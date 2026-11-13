# Dependency của bản tái lập

Dùng Python 3.13 trong `.venv` Windows và các package đúng requirements.txt.
Không dùng WSL, bash hoặc Linux engine để thực thi.

1. Lấy thư mục `invsqrt_source` do người dùng cung cấp trong chat này. Chưa có URL phát hành công khai đã xác minh. Copy nguyên thư mục vào `artifacts/invsqrt/INV-51/dependencies/invsqrt_source` dưới root checkout đang build. Không dùng đường dẫn Downloads trong config.
2. Tất cả 560 file phải khớp `data/SHA256SUMS`; solution kiểm tra từng file trước khi copy. Giữ `LICENSE` và `NOTICE`. File lạ không thuộc manifest không được copy vào cây chạy.
3. Cấp `kickmix/kickmix.so` và verifier theo DATA.md. `.so` chỉ giữ để các hash assertion nguồn tác giả hoạt động; module thực thi là pip Kickmix Windows được preload từ `.venv`. Verifier gốc chỉ được copy/kiểm tra hash, không chạy.
4. Chạy từ bất kỳ cwd với đường dẫn tuyệt đối đến solution và config, ví dụ `D:/GQA/.venv/Scripts/python.exe D:/GQA/artifacts/worktrees/INV-51/src/invsqrt/INV-51/solution.py --config D:/GQA/artifacts/worktrees/INV-51/src/invsqrt/INV-51/configs/reconstructed.json`.

Build không đọc submission đầu vào hoặc KMX khứ hồi. Source tác giả có một số KMX/KMB component và certificates trong manifest; giữ nguyên để đáp ứng pin và mô tả provenance, không thay bằng whole-submission payload. Chỉ các module build khai báo mới chạy.

Adapter Python thực hiện thứ tự của build.sh/pipeline.sh; không chạy prove_any.py hoặc official verifier. Nếu hash không khớp thì dừng và giữ thư mục build để điều tra. `windows_runner.py` chỉ tương thích import resource/setrlimit; ghi rõ requests không được enforce trên Windows. Mỗi subprocess timeout 600 giây. Không sửa các nguồn đã pin trên đĩa, ngoại trừ thay @FG_ROOT@ bên ngoài work/c10 theo cơ chế upstream.
