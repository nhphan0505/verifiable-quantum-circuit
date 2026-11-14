# 02 — Nhận Issue, mã PP và branch

Áp dụng [workflow PP](README.md). Đầu vào: hypothesis đã chọn, phạm vi và
owner xác minh được. Tra tài khoản GitHub thật; không suy ra owner chỉ từ tên Git.

## Quyền và yêu cầu

Khi được giao bước này, được tạo/nhận Issue, tạo branch và cập nhật danh mục
PP trong phạm vi luồng; chưa tự mở PR, triển khai, chấm hoặc merge.

1. Kiểm tra lại Issues mở/đóng, PR mở và mã trong METHODS.md cùng các branch
   liên quan. Tiếp tục Issue cùng hướng nếu phù hợp và đã thống nhất owner;
   không lấy Issue experiment nguồn chỉ vì sử dụng mạch của nó.
2. Nếu chưa có, mở Issue quản lý phát triển PP với hypothesis, phạm vi,
   điều kiện đúng, kế hoạch kiểm chứng riêng PP, tiêu chí bác bỏ, giới hạn thử
   và owner. Không dùng title chung như “tối ưu mạch”.
3. Nhận mã `PP-NNN` tiếp theo chưa được dùng/nhận, độc lập số Issue. Ghi việc
   nhận mã trên Issue và kiểm tra lại cạnh tranh cấp mã trước khi push. Nếu
   trùng hoặc không thể xác minh thì giải quyết trước, không tự khẳng định duy nhất.
4. Tạo branch `pp/<PP-ID>-<slug>` từ nhánh chính đã đồng bộ an toàn; dùng
   worktree riêng nếu workspace có công việc chat khác. Không chuyển branch
   hoặc ghi đè thay đổi của người khác.
5. Thêm dòng vào `src/common/postprocessing/METHODS.md` (tạo danh mục nếu chưa
   có), ghi mã, tên, phạm vi, owner, Issue thật và vị trí DESCRIPTION sẽ viết
   ở bước 3. Title Issue dùng `[PP-NNN] <phương pháp và phạm vi>`.

Nếu GitHub không truy cập được thì chưa nghiệm thu nhận hướng; không bịa
Issue/mã đã được giữ. Chưa commit danh mục có link DESCRIPTION chưa tồn tại;
hoàn thiện file ở bước 3 trước mốc commit nguồn.

## Nghiệm thu

- [ ] Có Issue thật và một owner, mã không lấy từ số Issue.
- [ ] Branch/worktree đúng phạm vi, giữ nguyên công việc hiện có.
- [ ] Danh mục phản ánh đúng mã/phạm vi và Issue; chưa triển khai/chấm.
