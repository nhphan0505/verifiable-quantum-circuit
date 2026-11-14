# 06 — Hoàn thiện mô tả, checks và push

Áp dụng [workflow PP](README.md). Được hoàn thiện file của PP/dòng danh mục,
đồng bộ Issue, commit và push branch của owner. Không tự mở PR, review, merge,
đóng Issue hoặc áp dụng PP vào experiment khác.

## Yêu cầu

Cập nhật DESCRIPTION: cách tái chạy kiểm tra, nguồn/hash mạch đã dùng, commit
PP thực tế, tham số/profile, kết luận hypothesis, phạm vi hữu ích và giới hạn.
Giữ rõ phần dự đoán trước thử và kết luận sau thử. Không chép log/bảng điểm,
không thêm config hay run/results; số đo chấm báo trong chat. Giải thích không
lưu output chấm, do đó muốn xác nhận lại cần chạy lại, không dẫn link run giả.

Kiểm tra diff chỉ gồm postprocessing của phương pháp và dòng danh mục liên
quan. Kiểm tra link, tests, file tạm và việc experiment nguồn vẫn nguyên vẹn.
Chạy checks phù hợp theo [REPOSITORY_CHECKS](../../docs/REPOSITORY_CHECKS.md),
bao gồm checker repo, tests trong scripts/tests và diff scope nếu được hỗ trợ;
chạy thêm tests của PP. Nếu checker chưa hỗ trợ PP, báo lỗi thật và giới hạn,
không tự sửa checker hoặc thêm miễn trừ, không tuyên bố checks đạt.

Commit mô tả/code cần giữ và push đúng branch; không force-push làm mất commit
nguồn đã kiểm chứng. Cập nhật Issue bằng trạng thái bàn giao và commit đã push,
không chuyển completed hoặc đóng Issue chỉ vì push thành công.

Báo mã PP/Issue, branch/commit, file, lệnh kiểm tra thực tế, kết luận chấm và
giới hạn. Chỉ gọi bàn giao đã kiểm chứng khi có bằng chứng đúng phạm vi; nếu
còn lỗi/blocker thì ghi rõ, không dùng push thành công thay nghiệm thu kỹ thuật.

## Nghiệm thu

- [ ] DESCRIPTION khớp code, có cách kiểm chứng/kết luận/giới hạn, không có run giả.
- [ ] Tests/checks và diff đã kiểm tra, báo đúng các lỗi còn lại.
- [ ] Commit và push đã xác nhận bằng công cụ; experiment nguồn giữ nguyên.
- [ ] Dừng ở bàn giao. Review/PR/merge và cập nhật experiment chờ nhiệm vụ riêng.
