# Quantum AI - DF-THC Group Compression

Ahmed Berat Özer. Notebook v23, scriptVersionId 366387300, hiển thị ngày 07/11/2026 theo giờ Việt Nam và truy cập ngày 08/11/2026. Bản chụp diễn giải các mục Markdown và ghi lại các output hiển thị của ba cell. [Notebook v23](https://www.kaggle.com/code/ahmedberatozer/quantum-ai-df-thc-group-compression?scriptVersionId=366387300)

## Mở đầu và thay đổi so với bản gốc

Tác giả xuất phát từ portfolio của maoxin123 và thay DQI bằng tệp 17 tuyến tái dùng tích của Atakan Aldemir trước khi so sánh. Mỗi bài có một thay đổi. Bảng trong mục “What changed from the base” báo kết quả sau đây ở salt mặc định.

| Bài | Tệp gốc → tệp v23 (tiền tố hash) | Chi phí gốc → v23 |
| --- | --- | ---: |
| Invsqrt | c17971af → 87cb9aa9 | 97.746,90 → 97.744,88 |
| DQI | 7b6cbb92 → 77bace9d | 374.755.600.651 → 374.751.757.175 |
| DFTHCSOS | 63d2c7bc → afe042b5 | 299.667.341,53 → 299.666.272,97 |

Trung bình nhân local ở salt mặc định tăng từ 24,94137 lên 24,94165. Bảng output phía dưới thuộc lần chạy có salt `notebook-verification`, nên có thể khác nhẹ với bảng so sánh này. Badge điểm Kaggle 23,94701 gắn với v22.

## FeMoCo

Tác giả giữ bảng (8, 143, 44), word góc và 15 mạch nạp của Syed Asad Ali. Chỉ W và H2_I được refit từ trọng số của maoxin123, bằng SQP theo khối rồi Newton với Hessian chính xác trên mặt ràng buộc đang hoạt động. Tác giả báo 41.152 trong 50.336 phần tử W và 352 phần tử H2_I thay đổi, 83 phần tử 0 được giải phóng và xuất hiện 540 phần tử 0 mới. λ_eff giảm từ 46,8927604 xuống 46,8925932. Hai sai số là 19,999997 mHa và gap 3,914898003 Ha, theo số đã hiển thị. Tác giả báo 427 qubit, 14.966 Toffoli, trong đó 8.304 cho hai lượt mạch nạp góc. Notebook cũng báo kiểm biểu tượng các mạch nạp đã có trên toàn bộ 1.220 địa chỉ, cả hai chiều và mọi kết quả đo. Bước Newton cuối vẫn cải thiện và vòng CG chạm giới hạn số vòng.

## DQI

Nhóm ghép bốn chuỗi tái dùng tích của MAIDANG/daifanhao vào tệp 17 tuyến của Atakan Aldemir. Một tích giữ trên dây đã chứng minh rảnh qua khoảng giữa hai lần sử dụng cho phép thay lần tính thứ hai bằng Clifford và uncompute qua đo. Số Toffoli tĩnh từ 395.662 xuống 395.658 với cùng 892 qubit. Notebook báo đối chiếu affine dưới 61 hằng đầu vào đã chứng minh, kiểm dây rảnh và kiểm đồng nhất thức pha trên 512 trường hợp.

| Biến thể | Toffoli tĩnh tiết kiệm | Lỗi giá trị + pha, salt mặc định | Lỗi giá trị + pha, salt notebook |
| --- | ---: | ---: | ---: |
| 77bace9d, bốn chuỗi | 4 | 0 + 0 | 0 + 0 |
| 70aa897c, ba tuyến mới | 3 | 0 + 0 | 0 + 0 |
| b1234e21, cả bảy | 7 | 1 + 1 | 0 + 0 |

Tác giả phát hành bản bốn chuỗi và ghi nhận việc chọn tệp có phụ thuộc lượt rút mẫu. Trên tệp gốc, 48 lượt cố định salt trước, mỗi lượt 102.400 shot, cho 13 lỗi, gồm 11 lỗi giá trị và 2 lỗi pha. Tác giả báo trung bình 0,27 lỗi mỗi lượt với khoảng 95% từ 0,14 đến 0,46. Tác giả kỳ vọng các rewrite giữ kênh của decoder, và dẫn phản ví dụ trọng số 16 của David Pilný cho baseline.

## Invsqrt

Khối pha của yoyobar chỉ có tác dụng khi q18·q21 khác 0, xảy ra tại 12 đầu vào x từ 4 đến 15. Tác giả dùng bảy mẫu pha độc lập có thể tạo bằng Z/CZ trên các dây còn sống về sau. Một kiểm tra cổ điển năm bit chọn 16.384 trong 524.288 mask để dùng khối pha đó, trong đó 16.383 mask trước đây cần CCZ. Mức tiết kiệm kỳ vọng chính xác do nguồn báo là 16.383/524.288 Toffoli mỗi shot. Mạch vẫn có 62 qubit. Nguồn báo kiểm BDD cho kỳ vọng và đối chiếu pha cùng hành vi trên mọi đầu vào hợp lệ và nhánh đo bằng DAG/SAT.

## Những hướng được thử và những hướng còn mở

- **Invsqrt.** Các kế hoạch đưa 62 xuống 61 dây vượt ngưỡng hòa vốn về cổng và chưa sinh ra mạch 61 qubit. Tìm kiếm 52.059.392 ứng viên lân cận lookup không giảm được mốc 169 AND trong phạm vi đã xét. SAT trên bốn cửa sổ trả UNKNOWN. Các phương án giảm phép quay hoặc đổi kiến trúc còn ở mức ước lượng hay thử cục bộ.
- **DQI.** Mạch 891 qubit được so còn thiếu khoảng 657 Toffoli so với hòa vốn. Tìm trong họ đối xứng đã chọn cho nhân GF(2¹²) dừng ở 45 AND, trong khi mạch dùng 42. Bảy tuyến lấp bảy dây rảnh trong mô hình cache trực tiếp. Một phép cắt guard tăng lỗi từ 13 lên 26. Một lượt thử xóa CCZ cho 50.819 lỗi pha vì parser nhầm bit đích với bit điều kiện. Tác giả báo đã sửa parser và chứng minh lại các biến thể phát hành.
- **DFTHCSOS.** Relaxation số cho sàn λ_eff 46,8485 ở word cố định, chưa có chứng chỉ số học chính xác. Loader thứ hai tái tạo 4.152 Toffoli mỗi lượt. Các thử đổi gauge, cache trên bảng đầy đủ hoặc sửa word để bỏ một tích chưa cho lợi ích trên mạch hợp lệ. C = 43 thử với 325 word sửa vẫn có sàn error₂ khoảng 21,259 mHa. Huấn luyện lại từ nghiệm liên tục khác, họ loader J = 4 đầy đủ và thêm bước Newton là các hướng tác giả để ngỏ.

Nguồn ghi công maoxin123 cho portfolio và trọng số ban đầu, Syed Asad Ali cho bảng, loader và dòng decoder, yoyobar cho mạch invsqrt gốc, Atakan Aldemir và MAIDANG cho hai họ tái dùng tích, Lera/marculera cho pipeline compact-group, và heliosli cùng manwithacat cho các bước refit trước. Các ghi công chi tiết nằm trong mục “Sources and credits”.

## Output hiển thị của lần chạy notebook

- **Cell 1.** Giải nén `dqi.kmb.xz` thành `dqi.kmb` 504 MiB tại `/tmp/v23_xz/0/`. Notebook in đường dẫn dữ liệu cuộc thi, thư mục `/kaggle/input/vqcc-v23-portfolio`, hai đầu vào `vqcc-v23-portfolio` và `v23_xz`, cùng 4 worker.
- **Cell 2.** Output liệt kê các tệp `dfthcsos/angle_k_0.kmb` đến `dfthcsos/angle_k_14.kmb`, `dfthcsos/submission.npz` và `invsqrt.kmb` từ thư mục portfolio, cùng `dqi.kmb` từ thư mục giải nén. Báo ghi `submission.zip` 26 MiB. Các dòng PASS được ghi trong bảng dưới.
- **Cell 3.** Hiển thị bảng tài nguyên và tỉ số làm tròn, cùng trung bình nhân 24,9416.

| Bài | Trạng thái (cell 2) | Chi phí (cell 2) | Thời gian | Qubit (cell 3) | Toffoli trung bình (cell 3) | Chi phí làm tròn | Chi phí đối chứng | Tỉ số |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Invsqrt | PASS | 97744.90279109387 | 777 s | 62 | 1.281 | 97745 | 2.0768e+06 | 21.247 |
| DQI | PASS | 374751927990.3516 | 163 s | 892 | 395.373 | 3.7475e+11 | 2.4439e+13 | 65.215 |
| DFTHCSOS | PASS | 299666272.9739243 | 29 s | 427 | 14.966 | 2.9967e+08 | 3.3556e+09 | 11.198 |
