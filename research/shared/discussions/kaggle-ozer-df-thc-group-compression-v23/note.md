# Özer v23: refit trọng số FeMoCo, tái dùng tích DQI và chuyển khối pha invsqrt

Status: ready
Track: shared
Source: https://www.kaggle.com/code/ahmedberatozer/quantum-ai-df-thc-group-compression?scriptVersionId=366387300
Version: Kaggle v23 (scriptVersionId 366387300)

- Ahmed Berat Özer, truy cập 08/11/2026. Snapshot gồm nội dung Markdown diễn giải và output của ba cell hiển thị. [Notebook v23](https://www.kaggle.com/code/ahmedberatozer/quantum-ai-df-thc-group-compression?scriptVersionId=366387300) · [Snapshot](source.md)

## Câu hỏi và bối cảnh

Notebook thử ba thay đổi nhỏ trên portfolio của maoxin123 sau khi thay DQI bằng tệp 17 tuyến của Atakan Aldemir. Bảng Markdown ở salt mặc định báo trung bình nhân local tăng từ 24,94137 lên 24,94165. Output tại salt `notebook-verification` ghi cả ba bài PASS và trung bình nhân hiển thị là 24,9416. Điểm public 23,94701 trên giao diện thuộc v22. [Notebook v23, mục Results of this run và What changed from the base](https://www.kaggle.com/code/ahmedberatozer/quantum-ai-df-thc-group-compression?scriptVersionId=366387300)

## Các phương án và lập luận

| Bài | Biến đổi và kết quả nguồn báo cáo | Điều kiện và đánh đổi |
| --- | --- | --- |
| **DFTHCSOS** | Giữ bảng (8, 143, 44), word góc và 15 loader của Syed. Refit W và H2_I bằng SQP theo khối, sau đó dùng Newton trên mặt ràng buộc đang hoạt động. λ_eff giảm 46,8927604 → 46,8925932. Output ghi 427 qubit, 14.966 Toffoli và chi phí 299666272.9739243. [Notebook, mục FeMoCo chemistry](https://www.kaggle.com/code/ahmedberatozer/quantum-ai-df-thc-group-compression?scriptVersionId=366387300) | Hai sai số đều 19,999997 mHa và gap 3,914898003 Ha theo nguồn. So với ngưỡng verifier trong repo, biên hiển thị của mỗi điều kiện khoảng 3 × 10⁻⁹ Ha. Cần số chưa làm tròn và cùng môi trường để đánh giá độ ổn định của biên. Lượt Newton cuối vẫn cải thiện theo tác giả. |
| **DQI** | Chuyển bốn chuỗi tái dùng tích của MAIDANG/daifanhao vào tệp 17 tuyến của Atakan. Giữ tích trên dây rảnh giữa hai lượt dùng và thay lần tính thứ hai bằng Clifford cùng uncompute qua đo. Toffoli tĩnh giảm 395.662 → 395.658 ở 892 qubit. Bản bốn chuỗi có 0 lỗi ở hai salt. Bản bảy tuyến tiết kiệm thêm cổng nhưng có một lỗi giá trị và một lỗi pha ở salt mặc định. [Notebook, mục DQI](https://www.kaggle.com/code/ahmedberatozer/quantum-ai-df-thc-group-compression?scriptVersionId=366387300) | Tác giả báo kiểm đồng nhất thức pha, tính rảnh của dây và tương đương affine dưới 61 hằng đầu vào đã chứng minh. Trên tệp gốc, 48 lượt × 102.400 shot cho 13 lỗi. Đổi bytes mạch có thể đổi mẫu, nên kết quả hai salt chưa đủ để tách chênh lệch lỗi do đổi mẫu khỏi lỗi do rewrite. |
| **Invsqrt** | Khối pha chỉ hoạt động tại x = 4…15. Nếu mẫu pha cần thiết thuộc không gian sinh bởi bảy mẫu Z/CZ có sẵn về sau, mạch bỏ khối gốc và áp pha ở các dây còn sống. Trong 524.288 mask, 16.383 mask từng trả phí CCZ và được thay. Tác giả báo tiết kiệm kỳ vọng 16.383/524.288 Toffoli mỗi shot với cùng 62 qubit. [Notebook, mục Inverse square root](https://www.kaggle.com/code/ahmedberatozer/quantum-ai-df-thc-group-compression?scriptVersionId=366387300) | Cần bảo toàn pha trên mọi đầu vào và nhánh đo, gồm cả trường hợp giữ nguyên khối gốc. Chi phí đo giữa hai tệp có thể chênh nhẹ vì lượt lấy mẫu. Tác giả báo đã kiểm bằng BDD và DAG/SAT. |

## Kết luận hiện tại

- Repo dùng hash mạch và salt để lấy seed DQI khi không truyền seed tường minh. Một so sánh có seed ghép cặp hoặc bằng chứng tương đương theo từng đoạn giúp kiểm riêng tác động của rewrite lên lỗi. Với DFTHCSOS, repo kiểm hai sai số tối đa 0,020 Ha và sàn gap nghiêm ngặt 3,914898 Ha. [Verifier DQI](../../../../verifiers/dqi/verify_submission_dqi.py) · [Verifier DFTHCSOS](../../../../verifiers/dfthcsos/verify.py)
- Kết quả âm chỉ áp dụng trong phạm vi thử đã ghi. Tìm cục bộ quanh lookup invsqrt chưa hạ mốc 169 AND. Bảy tuyến DQI dùng hết dây rảnh trong mô hình cache trực tiếp. Thử C = 43 trên fit hiện có vẫn vượt ngưỡng error₂. Sàn λ_eff 46,8485 là kết quả relaxation số ở word cố định. [Notebook, mục What we measured this round](https://www.kaggle.com/code/ahmedberatozer/quantum-ai-df-thc-group-compression?scriptVersionId=366387300)

## Hypothesis đề xuất và kiểm chứng tiếp

- **DFTHCSOS.** Giữ nguyên word và loader, so refit bổ sung với trọng số v23 hoặc đối chứng đã định phiên bản. Dùng các giá trị đầy đủ để kiểm cả hai sai số và gap trước khi kết luận lợi ích λ_eff có thể tái lập.
- **DQI.** Kiểm từng tuyến cache về thời gian sống và pha qua phép đo. So các ứng viên với cùng panel đã chốt trước và tách Toffoli tĩnh khỏi số cổng trung bình cùng lỗi theo trọng số.
- **Invsqrt.** Thử bổ sung mẫu pha từ các dây còn sống. Kiểm điều kiện hoạt động trên toàn miền hợp lệ, pha theo từng mask và kỳ vọng số cổng trên mọi nhánh đo.

## Liên kết và câu hỏi còn mở

- [Mốc invsqrt](../../../../src/invsqrt/SCORES.md) · [DQI](../../../../src/dqi/SCORES.md) · [DFTHCSOS](../../../../src/dfthcsos/SCORES.md)
- PASS ở đây là output đã hiển thị trên Kaggle. Bước đọc tài liệu chưa chạy lại notebook hoặc kiểm độc lập các chứng minh và relaxation số. Tab bình luận nằm ngoài phạm vi đọc.
