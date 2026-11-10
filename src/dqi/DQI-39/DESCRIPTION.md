# [DQI-39] Viết lại khối tổng hợp locator của Kirill V5 bằng Python và giảm tích lặp ở hai chiều

**Loại** — Tinh chỉnh một phương án.

## File gốc

Đối chứng là mạch Kirill V5 có SHA-256 `4e9b50b1ee34b3eaf2b7f394873c2dd3dad4cddbdd1f12a348b4323b5eb41771`. Bộ sinh cổng cục bộ nằm ở `GQA-local-dqi-v5/recovered_generator/`. `rebuild.py` có SHA-256 `049c49acdda2faa049cd3e7cfedd1b24da54347a32b4a86be03bab2428635d19`, `scan_kernel.py` có SHA-256 `fb7b22182f05baf35e3ec5782d41559bf681f8a7e147a8e90a772136827d7c53`, và `stages.zip` có SHA-256 `9c3d3f1ffdbd1ce47435b99d9e68f33b55ce794fe86edb2f7b40dc9ace3c46e3`. Bản dựng lại khớp từng byte với mạch đối chứng. Python sinh kernel kiểm nghiệm và áp pha tại 4.025 vị trí quét. Synthesis, conversion và các khối còn lại vẫn dựa vào dữ liệu cổng đã tách theo nhãn. Bộ sinh và archive này hiện là đầu vào cục bộ, chưa có permalink hoặc provenance build trong repo.

Giữ attribution của mạch V5. Nếu bước 03 còn cần dữ liệu cổng của V5 để build, mô tả cách lấy đúng artifact bằng hash và kiểm tra điều khoản phân phối trước khi đưa dữ liệu bên thứ ba vào repo. Giữ nguyên [verifier DQI](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/a19b0e08bb6af0f7b4cdf6fe10569d2ad43e870f/verifiers/dqi/verify_submission_dqi.py). [DQI-27](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/a19b0e08bb6af0f7b4cdf6fe10569d2ad43e870f/src/dqi/DQI-27/DESCRIPTION.md) là hướng trước về quản lý bộ nhớ trên decoder Schur của nhóm. Phạm vi lần này là cặp khối synthesis của V5.

## Phần tinh chỉnh và lý do

Thay đúng hai đoạn `synthesis` và `unsynthesis` bằng bộ sinh Python có cấu trúc theo phép cập nhật locator. Giữ `mask_projection`, `initial`, `extract`, `convert`, `scan`, `unconvert`, `unextract`, `uninitial` và `restore_masks` của đối chứng trong lần so sánh đầu. Giữ GF(2^12), 70 word syndrome, 4.095 vị trí, trọng số hỗ trợ đến 35 và mask runtime. Tách việc kiểm chứng bản viết lại khỏi thay đổi lịch cổng để đo phần tiết kiệm do synthesis.

## Cách thực hiện và đánh đổi

1. Dùng marker và hai stage gốc để lập bảng dây đọc/ghi ở biên `extract → synthesis → convert` và `unconvert → unsynthesis → unextract`. Ghi biểu diễn từng word, thứ tự bit, vị trí locator và hệ số sống, độ bậc và lịch sử điều khiển, thanh ghi cổ điển dùng lại, cùng dây sạch và dây mượn. Kiểm basis, modulus, chuẩn hóa và mapping đầu ra bằng fixture trước khi thay cổng.
2. Từ chuỗi cập nhật lặp trong gate stream, khôi phục quy tắc rẽ nhánh, thứ tự hệ số và biểu diễn field. Dùng phép nhân cộng `target ^= left * right` trên GF(2^12) để mô hình hóa các cập nhật song tuyến tính đã xác nhận. Sinh forward và inverse từ cùng quy tắc với thứ tự và dữ liệu điều khiển tương ứng. Kiểm locator độc lập bằng nghiệm tại vị trí lỗi và kiểm riêng layout, hệ số chuẩn hóa và lịch sử với V5 vì cùng locator toán học có thể có biểu diễn khác. Nhánh hụt bậc, locator hằng và hệ số đầu bằng 0 cần đi đúng tuyến V5.
3. Đối chiếu trên cùng input ở cả hai biên. Cặp mới phải để `convert` đọc được cùng trạng thái, giữ các dây sống và phục hồi dữ liệu đầu vào cũng như workspace sau `unsynthesis`. Xét pha phụ thuộc đầu vào trên các nhánh đo. Với xóa đo X một tích bit `a*b`, outcome `h` sinh pha `(-1)^(h*a*b)`. Chỉ dùng CZ điều kiện `h` khi hai factor đúng còn sống hoặc có thể dựng lại. Nếu predicate khác tích hai bit thì xác định phép sửa pha tương ứng trước khi bỏ lịch cũ.
4. Sau khi bản tương đương qua kiểm tra, thống kê Toffoli-like riêng ở cả hai chiều và xác định một cặp cập nhật lặp có thể dùng chung tích hoặc scratch đã sạch. Chỉ tái dùng tích khi cả hai toán hạng và điều kiện điều khiển còn tương đương trên mọi nhánh sử dụng. Ghi chi phí giữ qubit sống, dựng lại và xóa pha. Với repetition factor cố định, điều kiện hòa vốn là `T_new/T_v5 < (892/Q_new)^2`. Nếu lỗi thay đổi, so điểm trực tiếp. Tên config, layout và lựa chọn lịch cổng cụ thể thuộc bước 03.

