# Xử lý review PR #52

Review gốc: Reece1512, CHANGES_REQUESTED tại dcd8f5e3866ff1bd5b6ce5d60ddde1b879edf8d2.

1. Dependency: đã có link tải API version 12 cố định, tên invsqrt_source_zip, SHA-256 và kích thước. Tải lại không đăng nhập HTTP 200, hash khớp, đủ 560 file khớp manifest. Bỏ yêu cầu nguồn từ chat.
2. Public source: API dataset listing isPrivate=false, Apache 2.0; bằng chứng trong src/invsqrt/INV-51/evidence/public_source.json. Không kết luận thay về quy định cuộc thi.
3. Full: chưa có. Thành viên cần chấm notebook mode full hoặc profile độc lập. Không tự chạy verifier theo instructions decompiler bước 08.
4. DESCRIPTION: dùng đúng “Tái dựng từ submission” theo ngoại lệ được ghi rõ ở instructions/decompiler/04_claim.md; không nhận là ý tưởng mới. Đã bổ sung bảng lịch root/residual, D/H/seed/product, divider/phase, history debt và HMR correction, dẫn component source.
5. Provenance mới: code chuẩn hóa executable/lệnh sang POSIX tương đối root; build_only build_run=null. Đã build lại từ commit 4872943, bytes/hash vẫn exact. Không sửa provenance hay raw results cũ.
6. PR description: thay khẳng định diff-check toàn PR bằng kết quả checker/scope và ghi rõ raw logs CRLF gây cảnh báo whitespace khi diff base. Không normalize dữ liệu run.
7. Tùy chọn: giữ LICENSE/NOTICE gốc để bảo toàn attribution của release và bản .txt để fixture tests sao chép được. Không sửa hai provenance cũ để giảm metadata trùng.

Validation: tests 21/21 OK (82.193s); root-relative build_command test; independent byte comparison of rebuilt output. Checker/scope chạy lại sau hoàn thiện tài liệu. Chưa có approval cho HEAD mới.
