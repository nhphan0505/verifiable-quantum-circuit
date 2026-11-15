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

API và 13 tests semantic/guard đã đạt; hai lượt smoke riêng PP đã PASS. Tích hợp INV-66 là công việc riêng được người dùng giao cùng yêu cầu; chỉ làm sau kiểm chứng PP. Giữ run/provenance lịch sử, build source mới từ checkout sạch và so exact target. Sau yêu cầu gộp PR của người dùng, phương pháp và integration được nộp chung PR #67; folder và Issue PP vẫn riêng. Checker scope hiện chưa hỗ trợ diff experiment kèm module PP; không sửa/bypass checker trong nhiệm vụ gộp PR. Không merge hoặc đóng Issue trong lượt này.

## Kết luận kiểm chứng riêng PP

Source PP được kiểm chứng tại commit `1298d954ef9e06a552edf9e8f38e040e3efe97f8`. Raw baseline được dựng trực tiếp bằng `build_nr_circuit(10)` từ INV-BASELINE, không gọi finishing pipeline; thêm identity harness bằng scratch mới q[num_qubits] và bit mới b[num_bits], controls q0/q1. Chọn operation_index bằng số operation raw baseline (bỏ qua metadata). Hàm rewrite chỉ được gọi một lần tại site harness, không gọi PP khác.

Hash input raw+harness: `8603bd912c36fe00b4ff2d10d8a31f4ae4f9f1e324ceb479dd8459f8092c98de`; hash sau PP: `d92db9500de029768dcf0fc143f9ce80adec8d5ce7fb189db3f88a628c733909`. Môi trường chấm Python 3.13.18, kickmix 1.0.0, numpy 2.5.4, scipy 1.18.1, kickmix-engine 0.6.0 trên WSL Linux. Profile smoke max-x=4096, shots-per-x=1, seed=12345, threads=4, --no-cache; verifier repository giữ nguyên. Dùng CLI `python -m kickmix_engine verify invsqrt FILE --verifier VERIFIER --max-x 4096 --shots-per-x 1 --seed 12345 --threads 4 --no-cache` lần lượt cho control/candidate.

Cả control và candidate đều smoke PASS, candidate giảm đúng một Toffoli mỗi shot, giữ nguyên Q và worst error. Kết quả ủng hộ hypothesis local rewrite trong phạm vi guard và smoke đã thử; không gọi là full PASS riêng PP hay lợi ích toàn cục trên mọi mạch. Mạch nhỏ được so full branch Kraus matrices nên bao phủ target coherent/entangled và controls đổi sau CCX, không chỉ input target zero.

Artifacts/log chỉ tồn tại trong TemporaryDirectory /tmp/pp005-validation-* rồi tự dọn sau khi đọc output; không có config/run/results hay bảng điểm PP mới. Số đo đã báo trong chat, muốn xác nhận lại phải dựng baseline+harness và chạy lại. INV-66 fixed frontier không được dùng làm benchmark được gọi là chưa PP; việc tích hợp của nó được kiểm tra exact riêng trên branch experiment, không gộp vào kết luận smoke riêng PP.

API từ chối index ngoài phạm vi cũng như index âm/bool/không nguyên. Chưa hỗ trợ rewrite trong hoặc xuyên qua condition stack, debug/metadata hoặc instruction chưa biết. Đây là giới hạn bảo thủ, không phải chứng minh các trường hợp đó sai.

SHA-256 source baseline dùng kiểm chứng: `fddc7ecc89a67a4a897a5bf509c902805383b31c94964221f8ae70c2f695cfad`.
