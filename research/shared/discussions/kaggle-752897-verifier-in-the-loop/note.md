# Vòng lặp verifier trong tối ưu ba bài thi Kaggle

Status: ready
Track: shared
Source: https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/752897
Version: snapshot 2026-11-08

- **Nguồn.** Bài đăng của manwithacat ngày 27/10/2026, truy cập 08/11/2026. [Snapshot diễn giải và phạm vi đọc](source.md)
- **Phạm vi.** Đã đọc mọi mục của bài đăng hiển thị và thấy 0 bình luận. Các paper, notebook, artifact, số đo leaderboard và kết quả âm được tác giả dẫn chưa được xác minh độc lập.

## Câu hỏi và bối cảnh

Tác giả hỏi lợi thế thực tế đến từ thiết kế thuật toán lượng tử mới hay từ việc thử nhanh nhiều cách biên dịch cho cùng hợp đồng verifier. Lập luận của tác giả dựa trên các ví dụ công khai: bộ giải mã Schur cho DQI, tối ưu gauge và fit lượng tử hóa cho hóa học, và cấp phát lại bộ nhớ cho invsqrt. Đây là các ví dụ tác giả chọn để minh họa. Bài đăng chưa định lượng đóng góp riêng của agent, thuật toán và tốc độ vòng lặp. [Bài đăng, mục thiết kế và ví dụ](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/752897)

## Các phương án và lập luận

| Bài | Cơ chế và bằng chứng được báo cáo | Đánh đổi và giới hạn |
| --- | --- | --- |
| Invsqrt | Giảm thời gian sống của thanh ghi và dọn workspace, giữ đa thức và góc quay trong ví dụ của mrmeows. Tác giả nêu 63 qubit, khoảng 1.400 Toffoli và sử dụng 95–99% ngân sách sai số. | Kết quả âm về Newton, đoạn bậc ba và đổi độ rộng bảng chỉ có phạm vi các cấu hình được kể lại. Cận Toffoli được nêu cho kiến trúc đó. Tính trực tiếp bit pha theo x vẫn là gợi ý chưa kèm số đo. [Bài 752897, mục invsqrt](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/752897) |
| DQI | Thay kiến trúc giải mã và chỉ dùng Forney sweep để tạo pha cần thiết. Tác giả nêu khoảng 11 Toffoli mỗi điểm so với 80–85 và chi phí reverse cao hơn forward khoảng 31 Toffoli mỗi cặp nút. | Cần giữ pha và khôi phục syndrome, dọn ancilla, rồi đo chi phí của cả mạch. Cận của sweep và rank 42 của bộ nhân là nhận định trong bài, chưa xác minh. [Bài 752897, mục DQI](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/752897) |
| DFTHCSOS | Refit hệ số khi word góc đã bị lượng tử hóa. Tác giả nêu workspace giảm mạnh ở 8 bit và thêm một ngưỡng ở 7 bit. Ví dụ làm tròn fit 10 bit xuống 8 bit cho khoảng 111 mHa. | Từ điển lớn có thể giúp fit nhưng làm lookup đắt hơn. Bài đăng báo B = 255 dừng ở 48 mHa và cắt từ điển ở 10–11 bit với R = 1 còn 20,5–22 mHa. Các mốc này phụ thuộc fit và triển khai cụ thể. [Bài 752897, mục Chemistry và kết quả âm](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/752897) |

## Kết luận hiện tại

- **Ý kiến và mức đồng thuận.** Tác giả ưu tiên thông lượng của vòng dựng–kiểm chứng–đo, đồng thời để ngỏ khả năng có thuật toán mới. Tác giả báo đã tự kiểm lại các mạch ở mốc công khai trước đó. Thread chưa có người phản biện hay xác nhận các nhận định này. [Bài 752897](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/752897)
- **DQI đối chiếu trong repo.** Điểm là `R(ε₊) × Q² × T`, với `Q` là số qubit, `T` là số cổng kiểu Toffoli trung bình mỗi shot và `ε₊` là cận trên một phía Clopper–Pearson của tỉ lệ lỗi. `R(ε₊) = ln(2) / [-ln(1/2 + 2√ε₊)]` và verifier yêu cầu `ε₊ < 1/16`. Cấu hình full dùng 102.400 shots và 70 syndrome 12 bit, tương ứng 840 qubit cho các thanh ghi đầu vào. So sánh trực tiếp điểm giữa số shot khác nhau trộn chi phí mạch với độ chặt của cận lỗi. [Verifier](../../../../verifiers/dqi/verify_submission_dqi.py) · [Checker cấu hình full](../../../../scripts/check_repo.py)
- **DFTHCSOS đối chiếu trong repo.** Verifier kiểm tra riêng `error_1 ≤ 0,020 Ha` và `error_2 ≤ 0,020 Ha` và tính điểm `lambda_eff × T_total × Q_total`. Vì vậy giảm bit hoặc workspace cần được đánh giá cùng cả hai sai số và các thừa số của điểm. Bài đăng không chỉ rõ đại lượng nào tương ứng với từng mốc mHa đã nêu. [Verifier](../../../../verifiers/dfthcsos/verify.py)

## Hypothesis đề xuất và kiểm chứng tiếp

Các đề xuất dưới đây là cách kiểm tra suy ra từ bài đăng. Note chưa có kết quả thử mới.

- **Invsqrt.** So với một mạch đối chứng đã định phiên bản, giữ cùng hợp đồng đầu vào và độ chính xác khi thay cách sinh pha. Chỉ coi hướng này được ủng hộ nếu verifier đạt và tổng chi phí giảm. Kiểm tra riêng các giá trị sát biên đoạn và ngân sách sai số.
- **DQI.** Đo chi phí forward và reverse riêng trước khi đổi lịch dọn dữ liệu. Giữ cấu hình full và hợp đồng pha như nhau. Ủng hộ hướng nếu mạch đạt verifier và giảm điểm tổng, kể cả khi giảm một loại tài nguyên làm tăng loại còn lại.
- **DFTHCSOS.** So fit ở word ngắn với cả mốc precision cao và đối chứng làm tròn trực tiếp, dùng cùng Hamiltonian. Giả thuyết được ủng hộ khi cả hai sai số qua ngưỡng và chi phí lookup/chuẩn bị không triệt tiêu lợi ích trên điểm tổng.

## Liên kết triển khai và câu hỏi còn mở

- [SCORES invsqrt](../../../../src/invsqrt/SCORES.md) · [SCORES DQI](../../../../src/dqi/SCORES.md) · [SCORES DFTHCSOS](../../../../src/dfthcsos/SCORES.md)
- Các mốc Kaggle cần notebook/commit, cấu hình verifier và log khớp phiên bản trước khi dùng làm đối chứng định lượng. Cần xác minh riêng các cận theo kiến trúc, nguồn gốc mốc 7–8 bit và cách tổng hợp điểm trước khi suy ra ưu tiên giữa các bài.
