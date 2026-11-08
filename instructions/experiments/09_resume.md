# 09 — Khôi phục ngữ cảnh khi đổi chat/model

Áp dụng [quy tắc chung và ngữ cảnh](../README.md), AGENTS.md, CONTRIBUTING.md và
[workflow thử nghiệm](../../docs/EXPERIMENT_WORKFLOW.md).
Lấy thông tin từ chat/project/GitHub; không yêu cầu điền lại form.

## Ràng buộc và quyền thao tác

Chỉ đọc để khôi phục; không tự tạo Issue/branch/run hoặc cấp thêm quyền. Khi đã xác định bước được giao tiếp tục, áp dụng đúng phạm vi/branch của bước đó.

## Yêu cầu thực hiện

Kiểm tra branch/working tree, Issue/PR, DESCRIPTION, code/config và các run
thực tế để khôi phục trạng thái. Không mặc định công việc trước đã hoàn tất,
không tạo lại Issue/branch/run hay chạy lại build nếu đã có bằng chứng phù hợp.
Giữ thay đổi hiện có của người dùng; kiểm tra artifact bằng hash nếu dùng lại.

Tiếp tục đúng giai đoạn được giao theo instructions bước tương ứng trong instructions/experiments/.
Thiếu quyền cho push/PR/merge thì không tự suy ra từ việc đổi chat. Không tự chạy notebook, mở
Colab hoặc theo dõi runtime. Báo trạng thái đã xác minh và chỉ hỏi thông tin
còn thiếu mà không tra được từ project/GitHub.

## Danh sách nghiệm thu

- [ ] Owner/branch/HEAD/Issue/PR/config/run và bằng chứng công việc đã được đối chiếu thực tế.
- [ ] Không lặp công việc có bằng chứng phù hợp; xác định bước tiếp và chỉ hỏi dữ kiện chưa thể tra được.
