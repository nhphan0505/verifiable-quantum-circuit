# 02 — Đọc paper và viết note.md

Áp dụng [quy tắc chung](../README.md), [ràng buộc research](../research-common.md)
và [mẫu note paper](../../templates/research/notes.md).

## Ràng buộc

Trên `research/<username>` đúng owner, chỉ sửa note.md/source.json và dòng mục lục
của paper được giao. Đọc đúng nguồn/phiên bản đã nhận; không đổi nguồn âm thầm.
Được commit/push, cập nhật draft PR; không đặt ready/merge, sửa experiment hoặc chạy chấm.

## Yêu cầu

Lấy SOURCE_DIR/danh sách paper và PR từ ngữ cảnh/project; nếu nhiều lựa chọn chưa rõ
thì hỏi. Kiểm tra metadata/hash/phiên bản trước khi đọc. Tự chọn phần liên quan đến
track bằng cách đối chiếu bài/verifier/baseline; nguồn shared tập trung kỹ thuật dùng
chung và track có liên hệ. Đọc thêm định nghĩa/giả định/chứng minh/phụ lục cần thiết,
không dừng ở abstract hoặc hỏi người dùng chọn phạm vi thường lệ.

Đọc trực tiếp nguồn, kiểm tra trực quan trang có công thức/bảng khi trích xuất không rõ.
Ghi trang PDF, mục/phương trình, định nghĩa ký hiệu, giả định/điều kiện đúng, sai số,
tài nguyên/chi phí và giới hạn. Được tra nguồn dẫn cần thiết trong phạm vi đã giao;
ghi căn cứ và giới hạn truy cập. Không đoán công thức từ OCR lỗi. Phân biệt kết quả
tác giả, suy luận áp dụng của nhóm và kết quả project thực đo; chỉ đọc code/results
liên quan để đối chiếu, không tạo hướng thử.

Viết note.md đủ dùng độc lập theo template với Status: draft, Track/Source/Version.
Ghi mục/trang đã đọc/chưa đọc trong note và coverage source.json; metadata/hash phải
khớp nguồn. Cập nhật mục lục draft, commit/push và draft PR; bàn giao SHA cho bước 3/4.

## Danh sách nghiệm thu

- [ ] Note draft đúng template/metadata, công thức/ký hiệu/điều kiện/citation có căn cứ.
- [ ] Phân biệt nguồn/suy luận/đo đạc; nêu coverage/giới hạn và phần chưa kiểm chứng.
- [ ] source.json và mục lục khớp note; commit/PR cập nhật, chưa ready/merge.
- [ ] Nếu bước 3 đã được giao, tự rà tiếp; review độc lập vẫn ở bước 4.
