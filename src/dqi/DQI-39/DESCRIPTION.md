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

- **Đối chứng.** V5 và bản dựng lại có cùng hash ở trên. Lượt dev cục bộ do owner cung cấp dùng profile v1, seed `20261106`, 4.096 shots và có 0 lỗi value/phase. Lượt chấm theo schema và đối chiếu môi trường được ghi ở phần kết luận.
- **Dự đoán.** Tái sử dụng tích lặp có thể giảm tổng Toffoli-like của cặp synthesis mà không tăng đỉnh qubit nếu tìm được dây sạch xuyên suốt khoảng sống. Bản Python tương đương dùng làm mốc kiểm tra trước khi đo lợi ích.
- **Ủng hộ hoặc bác bỏ.** Kiểm tra weight 0, 1, 35, tụt bậc và syndrome đầu bằng zero, vị trí biên và mask runtime khác nhau. Lỗi value, phase hoặc workspace bác bỏ lịch cổng. Sau kiểm tra thành phần, ứng viên phải dev PASS với điểm thấp hơn V5 trên cùng harness, seed, profile và số shots. Chỉ số operation count hoặc runtime thấp hơn không đủ để ủng hộ giả thuyết về điểm.
- **Điều kiện dừng.** Giới hạn ở một bản tham chiếu Python và một lịch tối ưu của cặp synthesis. Nếu chưa khớp được giao diện hoặc không tìm được tiết kiệm có chứng chỉ đủ bù chi phí, ghi lại kết quả và dừng ở khối này. Thay converter hoặc ghép decoder khác cần mở rộng phạm vi riêng.
- **Kiểm tra ứng viên cuối.** Sau dev, owner chạy full 102.400 shots hoặc dùng bộ seed giữ lại có đối chứng chạy cùng điều kiện. Dùng thêm ca biên và kiểm phase/cleanup của thành phần. Dev không thay thế kiểm tra bổ sung.

## Kết luận và phiên bản tái lập

Cả dev_5min và full đều PASS, 0 lỗi value và phase trên lần lượt 4.096 và 102.400 shots. Hai run khớp build qua hash artifact và source/config snapshot. Dev profile v1, seed `20261106` và cùng số shots cho đúng tài nguyên và điểm của V5 đã chấm trước đó. Full dùng verifier chính thức với seed mặc định suy từ hash mạch, nên cùng binary cũng dùng cùng seed mặc định. V5 được tái lập ở cấp binary. Giả thuyết giảm Toffoli của synthesis vẫn chưa có ứng viên được kiểm chứng.

Mạch dùng 892 qubit, 395.593 Toffoli-like tĩnh, trung bình khoảng 395.307 ở dev và 395.308 ở full. Chênh lệch score giữa hai mode chủ yếu đến từ repetition factor (2,9848 và 1,1913), vì số shots khác nhau ảnh hưởng cận trên xác suất lỗi.

### Đối chứng DQI-BASELINE chạy lại cục bộ

| Mode | Run baseline cục bộ | Score baseline | Score DQI-39 | Baseline / DQI-39 |
| --- | --- | ---: | ---: | ---: |
| dev_5min | `20261110T033155Z-local-dev_5min-4cf478` | 61.234.661.450.380,1 | 938.805.873.038,7448 | 65,2261× |
| full | `20261110T033335Z-local-full-fc3712` | 24.439.467.666.108,316 | 374.690.051.360,2488 | 65,2258× |

Cả hai mạch đều PASS với 0 lỗi value/phase trong mỗi mode. Metadata hai phía khớp Python 3.13.7, phiên bản package và toàn bộ bảng hash verifier. Hai run dev còn khớp hash harness, profile v1, seed `20261106` và 4.096 shots. Hai run full dùng cùng thiết lập 102.400 shots và seed mặc định suy từ hash của từng mạch, nên mẫu full khác nhau. Baseline dùng 1.893 qubit và khoảng 5,725 triệu Toffoli-like trung bình. Ở dev, tỷ số khoảng 65,23× đến từ hệ số 4,50× của `Q²` và 14,48× của `T`, với cùng repetition factor.

Artifact baseline chạy lại có SHA-256 `5dfb9991335e41f709a2b2cd0c1e8b28f5ad50e9672b11539d77480b39e9f98f`, khác artifact lịch sử, và các run mới chưa có provenance build. Các tỷ số trên dùng làm tham khảo cục bộ cho V5 đã tái lập. Hàng DQI-BASELINE trong SCORES.md vẫn dẫn các run lịch sử, nên cột cải thiện chính thức của DQI-39 để trống.

### Quyết định sau bước 04

Dừng ở `rank42_reference` theo điều kiện dừng đã đặt trước và chuyển sang chuẩn bị review. Phạm vi bàn giao là tái lập V5 và bộ sinh nhân-cộng. Giả thuyết giảm chi phí synthesis chưa có ứng viên để chấm. Việc đổi cách sinh cùng tensor hoặc hủy thêm CNOT không tạo lợi ích (Q^2T). Các phase fold local đã đo giảm khoảng 3,47 Toffoli trung bình, tương đương 0,00088% ở cùng Q và repetition factor.

