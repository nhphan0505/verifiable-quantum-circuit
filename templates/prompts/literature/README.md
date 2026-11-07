# Luồng đọc tài liệu

Đọc [research/AGENTS.md](../../../research/AGENTS.md). Mỗi thành viên dùng research/<username>, một đợt có thể thêm nhiều nguồn.
Issue theo nguồn là tùy chọn. Luồng này độc lập với experiment.

Prompt 01 nhận PDF đính kèm: thành viên điền OWNER, TRACK và gửi file cùng prompt.
TRACK có các lựa chọn invsqrt/dqi/dfthcsos/shared hoặc **agent tự chọn**;
không cần link hoặc biết trước track. Agent tự phân loại paper/discussion và chọn
track bằng cách đọc lướt tài liệu, đối chiếu bài trong repo; nêu căn cứ khi bàn giao.
Có thể chỉ định track nếu đã biết. Agent dùng đúng bản gửi, không tự tìm/tải bản khác.
Sau đó dùng prompt 02 để đọc paper thành note.
Prompt 02 chỉ cần điền SOURCE_DIR và BRANCH / OWNER; agent tự chọn phần liên quan
đến track, đọc thêm căn cứ cần thiết và ghi rõ phạm vi đã đọc/chưa đọc.
Với discussion dùng nguồn/snapshot đã giao và prompt 03.

| Giai đoạn | Prompt | Kiểm tra thủ công / điểm dừng |
| --- | --- | --- |
| Nhận nguồn | [01](01_register_source.md) | Đúng nguồn/track/thư mục, branch cá nhân và draft PR thật; chưa đọc sâu |
| Đọc paper | [02](02_read_paper.md) | Có note.md draft, source.json và căn cứ |
| Đọc discussion | [03](03_read_discussion.md) | Có snapshot và note.md draft |
| Review riêng | [04](04_review_note.md) | Findings/SHA do agent khác trả về |
| Hoàn thiện/xuất bản | [05](05_publish_note.md) | Tác giả đặt ready, chạy checks và merge sau review bước 04 đạt |
| Tiếp tục chat | [06](06_resume.md) | Khôi phục nguồn, branch, giai đoạn thật |

Luồng: 01 → 02 hoặc 03 → 04 → sửa findings và review lại nếu cần → 05 tác giả hoàn thiện/merge.
Agent độc lập review không sửa branch tác giả. Review bước 04 ghi kết luận và SHA;
không cần họp nhóm hoặc đăng approval GitHub riêng. Nội dung đã review thay đổi thì
quay lại 04; chỉ đặt ready và đồng bộ trạng thái mục lục thì không cần review lại.
PDF được lưu nháp trước khi có note; CI chặn merge nguồn thiếu note.md hoặc note rỗng.
Trước merge chạy checker/tests/scope và chờ CI đạt; không bypass rules GitHub thực tế.
Sau merge, đồng bộ main vào branch cá nhân trước đợt tiếp.
