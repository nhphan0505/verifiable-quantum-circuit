# 01 — Nhận discussion vào branch research cá nhân

Áp dụng [quy tắc chung](../README.md), [ràng buộc research](../research-common.md)
và [quy chuẩn nguồn](../../research/README.md).

## Ràng buộc

Chỉ tạo/tiếp tục `research/<username>` đúng owner, sửa
`research/<TRACK>/discussions/<topic-slug>/` được giao và dòng mục lục discussion liên quan.
Được commit/push, mở/cập nhật draft PR; Issue tài liệu tùy chọn. Không viết note sâu,
sửa paper/experiment/hạ tầng, chạy chấm hoặc merge. Không lấy DOI/arXiv của paper
được thảo luận làm identity của discussion.

## Yêu cầu

Xác định thread/URL/file/snapshot và câu hỏi từ chat; nếu chưa có nguồn hoặc có nhiều
thread chưa rõ, hỏi đúng phần thiếu. Kiểm tra owner/branch/working tree, mục lục,
Issues mở/đóng và PR mở tránh trùng. Tự chọn track theo liên hệ với bài/verifier/baseline
nếu chưa chỉ định; nhiều track thì shared, không nhân bản. Tôn trọng track đã giao.

Lưu `source.md` là snapshot đúng phần discussion được giao/đã truy cập, có URL,
ngày truy cập, permalink/comment ID và bối cảnh; nguồn nội bộ ghi người cung cấp.
Nếu đầu vào là PDF chụp discussion, giữ PDF nguyên bytes làm source_file và lưu
source.md cho bối cảnh/snapshot phần văn bản đọc được, không tự tìm bản thay thế.
Chỉ chép nội dung trong phạm vi và được phép; không lưu credential hoặc dữ liệu riêng
ngoài nhiệm vụ. Ghi thiếu bối cảnh/phần không truy cập thay vì tạo phát biểu giả.

Đặt topic-slug rõ nội dung, tạo source.json với `kind: discussions`, URL/phiên bản/ngày
truy cập/coverage và hash file thật; source_file trỏ bản nguồn chính cùng thư mục.
Không ghi đè snapshot cũ đã được dẫn; bản mới lưu có phiên bản. Cập nhật mục lục
source_only, commit/push, tạo/cập nhật draft PR. CI thiếu note ở bước này là dự kiến,
không tạo note placeholder để merge.

## Danh sách nghiệm thu

- [ ] Đúng owner/branch, thread/phạm vi/track/topic-slug rõ, đã kiểm tra trùng.
- [ ] Snapshot có bối cảnh, URL/comment/ngày hoặc người cung cấp; PDF gốc giữ nguyên nếu có.
- [ ] source.json đúng loại/phiên bản/coverage/hash; mục lục source_only và draft PR thật.
- [ ] Báo đường dẫn/hash/commit/PR/giới hạn; bước 2 đã giao thì tiếp tục, chưa merge.
