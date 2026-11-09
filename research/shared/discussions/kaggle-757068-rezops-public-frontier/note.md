# Bản tin RezOps 757068 — tối ưu sát mốc công khai của ba bài

Status: ready
Track: shared
Source: https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/757068
Version: snapshot 2026-11-09

- Bài của [manwithacat](https://www.kaggle.com/manwithacat), do RezOps soạn theo lời người đăng. Cửa sổ bản tin kết thúc 08/11/2026 lúc 18:50 UTC.
- Đã đọc toàn bộ mục hiển thị, với 0 bình luận lúc chụp. [Snapshot diễn giải](source.md) và [metadata](source.json).

## Câu hỏi và bối cảnh

Bản tin đặt cạnh nhau ba cải thiện nhỏ trên mạch công khai. Câu hỏi đối với repo là cách phân biệt lợi ích của một thay đổi mạch với biến thiên do draw của verifier, hoặc với giới hạn của một thiết kế cụ thể. Bài tách quan sát leaderboard, báo cáo của tác giả notebook, kết quả RezOps báo đã chạy lại và chi phí DQI trung bình 48 draw. Điểm 25,1409 là dự phóng ghép chi phí của ba bài. [Bài 757068, mở đầu và mục 1–2](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/757068).

## Các phương án và lập luận

| Phương án | Cơ chế và bằng chứng được bài dẫn | Điều kiện và câu hỏi |
| --- | --- | --- |
| Invsqrt — bỏ swap và gom ghi trước lần đọc | RezOps dẫn Atakan v2 bỏ controlled swap trên miền hợp lệ. Hosen v6–v7 dùng một CCX cho giá trị tại lần đọc duy nhất của dây đã được đo. maoxin123 v3 ghép thêm chia uncompute Block 4 theo hai bit đo. Bản tin báo nhóm chạy lại đủ 3.133.452 đầu vào, với mốc 62 qubit và chi phí 95.368,95. | Cần chứng minh swap dư trên đúng miền và kiểm mọi truy cập xen giữa của dây gộp ghi. Hai bit đo tạo bốn trường hợp. Audit phải kiểm pha và ancilla sạch ở từng nhánh, kể cả nhánh sửa pha. Mốc 62 qubit phụ thuộc thiết kế đang xét. [Bài 757068, mục 2–4](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/757068) |
| DQI — lưu thêm tích trên dòng Syed Asad Ali | Bản tin nêu file `4432ec5fd63d` có chi phí khoảng 3,747 × 10¹¹ ở salt mặc định. Ba file mới trung bình khoảng 3,7506–3,7507 × 10¹¹ trên 48 draw, so với 3,7504 × 10¹¹ của mốc `2c94a1d57125`. | maoxin123 báo một shot lỗi ở mỗi salt s2, s3 cho file trên. Bài thiếu số từng draw để tính độ bất định hoặc xác nhận hai phía dùng cùng mẫu. Chênh lệch mean nhỏ theo độ chính xác được công bố. [Bài 757068, mục 2–3 và 4b](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/757068) |
| DFTHCSOS — refit trọng số với word và loader cố định | Bản tin nêu λ_eff giảm từ 46,89128 xuống 46,89113, với mốc ghép 427 qubit và chi phí 2,99657 × 10⁸. | Theo báo cáo maoxin123 được dẫn, cận ở bộ word cố định là 46,8497. Cấu hình (7, 143, 54) đạt 18,7 mHa trước làm tròn rồi trượt ngưỡng 20 mHa sau làm tròn. Cần đo lại với word sau lượng tử hóa. Cận phụ thuộc bài toán fit và bộ word cụ thể. [Bài 757068, mục 2–3](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/757068) |

### Đối chiếu với project

- **Invsqrt.** [Verifier](../../../../verifiers/invsqrt/verify_submission_invsqrt.py) tính chi phí qubit nhân Toffoli-equivalent, gồm chi phí tổng hợp phép quay theo dung sai còn lại. [INV-3](../../../../src/invsqrt/INV-3/DESCRIPTION.md) là tiền lệ rút khoảng sống và kiểm trạng thái sạch qua các nhánh HMR trên mạch riêng của repo.
- **DQI.** [Verifier](../../../../verifiers/dqi/verify_submission_dqi.py) dùng $R(ε_+)·Q^2·T$. Cận lỗi một phía $ε_+$ ảnh hưởng $R$ dù số qubit $Q$ giữ nguyên. Mức khoảng 0,15% trong mục 4b là ước tính điểm tổng tại mốc bài viết. [DQI-25](../../../../src/dqi/DQI-25/DESCRIPTION.md) đo giảm 1.332 mean Toffoli-like ở cùng profile dev và $Q=1893$, với đối chứng riêng của repo.
- **DFTHCSOS.** [Tài liệu verifier](../../../../verifiers/dfthcsos/SCORING_README.md) tính $λ_{eff}·T_{total}·Q_{total}$ sau kiểm factorization và ANGLES. Có thể tách ảnh hưởng của refit lên $λ_{eff}$ nếu xác minh lại word, các điều kiện sai số và cả hai hệ số tài nguyên. Nếu shape hoặc layout đổi, cần đếm lại chi phí.

**Kiểm lại chênh lệch DQI.** Chia các mean làm tròn trong bản tin cho mốc `3,7504 × 10¹¹` cho mức tăng khoảng 0,005–0,008%. Đây là phép tính lại từ số công bố. So sánh theo verifier của repo cần cùng cấu hình, số shot và bộ đầu vào đã xác định, đồng thời báo riêng số lỗi, $Q$ và mean $T$. Mean của tích $R·Q^2·T$ qua nhiều draw có thể khác tích tính từ các thành phần trung bình.

## Kết luận hiện tại

RezOps báo một ví dụ cache DQI đổi thứ hạng giữa một salt và mean nhiều draw. Kết quả âm về hóa học cho thấy cấu hình sát ngưỡng trước làm tròn có thể trượt sau làm tròn. Giao diện hiển thị 0 phản hồi, nên chưa có phản biện trực tiếp trong thread. Các điều kiện ở bảng là phân tích của note hoặc kết quả âm được người đăng dẫn lại.

## Hypothesis đề xuất và kiểm chứng tiếp

Nếu tìm được một cửa sổ invsqrt có dây sạch sau đo và chỉ một lần đọc sau chuỗi ghi, gộp ghi có thể giảm Toffoli. Điều kiện là chứng minh biểu thức Boolean tại lần đọc, không có truy cập xen giữa và giữ pha cùng cleanup trên từng nhánh đo. Đối chứng giữ phép gần đúng, ngân sách phép quay và cấu hình verifier. Bác bỏ nếu có truy cập xen giữa, sai pha hoặc scratch bẩn. Chưa xác định được cửa sổ cụ thể trong repo.

## Liên kết triển khai và câu hỏi còn mở

- [INV-3](../../../../src/invsqrt/INV-3/DESCRIPTION.md) và [DQI-25](../../../../src/dqi/DQI-25/DESCRIPTION.md) có kết quả repo cho cơ chế liên quan. Chưa có run repo cho các file được nêu trong 757068.
- Chưa mở notebook, artifact hoặc thread liên quan. Còn thiếu chi tiết từng draw DQI, hash đầy đủ và cấu hình chạy lại của bên đăng. Phạm vi ghi trong [source.json](source.json).
