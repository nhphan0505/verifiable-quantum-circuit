# Quantum Circuits | 24.65 Local GM: Chem Refit

- Agniv Banerjee (SomeJoint), phiên bản 36, scriptVersionId 365753941. Kaggle hiển thị ngày 05/11/2026 theo giờ Việt Nam. Truy cập 08/11/2026. [Notebook v36](https://www.kaggle.com/code/somejoint/quantum-circuits-24-65-local-gm-chem-refit?scriptVersionId=365753941)
- Snapshot diễn giải các phần kỹ thuật về invsqrt, DQI và hóa học, cùng phản hồi liên quan. Phạm vi bỏ qua mục hướng dẫn tính điểm, các cell code và quy trình chạy, kiểm tra hoặc đóng gói submission.

## Kết quả được công bố

Kaggle hiển thị 24,65393 cho v36. Tác giả báo kết quả local 24,65394 ở cấu hình mặc định của các verifier. Hai số này đến từ hai phép đo. Bảng dưới đây ghi các tài nguyên và chi phí tác giả công bố.

| Bài | Qubit | Toffoli trung bình do nguồn ghi | Chi phí do nguồn ghi |
| --- | ---: | ---: | ---: |
| Invsqrt | 62 | 1.281,6647 | 97.921,58 |
| DQI | 891 | 396.918,5 | 3,75373 × 10¹¹ |
| DFTHCSOS | 427 | 15.347 | 309.207.580 |

## Invsqrt: bỏ hiệu chỉnh do hai bit đo không mang pha

Tác giả áp dụng thủ thuật của Kirill Tymchishin lên mạch v33. Hai phép đo đọc dây đã ở trạng thái 0 trên mọi nhánh. Theo notebook, kết quả ngẫu nhiên của hai phép đo này không để lại pha cần sửa, nên cố định hai bit cổ điển về 0 để các hiệu chỉnh do chúng điều khiển không chạy. Tác giả báo tiết kiệm trung bình 0,5 Toffoli và 3 cổng T mỗi shot. Khảo sát 899 phép đo không tìm thêm vị trí có lợi. Bản v33 đã có biến đổi gộp bốn Toffoli thành hai ở một accumulator. Tác giả ghi nhận qiuqiuh đã công bố mức giảm ở cùng vị trí sớm hơn, với cách đặt cổng khác.

Tác giả báo đạt verifier ở lần mặc định và ba salt mới, với lỗi xấu nhất bằng 0,99932 lần dung sai. Tác giả cũng báo replay trên 3.133.452 đầu vào với mọi kết quả đo, và kiểm tra bằng engine riêng trên tám nhóm đầu vào.

## DQI: sử dụng bản viết lại của yoyobar

SomeJoint dùng nguyên mạch 891 qubit từ lần viết lại thứ ba của yoyobar trên decoder C1 của Syed Asad Ali. Nguồn mô tả bản này tiết kiệm thêm một CCZ so với lần viết lại trước của yoyobar. Dòng thiết kế đi qua narrow return của SomeJoint và flag carry do Ali Haydar Özdağ đề xuất. Notebook dẫn bản xuất khoảng 15:23 UTC ngày 04/11/2026 từ [portfolio yoyobar](https://www.kaggle.com/code/yoyobar/lb-22-99-invsqrt-101-62-qubits).

## DFTHCSOS: giữ word góc và mạch, refit trọng số

Mạch nạp góc của qwertykeypadapple dùng tìm quan hệ kernel trên compiler của Lera, cho bảng compact-group (8, 143, 45). Tác giả báo dùng nguyên 15 mạch, với 303 Toffoli ở mỗi mạch 0–3 và 281 ở mỗi mạch 4–14. Phần refit thay hai mảng trọng số W và H2_I. Word góc và các hệ số còn lại lấy từ các nguồn được notebook ghi công.

Refit dùng các bước tiếp tuyến có kiểm soát, xen kẽ quét gauge. Theo tác giả, chuẩn hóa hiệu dụng λ_eff giảm từ 47,266713 xuống 47,184436 sau năm lượt. Kết quả cuối ghi hai sai số 11,195 và 19,999999 mHa, và gap 3,9148990 Ha. Notebook nêu ngưỡng sai số 20 mHa và mốc gap 3,914898 Ha. Tác giả ghi công [QCC Kernel Search v1](https://www.kaggle.com/code/qwertykeypadapple/qcc-kernel-search-24-65) cho mạch góc và [portfolio của ayodejiibrahimlateef](https://www.kaggle.com/code/ayodejiibrahimlateef/quantum-portfolio-24-56308-local) cho tệp hệ số mà refit kế thừa.

## Phản hồi liên quan

- Trên v8, manwithacat đề xuất thử nhiều mức ngân sách qubit/cổng, phân bổ thanh ghi theo thời gian sống và kiểm tương đương theo từng đoạn. Đây là đề xuất.
- Trên v26, Tobias Oberrauch báo thiếu một phần lõi khi thử tái dựng decoder cũ. SomeJoint trả lời trên v27 rằng phần đó có thể nằm trong notebook. Khả năng tái dựng chưa được xác minh ở đây.
- Các phản hồi v14–v22 hỏi về xuất xứ và giấy phép của những mạch DQI cũ. SomeJoint nói ở v16 rằng họ tự triển khai decoder từ mô tả thiết kế và dùng một mạch khác ở bản đó. Trao đổi này đề cập các phiên bản trước. [Các bình luận](https://www.kaggle.com/code/somejoint/quantum-circuits-24-65-local-gm-chem-refit/comments?scriptVersionId=365753941)
