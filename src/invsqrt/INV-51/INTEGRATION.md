# Compiler gọn INV-51

Ba file runtime là solution.py, circuit.py và tables.json; configs/reconstructed.json chọn bản Q46 cố định. Không cần thư mục engine hoặc source bundle. Dùng .venv Windows với requirements của repo.

## Thay đổi

- Các định nghĩa Python được gom theo namespace, đổi tên scope-aware thành tên toán học rõ ràng. Đây là hàm/class Python thực, không phải chuỗi code, ZIP hoặc payload mạch. Bộ liên kết nội bộ gọi trực tiếp các hàm khởi tạo đã định nghĩa; exec_module là tên phương thức compatibility, không gọi exec/eval.
- Giữ bốn ngữ cảnh arithmetic riêng vì các binding carry/cleanup bị thay đổi độc lập. Gom chung globals của chúng sẽ có thể đổi gate stream.
- Bỏ 89 định nghĩa không được gọi/tham chiếu, biến khởi tạo không dùng và preflight chỉ kiểm tra hồ sơ giá/ủy quyền của các phiên bản cũ. Không thay toán học, phép quay hoặc correction.
- Trường JSON được chọn theo truy cập thực tế, giữ cả subtree khi so sánh/copy/serialize cần nó; giữ độ dài/thứ tự mảng và giá trị scalar. Sau pruning phải kiểm tra lại build sạch và so bytes, không chỉ tin trace.
- Adapter path Q46 và V10_FROM_G1 được cố định theo cấu hình e2 đã được nghiệm thu. Các environment variant upstream không phải API hỗ trợ.
- engine_manifest.json kiểm tra circuit.py/tables.json trước build; check_committed kiểm tra snapshot Git của source/config. Thay source/data phải cập nhật manifest rồi commit và build lại.

upstream_changes.json ghi commit cơ sở, nguồn Apache-2.0, danh sách định nghĩa/biến đã bỏ và cách lấy lineage trước refactor. Các source/result cũ còn nguyên trong Git. Bản file legacy còn được lưu ngoài Git dưới artifacts/inv51-compact/legacy-source-preserved để hoàn tác, nhưng compiler không đọc chúng.

## Cách chạy

```powershell
.venv/Scripts/python.exe src/invsqrt/INV-51/solution.py --config src/invsqrt/INV-51/configs/reconstructed.json
```

Stage sinh mạch thô → audit affine/pairs → giữ tích → tối đa bốn lượt rewrite affine → merge Z_POW → relocate → compile KMB. Audit file-open được lưu ở thư mục build mới. Không tự chạy official verifier hoặc symbolic proof upstream; kết quả exact và PASS là các loại bằng chứng khác nhau.
