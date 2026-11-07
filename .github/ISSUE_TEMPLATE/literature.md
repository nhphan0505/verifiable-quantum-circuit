---
name: Read a paper or discussion
about: Nhận một nguồn để tạo note cho agent nghiên cứu
title: "[LIT] <track>: <nguồn + phạm vi đọc>"
labels: ""
assignees: ""
---

Sau khi có số Issue thật, đổi title thành `[LIT-<số>] <track>: <nguồn + phạm vi>`.

- Owner:
- Track: invsqrt / dqi / dfthcsos / shared
- Loại: papers / discussions
- SOURCE_ID và thư mục:
- DOI/arXiv/URL hoặc file nguồn:
- Phiên bản / ngày snapshot:
- Phạm vi cần đọc, phần chưa đọc:
- Nguồn/note tương tự đã kiểm tra để tránh trùng:
- Branch / draft PR:

Issue này là tùy chọn; branch research/<username> có thể chứa nhiều nguồn/Issue.
Đầu ra: note.md có căn cứ và source.json; paper.pdf hoặc source.md nếu lưu local.
Trình tự: source_only → draft → review độc lập → sửa → ready → review/approval
HEAD cuối → nhóm họp và giao merge. Chỉ sau merge mới dùng làm đầu vào nghiên cứu chuẩn.
Không sửa implementation/config/score/results trong Issue tài liệu.
