# 07 — Review PR (không sửa hoặc merge)

Áp dụng [quy tắc chung và ngữ cảnh](../README.md), AGENTS.md, CONTRIBUTING.md và
[workflow thử nghiệm](../../docs/EXPERIMENT_WORKFLOW.md).
Lấy thông tin từ chat/project/GitHub; không yêu cầu điền lại form.

## Ràng buộc và quyền thao tác

Reviewer dùng phiên agent riêng, checkout/worktree review riêng; chỉ đọc và chạy checks phù hợp, không sửa branch tác giả, đăng comment/review GitHub, merge hoặc đóng Issue.

## Yêu cầu thực hiện

Thực hiện bằng vai trò teammate reviewer, phiên agent riêng với tác giả. Đọc PR head
SHA trước khi review; cuối lượt ghi SHA đã kiểm tra cùng kết luận/findings.
Nếu HEAD đổi trong lúc review, nêu phần chưa kiểm tra của HEAD mới.

Thực hiện review PR này. Đọc diff, Issue, mô tả và kết quả thật; không chỉ
đọc báo cáo của agent tác giả. Kiểm tra phạm vi, nguồn kế thừa, điều kiện đúng,
sai số/uncompute/sửa pha, config, provenance và hash. Xác nhận điểm đúng mode,
profile và phép tính baseline/candidate; chỉ ra thiếu bằng chứng nếu có.

Kiểm tra link, artifact có lỡ vào Git, thay đổi hạ tầng/verifier ngoài phạm vi,
và việc giữ đủ các hướng trong bảng. Có thể chạy kiểm tra local cần thiết,
nhưng không mở hoặc tự chạy chấm thay thành viên.

Báo các lỗi cần sửa với file/dòng và ảnh hưởng, hoặc nói rõ không thấy lỗi
trong phạm vi đã kiểm tra; nêu kiểm tra chưa làm. Không tự sửa branch, đăng
comment/approve lên GitHub, merge hay đóng Issue. Đây là review trả về chat.
Nếu có findings, tác giả sửa và push rồi reviewer kiểm tra lại commit mới khi được giao.
Đăng kết luận lên GitHub là giai đoạn 07b, được giao bằng lệnh giao bước 07b.

## Danh sách nghiệm thu

- [ ] Đọc diff/Issue/code/results trực tiếp, kiểm tra thuật toán/sai số/provenance/hash/điểm và phạm vi.
- [ ] Findings có file/dòng, căn cứ và ảnh hưởng; ghi checks đã/chưa làm, SHA đã review và kết luận.
- [ ] Nếu HEAD thay đổi, nêu phần chưa review; kết luận chat chưa thay approval GitHub.