Ưu tiên một hypothesis riêng về ghép giao diện synthesis/conversion và chiều đảo. Audit xem biểu diễn trung gian nào chỉ dùng ở giao diện và có thể được truyền trực tiếp vào converter, bỏ các phép nhân hoặc tái dựng rồi xóa biểu diễn đó. Đo tổng chi phí của cả hai chiều, giữ mask runtime và scan, kiểm đúng locator, dữ liệu converter, khôi phục syndrome và pha ở weight 0/1/29/33/35 và tụt bậc. Dùng [note Kirill đã review và merge](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/c4d8b66974ee7bc958d9adf7a1505eac3e7b249e/research/dqi/discussions/kaggle-kirilltym-conditional-uncompute-audit/note.md) cho mốc phân rã: cặp synthesis khoảng 72.000 Toffoli tĩnh, cả bốn stage synthesis/conversion khoảng 195.000 trên bản local chỉ ghép phase fold. Các số tĩnh này dùng để định vị chi phí.

Mốc sàng lọc đề xuất trước khi compile biến thể mới là khoảng 20.000 Toffoli trung bình tiết kiệm được (~5,1% proxy ở 892 qubit, nếu lỗi và repetition factor giữ nguyên). Mốc tham khảo 80× cần khoảng 322.300 Toffoli trung bình ở cùng Q và repetition factor, tức giảm khoảng 73.000 so với V5, xấp xỉ toàn bộ cặp synthesis hiện tại. Sau kiểm tra thành phần, so dev trên cùng profile/seed và đánh giá full riêng, do hash mạch mới đổi seed mặc định. Chưa có ước lượng chi phí đã đo cho phép ghép.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | [rank42_reference](configs/rank42_reference.json) | `cde21590a4027faf0950ea087e21d3516d405f21` | [20261110T031338Z-local-dev_5min-92db22](../../../results/dqi/DQI-39/rank42_reference/dev_5min/20261110T031338Z-local-dev_5min-92db22/verifier.json) · [provenance](../../../results/dqi/DQI-39/rank42_reference/dev_5min/20261110T031338Z-local-dev_5min-92db22/provenance.json) |
| Full | [rank42_reference](configs/rank42_reference.json) | `cde21590a4027faf0950ea087e21d3516d405f21` | [20261110T031736Z-local-full-f7e2d6](../../../results/dqi/DQI-39/rank42_reference/full/20261110T031736Z-local-full-f7e2d6/verifier.json) · [provenance](../../../results/dqi/DQI-39/rank42_reference/full/20261110T031736Z-local-full-f7e2d6/provenance.json) |

Điểm và các run xem trong [SCORES.md](../SCORES.md).

## Cấu hình bước 03

[rank42_reference](configs/rank42_reference.json) dùng [bộ sinh Python](solution.py) để nhận dạng các khối nhân-cộng 42 Toffoli trong cả hai chiều. Mỗi khối được mô tả bằng ba word 12-bit rời nhau và 42 hạng song tuyến tính. Mỗi hạng dùng CNOT để đưa parity hai toán hạng vào hai dây trụ và đổi cơ sở đầu ra, sau đó dùng một CCX rồi hoàn nguyên CNOT. Toàn khối thực hiện `out ^= left * right` với hai toán hạng giữ nguyên. Vì ánh xạ là song tuyến tính, kiểm trên cả 144 cặp bit cơ sở đủ để xác nhận tensor so với phép nhân GF(2^12) của Kickmix.

Kiểm trên gate stream cục bộ nhận diện và sinh lại 734 khối thuận và 801 khối đảo. Đối chiếu từng lệnh sau sinh trên cả 1.535 khối. Mọi phần điều tuyến, history, phép đo và sửa pha bên ngoài khối nhân tiếp tục dùng dữ liệu cổng V5. Phạm vi tái dựng ở cấp phép nhân chưa thay cho việc khôi phục toàn bộ thuật toán locator. Các kiểm tra cục bộ về hai tích lặp qua CNOT và điều kiện điều khiển affine chưa tìm được lịch giảm Toffoli có chứng chỉ trong phạm vi đã kiểm tra.

Cấu hình này là mốc tham chiếu để kiểm chứng phần Python. Build yêu cầu file V5 đúng SHA-256 trên và tự kiểm hash đầu ra. Nếu khớp byte, số qubit, Toffoli và điểm của cùng profile/harness sẽ khớp đối chứng. Không dùng config này làm bằng chứng giảm điểm hoặc làm ứng viên đã chấm chính thức. Chỉ mở lịch tối ưu nếu tìm được cách giảm chi phí của cặp synthesis và giữ đúng giao diện.
