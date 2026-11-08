# 01 — Nhận paper vào branch research cá nhân

Áp dụng [quy tắc chung](../README.md), [ràng buộc research](../research-common.md)
và [quy chuẩn PAPER_ID](../../research/README.md).

## Ràng buộc

Chỉ tạo/tiếp tục `research/<username>` đúng owner, sửa
`research/<TRACK>/papers/<PAPER_ID>/` của nguồn được giao và dòng mục lục paper liên quan.
Được commit/push và mở/cập nhật draft PR; Issue tài liệu tùy chọn. Không viết note sâu,
compile/chấm, sửa discussion/thí nghiệm/hạ tầng hoặc merge. Giữ nguyên bản PDF được giao.

## Yêu cầu

Xác định nguồn từ file đính kèm/local hoặc URL đã giao trong chat; thiếu nguồn thì hỏi.
Kiểm tra branch/owner/working tree, mục lục, Issues mở/đóng và PR mở để tránh trùng.
Không yêu cầu điền OWNER/TRACK nếu đã biết. Nếu track chưa chỉ định, đọc lướt title,
abstract/mục lục và phần cần thiết, đối chiếu mô tả bài/verifier/baseline để tự chọn
invsqrt/dqi/dfthcsos/shared. Nhiều track dùng chung thì đặt shared, không copy nhiều lần.
Nếu chưa chắc thì shared và nêu giới hạn; không tự đổi track người dùng đã chọn.

Phân biệt paper với bản chụp discussion theo nội dung; nếu là discussion thì báo và
dùng chuỗi discussions, không gán DOI/arXiv paper được thảo luận cho discussion.
Từ đúng PDF được giao, lấy title/tác giả/arXiv/DOI/phiên bản; không tìm bản khác hoặc
bổ sung metadata ngoài khi chỉ được giao file. Thiếu mã đặt folder thì hỏi, không lấy
mã tài liệu trích dẫn. PAPER_ID theo research/README.md, ưu tiên arXiv.

Copy nguyên bytes vào `research/<TRACK>/papers/<PAPER_ID>/paper.pdf`, đối chiếu SHA-256
bản gốc/copy; không ghi đè bản khác đã có. File từ 10 MiB giữ ngoài Git và báo giới hạn;
không tự tìm link thay thế. Tạo source.json theo schema, chỉ ghi thông tin có căn cứ;
source_url có thể null khi PDF không có URL. Coverage chỉ gồm phần đã xem để định danh.
Cập nhật mục lục source_only, commit/push và tạo/cập nhật draft PR của đợt research.
CI thiếu note ở bước này là dự kiến, chưa đủ điều kiện merge; không tạo note placeholder.
Trường `kind` trong source.json là `papers`, đúng schema và tên thư mục loại nguồn.

## Danh sách nghiệm thu

- [ ] Đúng owner/branch, không trùng nguồn; nguồn/track/PAPER_ID có căn cứ.
- [ ] Bản gốc/copy khớp SHA-256, phiên bản và source.json đúng; file lớn không vào Git.
- [ ] Mục lục source_only và draft PR thật được cập nhật, có commit/URL/hash/đường dẫn.
- [ ] Chưa merge; nếu bước 2 đã được giao thì tiếp tục đọc, không hỏi lại quyền.