## Kế hoạch kiểm chứng hypothesis

- **Đối chứng.** V5 và bản dựng lại có cùng hash ở trên. Lượt dev cục bộ do owner cung cấp dùng profile v1, seed `20261106`, 4.096 shots và có 0 lỗi value/phase. Xác minh môi trường và hash harness của phép so chính thức khi có run lưu đúng schema. Chưa có run của ID này.
- **Dự đoán.** Tái sử dụng tích lặp có thể giảm tổng Toffoli-like của cặp synthesis mà không tăng đỉnh qubit nếu tìm được dây sạch xuyên suốt khoảng sống. Bản Python tương đương dùng làm mốc kiểm tra trước khi đo lợi ích.
- **Ủng hộ hoặc bác bỏ.** Kiểm tra weight 0, 1, 35, tụt bậc và syndrome đầu bằng zero, vị trí biên và mask runtime khác nhau. Lỗi value, phase hoặc workspace bác bỏ lịch cổng. Sau kiểm tra thành phần, ứng viên phải dev PASS với điểm thấp hơn V5 trên cùng harness, seed, profile và số shots. Chỉ số operation count hoặc runtime thấp hơn không đủ để ủng hộ giả thuyết về điểm.
- **Điều kiện dừng.** Giới hạn ở một bản tham chiếu Python và một lịch tối ưu của cặp synthesis. Nếu chưa khớp được giao diện hoặc không tìm được tiết kiệm có chứng chỉ đủ bù chi phí, ghi lại kết quả và dừng ở khối này. Thay converter hoặc ghép decoder khác cần mở rộng phạm vi riêng.
- **Kiểm tra ứng viên cuối.** Sau dev, owner chạy full 102.400 shots hoặc dùng bộ seed giữ lại có đối chứng chạy cùng điều kiện. Dùng thêm ca biên và kiểm phase/cleanup của thành phần. Dev không thay thế kiểm tra bổ sung.

## Kết luận và phiên bản tái lập

Chưa đủ bằng chứng về giảm chi phí synthesis. Bản dựng byte-exact là đối chứng đã kiểm tra, chưa có bản viết lại thuật toán của cặp synthesis.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa tạo | Chưa có | Chưa chấm |
| Full | Chưa tạo | Chưa có | Chưa chấm |

Điểm và các run xem trong [SCORES.md](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/a19b0e08bb6af0f7b4cdf6fe10569d2ad43e870f/src/dqi/SCORES.md).

## Cấu hình bước 03

[rank42_reference](configs/rank42_reference.json) dùng [bộ sinh Python](solution.py) để nhận dạng các khối nhân-cộng 42 Toffoli trong cả hai chiều. Mỗi khối được mô tả bằng ba word 12-bit rời nhau và 42 hạng song tuyến tính. Mỗi hạng dùng CNOT để đưa parity hai toán hạng vào hai dây trụ và đổi cơ sở đầu ra, sau đó dùng một CCX rồi hoàn nguyên CNOT. Toàn khối thực hiện `out ^= left * right` với hai toán hạng giữ nguyên. Vì ánh xạ là song tuyến tính, kiểm trên cả 144 cặp bit cơ sở đủ để xác nhận tensor so với phép nhân GF(2^12) của Kickmix.

Kiểm trên gate stream cục bộ nhận diện và sinh lại 734 khối thuận và 801 khối đảo. Đối chiếu từng lệnh sau sinh trên cả 1.535 khối. Mọi phần điều tuyến, history, phép đo và sửa pha bên ngoài khối nhân tiếp tục dùng dữ liệu cổng V5. Phạm vi tái dựng ở cấp phép nhân chưa thay cho việc khôi phục toàn bộ thuật toán locator. Các kiểm tra cục bộ về hai tích lặp qua CNOT và điều kiện điều khiển affine chưa tìm được lịch giảm Toffoli có chứng chỉ trong phạm vi đã kiểm tra.

Cấu hình này là mốc tham chiếu để kiểm chứng phần Python. Build yêu cầu file V5 đúng SHA-256 trên và tự kiểm hash đầu ra. Nếu khớp byte, số qubit, Toffoli và điểm của cùng profile/harness sẽ khớp đối chứng. Không dùng config này làm bằng chứng giảm điểm hoặc làm ứng viên đã chấm chính thức. Chỉ mở lịch tối ưu nếu tìm được cách giảm chi phí của cặp synthesis và giữ đúng giao diện.
