# 09 — Review và hoàn tất

Áp dụng [experiments 06](../experiments/06_prepare_pr.md),
[07](../experiments/07_review_pr.md), [07b](../experiments/07b_publish_review.md)
và [08](../experiments/08_merge_complete.md), cùng
[REPOSITORY_CHECKS](../../docs/REPOSITORY_CHECKS.md).

Giao bước 9 cho tác giả cấp quyền chuẩn bị PR, commit/push sửa trong phạm vi và
merge sau review/check thật; không cấp quyền tự review hoặc đăng approval bằng
tài khoản khác. Reviewer nhận phần review riêng, dùng phiên độc lập và tài khoản
GitHub khác tác giả. Nếu chỉ được giao review thì không tự merge. Không có reviewer
thì bàn giao trạng thái chờ, không tự đóng vai reviewer để vượt điều kiện.

Trước PR chạy checker, unittest và diff scope theo tài liệu repo. PR nêu mục tiêu
tái dựng, mức exact đạt/chưa đạt, source/hash, dependency, provenance và giới hạn
thuật toán. Không lấy CI/checker làm bằng chứng hiểu mạch hoặc full verification.

Reviewer kiểm tra thêm: nguồn và attribution, code thực sự dựng mạch, dependency
đủ và không dùng binary gốc ngầm, dữ liệu góc không bị làm tròn, hash toàn container
so với từng thành phần, SHA nguồn đúng build, hypothesis không bị nhận thành sự
thật và results không bị sửa. Head thay đổi thì review lại theo quy tắc repo.

Chỉ merge commit khi đủ quyền, approval/check trên HEAD hiện tại và không conflict.
Nếu exact không đạt, có thể bàn giao findings nhưng không đóng Issue là hoàn tất
mục tiêu exact; chỉ hoàn tất phạm vi khác khi người dùng đã chấp thuận rõ. Giữ
Issue mở cho phần còn lại. Không bypass GitHub hoặc đổi cách merge.

Nghiệm thu: báo URL PR/Issue, commit merge thật nếu đã merge, checks/review và phần
còn thiếu. Nếu chờ chấm/reviewer/check, nêu rõ trạng thái thay vì báo hoàn tất.
