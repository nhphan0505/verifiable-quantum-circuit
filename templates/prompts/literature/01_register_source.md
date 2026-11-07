# 01 — Thêm nguồn vào branch research cá nhân

```text
Đọc AGENTS.md, CONTRIBUTING.md và research/AGENTS.md trước khi làm.

OWNER: <GitHub username>
TRACK: <invsqrt | dqi | dfthcsos | shared | agent tự chọn>

Tôi gửi kèm PDF trong tin nhắn này; dùng chính file đính kèm làm nguồn.
Không yêu cầu tôi cung cấp link, không tìm hoặc tải một bản khác trên mạng.

Tôi giao thêm resource vào branch research/<OWNER>. Kiểm tra working tree, owner,
branch và PR đang mở. Khi workspace an toàn, tạo branch cá nhân từ main đã đồng bộ
nếu chưa có; nếu đã có thì tiếp tục đúng branch, không reset công việc cũ.
Dùng workspace/worktree riêng khi experiment đang làm ở workspace khác.
Kiểm tra mục lục/PR/Issues để tránh trùng nguồn; không bắt buộc tạo Issue từng nguồn.
Nếu có nhiều PDF, xử lý từng file; dùng track tôi đã chỉ định cho từng nguồn nếu có.
Nếu TRACK là "agent tự chọn" hoặc để trống, tự chọn invsqrt/dqi/dfthcsos/shared.
Nếu tôi chọn track cụ thể thì dùng track đó; nếu thấy không phù hợp, báo căn cứ
và đề xuất thay vì tự đổi lựa chọn của tôi. Khi tự chọn, đọc lướt title,
abstract, mục lục và phần cần thiết; đối chiếu mô tả bài/verifier/baseline để phân loại.
Ưu tiên track có liên hệ trực tiếp rõ nhất; nguồn phục vụ nhiều bài hoặc kỹ thuật
chung đặt shared, không copy một nguồn vào nhiều track. Nếu chưa đủ căn cứ phân
loại cụ thể, tạm đặt shared và ghi rõ chưa chắc chắn. Không hỏi tôi chọn track khi
có thể tự quyết định; báo lựa chọn, căn cứ và mức độ chắc chắn khi bàn giao.
Phân biệt paper với bản chụp discussion theo nội dung, không chỉ phần mở rộng PDF;
nếu là discussion dùng discussions/<topic-slug>/ và ghi metadata đúng loại nguồn,
giữ PDF gốc làm source_file. Không tự gán DOI/arXiv của paper được thảo luận cho
chính discussion. Đề xuất bước 02 cho paper hoặc 03 cho discussion tương ứng.
Đọc metadata/trang đầu và phần cần thiết để xác định title, tác giả, DOI/arXiv
và phiên bản từ PDF. Không tìm nguồn ngoài để bổ sung metadata. Với paper, nếu không
xác định được mã cần thiết để đặt folder, báo phần thiếu; không tự bịa mã hoặc dùng nhầm
DOI/arXiv của tài liệu được paper trích dẫn.
Copy nguyên PDF vào research/<TRACK>/papers/<PAPER_ID>/paper.pdf (hoặc thư mục
discussion đã xác định) theo quy chuẩn; đối chiếu
SHA-256 file đính kèm và bản copy. Không chỉnh sửa PDF hoặc ghi đè bản khác đã có.
File từ 10 MiB trở lên giữ ngoài Git và báo giới hạn; không tự tìm link thay thế.
Chưa viết note hoặc đọc sâu. Tạo source.json với thông tin xác định được; source_file
là tên PDF đã lưu, source_sha256 là hash thật. source_url có thể null khi không có URL
trong file; không bịa URL. Ghi coverage đúng phần đã xem để định danh/phân loại,
chưa phân tích sâu. Cập nhật mục lục source_only. Commit/push phần hợp lệ, tạo hoặc cập nhật
draft PR; báo rõ CI thiếu note.md là dự kiến ở bước này, chưa đủ điều kiện merge.
Báo branch, PR, danh sách đường dẫn/hash. Không sửa experiment hoặc tự merge.
Dừng chờ giao đọc nguồn bằng 02/03; nhóm sẽ họp quyết định merge đợt research sau.
```
