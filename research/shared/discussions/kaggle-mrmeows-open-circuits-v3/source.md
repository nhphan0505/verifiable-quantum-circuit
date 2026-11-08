# QCC 14.50 | Everything I learned + open circuits

mrmeows, v3, scriptVersionId 362387953. Kaggle hiển thị ngày 26/10/2026 theo giờ Việt Nam. Truy cập 08/11/2026. Snapshot diễn giải các ô Markdown. [Notebook v3](https://www.kaggle.com/code/mrmeows/qcc-14-50-everything-i-learned-open-circuits?scriptVersionId=362387953)

## Mục đích và kết quả

Tác giả công bố mạch, phương pháp, các thử nghiệm âm và những cận tìm được để người đọc có thể tập trung vào kiến trúc mới. Markdown nêu điểm public 14,49721 và cho biết các chi phí bên dưới được đo trên đúng bytes của bộ mạch công bố, với verifier chính thức và số shot mặc định đầy đủ.

| Bài | Phương án | Qubit | Toffoli trung bình | Chi phí | Tỉ số |
| --- | --- | ---: | ---: | ---: | ---: |
| Invsqrt | Bản tái bố trí workspace 68 qubit | 68 | 1.448,1 | 120.219,30 | 17,27 |
| DQI | Gluzdov round12 | 881 | 964.394 | 8,917 × 10¹¹ | 27,41 |
| DFTHCSOS | Word góc 8 bit, R = 4, B = 303, C = 128 | 448 | 23.500 | 5,214 × 10⁸ | 6,435 |

## DFTHCSOS

Với factorization cố định, tập địa chỉ hợp lệ 0…875 đóng dưới phép lấy tập con bit. Tác giả biểu diễn từng bit đầu ra bằng XOR của các đơn thức bit địa chỉ. Phiên bản lookup ban đầu cần 865 Toffoli mỗi mạch, xóa tích bằng đo X và hiệu chỉnh pha. Loader bốn địa chỉ giảm thanh ghi góc giữ lâu từ 110 xuống 30 qubit. Các compiler chia miền, lồng lookup và dùng chung tích giảm tổng T xuống 17.063. Vì factorization giữ nguyên, tác giả báo hai sai số giữ nguyên và tỉ số tốt nhất ở 10 bit là 5,62.

Theo tác giả, xoay cột và phép đẳng cự trong từng khối giữ Gram, dịch một hạt và gap. Cận được nêu là Λ₂ ≥ ¼ Σᵢⱼ |(AAᵀ)ᵢⱼ|, với A là ma trận đang xét trong phép refit theo khối. Tác giả suy ra khả năng giảm λ_eff dưới 0,3% cho factorization này.

Ở 8 bit, workspace chuẩn bị trạng thái giảm từ 607 xuống khoảng 300, tổng Q từ 742 xuống 448. Tác giả báo hiệu ứng này chưa xảy ra ở 9 bit. Làm tròn trực tiếp fit 10 bit xuống 8 bit cho error₂ khoảng 111 mHa. Refit word rời rạc có ràng buộc, chuyển hệ số và tăng từ điển lên khoảng B = 300–350 giúp khôi phục độ chính xác với λ_eff khoảng 47,5–49,5. Kết quả tiến từ 6,15 với B = 333 lên 6,435 với B = 303.

Kết quả âm gồm word 7 bit cho error₂ khoảng 60–70 mHa, làm tròn ghép cặp khôi phục độ chính xác nhưng từ điển tăng gấp đôi, và shape B = 191, C = 136 có error₂ liên tục 19,35 mHa rồi tăng lên 26,8 mHa sau lượng tử hóa. Tác giả ghi mixed word width nằm ngoài định dạng submission, chia sẻ cơ sở qua các khối không giao hoán không hợp lệ, và shape một nhóm R = 1, B = 496, C = 384 đạt khoảng 4,15 ở 10 bit. Fit 8 bit với ít vector dừng gần 41 mHa trong các bước cục bộ. Nguồn để ngỏ LLL/Babai theo độ nhạy tuyến tính và huấn luyện có xét lượng tử hóa.

## Invsqrt

Mạch 78 qubit của dòng Gluzdov → DePie → busyaprime chuẩn hóa bằng một bit, đọc đa thức bậc hai theo đoạn từ QROM, tính Horner bằng chữ số có dấu, dọn curvature lookup bằng phép đo và tạo pha bằng 44 phép quay đã hiệu chỉnh. Tác giả giữ đa thức và góc quay, tính lại đầu ra QROM phụ thuộc tại điểm dùng, dọn sớm 30 tiền tố carry, tạm xóa bit cao của accumulator, luân phiên hai buffer ở lượt pha thứ hai và cất cờ vào các vị trí đã giải phóng. Tác giả báo kiểm các đồng nhất thức trên 3.133.452 đầu vào hợp lệ, giảm 78 xuống 68 qubit và giữ lỗi xấu nhất ở 0,99966 lần dung sai.

Tác giả ước lượng cận 1.450–1.550 Toffoli tương đương trong kiến trúc này và báo Newton, đa thức bậc ba, độ rộng bảng khác, cắt bớt ít hơn và đổi cách gán thanh ghi cho kết quả ngang hoặc kém hơn. Phương án tính trực tiếp bit pha theo x vẫn còn mở. Tác giả nhắc bản 67 qubit đạt 119.054 và tỉ số 17,44 ngoài gói phát hành.

## DQI

Tác giả giữ mạch Gluzdov round12. Mạch dùng continued fraction tại chỗ trên bank syndrome 840 qubit, kết hợp pha Bézout/Hankel của SomeJoint, chiếu mask và nén lịch sử. Một nhóm khác được tác giả dẫn đã thấy hai lỗi pha trong 102.400 shot.

Các thiết kế riêng của tác giả gồm BM và EEA dạng streaming/windowed/journaled với cận độ rộng được báo là 1.704 và 1.296 qubit trong các mô hình đã xét. Tác giả loại phương án Forney song tuyến tính 64 Toffoli mỗi vị trí theo cận rank tối thiểu 15 của nhân GF(64). Sweep biên độ không dùng nghịch đảo cho pha dùng khoảng 45.000 Toffoli ở 851 qubit, so với khoảng 328.000 cho Chien/Forney. Tiền xử lý Bézoutian có cấu trúc được báo là 871 qubit và khoảng 73.000 Toffoli ở chiều thuận, đúng cho bậc 35 với pivot đều. Trường hợp bậc Euclid tụt sâu còn mở.

Tách σ(x) = E(x²) + x·O(x²) trong đặc số 2 cho σ′(x) = O(x²), với E và O là phần hệ số chẵn và lẻ. Nguồn còn nêu phép cộng bội của F vào G để chuẩn hóa G và giữ Bézoutian trong bố trí của tác giả. Tác giả ước tính khoảng 610.000 Toffoli nằm ở hai chiều extraction và ghi các kịch bản chi phí giả định khi giảm độ rộng lẫn số cổng.

## Ghi chú thực hành và ghi công

Tác giả phân biệt screening invsqrt với chấm đầy đủ, lưu ý ancilla có thể phát sinh khi dựng mạch và cổng điều kiện theo phép đo chỉ được tính khi chạy. Tác giả báo bỏ reset Z trên các mạch cụ thể cho cùng điểm đã kiểm và lưu ý hiệu ứng của cận tin cậy khi chạy DQI ít shot. Đây là nhận xét cho môi trường và phiên bản nguồn.

Nguồn ghi công busyaprime, DePie, Gluzdov và marsyas cho invsqrt. Nguồn ghi công Gluzdov, SomeJoint, ViberTeam, manwithacat và Phuc Thai cho DQI. Nguồn ghi công Ahmed Berat Özer và marculera cho DFTHCSOS, đồng thời ghi nhận Michael Rustad độc lập đạt chế độ 8 bit với Q = 448. Google Quantum AI cung cấp verifier và kickmix.
