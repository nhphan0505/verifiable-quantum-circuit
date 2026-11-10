# Kiểm chứng readout và phase fold trong DQI 892 qubit của Kirill

Status: ready
Track: dqi
Source: https://www.kaggle.com/code/kirilltym/quantum-circuits-conditional-uncompute-audit
Version: Kaggle notebook 140275987 v6, V5 output scriptVersionId 367172760

- Từ khóa: Schur, terminal X readout, phase fold, reverse extraction, paired verification.
- Đọc mục readout, full verification, receipts và attribution DQI của notebook ngày 2026-11-10. [Snapshot](source.md) · [Audit v6](https://www.kaggle.com/code/kirilltym/quantum-circuits-conditional-uncompute-audit)

## Câu hỏi và bối cảnh

V5 là mốc để đánh giá tối ưu score trên một decoder khoảng 395 nghìn cổng. Audit so sánh V5 với bản V6 tái dựng từ Atakan. Cần tách khác biệt giữa hai binary này khỏi khoảng cách giữa V5 và bản ghép Schur/Bézout 882 qubit do Alex Chilton công bố. Verifier tính chi phí từ qubit, mean Toffoli-like và hệ số lặp theo lỗi. [Verifier DQI](../../../../verifiers/dqi/verify_submission_dqi.py) · [Bản 882 qubit](https://www.kaggle.com/datasets/alexchilton/qcc-schur-dqi-rebuild/versions/5)

## Các phương án và lập luận

| Bản | Thiết kế và số nguồn báo | Giới hạn |
| --- | --- | --- |
| **Alex Chilton / Özer / mrmeows, 882 qubit** | Phép ghép cụ thể giữa dòng Schur CF của jday96314, khối pha Bézout round 17 và mask projection được Özer tích hợp, cùng reverse synthesis thu hẹp scratch của Chilton. Dataset báo 519.152 Toffoli và cost khoảng 4,8519 × 10¹¹. | Đây là binary riêng, SHA-256 bắt đầu `545189b9`. Phép đếm tĩnh local là 519.157. Chưa có phân rã stage ghép cặp với V5 để quy riêng phần tiết kiệm cho từng thay đổi. [Dataset](https://www.kaggle.com/datasets/alexchilton/qcc-schur-dqi-rebuild/versions/5) |
| **Kirill V5, 892 qubit** | Dùng dòng decoder đã có các tối ưu upstream và bốn cửa sổ terminal readout theo V70. Receipt báo 395.593 Toffoli-like tĩnh, 395.308,2494 trung bình và full cost 374.690.183.327,03, 0 lỗi. | Phần lớn chênh lệch với bản 882 qubit đã có ở V5. Audit ghi công các thành phần và xác định binary, còn mức tiết kiệm riêng của từng stage so với bản Chilton chưa được đo. [V5](https://www.kaggle.com/code/kirilltym/quantum-circuits-conditional-uncompute-audit?scriptVersionId=367172760) |
| **Kirill V6 / Atakan V1, 892 qubit** | Đổi thứ tự phép đo X trên 48 cặp, remap outcome và sửa pha theo outcome. Bảy phase fold giảm Toffoli-like tĩnh xuống 395.586. Receipt báo 395.304,6741 trung bình và full cost 376.407.597.314,35, một lỗi phase. | Hai full run dùng draw khác nhau. Kiểm ghép cặp MPS báo riêng 2.048 trajectory và không xác định xác suất lỗi toàn miền. Audit ghi các value counterexample thừa kế ở trọng số 29 và 33. [Audit v6](https://www.kaggle.com/code/kirilltym/quantum-circuits-conditional-uncompute-audit) · [Atakan V1](https://www.kaggle.com/code/atakanaldemir/qcc-terminal-readout-and-phase-folds?scriptVersionId=367191797) |

Với hai dây đi thẳng tới X readout, đổi basis của cặp outcome bằng XOR và trả pha điều kiện theo bảng ánh xạ. Không áp dụng ở nơi còn truy cập lượng tử sau biên terminal. Với phase fold, `CCX(a,b,t)` trước và sau `CZ(c,t)` đưa target về giá trị ban đầu. Pha có số mũ `c(t XOR ab) = ct XOR abc`, nên có thể thay bằng `CZ(c,t)` và `CCZ(a,b,c)` trên bốn dây phân biệt, kể cả khi target ban đầu khác zero. [Derivations](https://www.kaggle.com/code/kirilltym/quantum-circuits-conditional-uncompute-audit)

## Kết luận hiện tại

Các binary V5, V6 đã được đối chiếu hash và đếm tĩnh bằng Kickmix 1.0.0. Bản local V5 chỉ ghép bảy phase fold giữ lịch readout V5, có hash bắt đầu `857afdb2` và 395.586 cổng tĩnh. Phép chấm dev do thành viên chạy với cùng seed 20261106 và 4.096 shots cho cả V5 và bản chỉ ghép fold đều 0 lỗi, giảm 3,469 mean Toffoli-like. Đây là kết quả local của ablation, riêng với receipt V6.

Đọc marker của bản local chỉ ghép fold cho các số tĩnh sau. Extraction 59.169, reverse extraction 96.881, synthesis 31.635, reverse synthesis 40.429, conversion 60.663, reverse conversion 62.534 và scan 44.275. Các phần cộng thành 395.586. Hủy CNOT local giảm số instruction nhưng giữ nguyên T, Q và điểm dev. Các kết quả này là đối chiếu local, không phải số stage do Kirill công bố.

## Hypothesis đề xuất và kiểm chứng tiếp

Đo một giao diện synthesis/conversion ghép và chiều đảo của nó, giữ nguyên mask runtime, pha và khôi phục syndrome. Bốn stage liên quan hiện tốn 195.261 cổng tĩnh. Đây là đối chứng để đánh giá khả năng giảm phép nhân trường, còn chi phí của thiết kế mới cần được đo. Với ablation terminal readout hoặc fold, dùng cùng seed và ghi riêng lỗi, mean T, Q và chi phí. Kiểm thêm ca trọng số 29, 33, 35, locator hằng và tụt bậc.

## Liên kết triển khai và câu hỏi còn mở

- [ZIP V5 đã pin theo version](https://www.kaggle.com/api/v1/kernels/output/download/kirilltym/quantum-circuits-conditional-uncompute-audit/submission.zip?versionNumber=5) · [Heliosli v84 cho V6](https://www.kaggle.com/datasets/heliosli/qcc-circuits-live/versions/84). Hash đầy đủ nằm trong snapshot.
- Chưa tái dựng generator decoder hay đo mức tương đương tại biên giữa hai kiến trúc. Chưa chấm full ghép cặp cho các binary local trong đợt tài liệu này.
