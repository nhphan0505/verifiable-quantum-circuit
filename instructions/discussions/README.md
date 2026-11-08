# Instructions đọc discussion

Đọc [quy tắc chung](../README.md), [quy tắc research](../research-common.md) và
[research/AGENTS.md](../../research/AGENTS.md). Chuỗi này chỉ xử lý discussion;
không cần chép prompt hay truyền lại OWNER/SOURCE_DIR/PR trong mỗi tin nhắn.
Trong chat đã xác định luồng, có thể giao **“thực hiện các bước 1 2 3”**.
Nếu chưa có nguồn hoặc không rõ owner/PR sau khi tra ngữ cảnh/project/GitHub, hỏi đúng
phần thiếu. Nếu có nhiều nguồn, dùng danh sách đã giao; không tự nhận nguồn ngoài phạm vi.

| Bước | Instructions | Đầu ra / điều kiện chuyển tiếp |
| --- | --- | --- |
| 1 | [Nhận nguồn](01_register_source.md) | Nguồn đúng phiên bản/hash, source.json, mục lục, draft PR; chưa note |
| 2 | [Đọc và viết note](02_read_source.md) | note.md draft có căn cứ, coverage và source.json khớp |
| 3 | [Tự kiểm tra / sửa findings](03_check_revise.md) | Bản draft tác giả đã rà, commit/PR cập nhật; chưa thay review độc lập |
| 4 | [Review độc lập](04_review_note.md) | Phiên agent độc lập trả findings/kết luận và SHA |
| 5 | [Hoàn thiện / merge](05_publish_note.md) | Tác giả đặt ready, checks/CI đạt và merge commit sau review |
| 6 | [Khôi phục](06_resume.md) | Đối chiếu trạng thái, tiếp tục đúng bước được giao |

Luồng: **1 → 2 → 3 → 4 → 5**. Nếu có findings: **3 → 4 → 5**.
Bước 3 là bước tác giả tự rà; bước 4 luôn độc lập. Bước 1/2 không tự tạo điểm dừng
xác nhận nếu bước kế tiếp đã được giao và đủ đầu vào. Review hoặc chấm/check chưa đạt
vẫn chặn chuyển bước phụ thuộc. Một đợt có thể cùng PR với nguồn khác đã giao.
Chỉ sửa `research/<TRACK>/discussions/<SOURCE_ID>/` và dòng mục lục liên quan,
trên `research/<username>` đúng owner; Issue tài liệu là tùy chọn.
