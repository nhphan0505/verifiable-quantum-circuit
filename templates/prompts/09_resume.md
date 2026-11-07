# 09 — Khôi phục ngữ cảnh khi đổi chat/model

```text
Đọc AGENTS.md và CONTRIBUTING.md trước khi làm.

TRACK: <bài>
EXPERIMENT_ID: <ID>
ISSUE: <URL>
BRANCH: <branch>
GIAI ĐOẠN CẦN TIẾP TỤC: <triển khai / compile / phân tích results / chuẩn bị PR / ...>
THÔNG TIN BỔ SUNG: <run mới, config cần thử hoặc kết luận gần nhất>

Kiểm tra branch/working tree, Issue/PR, DESCRIPTION, code/config và các run
thực tế để khôi phục trạng thái. Không mặc định công việc trước đã hoàn tất,
không tạo lại Issue/branch/run hay chạy lại build nếu đã có bằng chứng phù hợp.
Giữ thay đổi hiện có của người dùng; kiểm tra artifact bằng hash nếu dùng lại.

Tiếp tục đúng giai đoạn được giao theo prompt tương ứng trong templates/prompts/.
Thiếu quyền cho push/PR/merge thì không tự suy ra từ việc đổi chat. Không tự chạy notebook, mở
Colab hoặc theo dõi runtime. Báo trạng thái đã xác minh và chỉ hỏi thông tin
còn thiếu mà không tra được từ project/GitHub.
```
