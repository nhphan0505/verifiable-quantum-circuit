# Schur phân số liên tục và khối pha Bézout trong mạch DQI 882 qubit

Status: draft
Track: dqi
Source: https://www.kaggle.com/code/alexchilton/24-94-lb-verified-three-task-portfolio
Version: Kaggle notebook 140386665 v129, Schur rebuild dataset v5

- Từ khóa: Schur CF, reverse synthesis, destructive quotient, Bézout, scratch, phase scan.
- Phạm vi đối chiếu ngày 2026-11-10 gồm mục 3, phần ghi công và manifest DQI trong notebook, cùng mô tả và giấy phép của dataset v5. [Snapshot có hash](source.md) · [Notebook](https://www.kaggle.com/code/alexchilton/24-94-lb-verified-three-task-portfolio) · [Dataset v5](https://www.kaggle.com/datasets/alexchilton/qcc-schur-dqi-rebuild/versions/5)

## Câu hỏi và bối cảnh

DQI cần trả lại syndrome và scratch sạch sau khi áp pha theo mask cổ điển runtime. DQI-27 đạt 890 qubit, nhưng vẫn gọi nghịch đảo chuỗi tam giác trong extraction thuận và đảo, đồng thời tính nghịch đảo trường bên trong vòng quét Forney. Mạch công khai của dòng Schur CF là đối chứng để kiểm tra mức giảm có thể đạt khi đổi cách biểu diễn và lịch khôi phục trạng thái. [DQI-27](../../../../src/dqi/DQI-27/DESCRIPTION.md) · [Verifier](../../../../verifiers/dqi/verify_submission_dqi.py)

## Các phương án và lập luận

| Bản | Cách làm và kết quả nguồn báo | Phạm vi của bằng chứng |
| --- | --- | --- |
| **Schur CF dựng lại, 892 qubit** | Chilton ghi công jday96314 cho quadratic-extension Schur extraction. Synthesis cập nhật hai đa thức theo `(N,B) ← (l_i N + q_i B, N)`, với `l_i,q_i` là các hệ số hoặc đa thức của bước hiện tại. Nguồn mô tả phép chia tiêu thụ phần dư ở chiều đảo và scan 11 Toffoli/điểm sau khi chuẩn bị biên độ. Chilton báo 535.334 Toffoli cho bản dựng lại. | Mục 3 mô tả cơ chế và kết quả của bản dựng. Generator gốc trả HTTP 404 lúc đối chiếu, nên chưa xác nhận được invariant, lịch cổng và độ phủ các ca suy biến từ source. |
| **Schur CF, 883 qubit** | Chilton ghi sản phẩm thẳng vào đích, mượn dây output đã biết bằng zero trong kernel nghịch đảo và dùng phép đo X để thu hồi workspace của norm trong lúc scale. Báo 536.804 Toffoli, full PASS với một lỗi value và zero lỗi phase. Chi phí extraction được báo là 114.240 thuận và 132.685 đảo cho 595 cặp. | Chi phí theo chiều là của bản được mô tả trong mục 3. Chưa có phép đo theo stage trên binary 882 qubit ở dòng kế tiếp. |
| **Bản ghép 882 qubit, `dqi_oz882.qzip`** | Theo mô tả dataset, Özer ghép khối Bézout round 17 của mrmeows và mask projection vào dòng Schur. Chilton đưa reverse synthesis của mình trở lại, cho tích nhiều đích fanout qua đích đầu tiên để tiết kiệm một dây scratch. Dataset báo 519.152 Toffoli, PASS và cost khoảng 4,8519 × 10¹¹ ở salt mặc định. | Manifest notebook khớp SHA-256 của member `dqi.kmb` lấy từ dataset v5. Số 519.152 là số nguồn công bố. Đọc binary đã pin bằng Kickmix 1.0.0 cho **519.157 Toffoli-like tĩnh**. Hai con số được lưu riêng vì chưa xác minh được cách đếm của số công bố. |

[Notebook, mục 3 và manifest](https://www.kaggle.com/code/alexchilton/24-94-lb-verified-three-task-portfolio) · [Mô tả bản ghép và điều khoản dataset](https://www.kaggle.com/datasets/alexchilton/qcc-schur-dqi-rebuild/versions/5)

## Kết luận hiện tại

SHA-256 của public reference là `545189b999f49a4d226480df711fe66dbf996250a92dcc3fc42c4bad6ca65822`. Bản local `schur_affine_folds.kmb`, SHA-256 `9875ccfb6f48142fc06c84bd88e630054de735a04f8f39bd9444c6b5fc285c56`, giữ 882 qubit và giảm 20 Toffoli-like tĩnh qua tám cửa sổ dùng chung tích. Prototype local dùng CNOT để chia sẻ tác dụng của một CCX lên nhiều đích và kiểm tương đương giá trị lẫn pha cho từng cửa sổ bằng dạng chuẩn đại số Boolean.

Lượt full do thành viên chạy cho bản local khớp hash, PASS với 102.400 shots, 5 lỗi value, 0 lỗi phase, mean Toffoli-like 519.132,1768359375 và score 489.906.935.579,1366. Đây là kết quả local của binary phái sinh. Nguồn của phần giảm chi phí lớn so với DQI-27 là kiến trúc công khai. Chênh lệch score giữa bản local và số dataset báo chưa được kiểm bằng lượt đối chứng ghép cặp. Các file build và output local nằm ngoài phạm vi lưu của note này.

## Hypothesis đề xuất và kiểm chứng tiếp

Dùng public binary đã pin làm đối chứng trực tiếp cho các rewrite dùng chung tích, chứ không dùng DQI-27 để quy tác động của riêng 20 cổng. Chấm hai binary với cùng seed tường minh, cùng số shot và cùng verifier. So riêng lỗi value, lỗi phase, peak qubit, mean Toffoli-like và score. Nếu mở rộng qua biên phép đo, cần chứng minh wire cache sạch và hiệu chỉnh đúng pha theo outcome trên từng nhánh. Giữ riêng phép so theo seed ghép cặp và phép chấm full với thiết lập mặc định. [DQI-25 về liveness và cache tích](../../../../src/dqi/DQI-25/DESCRIPTION.md)

## Liên kết triển khai và câu hỏi còn mở

- Chưa truy cập được [generator được ghi công](https://github.com/jday96314/QuantumAI). Chưa tái dựng source, phân rã chi phí theo stage của binary 882 qubit hoặc chấm lại public reference trong đợt đọc này.
- Dataset ghi điều khoản theo từng thành phần và Apache-2.0 cho build scripts của Chilton. Điều khoản cụ thể của binary phái sinh cần được đối chiếu trước khi phân phối. [Dataset v5, phần giấy phép](https://www.kaggle.com/datasets/alexchilton/qcc-schur-dqi-rebuild/versions/5)
