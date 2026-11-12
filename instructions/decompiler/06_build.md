# 06 — Build và nghiệm thu exact

Đầu vào: bước 5 đạt. Được build, sửa code/config trong phạm vi rồi commit/push và
build lại khi cần; lưu records mới. Không tự chạy verifier/chấm điểm.

- Theo [experiments 03](../experiments/03_implement_compile.md) và
  [REPOSITORY_CHECKS](../../docs/REPOSITORY_CHECKS.md): kiểm tra bytes source/config
  local khớp snapshot commit trước build, dùng Python/package pin của repo.
- Chạy solution với dependency đã khai báo, không đọc input gốc hoặc scratch khi
  build. Kiểm tra đường dẫn/dependency trong code; chạy với cwd khác khi cần để
  phát hiện phụ thuộc ngầm. Chỉ công cụ đối chiếu mới đọc file gốc.
- Ghi provenance build_only đúng schema: commit, source/config hash, artifact hash,
  command, environment; thêm dependency hashes. Lưu reconstruction_check.json mới
  bên cạnh: input/output hash/bytes, từng file con, cách so, kết quả, environment,
  source_commit và liên kết manifest. Không tạo điểm verifier cho build_only.
- So bytes theo luồng và SHA-256. Task 3 so toàn ZIP, từng member, NPZ/NPY và mảng
  với semantics so đã khai báo (dtype/shape/order/bytes, không dùng allclose).
- Khác hash thì tìm sai khác, sửa trong phạm vi, commit rồi dựng lại với run mới.
  Không vá output bằng dữ liệu file gốc, sửa record cũ hoặc tuyên bố tương đương
  là exact. Không lặp vô hạn: nếu do thiếu dữ liệu/serializer không tái lập được,
  báo nguyên nhân, bằng chứng và phần đạt; cần người dùng đổi tiêu chí rõ ràng
  trước khi nghiệm thu ở mức thấp hơn. Giữ trace tiêu chí gốc và tiêu chí mới.

Nghiệm thu mặc định: RECONSTRUCTED_EXACT cho toàn artifact, build/provenance có
bằng chứng thật. COMPONENTS_EXACT_CONTAINER_DIFFERS chưa đạt mục tiêu hash ZIP.
Báo BUILT độc lập với exact; cả hai không đồng nghĩa PASS.
