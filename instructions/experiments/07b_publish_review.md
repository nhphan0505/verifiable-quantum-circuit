# 07b — Teammate đăng kết luận review lên GitHub

Áp dụng [quy tắc chung và ngữ cảnh](../README.md), AGENTS.md, CONTRIBUTING.md và
[workflow thử nghiệm](../../docs/EXPERIMENT_WORKFLOW.md).
Lấy thông tin từ chat/project/GitHub; không yêu cầu điền lại form.

## Ràng buộc và quyền thao tác

Reviewer bằng tài khoản GitHub khác tác giả; chỉ được đăng review lên PR được giao. Không sửa branch tác giả, tự đổi tài khoản, merge hoặc đóng Issue.

## Yêu cầu thực hiện

Đăng kết luận review lên PR được giao bằng vai trò teammate reviewer. Kiểm tra
tài khoản GitHub đang dùng là của reviewer và khác tác giả PR; nếu sai tài
khoản hoặc thiếu quyền thì báo rõ, không tự đổi tài khoản để approve.

Đọc lại PR head, diff và bằng chứng review; không chỉ dựa vào lời tác giả rằng
đã sửa. Nếu HEAD khác SHA đã review, kiểm tra phần thay đổi và các findings
liên quan trên HEAD mới trước khi quyết định. Nếu thiếu ngữ cảnh review cũ,
thực hiện lại việc review theo bước 07. Ghi rõ SHA thực sự đã kiểm tra.

Chỉ đăng Approve khi các findings cần sửa đã giải quyết, bằng chứng đủ và
các check kỹ thuật bắt buộc của repository đã đạt trên phiên bản hiện tại.
Không coi yêu cầu approval đang thiếu là một check kỹ thuật thất bại.
Nếu còn lỗi cần tác giả sửa, đăng Request changes kèm file/dòng, ảnh hưởng
và bằng chứng cụ thể. Nếu chỉ đang chờ CI hoặc thiếu quyền/dữ liệu để kết
luận, báo điều kiện còn thiếu, chưa approve và không bịa findings.

Ngay trước khi đăng, đọc lại HEAD. Nếu thay đổi, kiểm tra phần mới trước.
Gắn review với đúng commit đã kiểm tra khi công cụ hỗ trợ; đọc lại review
đã đăng để xác nhận trạng thái, tài khoản và commit_id. Nếu HEAD đổi trong
lúc đăng, báo review chưa đủ cho HEAD mới và review lại phần thay đổi.
Nếu review phù hợp đã được đăng cho đúng SHA, báo URL thay vì đăng trùng.

Kết thúc báo URL review, SHA đã review, Approve/Request changes và việc còn
lại. Không sửa branch tác giả, tự resolve findings chưa kiểm chứng, merge
hoặc đóng Issue. Bước merge dành riêng cho tác giả khi được giao, sau review đạt.

## Danh sách nghiệm thu

- [ ] HEAD hiện tại đã review, findings được kiểm chứng; khi thiếu ngữ cảnh thì thực hiện lại bước 07.
- [ ] Approve chỉ khi đủ bằng chứng và check kỹ thuật bắt buộc đạt; Request changes có lỗi thực, chờ CI thì chưa approve.
- [ ] Đã đọc lại review URL/tài khoản/commit_id; không đăng trùng review phù hợp cho cùng SHA.
