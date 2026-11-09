# Kaggle discussion 757068 — Bản tin RezOps về ba bài thi

- Bài đăng của [manwithacat](https://www.kaggle.com/manwithacat), soạn bởi RezOps theo lời người đăng. Hiển thị thời gian đăng 09/11/2026 lúc 01:53:30 (UTC+7).
- [Permalink bài đăng và ID 757068](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/757068)
- Snapshot ngày 09/11/2026, bản diễn giải tiếng Việt của nội dung hiển thị. Giao diện có 0 bình luận.
- Cửa sổ bản tin 07/11 18:51 đến 08/11 18:50 UTC. Tác giả phân biệt quan sát leaderboard, kết quả do tác giả notebook báo, kết quả nhóm RezOps tự chạy lại verifier và ước tính qua nhiều lần lấy mẫu.

## Mục 1 và 2 — Leaderboard và mốc công khai

Ở snapshot leaderboard ngày 08/11 lúc 18:09 UTC, điểm đầu bảng vẫn là 29,30100. Hai nhóm lớn tụ quanh 25,1477. Giá trị 25,1409 trong mục 2 là trung bình nhân do RezOps tính từ chi phí mốc công khai của ba bài, với DQI lấy mean qua 48 draw. Đó là một phép dự phóng riêng, khác giá trị trên leaderboard.

| Track | Mốc nhóm RezOps báo | Cơ sở được nêu |
| --- | --- | --- |
| Invsqrt | `1c5b1ee28290`, 62 qubit, chi phí 95.368,95 | Mạch maoxin123 v3, báo đã chạy lại verifier. |
| DQI | `2c94a1d57125`, 892 qubit, chi phí trung bình khoảng 3,7504 × 10¹¹ | Mốc Syed Asad Ali v10, trung bình 48 draw cố định theo phương pháp nhóm. |
| Hóa học | `cfe4e821ff6e`, 427 qubit, chi phí 2,99657 × 10⁸ | Word góc và loader của Syed Asad Ali kết hợp trọng số maoxin123, λ_eff 46,89113. |

## Mục 3 — Thay đổi và kết quả âm

- **Invsqrt.** RezOps quy việc bỏ controlled swap dư trên miền hợp lệ cho [Atakan Aldemir v2](https://www.kaggle.com/code/atakanaldemir/qcc-early-measurement-and-domain-aware-inverse). Theo bản tin, [Hosen v6–v7](https://www.kaggle.com/code/hosen42/vqcc-our-submission) gộp 11 lần ghi vào một dây đã về 0 sau đo thành một CCX ngay trước lần đọc duy nhất. maoxin123 v3 ghép thay đổi đó với việc chia cửa sổ uncompute Block 4 theo hai bit đo. [Audit của Kirill Tymchishin](https://www.kaggle.com/code/kirilltym/quantum-circuits-conditional-uncompute-audit) được dẫn cho bốn cửa sổ nhánh và các ca âm. Bản tin báo mỗi bước trong chuỗi giảm một Toffoli mỗi shot và đã kiểm lại đủ 3.133.452 đầu vào bằng verifier chính thức.
- **DQI.** `4432ec5fd63d` và mạch bốn tuyến `f277b054af21` của Heliosli v26 lưu thêm tích trên dòng mạch Syed Asad Ali. RezOps nêu `4432ec5fd63d` đạt khoảng 3,747 × 10¹¹ ở salt mặc định, nhưng ba file mới trung bình khoảng 3,7506–3,7507 × 10¹¹ qua 48 draw, so với 3,7504 × 10¹¹ của mốc. maoxin123 báo một shot lỗi ở mỗi salt s2, s3 cho `4432ec5fd63d`. Bài dẫn [notebook prvsiyan](https://www.kaggle.com/code/prvsiyan/verifier-guided-quantum-circuit-optimization) về cách đọc ảnh hưởng của số shot lỗi.
- **Hóa học.** Refit W và H₂ᴵ giữ word góc và loader cố định, từ λ_eff 46,89128 xuống 46,89113 theo bản tin. maoxin123 báo mốc λ_eff ≥ 46,8497 khi cố định word và thử giảm nhóm/tăng bản sao: cấu hình (7, 143, 54) cho 18,7 mHa trước làm tròn, so với 14,2 của (8, 143, 45), rồi không qua ngưỡng 20 mHa sau làm tròn theo báo cáo được dẫn.

## Mục 4–6 — Góc nhìn của tác giả

- Mục 4 dẫn [thread 757030](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/757030) về các câu hỏi mở cho ba bài, các trao đổi về bài nào còn dư địa, số nhân song tuyến tính và giải thưởng. Bản tin trình bày mức quanh 62 qubit của invsqrt như kết quả phụ thuộc thiết kế đã xét.
- Mục 4b nêu một shot lỗi DQI có thể làm đổi điểm tổng khoảng 0,15% ở mốc đang xét, lớn hơn chênh lệch giữa nhiều nhóm đồng điểm. Dự báo private draw của RezOps dùng 48 lần lấy mẫu. Mục 4c theo dõi giải thưởng từ snapshot leaderboard.
- Mục 5 liên kết [dataset](https://www.kaggle.com/datasets/manwithacat/vqcc-apache-public-circuits) và [notebook ghép mạch](https://www.kaggle.com/code/manwithacat/the-real-150k-was-the-friends-we-made) của nhóm. Mục 6 đưa ra ý kiến rằng kiến trúc invsqrt mới có thể mang lại mức giảm lớn hơn các chỉnh sửa nhỏ trên mạch hiện có.

Chưa đọc trực tiếp các notebook, artifact, thread khác hoặc bản ghi chạy mà bài đăng dẫn. Các định danh mạch là tiền tố do tác giả hiển thị.
