# Đo chi phí từng khối và ghép module trong decoder DQI của hengck23

Status: draft
Track: dqi
Source: https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/753607
Version: Kaggle thread 753607, snapshot 2026-11-09

- Từ khóa: circuit surgery, profiling theo khối, A/B test, iter014, generator.
- Đọc trực tiếp bài của hengck23 và tám bình luận hiển thị ngày 2026-11-09. Phần đã lưu là [snapshot diễn giải](source.md). Dùng tác giả và chủ đề bình luận để định vị vì snapshot không lưu permalink từng bình luận. [Thread gốc](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/753607)

## Câu hỏi và bối cảnh

Hengck23 mô tả hai tầng tối ưu decoder. Tầng toán chọn cách giải mã. Tầng biên dịch thay cách biểu diễn và thao tác trên thanh ghi. Tiêu đề bài đăng nêu ratio 60,11134658530358. Notebook mà bài dẫn có tên chứa 59,56854. Lời bình luận của Wan Xiaolong nhắc đến iter014. Thread chưa nối cả ba tên/mốc này bằng hash đầy đủ và log chấm. [Bài gốc và phản hồi của Wan Xiaolong](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/753607)

## Các phương án và lập luận

| Phát biểu | Căn cứ trong thread | Giới hạn |
| --- | --- | --- |
| **Hengck23, chọn mô hình decoder rồi biên dịch từng khối.** Tách pipeline thành các đoạn và đo Q/T để chọn đoạn cần sửa. | Bài gốc, mục *High-level modeling* và *Low-level compilation*, cùng bình luận bắt đầu bằng mô tả phân rã baseline thành các bước. | Bài không cung cấp bảng chi phí theo đoạn cho một hash cụ thể. So sánh BM khoảng 14,2× là nhận định của tác giả bài đăng. Thiếu cấu hình để đối chiếu. |
| **Hengck23, ghép module và A/B test.** Dùng đoạn phù hợp từ các mạch công khai, ghép ở mức .kmb và chọn biến thể theo số đo. | Bình luận về circuit surgery. Tác giả nói còn phải dựng lại generator Python. | Cần xác minh biên giữa module, mapping dây, pha và cleanup. Thành công trên artifact chưa xác nhận có thể dựng lại từ generator hoặc áp dụng cùng kỹ thuật cho mạch khác. |
| **Wan Xiaolong báo kiểm iter014 trên salt mặc định và ba salt khác.** Jack gợi ý mốc 65. | Hai bình luận được quy riêng cho người viết. | Không có raw log trong thread. Lời báo bốn salt là bằng chứng được người tham gia báo lại. Mốc 65 trong bình luận của Jack là gợi ý, chưa có phép đo kèm theo. |

## Kết luận hiện tại

Thread xác nhận quy trình của tác giả là chia mạch, đo tài nguyên và thử thay từng module. Chưa thể quy kết ratio trong tiêu đề cho riêng một đổi mới toán học, hay gọi iter014 là decoder tái dựng được từ source chỉ dựa vào bài đăng. Mốc riêng của repo là DQI-27 full với 890 qubit và khoảng 11,65 triệu mean Toffoli-like. Độ rộng này giúp xác định câu hỏi tiếp theo là chi phí từng bước và khôi phục trạng thái trong chiều đảo. Các số liệu của thread chưa là đối chứng tương thích cho kết quả repo. [Kết quả DQI-27 tại main b61293b](../../../../src/dqi/DQI-27/DESCRIPTION.md)

## Hypothesis đề xuất và kiểm chứng tiếp

Chọn một đoạn có giao diện rõ, chẳng hạn một bước cập nhật locator và replay. Ghi chính xác trạng thái vào/ra, các dây được mượn, vị trí áp pha và cách dọn rác. Kiểm bản thay thế và bản gốc trên cùng miền đầu vào và các kết quả đo liên quan. Báo Toffoli của đoạn và peak Q của toàn mạch, vì giảm peak cục bộ có thể chưa đổi peak tổng. Nếu chỉ dùng bằng chứng dev, giữ cùng profile và seed. Nếu chạy nhiều salt theo hash, báo riêng số lỗi và R của mỗi draw. Đây là quy trình đề xuất cho project. [Verifier DQI](../../../../verifiers/dqi/verify_submission_dqi.py)

## Liên kết triển khai và câu hỏi còn mở

- [Notebook được bài đăng dẫn](https://www.kaggle.com/code/hengck23/dqi-kmb-at-59-56854). Nội dung notebook, artifact, generator và các log bên ngoài nằm ngoài phạm vi đọc.
- [DQI-23](../../../../src/dqi/DQI-23/DESCRIPTION.md) và [DQI-27](../../../../src/dqi/DQI-27/DESCRIPTION.md) là đối chứng của project cho routing và narrow return. Thread không thiết lập tương đương với các mạch này.
- Còn thiếu hash khớp từng mốc, biên module có đủ thông tin để chứng minh tương đương, và chi phí đo riêng của chiều thuận, chiều đảo và quét pha.
