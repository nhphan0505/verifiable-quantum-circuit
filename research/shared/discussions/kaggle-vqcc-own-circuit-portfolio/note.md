# Portfolio VQCC v11: tối ưu lookup, uncompute và lượng tử hóa

Status: draft
Track: shared
Source: https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook?scriptVersionId=366611575
Version: Kaggle v11 (scriptVersionId 366611575)

- **Nguồn.** Syed Asad Ali (syed3000), truy cập 08/11/2026. [Notebook v11](https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook?scriptVersionId=366611575) · [Snapshot diễn giải](source.md)
- **Phạm vi.** Phần mô tả ba bài, kết quả âm, điểm public và output đóng gói hiển thị. Kaggle hiển thị 0 bình luận. Snapshot lưu nội dung và số liệu chọn lọc, không lưu mã, dữ liệu hoặc artifact.

## Câu hỏi và bối cảnh

Tác giả kết hợp các mạch và phương pháp công khai với những biến đổi cục bộ để hạ chi phí cho ba bài. Kaggle hiển thị **25,06570** cho v11. Tác giả báo trung bình nhân local **25,0657** khi lượt rút mẫu DQI có 0 lỗi, từ các tỉ số reference/chi phí invsqrt 21,57×, DQI khoảng 65,2× và hóa học 11,20×. Các tỉ số đã làm tròn. Output của cell chỉ xác nhận đã đóng gói 18 thành phần và in hash từng thành phần. [Notebook v11, phần Methods by task và output](https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook?scriptVersionId=366611575)

## Các phương án và lập luận

| Bài | Phương pháp và số đo tác giả báo cáo | Điều kiện và đánh đổi |
| --- | --- | --- |
| **Invsqrt** | Giữ dòng mạch mrmeows → busyaprime → yoyobar với bảng bán log 8 bit, Horner bậc hai và hai lượt pha. Hoãn fan-in khi lookup, dùng phép đo X và CZ hiệu chỉnh để dọn carry, tái tổng hợp các cửa sổ tối đa 12 dây có xét pha và tái dùng dây rảnh. Bảy cửa sổ thay ba Toffoli bằng hai. Mốc cuối 62 qubit, 1.552,71 Toffoli tương đương và chi phí 96.267,97. [Notebook, §1 Fusion](https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook?scriptVersionId=366611575) | Tác giả báo các rewrite cuối được kiểm trên 3.133.452 đầu vào và mọi kết quả đo, và mạch đạt bốn salt. Khi áp dụng, phải kiểm cả giá trị, pha, điều kiện qubit sạch và chi phí của phép hiệu chỉnh. Số cổng tĩnh và chi phí tương đương được báo riêng. |
| **DQI** | Dòng C1 giữ head, dùng bước nhảy prefix block-Wronskian và narrow return của SomeJoint. Flag carry chuyển lưu cờ sang phép đo X, tái tạo cờ ở reverse và hiệu chỉnh CZ. Tái dùng các tích lặp trên dây rảnh, kể cả tích có cùng hàm Boolean. Dùng qubit thứ 892 để chọn converter và reverse ít cổng hơn. Mốc cuối khoảng 395.510 Toffoli trung bình. [Notebook, §2 DQI](https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook?scriptVersionId=366611575) | Fingerprint chỉ sàng lọc ứng viên. Tác giả báo kiểm từng chuỗi trên mẫu giữ lại và so với mạch trước đó trên hơn 300.000 shots ở vòng tối ưu trước bản cuối. Rủi ro còn lại gồm lỗi ở lớp trọng số thấp và sự kiện zero hiếm. Giữ hai cờ cho trọng số 17 tốn thêm khoảng 175 Toffoli, giảm 27 xuống 21 shot lỗi trên 72 lượt rút mẫu ghép cặp theo tác giả. |
| **DFTHCSOS** | Dựa trên pipeline marculera và progressive rounding của Özer. Fit bảng 8 × 143 × 44, làm tròn kiểu Babai và refit từng giai đoạn. Loader kết hợp đổi thứ tự Givens, gauge π, cache tích qua batch và ghép cặp matroid parity. Tác giả báo 4.152 Toffoli mỗi lượt loader và giảm 202 xuống 195 tích trên mỗi loader có mã hóa. Refit trọng số giữ word, theo tiền lệ của Heliosli. Mốc cuối λ_eff 46,892646, 14.966 Toffoli, 427 qubit và chi phí 299.666.607. [Notebook, §3 Chemistry](https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook?scriptVersionId=366611575) | Việc đổi loader cần bảo toàn word hiệu dụng và trạng thái workspace khi gọi xuôi, gọi lại và đảo ngược. Tác giả báo kiểm đủ 1.220 địa chỉ. Refit phải qua cả hai ngưỡng 20 mHa. Các thừa số trong notebook được hiển thị với precision hữu hạn. |

