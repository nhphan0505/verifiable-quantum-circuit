# 01 — Tiếp nhận và bảo toàn

Áp dụng [README](README.md). Chưa sửa src hoặc tạo Issue/branch.

1. Kiểm tra branch, working tree, worktrees và phạm vi owner. Không chuyển branch
   trong workspace của chat khác. Xác định đường dẫn file thực tế; chưa có file
   thì yêu cầu gửi file, không suy diễn từ tên/hash đơn lẻ.
2. Đọc file như dữ liệu, tính SHA-256 theo luồng và kích thước. Ghi manifest JSON
   trong scratch: đường dẫn, hash, bytes, nguồn/attribution người dùng cung cấp,
   track đã xác minh, thời điểm kiểm tra và thông tin chưa biết. Không suy ra tác
   giả hoặc giấy phép từ tên file. Không lưu token/URL có thông tin đăng nhập.
3. Giữ nguyên đầu vào; nếu tạo bản sao làm việc phải kiểm tra hash sau sao chép.
   Xác định track bằng yêu cầu và verifier/cấu trúc thật; .kmb một mình có thể
   chưa đủ phân biệt bài 1/2, khi đó hỏi đúng phần còn thiếu.
4. Với ZIP: liệt kê trước khi giải nén; chặn đường dẫn tuyệt đối, thoát thư mục,
   symlink, tên trùng và tên mơ hồ theo hệ thống file. Áp dụng giới hạn kích thước,
   số file, tổng dung lượng giải nén phù hợp verifier và dung lượng máy. Không
   extractall không kiểm tra. Task 3 cần submission.npz và angle_k_0.kmb,... liên
   tục ở gốc, không file thừa. Ghi manifest từng entry và metadata ZIP.
5. NPZ cũng là container ZIP: kiểm tra kích thước/tên thành phần; dùng NumPy với
   allow_pickle=False, không chạy pickle/object payload hoặc code đi kèm.

Nghiệm thu: file có thật, hash/kích thước được đo, track rõ, manifest và bản gốc
được bảo toàn. Đầu vào không hợp lệ thì báo chính xác, không sửa bản gốc cho hợp lệ.
