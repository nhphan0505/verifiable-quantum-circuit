# 02 — Chuyển đổi KMB/KMX và đối chiếu

Đầu vào: [bước 1](01_receive.md) đạt. Chỉ ghi scratch, chưa build solution.

1. Xác minh Python và phiên bản package bằng importlib.metadata theo requirements
   của repo; không tự nâng cấp. Tham khảo API/tài liệu chính thức Kickmix phù hợp
   phiên bản, không đoán cú pháp từ tên lệnh.
2. Dùng km.Circuit.from_file(path, format='kmb'), rồi to_file(..., format='kmb')
   để kiểm tra đường trực tiếp. Dùng to_file(..., format='kmx') và đọc KMX rồi
   ghi KMB để kiểm tra đường qua text. Mọi output dùng tên mới.
3. So bytes theo luồng và SHA-256 với bản gốc cho cả hai đường; lưu lệnh, phiên
   bản, đường dẫn, kích thước, hash, kết quả và lỗi thật trong báo cáo JSON mới.
   Không coi Circuit equality hoặc số cổng bằng nhau là bytes bằng nhau.
4. Giữ nguyên độ chính xác góc quay, thứ tự lệnh, bit/qubit, thanh ghi, tên và
   INFO_TAG. Không chuyển góc sang float hoặc chuẩn hóa/lược bỏ lệnh tùy ý.
5. Nếu khác: xác định byte/khối khác đầu tiên, kiểm tra serializer/version,
   registers, angles và metadata. Không tự vá file output bằng bytes gốc để gọi
   là tái dựng. Nếu KMX làm mất thông tin, dùng đường dữ liệu chính xác từ KMB
   hoặc parser theo đặc tả có kiểm chứng; ghi rõ phần phải tránh trung gian KMX.
6. Với task 3 chạy cho từng KMB; ghi hash NPZ, hash từng NPY bên trong và mô tả
   mảng (key, dtype kể cả byte order, shape, order). Nếu hash dữ liệu mảng, khai
   báo cách canonicalize; hash đó không thay thế hash bytes NPY/NPZ.

KMX có thể rất lớn: kiểm tra dung lượng trước, phân tích theo khối, không đổ toàn
bộ vào chat. Đọc bản gốc bằng công cụ thư viện, không tự thực thi nội dung file.

Nghiệm thu: báo cáo từng file và kết luận ROUNDTRIP_EXACT hoặc lỗi/sai khác.
Chỉ chuyển tới triển khai exact khi có phương án bảo toàn dữ liệu đã kiểm chứng;
có thể tiếp tục phân tích độc lập nhưng không hạ tiêu chí để vượt bước này.
