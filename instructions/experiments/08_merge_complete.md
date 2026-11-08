# 08 — Merge và hoàn thành hướng

Áp dụng [quy tắc chung và ngữ cảnh](../README.md), AGENTS.md, CONTRIBUTING.md và
[workflow thử nghiệm](../../docs/EXPERIMENT_WORKFLOW.md).
Lấy thông tin từ chat/project/GitHub; không yêu cầu điền lại form.

## Ràng buộc và quyền thao tác

Tác giả chỉ xử lý PR/Issue của hướng được giao, trên branch đúng owner. Được sửa conflict đúng phạm vi, commit/push, merge commit khi đủ review/check và đóng Issue thực sự hoàn tất. Không bypass rule, squash/rebase, force-push hoặc xóa branch/worktree.

## Yêu cầu thực hiện

Thực hiện merge PR này và hoàn thành Issue nếu đúng phạm vi đã xong.
Bước này dành cho tác giả PR. Kiểm tra PR head, approval của teammate trên GitHub và
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

## Danh sách nghiệm thu

- [ ] Approval GitHub của teammate còn hiệu lực và đúng HEAD, mọi check/rule bắt buộc đạt.
- [ ] Nếu sửa conflict/đổi HEAD, đã có review và approval lại trước merge.
- [ ] PR thật đã merged bằng merge commit; báo merge SHA và Issue đóng hoặc còn mở đúng phạm vi.