## Kết luận hiện tại

- **Đối chiếu verifier.** Invsqrt chấm `Q × C`, với `Q` là số qubit và `C` là chi phí Toffoli tương đương. DQI chấm `R(ε₊) × Q² × T`, với `T` là số cổng kiểu Toffoli trung bình mỗi shot, `ε₊` là cận trên Clopper–Pearson của tỉ lệ lỗi và `R` là hệ số lặp tính từ cận đó. DFTHCSOS chấm `λ_eff × T_total × Q_total` và kiểm riêng `error_1 ≤ 0,020 Ha` và `error_2 ≤ 0,020 Ha`. Đây là đối chiếu hợp đồng trong repo. [Verifier invsqrt](../../../../verifiers/invsqrt/verify_submission_invsqrt.py) · [Verifier DQI](../../../../verifiers/dqi/verify_submission_dqi.py) · [Verifier DFTHCSOS](../../../../verifiers/dfthcsos/verify.py)
- **Suy luận từ công thức DQI.** Giữ `R` cố định, từ 891 lên 892 qubit cần `T_mới / T_cũ < (891/892)²`. Tại khoảng 396.921 Toffoli trung bình, cần tiết kiệm khoảng 890 Toffoli để hòa vốn. Nếu biến đổi làm đổi lỗi, phải so cả `R` trên cùng giao thức chấm. Lượt 0 lỗi của notebook và thống kê 72 lượt ghép cặp trả lời hai câu hỏi khác nhau.
- **Kết quả âm và phạm vi.** Tác giả báo fit 7 bit tăng nhiễu, các cách chia địa chỉ loader khác tốn hơn cách 4/7 đang dùng và hướng DQI key-equation/Hankel tại chỗ vượt ngân sách khoảng 14 lần. Các kết quả áp dụng cho những thiết kế được thử. Thread chưa có bình luận phản biện. [Notebook, mục kết quả âm](https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook?scriptVersionId=366611575)

## Hypothesis đề xuất và kiểm chứng tiếp

- **Invsqrt.** Thử cô lập một cửa sổ lookup hoặc uncompute đang chi phối chi phí. So bảng chân trị có pha và mọi nhánh đo của cửa sổ với đối chứng. Chỉ ghi nhận cải thiện khi mạch đầy đủ qua verifier và `Q × C` giảm.
- **DQI.** So một biến thể cache hoặc giữ cờ với đối chứng cố định. Dùng cùng số shot và giao thức, báo lỗi theo trọng số, `Q`, `T` và điểm tổng. Xem lại hướng nếu phần tăng `R` hoặc workspace lấn át tiết kiệm cổng.
- **DFTHCSOS.** Với cùng Hamiltonian và word góc, tách thử thay loader khỏi thử refit trọng số. Với loader, kiểm word hiệu dụng và chiều đảo trên toàn miền địa chỉ hợp lệ. Với refit, giữ cả hai sai số trong ngưỡng rồi so chi phí tổng để thấy phần thay đổi ở λ_eff.

## Liên kết triển khai và câu hỏi còn mở

- [Mốc của repo cho invsqrt](../../../../src/invsqrt/SCORES.md) · [DQI](../../../../src/dqi/SCORES.md) · [DFTHCSOS](../../../../src/dfthcsos/SCORES.md)
- Chưa chạy lại verifier hoặc xác minh phép chứng minh equivalence của tác giả. Cần artifact đúng phiên bản, môi trường, salt/seed và log tương thích trước khi dùng số đo của notebook làm đối chứng định lượng.
