# 05 — Tác giả hoàn thiện và merge note

```text
Đọc AGENTS.md, CONTRIBUTING.md và research/AGENTS.md trước khi làm.

PR / SOURCES: <PR của đợt research và danh sách thư mục>
REVIEW: <kết luận review bước 04, findings đã xử lý và SHA đã review>

Tôi giao tác giả hoàn thiện và merge PR sau khi review độc lập bước 04 đạt và checks đạt.
Không cần họp nhóm hoặc một lượt đăng approval GitHub riêng.
PR dùng templates/research/pull_request.md; không dùng checklist compile thí nghiệm.

- Xác nhận branch/owner, working tree, HEAD và bằng chứng review bước 04 cho từng nguồn.
  Nếu còn findings chặn, sửa trong phạm vi rồi trả lại bước 04; chưa merge.
- So sánh SHA đã review với HEAD hiện tại. Nếu nội dung note, nguồn, metadata hoặc
  phạm vi PR thay đổi (kể cả xử lý conflict làm đổi nội dung), cần bước 04 review lại phần mới.
- Khi review đạt, ghi Status: ready, cập nhật trạng thái mục lục, commit/push và đưa PR
  khỏi draft. Chỉ đổi draft sang ready và đồng bộ trạng thái mục lục thì không cần review lại;
  ghi SHA đã review và HEAD cuối, xác nhận diff giữa hai mốc chỉ gồm thay đổi trạng thái đó.
- Xác minh source.json, phiên bản/hash, citation và mục lục khớp; mọi nguồn có note ready
  đã review. Không merge nguồn source_only, chỉ có PDF/link hoặc source.md thiếu note.md.
  Nếu còn nguồn chưa đủ điều kiện thì hoàn thiện và review trước merge; không tự xóa nguồn local.
- Chạy scripts/check_research_notes.py, checker, tests và scope --base/--branch;
  chờ CI đạt trên HEAD cuối. Tuân thủ rules GitHub thực tế: nếu rules yêu cầu approval,
  báo điều kiện còn thiếu; không tự approve, bypass hoặc thay cấu hình bảo vệ branch.
- Khi đủ điều kiện, tự merge bằng merge commit, xác nhận merged và đóng Issue liên quan
  nếu có và đã hoàn tất. Không cần xin lại quyền merge. Không tự xóa branch/worktree.

Nguồn chỉ trở thành đầu vào chuẩn khi note ready đã merge. Giữ đủ dòng mục lục nhóm.
Báo file/URL/SHA đã review, HEAD đã merge, các check và giới hạn; không sửa code/config/score/results.
Sau merge, khi được giao đợt tiếp theo thì đồng bộ main vào research/<username> bằng merge; không reset/force-push.
```
