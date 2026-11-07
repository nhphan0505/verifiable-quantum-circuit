# 05 — Hoàn thiện và xuất bản note

```text
Đọc AGENTS.md, CONTRIBUTING.md và research/AGENTS.md trước khi làm.

PR / SOURCES: <PR của đợt research và danh sách thư mục>
QUYẾT ĐỊNH NHÓM: <chưa họp | nguồn được chọn sau họp; bắt buộc khi giao merge>
VAI TRÒ: <author_prepare | reviewer_publish | author_merge>
REVIEW: <findings/SHA hoặc URL review nếu có>

Tôi giao đúng vai trò đã chọn, không tự chuyển sang vai trò khác.
PR dùng templates/research/pull_request.md; không dùng checklist compile thí nghiệm.
- author_prepare: sửa findings thuộc phạm vi, ghi Status: ready chỉ khi đã xử lý hết
  lỗi chặn; ready trên branch chưa phải đã xuất bản. Cập nhật mục lục, commit/push,
  chạy scripts/check_research_notes.py, check diff và tests, đưa PR khỏi draft; dừng chờ review của HEAD cuối.
- reviewer_publish: dùng tài khoản khác tác giả, đối chiếu nguồn và review lại mọi
  thay đổi từ SHA đã đọc đến HEAD hiện tại (kể cả đổi trạng thái/conflict). Chỉ approve
  khi không còn lỗi chặn và checks đạt; nếu không đăng Request changes có căn cứ.
  Đăng review gắn đúng commit và đọc lại URL/SHA. Không merge.
- author_merge: xác minh approval thật trên HEAD hiện tại, checks/rules đạt, note ready,
  source.json và mục lục khớp cho từng note. Bắt buộc có quyết định nhóm do người dùng
  cung cấp và quyền merge rõ ràng; chưa có thì dừng chờ nhóm họp. Chỉ merge nội dung
  được nhóm chọn; nếu cần chỉnh phạm vi PR, commit rồi review lại HEAD trước merge.
  Không merge nguồn source_only, chỉ có PDF/link hoặc source.md thiếu note.md.
  Nếu còn nguồn chưa viết note thì tiếp tục hoàn thiện hoặc tách khỏi PR theo quyết định nhóm;
  không tự xóa bản nguồn local. Merge commit,
  xác nhận merged; đóng Issue liên quan nếu có và đã hoàn tất.
  HEAD đổi thì quay lại reviewer_publish; không bypass hoặc tự approve.
Nguồn chỉ trở thành đầu vào chuẩn khi note ready đã merge. Giữ đủ dòng mục lục nhóm.
Báo file/URL/SHA, các check và việc còn lại; không sửa code/config/score/results.
Sau merge, khi được giao đợt tiếp theo thì đồng bộ main vào research/<username> bằng merge; không reset/force-push.
```
