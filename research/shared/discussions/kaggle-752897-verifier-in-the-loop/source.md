# Kaggle discussion 752897

- Bài đăng của [manwithacat](https://www.kaggle.com/manwithacat), ngày 27/10/2026 theo giờ Việt Nam.
- [Permalink bài đăng](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/752897)
- Snapshot ngày 08/11/2026. Trang hiển thị 0 bình luận.
- Bản chụp diễn giải các mục của bài đăng bằng tiếng Việt. Số liệu và nhận định dưới đây do tác giả bài đăng nêu. Paper, notebook, mã và artifact được nhắc đến nằm ngoài phạm vi snapshot.

## Thiết kế và các ví dụ công khai

Tác giả xem verifier chạy nhanh là nền tảng cho vòng lặp chỉnh bộ sinh, dựng mạch, kiểm chứng, đo chi phí rồi giữ hoặc loại ứng viên. Tác giả dẫn arXiv:2610.23832 khi mô tả logic cổ điển khả nghịch, pha và uncompute qua phép đo, và nhắc đến ecdsa.fail như tiền lệ tối ưu Toffoli với coding agent.

Ví dụ công khai gồm bộ giải mã Schur của jday96314 và kết quả tìm mạch độc lập trong arXiv:2610.22367, thay đổi gauge hóa học trong notebook của Alex Chilton, và chuỗi thay đổi cấp phát/uncompute của mrmeows cho invsqrt. Tác giả nêu một ví dụ fit hóa học 8 bit dùng trainer GPU với (R, B, C) = (10, 129, 60).

## Tình hình từng bài theo tác giả

- **Invsqrt.** Mốc được nêu là 63 qubit, khoảng 1.400 Toffoli và 19,1× so với reference. Kiến trúc đã dùng 95–99% ngân sách sai số. Newton, đoạn bậc ba, các độ rộng bảng khác và đổi cách gán thanh ghi được báo cáo là không cải thiện. Tính trực tiếp bit pha theo x là hướng còn bỏ ngỏ theo bài viết.
- **DQI.** Tác giả mô tả chuyển từ Berlekamp–Massey sang continued fractions rồi Schur, sweep Forney chỉ ghi pha với khoảng 11 Toffoli mỗi điểm thay cho 80–85, và giảm 892 xuống 883 qubit. Bài đăng nêu 840 qubit syndrome, bước reverse tốn thêm khoảng 31 Toffoli mỗi cặp nút so với forward và bộ nhân GF(2¹²) có rank 42. Các nhận định về cận tài nguyên gắn với triển khai được bàn.
- **Hóa học.** Mốc được nêu là 7,7× ở 415 qubit. Tác giả mô tả giảm mạnh workspace ở 8 bit góc và thêm một ngưỡng ở 7 bit. Làm tròn trực tiếp từ fit 10 bit xuống 8 bit cho khoảng 111 mHa so với ngưỡng 20 mHa. Làm tròn theo độ nhạy tuyến tính hóa, huấn luyện có xét lượng tử hóa và thu nhỏ từ điển là các hướng tác giả dẫn lại. Ví dụ B = 255 được báo cáo dừng ở 48 mHa.

## Thực hành và kết quả âm

Tác giả khuyên kiểm chứng local để giảm vòng chờ và dùng đủ 102.400 shots khi so điểm DQI do cận tin cậy ảnh hưởng hệ số lặp. Tác giả báo cáo đổi một tham số của reference cho cải thiện dưới 2%, bước gradient/gauge khi giữ word góc có biên độ nhỏ, và cắt từ điển ở 10–11 bit với R = 1 dừng khoảng 20,5–22 mHa. Tác giả nhận định thêm một bank thanh ghi khó có lợi dưới hệ số Q². Bài đăng mời đính chính và giao diện không hiển thị phản hồi.
