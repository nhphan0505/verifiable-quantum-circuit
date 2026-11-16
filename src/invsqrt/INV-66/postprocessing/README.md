# INV-66 postprocessing: dead-write HMR/CZ

Module riêng của INV-66, được bàn giao cùng PR67. Kế thừa implementation PP-005
của Cheemshoang tại commit 1298d954ef9e06a552edf9e8f38e040e3efe97f8,
SHA-256 28de23f261438791a871f0210e0ebe00bf2951eb635223dbc63104a61b4567ff.
Nguồn phép sửa: asteriospanoras qua walkthrough mizeroluckygall; xem ../NOTICE.txt.
Đây là tích hợp phục vụ exact reconstruction, không đăng ký method dùng chung mới.

`rewrite(circuit, operation_index=3292)` thay đúng một CCX vào target không
được đụng tới cho đến HMR bằng HMR sớm và CZ có điều kiện ở vị trí CCX cũ.
Đẳng thức branch operator `<m_X|X = (-1)^m <m_X|` đúng cả với target entangled;
không cần giả định target zero. Guard từ chối condition stack, metadata/debug
barrier, instruction chưa biết, target bị dùng giữa hai endpoint hoặc measurement
bit bị đọc/ghi. API không tự thực hiện I/O và không gọi PP khác.

13 semantic/guard tests ở ../tests/test_postprocessing.py so toàn bộ Kraus matrices
cho cả outcome. Các lượt smoke riêng PP ở source cũ là bằng chứng lịch sử mô tả
trong [PP-005 tại commit d2dded7](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/d2dded7ffeccefbb593ed08e2e2a3557c8d158b9/src/invsqrt/postprocessing/PP-005/DESCRIPTION.md),
không phải lượt chấm mới cho source sau khi di chuyển. Build INV-66 cần kiểm
exact hash riêng; không chuyển provenance lịch sử sang commit hiện tại.
