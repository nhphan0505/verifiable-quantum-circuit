# 08 — Merge và hoàn thành hướng

```text
Đọc AGENTS.md, CONTRIBUTING.md và docs/EXPERIMENT_WORKFLOW.md trước khi làm.

PR: <URL>
ISSUE: <URL>
REVIEW: <URL approval GitHub do teammate đăng ở 07b>

Tôi giao bạn merge PR này và hoàn thành Issue nếu đúng phạm vi đã xong.
Tôi là tác giả PR. Kiểm tra PR head, approval của teammate trên GitHub và
các check/branch rules bắt buộc. Approval phải còn hiệu lực và gắn với HEAD
hiện tại; nếu HEAD đã đổi, bàn giao teammate review lại phần mới và đăng
approval qua 07b trước khi merge. Kết luận trong chat chưa thay thế approval.
Không coi việc không có CI là đã chạy CI.

Nếu conflict ở mục lục/bảng điểm thì giữ đủ dòng, sửa đúng hướng và kiểm tra
lại link/điểm; commit sửa conflict tạo HEAD mới nên cần teammate review lại.
Không bypass checks, không force-push main, không viết lại lịch sử nguồn đã
được kết quả tham chiếu. Nếu bị chặn, báo rõ điều kiện còn thiếu; không merge ép.

Khi các điều kiện đạt, dùng merge commit để giữ các SHA nguồn trong lịch sử
nhánh chính; không squash merge hoặc rebase merge PR thử nghiệm. Nếu repository
không cho phép merge commit, báo điều kiện còn thiếu và dừng, không tự đổi
phương thức hoặc bypass rule. Xác nhận
PR đã merge và Issue đã đóng; nếu không tự đóng thì đóng Issue hoàn tất và
liên kết PR. Nếu phạm vi còn dang dở thì giữ Issue mở, không đánh dấu completed.
Không xóa branch/worktree hoặc dữ liệu local nếu chưa được giao dọn chúng.

Báo PR URL, merge commit, trạng thái Issue và việc còn lại. Không mở hướng mới.
```
