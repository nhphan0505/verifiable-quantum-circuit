# VQCC Own-Circuit Portfolio Notebook

- Tác giả [Syed Asad Ali (syed3000)](https://www.kaggle.com/syed3000). [Notebook Kaggle, phiên bản 11](https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook?scriptVersionId=366611575)
- Phiên bản 11, scriptVersionId 366611575, ngày hiển thị 07/11/2026 theo giờ Việt Nam. Truy cập 08/11/2026. Kaggle hiển thị Apache-2.0 và 0 bình luận.
- Snapshot diễn giải phần mô tả kỹ thuật và output hiển thị. Các mạch, cell code, log đầy đủ, dataset và ZIP nằm ngoài phạm vi lưu trữ. Số đo và các tuyên bố kiểm chứng kỹ thuật dưới đây do tác giả báo cáo, trừ điểm public hiển thị trên Kaggle.

## Tổng quan và kết quả hiển thị

Kaggle hiển thị điểm public 25,06570 cho v11. Notebook báo trung bình nhân local 25,0657 khi lượt rút mẫu DQI không có lỗi, với các tỉ số reference/chi phí lần lượt là invsqrt 21,57×, DQI khoảng 65,2× và hóa học 11,20×. Tác giả dùng kickmix-engine của manwithacat cho các số đo local. Output đóng gói liệt kê SHA-256 của 18 thành phần và báo hoàn tất, gồm mạch invsqrt, mạch DQI, 15 mạch góc DFTHCSOS và một tệp hệ số. Output này ghi nhận việc đóng gói.

## 1. Fusion / invsqrt

Tác giả dựa trên dòng mạch mrmeows → busyaprime → yoyobar, với bảng bán log 8 bit, Horner bậc hai và hai lượt pha gồm 41 phép quay. Các thay đổi gồm hoãn fan-in của lookup, giải mã hệ số bằng tích Boolean, xóa carry bằng phép đo X và CZ hiệu chỉnh, gộp carry-save và tái dùng qubit rảnh trong mạng dịch. Tìm kiếm cửa sổ đến 12 dây, có xét pha, tìm được bảy cửa sổ thay ba Toffoli bằng hai. Tác giả còn bỏ các hiệu chỉnh phụ thuộc kết quả đo trên qubit đã xác định ở trạng thái 0, tái tổng hợp decode và dùng bộ giải MinRank cho một phần lookup.

Tác giả báo các rewrite cuối bảo toàn hành vi trên 3.133.452 đầu vào và mọi kết quả đo, và mạch đạt verifier trên bốn salt. Mốc v11 được báo là 62 qubit, 1.552,71 Toffoli tương đương và chi phí 96.267,97. Các đại lượng trung bình, tương đương và số cổng tĩnh được báo riêng.

## 2. DQI / Reed–Solomon

Dòng giải mã C1 dùng chuỗi giữ head, bước nhảy prefix qua block-Wronskian và narrow return của SomeJoint. Flag carry do Ali Haydar Özdağ đề xuất đo pole flag theo cơ sở X ở lượt đi, tái tạo lúc quay lại và hiệu chỉnh bằng CZ. Tác giả kết hợp xóa qua phép đo, AND ladder sạch có điều kiện, tái dùng tích trên dây rảnh và nhận dạng các tích biểu diễn cùng hàm Boolean. Các nhóm ứng viên được tìm bằng fingerprint và kiểm tra trên mẫu giữ lại.

Tác giả báo thêm qubit thứ 892 để chọn biến thể converter và reverse dùng ít Toffoli hơn. Một số lớp hoặc trường hợp ngẫu nhiên vẫn có thể gây lỗi, gồm lớp trọng số ≤5 mà tác giả chấp nhận trả giá điểm và sự kiện zero ngẫu nhiên trong phép thử 24 bit. Giữ hai cờ cho lớp trọng số 17 tốn thêm 175 Toffoli và số shot lỗi trên 72 lượt rút mẫu ghép cặp giảm 27 xuống 21. Mốc cuối là 892 qubit, khoảng 395.510 Toffoli trung bình. Một lượt rút mẫu không lỗi và số liệu qua nhiều lượt ghép cặp là hai phép đo khác nhau.

## 3. Hóa học / DF-THC FeMoCo

Tác giả dựa trên pipeline DF-THC của marculera và progressive rounding của Özer. Fit liên tục bằng L-BFGS float64 trên A100 cho bảng 8 × 143 × 44 và 1.220 địa chỉ. Tác giả mô tả làm tròn nearest-plane kiểu Babai, thứ tự cố định tọa độ dựa trên độ cong có điều kiện, refit từng giai đoạn và hai ngưỡng lỗi 20 mHa. Loader dùng đổi thứ tự Givens, gauge π, mang tích địa chỉ qua batch và ghép cặp theo matroid parity. Tác giả báo chi phí 4.152 Toffoli mỗi lượt loader và kế hoạch năm khối giảm 202 xuống 195 tích cho mỗi loader có mã hóa.

Theo tác giả, loader qua các phép kiểm đại số, bảng chân trị và preload trên toàn bộ 1.220 địa chỉ, kiểm phục hồi word và verifier. Lượt refit cuối chỉ thay trọng số khi giữ word, theo tiền lệ công khai của Heliosli. Mốc v11 là λ_eff 46,892646, 14.966 Toffoli, 427 qubit và chi phí báo cáo 299.666.607.

## Kết quả âm được báo cáo

Ở fit được thử, giảm còn 7 bit làm tăng nhiễu làm tròn. Các cách chia địa chỉ loader 6/5, 5/6 và 3/4/4 tốn hơn cách 4/7 đang dùng. Hướng DQI key-equation/Hankel tại chỗ được báo vượt ngân sách khoảng 14 lần. Tác giả cũng chưa thấy kiến trúc mới từ đầu cho DQI hoặc invsqrt vượt mốc hiện tại trên tính toán sơ bộ.
