# Dependency của bản tái lập

Dùng Python 3.13 trong `.venv` Windows và các package đúng requirements.txt.
Không dùng WSL, bash hoặc Linux engine để thực thi.

1. Mở [dataset VQCC Own-Circuit Portfolio](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio) của `syed3000`, tải file **`invsqrt_source_zip`**. Theo README của gói phát hành, tác giả bỏ phần mở rộng `.zip` để Kaggle giữ nguyên archive. Đổi tên file đã tải thành `invsqrt_source.zip` (không nén lại). Kiểm tra SHA-256 **`7d9801ae20e942dba2211a656bba6014a0a16d57da534c0b60328d1c5d9d8254`** và kích thước **2563106 bytes**. Nếu dataset đã cập nhật, chỉ dùng archive khớp hash này; chưa xác định số version dataset trên Kaggle. Giải nén vào `artifacts/invsqrt/INV-51/dependencies/` dưới repo root để có `invsqrt_source/README.md`, `invsqrt_source/SHA256SUMS` và `invsqrt_source/src/`.
2. Tất cả 560 file phải khớp `data/SHA256SUMS`; solution kiểm tra từng file trước khi copy. Giữ `LICENSE` và `NOTICE`. File lạ không thuộc manifest không được copy vào cây chạy.
3. Cấp `kickmix/kickmix.so` và verifier theo DATA.md. `.so` chỉ giữ để các hash assertion nguồn tác giả hoạt động; module thực thi là pip Kickmix Windows được preload từ `.venv`. Verifier gốc chỉ được copy/kiểm tra hash, không chạy.
4. Từ repo root chạy `.venv/Scripts/python.exe src/invsqrt/INV-51/solution.py --config src/invsqrt/INV-51/configs/reconstructed.json`. Đường dẫn metadata/source/config/artifact được hiểu tương đối root; provenance cũ giữ lệnh thực tế của lần build lịch sử.

Build không đọc submission đầu vào hoặc KMX khứ hồi. Source tác giả có một số KMX/KMB component và certificates trong manifest; giữ nguyên để đáp ứng pin và mô tả provenance, không thay bằng whole-submission payload. Chỉ các module build khai báo mới chạy.

Adapter Python thực hiện thứ tự của build.sh/pipeline.sh; không chạy prove_any.py hoặc official verifier. Nếu hash không khớp thì dừng và giữ thư mục build để điều tra. `windows_runner.py` chỉ tương thích import resource/setrlimit; ghi rõ requests không được enforce trên Windows. Mỗi subprocess timeout 600 giây. Không sửa các nguồn đã pin trên đĩa, ngoại trừ thay @FG_ROOT@ bên ngoài work/c10 theo cơ chế upstream.

Đã xác minh archive local với hash trên chứa manifest đúng và cả 560 entry khớp hash từng file. Link dataset do người dùng xác nhận là nơi tải; công cụ web chưa truy cập được trang để xác minh độc lập tình trạng truy cập công khai hoặc version. Không dùng nhận định này làm kết luận về quy định cuộc thi.
