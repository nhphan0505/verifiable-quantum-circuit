# 07 — Review PR (không sửa hoặc merge)

```text
Đọc AGENTS.md và CONTRIBUTING.md trước khi làm.

PR: <URL>

Tôi là teammate reviewer, dùng phiên agent riêng với tác giả. Đọc PR head
SHA trước khi review; cuối lượt ghi SHA đã kiểm tra cùng kết luận/findings.
Nếu HEAD đổi trong lúc review, nêu phần chưa kiểm tra của HEAD mới.

Tôi giao bạn review PR này. Đọc diff, Issue, mô tả và kết quả thật; không chỉ
đọc báo cáo của agent tác giả. Kiểm tra phạm vi, nguồn kế thừa, điều kiện đúng,
sai số/uncompute/sửa pha, config, provenance và hash. Xác nhận điểm đúng mode,
profile và phép tính baseline/candidate; chỉ ra thiếu bằng chứng nếu có.

Kiểm tra link, artifact có lỡ vào Git, thay đổi hạ tầng/verifier ngoài phạm vi,
và việc giữ đủ các hướng trong bảng. Có thể chạy kiểm tra local cần thiết,
nhưng không mở hoặc tự chạy chấm thay thành viên.

Báo các lỗi cần sửa với file/dòng và ảnh hưởng, hoặc nói rõ không thấy lỗi
trong phạm vi đã kiểm tra; nêu kiểm tra chưa làm. Không tự sửa branch, đăng
comment/approve lên GitHub, merge hay đóng Issue. Đây là review trả về chat.
Nếu có findings, tác giả sửa và push rồi tôi giao review lại trên commit mới.
Đăng kết luận lên GitHub là giai đoạn 07b, được giao bằng prompt riêng.
```
