# [DQI-47] Ghép synthesis và converter của V5 bằng biểu diễn locator/evaluator dùng chung, giữ nguyên quét pha

**Loại** — Kết hợp các khối của V5 bằng biểu diễn chung.

## Các file gốc và thành phần kế thừa

Đối chứng là [DQI-39 rank42_reference](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/83ad82f2206e5b7c3be60c47ad8c43fff5b30e4c/src/dqi/DQI-39/DESCRIPTION.md), source build `cde21590a4027faf0950ea087e21d3516d405f21`. Input V5 có SHA-256 `4e9b50b1ee34b3eaf2b7f394873c2dd3dad4cddbdd1f12a348b4323b5eb41771`. Bản này tái sinh 734 phép nhân-cộng rank-42 ở synthesis và 801 phép ở unsynthesis, với gate stream và binary giữ nguyên. Hai lượt dev/full đều PASS 0 lỗi. [Note Kirill đã review và merge](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/83ad82f2206e5b7c3be60c47ad8c43fff5b30e4c/research/dqi/discussions/kaggle-kirilltym-conditional-uncompute-audit/note.md) pin artifact và báo khoảng 195.261 Toffoli-like tĩnh cho synthesis, conversion và hai chiều đảo trên bản local phase-folded. Đo riêng lại trên đúng V5 trước khi thay cổng.

Kế thừa tensor và detector cửa sổ nhân-cộng của [DQI-39 solution](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/cde21590a4027faf0950ea087e21d3516d405f21/src/dqi/DQI-39/solution.py) để nhận diện các phép dùng chung. Không thay extraction, scan, mask projection, reverse extraction hoặc verifier. Khác DQI-39, mục tiêu là tránh các phép tạo biểu diễn trung gian ở biên synthesis/conversion. Khác [DQI-43](https://github.com/nhphan0505/verifiable-quantum-circuit/issues/43) và [DQI-45](https://github.com/nhphan0505/verifiable-quantum-circuit/issues/45), đầu vào là V5 đã chấm, không phải Schur Narrow Return của repo.

## Cách kết hợp

1. Tách bốn đoạn theo marker synthesis/convert/unconvert/unsynthesis. Dùng log read/write để lập danh sách dây sống, lệnh ghi cuối trước biên và lần đọc đầu sau biên. Phân riêng các word hệ số, control bit, history và scratch theo bằng chứng. Đối chiếu cả output biên trước scan và input trước unextract.
2. Chọn một biểu diễn trung gian được tạo riêng cho converter. Tìm cặp tính/chuyển hoặc tái tạo giá trị mà có thể hấp thụ vào consumer. Nếu đổi basis tuyến tính, suy ma trận bit bằng propagation GF(2), đưa basis change vào các parity của tensor rank-42 và kiểm tra trên 144 cặp bit cơ sở. Nếu quy tắc dựa vào locator chuẩn hóa hoặc reciprocal, viết đẳng thức trên miền reachable, kiểm no-error và degree drops trước khi chuyển thành gate schedule. Chỉ bỏ phép nhân nếu chứng minh phép đó dư thừa trên mọi nhánh được thay. CNOT giảm riêng không đủ để đổi score.
3. Sinh forward và reverse cho cửa sổ thay đổi. Với output hoặc workspace cũ còn được đọc ở bất kỳ nhánh nào, giữ biểu diễn cũ hoặc cung cấp phép tái tạo cùng phase. Dùng cùng thứ tự bit, GF(2^12), primitive element và basis của V5. Nếu dùng phép đo X, chứng minh hiệu chỉnh phase theo outcome và dữ liệu còn sống. Tính đủ chi phí dựng lại, cờ, phép nhân có control và peak của cả hai chiều. Không coi một wire là sạch chỉ vì bằng zero trong vài mẫu.

## Xử lý chỗ không tương thích

Interface scan cố định gồm locator, evaluator, mask runtime và các điều khiển đọc ở biên. Đối chiếu bit-for-bit các dây còn sống tại scan và trước unextract. Phần thay đổi phải giữ parity trên 4.095 vị trí, phục hồi đủ 70 syndrome word và xóa workspace. Không có cutoff bậc hoặc bỏ mask tĩnh. Phân biệt kiểm toán gate stream, mô hình đại số và bằng chứng cho oracle coherent. Nếu cần input .kmb để build, pin hash V5 và giữ binary ngoài Git.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: DQI-39 rank42_reference ở source/hash trên, 892 qubit và khoảng 395.307 Toffoli-like trung bình ở dev. Profile v1, seed 20261106, 4.096 shots. Dev và full có link provenance trong mô tả DQI-39.
- Dự đoán: ít nhất một biểu diễn có thể dùng chung, giảm field work ở cả hai chiều. Định mức khoảng 20.000 Toffoli-like tiết kiệm ở 892 qubit là ngưỡng sàng lọc, không phải số đã đo. Với Q tăng, so proxy toàn mạch và tính đủ peak.
- Ủng hộ: chứng chỉ đúng cho cửa sổ thay đổi, các ca biên weight 0/1/29/33/35, degree drops, random runtime masks và nhiều HMR outcome. Sau component, chấm dev theo cùng harness, profile và seed, không có value/phase errors và score thấp hơn V5. Full hoặc bộ seed giữ lại dành cho ứng viên cuối.
- Điều kiện dừng: audit hai biên và một đường biểu diễn. Nếu chưa tìm được phép thay thế có chứng chỉ và budget, dừng trước submission build. Ghi rõ những mẫu đã loại và dữ liệu cần thêm để mở lại. Không dựng lại V5 như một ứng viên mới chỉ để có artifact.

## Kết luận và phiên bản tái lập

Chưa đo ứng viên. Bước đầu là audit giao diện và chọn một phép biến đổi có thể tính đủ chi phí.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa chọn | Chưa có | Chưa chấm |
| Full | Chưa chọn | Chưa có | Chưa chấm |
