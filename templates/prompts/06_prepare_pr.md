# 06 — Tổng kết hướng và chuẩn bị PR

```text
Đọc AGENTS.md và CONTRIBUTING.md trước khi làm.

TRACK: <bài>
EXPERIMENT_ID: <ID>
ISSUE: <URL>
BRANCH: <branch>
KẾT LUẬN CỦA THÀNH VIÊN: <đã thử đủ / dừng vì không hiệu quả / bàn giao một phần>

Tôi giao bạn tổng kết, commit phần hoàn thiện, push và tạo/cập nhật PR để review.
Rà code, docstring, config, DESCRIPTION, mục lục, score và results/provenance;
kiểm tra link và điểm khớp JSON. Đối chiếu kế hoạch kiểm chứng/điều kiện dừng;
ghi config/run tốt nhất của từng mode với SHA nguồn/provenance. Nêu kiểm tra
bổ sung độc lập hoặc full đã có cho ứng viên cuối; nếu chưa có, ghi giới hạn
và không khẳng định chất lượng đã được xác nhận đầy đủ. Giữ cả kết quả âm và giới hạn còn lại.

Đồng bộ nhánh chính bằng merge vào branch thử nghiệm; giữ nguyên các SHA
nguồn đã được run tham chiếu, không rebase/amend các commit đó.
Xử lý conflict của dòng hướng này, giữ đủ hướng khác; không dùng toàn bộ
"ours/theirs" để bỏ mất dữ liệu nhóm. Không force-push nhánh chính.

Viết PR theo mẫu, mô tả giải pháp cuối, hai commit nguồn/kết quả liên quan,
config/run tốt nhất, cách tái lập và giới hạn. Hướng thực sự hoàn tất dùng
Closes #<số>; nếu chỉ bàn giao một phần thì liên kết Issue nhưng không tự đóng.
Chạy scripts/check_repo.py, bộ test scripts/tests và kiểm tra diff --base/--branch
theo docs/REPOSITORY_CHECKS.md; sửa lỗi thuộc phạm vi trước khi báo PR sẵn sàng.

Đưa PR khỏi draft nếu sẵn sàng review. Không tự approve, merge hoặc đóng Issue
ở giai đoạn này. Báo PR URL, check đã chạy và nội dung cần reviewer xem.
Cuối lượt liệt kê file thực sự đã tạo/sửa kèm link thật để tôi kiểm tra thủ công.

```
