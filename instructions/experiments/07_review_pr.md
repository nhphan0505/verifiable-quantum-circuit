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

Đối chiếu implementation thực tế với thuật toán trong DESCRIPTION, không chỉ
kiểm tra cú pháp, thống kê cổng hoặc kết quả PASS. Lần theo từng bước chính từ
đầu vào đến đầu ra và các helper/config/data được gọi: công thức, thứ tự xử lý,
precision, điều kiện nhánh, cấp phát/cleanup, uncompute và sửa pha phải khớp mô tả.
Ghi vị trí code tương ứng và bằng chứng kiểm tra các invariant quan trọng; phân
biệt phần đã chứng minh, kiểm bằng test và chưa kiểm. Code khác thuật toán hoặc
mô tả khẳng định vượt bằng chứng là finding cần sửa; PASS không thay thế đối chiếu.

Kiểm tra khả năng người khác sử dụng: từ checkout sạch đúng SHA trên GitHub,
làm theo hướng dẫn trong repo để tạo venv, cài dependency pin, chạy entry point
với config đã track và tạo artifact mới. Không dựa vào file/cache máy tác giả,
chỉnh tay không được mô tả hoặc chạy stage riêng thay entry point. Kiểm tra đủ
source/helper/data, đường dẫn, lệnh setup/build và vị trí output; ghi lệnh,
environment, kết quả/hash hoặc blocker thực tế. Với decompiler, bắt buộc áp dụng
đầy đủ [nghiệm thu build sạch](../decompiler/06_build.md): mọi đầu vào dựng mạch
phải có trong repo, ngoài runtime/package đã khai báo. Thiếu file/hướng dẫn hoặc
entry point không chạy được là finding chặn khả năng tái lập, không ghi đã kiểm
chỉ dựa vào báo cáo tác giả. Không tự chạy grading để thay bước build này.

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
- [ ] Đối chiếu từng bước thuật toán với code/helper/config thực tế; ghi căn cứ và giới hạn.
- [ ] Tự build entry point từ checkout sạch bằng hướng dẫn repo; ghi lệnh, environment, hash hoặc blocker.
- [ ] Findings có file/dòng, căn cứ và ảnh hưởng; ghi checks đã/chưa làm, SHA đã review và kết luận.
- [ ] Nếu HEAD thay đổi, nêu phần chưa review; kết luận chat chưa thay approval GitHub.
