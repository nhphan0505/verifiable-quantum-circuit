# [PP-005] Thay dead-write Toffoli trước HMR bằng đo sớm và CZ sửa pha, phạm vi invsqrt

Loại: Tách phép biến đổi dead-write của INV-66 thành PP độc lập. Owner Cheemshoang; mã PP-005, phạm vi invsqrt. Không thay thuật toán số học và không nhận là ý tưởng mới.

## Nguồn và hypothesis

Kế thừa phép sửa asteriospanoras được walkthrough mizeroluckygall mô tả; source INV-66 tại commit 09a342b445eac08e7cafc46a9eb4713ec5e6a1e4, mạch fixed e46d90c36d1beb3ce7731a3e0b5c3659b3cda7f5f290b73c6c34513d96c005b6. Notebook ghi code fix Apache-2.0; giữ attribution và không suy ra giấy phép cho toàn lineage. PP-002 là rewrite affine theo quan hệ đã phân tích; PP này chỉ dùng local dead-target/HMR rule, không tìm quan hệ Boolean và không dùng backend INV-51.

## Thuật toán và điều kiện đúng

Tìm CCX a b t vô điều kiện ngoài condition stack. Lần chạm t tiếp theo phải là HMR t m, cũng vô điều kiện. Giữa hai vị trí không được dùng/ghi m, không có control-flow directive hoặc metadata/debug barrier. Thay CCX bằng HMR t m; CZ a b if m và bỏ HMR cũ. Giữ mọi lệnh khác và không đổi input tại chỗ. Không yêu cầu t ban đầu bằng zero: X-measurement bra m thỏa <m_X|X_t=<m_X|*(-1)^m, nên mỗi measurement branch trước/sau có cùng Kraus operator. Lệnh giữa cặp không chạm t/m nên có thể dời measurement; CZ correction được đặt đúng vị trí CCX để cho phép controls thay đổi sau đó. Từ chối target được đọc/ghi giữa cặp, bit m được dùng/ghi, cổng có condition hoặc scope không thỏa; không tự dùng mẫu để bỏ guard.

## API

rewrite(circuit, *, operation_index=None) -> (new_circuit, rewritten_count). Index là số operation từ zero, không đếm REGISTER/APPEND_TO_REGISTER/INFO_TAG/DEBUG_PRINT. None chọn candidate an toàn đầu tiên; index cụ thể chỉ xét site đó. Không có candidate thì trả circuit không đổi và 0. Index âm/bool/không nguyên bị từ chối. API không đọc/ghi artifact, không tạo configs hoặc results. Caller nạp solution.py theo đường dẫn vì mã PP có dấu gạch ngang.

## Kế hoạch kiểm chứng trước triển khai

Tests dense Kraus trên mạch nhỏ so từng outcome đo, gồm target ban đầu tùy ý/entangled, controls bị thay đổi sau CCX, và các trường hợp phải từ chối. Kiểm tra register/góc/thứ tự được giữ. Không dùng thống kê cổng làm chứng minh semantics.

Benchmark: build raw INV-BASELINE từ source repository (không bật finishing pass), thêm một identity harness trên scratch mới: CCX a b t; HMR t m; CZ a b if m. Harness không đổi phase/value baseline; chọn đúng operation CCX của harness để chỉ PP này chạy. Không dùng frontier INV-66 đã qua PP khác làm đối chứng được gọi là chưa PP. Hash input sẽ đo sau commit PP trước chấm. Đối chứng/ứng viên cùng input raw+harness, seed 12345, max-x 4096, shots-per-x 1, threads 4, engine 0.6.0. Hai lượt smoke tối đa; không chạy full hoặc quét setting trong kiểm chứng PP. Dự đoán cả hai PASS, candidate giảm một Toffoli/shot, không tăng Q hoặc numerical error. Bác bỏ nếu bất kỳ Kraus branch khác, guard thiếu hoặc verifier FAIL; dừng và sửa rồi commit lại trước chấm. Không lưu artifact/log/config/run/results chấm PP; dùng TemporaryDirectory trong WSL và dọn sau khi xem kết quả. DESCRIPTION chỉ lưu cách tái chạy, nguồn/hash, commit và kết luận; số đo báo trong chat.

## Kết luận ban đầu

Chưa triển khai hoặc chấm PP-005. Tích hợp INV-66 là công việc riêng được người dùng giao cùng yêu cầu; chỉ làm sau kiểm chứng PP. Giữ run/provenance lịch sử, build source mới từ checkout sạch và so exact target. PR experiment sẽ phụ thuộc branch PP để checker scope không cần sửa/bypass. Không merge hoặc đóng Issue trong lượt này.
