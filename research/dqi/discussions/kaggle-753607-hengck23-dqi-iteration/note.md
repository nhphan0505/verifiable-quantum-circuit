# Đo chi phí từng khối và ghép module trong decoder DQI của hengck23

Status: draft
Track: dqi
Source: https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/753607
Version: Kaggle thread 753607, snapshot văn bản API 2026-11-09

- Từ khóa: circuit surgery, profiling theo khối, A/B test, iter014, generator.
- Đọc trực tiếp bài của hengck23 và tám bình luận hiển thị ngày 2026-11-09, sau đó đối chiếu văn bản bài và 10 bình luận do API Kaggle trả, gồm bảy bình luận cấp đầu và ba phản hồi lồng. Giữ [snapshot giao diện](source.md) và [snapshot đối chiếu có ID bình luận](source-2026-11-09-api.md). Ảnh đính kèm nằm ngoài phạm vi đối chiếu. [Thread gốc](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/753607)

## Câu hỏi và bối cảnh

Hengck23 mô tả hai tầng tối ưu decoder. Tầng toán chọn cách giải mã. Tầng biên dịch thay cách biểu diễn và thao tác trên thanh ghi. Tiêu đề bài đăng nêu ratio 60,11134658530358. Notebook mà bài dẫn có tên chứa 59,56854. Lời bình luận của Wan Xiaolong nhắc đến iter014. Văn bản đã đọc chưa nối ba mốc này bằng hash và log chấm. [Bài gốc và phản hồi của Wan Xiaolong](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/753607)

## Các phương án và lập luận

| Phát biểu | Căn cứ trong thread | Giới hạn |
| --- | --- | --- |
| **Hengck23, chọn mô hình decoder rồi biên dịch từng khối.** Tách pipeline thành các đoạn và đo Q/T để chọn đoạn cần sửa. | Bài gốc, mục *High-level modeling* và *Low-level compilation*, cùng comment 3546276 về phân rã baseline thành các bước. | Phần văn bản đã đọc không cung cấp bảng chi phí theo đoạn cho một hash cụ thể. So sánh BM khoảng 14,2× là nhận định của tác giả bài đăng. Thiếu cấu hình để đối chiếu. |
| **Hengck23, ghép module và A/B test.** Dùng đoạn phù hợp từ các mạch công khai, ghép ở mức .kmb và chọn biến thể theo số đo. | Comment 3546421 về circuit surgery. Tác giả nói còn phải dựng lại generator Python. | Cần xác minh biên giữa module, mapping dây, pha và cleanup. Thành công trên artifact chưa xác nhận có thể dựng lại từ generator hoặc áp dụng cùng kỹ thuật cho mạch khác. |
| **Wan Xiaolong báo kiểm iter014 trên salt mặc định và ba salt khác.** | Comment 3546847. | Đây là lời báo của người kiểm. Phần văn bản không kèm raw log hoặc hash. |
| **Hengck23 kể về việc dùng mốc leaderboard bịa trong prompt. Jack gợi ý agent có thể đạt 65.** | Comment 3546299 và 3546422 của hengck23. Comment 3546436 của Jack là phản hồi lồng dưới 3546422. | Mốc 65 là gợi ý trong cuộc trao đổi về prompt. Ngữ cảnh này chưa xác định nguồn gốc hoặc độ chính xác của ratio cụ thể trong tiêu đề. |

## Kết luận hiện tại

Thread xác nhận quy trình của tác giả là chia mạch, đo tài nguyên và thử thay từng module. Chưa thể quy kết ratio trong tiêu đề cho riêng một đổi mới toán học, hay gọi iter014 là decoder tái dựng được từ source chỉ dựa vào bài đăng. Mốc riêng của repo là DQI-27 full với 890 qubit và khoảng 11,65 triệu mean Toffoli-like. Độ rộng này giúp xác định câu hỏi tiếp theo là chi phí từng bước và khôi phục trạng thái trong chiều đảo. Các số liệu của thread chưa là đối chứng tương thích cho kết quả repo. [Kết quả DQI-27 tại main b61293b](../../../../src/dqi/DQI-27/DESCRIPTION.md)

## Hypothesis đề xuất và kiểm chứng tiếp

Chọn một đoạn có giao diện rõ, chẳng hạn một bước cập nhật locator và replay. Ghi chính xác trạng thái vào/ra, các dây được mượn, vị trí áp pha và cách dọn rác. Kiểm bản thay thế và bản gốc trên cùng miền đầu vào và các kết quả đo liên quan. Báo Toffoli của đoạn và peak Q của toàn mạch, vì giảm peak cục bộ có thể chưa đổi peak tổng. Nếu chỉ dùng bằng chứng dev, giữ cùng profile và seed. Nếu chạy nhiều salt theo hash, báo riêng số lỗi và R của mỗi draw. Đây là quy trình đề xuất cho project. [Verifier DQI](../../../../verifiers/dqi/verify_submission_dqi.py)

## Liên kết triển khai và câu hỏi còn mở

- [Notebook được bài đăng dẫn](https://www.kaggle.com/code/hengck23/dqi-kmb-at-59-56854). Nội dung notebook, artifact, generator và các log bên ngoài nằm ngoài phạm vi đọc.
- [DQI-23](../../../../src/dqi/DQI-23/DESCRIPTION.md) và [DQI-27](../../../../src/dqi/DQI-27/DESCRIPTION.md) là đối chứng của project cho routing và narrow return. Thread không thiết lập tương đương với các mạch này.
- Còn thiếu hash khớp từng mốc, biên module có đủ thông tin để chứng minh tương đương, và chi phí đo riêng của chiều thuận, chiều đảo và quét pha.
