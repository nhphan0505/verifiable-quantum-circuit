# 03 — Tác giả tự kiểm tra và sửa note paper

Áp dụng [quy tắc chung](../README.md), [ràng buộc research](../research-common.md)
và yêu cầu nội dung [bước 2](02_read_source.md).

## Ràng buộc

Chỉ sửa note.md, source.json, bản nguồn bổ sung có phiên bản khi được giao và dòng
mục lục tương ứng trên `research/<username>` đúng owner, trong nguồn paper được giao.
Không ghi đè bản nguồn cũ, sửa experiment/hạ tầng, đặt ready, tự review độc lập hoặc merge.
Được commit/push và cập nhật draft PR. Bước này không thay bước 4.

## Yêu cầu

Nếu chưa có findings, tự đối chiếu note với nguồn, citation, công thức, giả định,
coverage/giới hạn và metadata/hash; sửa lỗi trong phạm vi. Nếu có findings, kiểm tra
từng lỗi với nguồn rồi sửa, báo rõ cách xử lý và mục còn mở. Nội dung đổi sau review
phải trở lại bước 4. Giữ Status: draft tới khi review độc lập đạt.
Chạy check_research_notes.py và checker phù hợp; commit/push bản đã rà, cập nhật PR
với danh sách nguồn, phạm vi đọc và chỗ cần reviewer chú ý, đủ ngữ cảnh cho phiên độc lập.

## Danh sách nghiệm thu

- [ ] Note và nguồn đã đối chiếu, citation/metadata/hash/coverage nhất quán.
- [ ] Findings có trạng thái xử lý rõ; không tuyên bố review độc lập đạt từ việc tự rà.
- [ ] Checks thực sự đã chạy được báo; commit/PR cập nhật, biết SHA cần review bước 4.
- [ ] Không đặt ready/merge; bàn giao phiên độc lập hoặc tiếp tục bước đã giao khi đúng vai trò.
