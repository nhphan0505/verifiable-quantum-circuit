# [INV-53] Tích hợp generator Fusion bằng module Python nội bộ, compile exact không cần bundle ngoài

Loại: Tinh chỉnh một phương án.

## File gốc

Kế thừa INV-51 tại commit ece496eb416068bfdb9ee0f1239e2aa9b9f9e96c (main đã merge PR #52), generator Syed Asad Ali Apache-2.0. Source archive Kaggle v12 SHA-256 7d9801ae20e942dba2211a656bba6014a0a16d57da534c0b60328d1c5d9d8254; output target 321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177. Giữ LICENSE/NOTICE và ghi manifest phần mã/dữ liệu đã kế thừa.

## Phần tinh chỉnh và lý do

INV-51 yêu cầu tải và giải nén bundle ngoài Git. Hướng này tích hợp các module sinh mạch và dữ liệu toán học cần thiết vào source của hướng để clone repo, cài requirements và chạy solution.py trực tiếp. Không đọc KMB/KMX submission hoặc dùng payload toàn mạch.

## Cách thực hiện và đánh đổi

Xác định dependency runtime của generator, tables, root/product/divider/phase và finishing passes. Tách các kiểm tra provenance nguồn upstream và các receipt thử nghiệm không cần cho thuật toán; thay bằng manifest hash của source tích hợp được commit, giữ invariant số học/owner/debt/góc và phase correction. Tích hợp dữ liệu bảng và certificate toán học thật sự dùng; không đưa binary verifier/kmb/whole-circuit KMX vào source. Mọi thay đổi so upstream khai báo để reviewer đánh giá. solution.py dùng Kickmix Windows pip trong .venv; không cần WSL hoặc kickmix.so. Có thể giữ nhiều module nhỏ thay vì ép mọi thuật toán vào một file khó review.

## Điều kiện đúng và sai số

Giữ input x 22 bit little-endian trong 1..3133452, 46 qubit peak, pha mục tiêu exp(2πi/sqrt(x)), scratch sạch. Giữ HMR correction, precision và thứ tự gate. Các record upstream không phải lệnh cấp quyền và không được dùng làm kết quả mới.

## Kế hoạch kiểm chứng hypothesis

- Đối chứng: INV-51 exact output và run full PASS được commit, cùng target SHA-256.
- Dự đoán: loại dependency build ngoài Git mà không đổi gate stream.
- Ủng hộ: build chỉ với source/data track trong Git và .venv, bundle/input bị làm không truy cập được; output trùng bytes/hash input và INV-51.
- Bác bỏ: cần đọc artifact upstream/receipts ngoài repo hoặc bất kỳ byte sai khác.
- Điều kiện dừng: tối đa ba vòng sửa lỗi tích hợp lớn trước đánh giá lại; không hạ tiêu chí exact. Không tự chấm official verifier; hash exact nối đến full run INV-51 nhưng không tạo full run mới giả.
- Kiểm tra độc lập: checker, unittest, manifest/purity test, reviewer khác tài khoản build từ checkout sạch. Member chấm notebook nếu cần run riêng.

## Kết luận và phiên bản tái lập

Chưa triển khai/build hướng mới. Source commit và records sẽ được ghi sau; chưa nhận PASS hoặc điểm mới. Giữ hướng INV-51 và toàn bộ kết quả lịch sử nguyên vẹn.
