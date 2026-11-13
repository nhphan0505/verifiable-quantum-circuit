# Source tích hợp Fusion

## Mục tiêu

`solution.py` compile mạch bằng source Python và JSON trong `engine/`. Không tải hoặc giải nén archive ở runtime, không phụ thuộc `artifacts/.../dependencies`, không dùng Linux .so, verifier hoặc file submission/KMX đã có.

Các module giữ tên/path component upstream để duy trì quan hệ import và owner token; đây là các file Python/JSON có thể đọc/sửa trong Git, không phải archive/payload. Credits Syed Asad Ali, Apache-2.0, giữ LICENSE.txt/NOTICE.txt. Bundle nguồn gốc Kaggle version 12 có hash 7d9801ae20e942dba2211a656bba6014a0a16d57da534c0b60328d1c5d9d8254, đã xác minh công khai ở INV-51.

## Điều chỉnh so với upstream

- Chuẩn hóa cú pháp Python bằng AST unparse, bổ sung docstring/attribution khi thiếu. Công thức, gate emission, thứ tự patch, exact angles và assertion số học/owner/debt được giữ.
- Những assertion SHA-256 và vòng kiểm tra INPUTS/SOURCE_READY kiểm tra archive lịch sử được tách khỏi thuật toán; không giả lập nội dung/hash các artifact bị bỏ. Trước build, engine_manifest.json kiểm tra hash từng file source/data tích hợp đã commit.
- Dữ liệu certificate và bảng được copy nguyên bytes; hash được giữ trong manifest và lineage. Một số receipt JSON cũng chứa cấu hình/angles và vẫn cần cho module; chúng chỉ là input dựng, không phải kết quả chấm mới.
- @FG_ROOT@ trở thành path của engine tính từ __file__; không sửa file nguồn/copy bundle trong quá trình build.
- Bỏ import resource và các setrlimit chỉ dùng cho giới hạn hệ thống Unix. Chạy pip Kickmix Windows và giới hạn 600s mỗi stage; không tuyên bố enforce giới hạn RAM Unix.
- So sánh đường dẫn certificate bằng Path.resolve để phù hợp Windows.

upstream_changes.json ghi path nguồn gốc, SHA trước/sau và từng loại thay đổi. Không sử dụng mạch được chấm sẵn làm dữ liệu của generator. Các KMB/KMX component và receipt chỉ dùng cho kiểm tra source upstream được bỏ khỏi dependency runtime.

## Giao diện

Cài requirements của repo vào .venv Windows, rồi từ root checkout:

```powershell
.venv/Scripts/python.exe src/invsqrt/INV-53/solution.py --config src/invsqrt/INV-53/configs/reconstructed.json
```

Config gồm hash target và timeout stage; không có source_bundle. Worker chạy từng module local và ghi audit các file đọc vào artifacts để chứng minh dependency closure. Chỉ phép kiểm tra đối chiếu bên ngoài build mới đọc submission đối chứng. Build_only provenance gắn source/config/engine hashes và commit thật; không tự chấm official verifier.
