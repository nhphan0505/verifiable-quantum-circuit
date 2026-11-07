# Luồng đọc tài liệu

Đọc [research/AGENTS.md](../../../research/AGENTS.md). Mỗi thành viên dùng research/<username>, một đợt có thể thêm nhiều nguồn.
Issue theo nguồn là tùy chọn. Luồng này độc lập với experiment.

| Giai đoạn | Prompt | Kiểm tra thủ công / điểm dừng |
| --- | --- | --- |
| Nhận nguồn | [01](01_register_source.md) | Đúng nguồn/track/thư mục, branch cá nhân và draft PR thật; chưa đọc sâu |
| Đọc paper | [02](02_read_paper.md) | Có note.md draft, source.json và căn cứ |
| Đọc discussion | [03](03_read_discussion.md) | Có snapshot và note.md draft |
| Review riêng | [04](04_review_note.md) | Findings/SHA do agent khác trả về |
| Hoàn thiện/xuất bản | [05](05_publish_note.md) | Chọn rõ một vai trò mỗi lần: tác giả chuẩn bị → reviewer đăng review → tác giả merge |
| Tiếp tục chat | [06](06_resume.md) | Khôi phục nguồn, branch, giai đoạn thật |

Luồng: 01 → 02 hoặc 03 → 04 → sửa findings → 05 author_prepare →
05 reviewer_publish → nhóm họp quyết định → giao 05 author_merge. Có lỗi thì quay lại sửa/review.
Agent độc lập review không sửa branch tác giả. Approval phải thuộc HEAD cuối.
PDF được lưu nháp trước khi có note; CI chặn merge nguồn thiếu note.md hoặc note rỗng.
Trước bàn giao PR, chạy scripts/check_research_notes.py; không tạo placeholder để đủ file.
Sau merge, đồng bộ main vào branch cá nhân trước đợt tiếp. Không tự merge khi chưa có
quyết định nhóm và giao quyền merge.
