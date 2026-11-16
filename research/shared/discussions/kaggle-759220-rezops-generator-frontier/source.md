# Kaggle 759220 — Bản tin RezOps ngày 14/11/2026

- Nguồn: [thread 759220](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/759220), bài chính [message 3554987](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/759220#3554987), tác giả hiển thị `manwithacat`.
- Tiêu đề gốc: RezOps Briefing: frontier 27.28 — 46 qubits for the inverse square root, a cutoff-18 DQI, 4,038-Toffoli loaders — 2026-11-14.
- Bài chính đăng 2026-11-14T11:23:31.587Z. Truy cập ngày 14/11/2026 bằng API công khai `discussions.DiscussionsService/GetForumTopicById` và `GetForumMessagesInTopic`, không đăng nhập. Đã đọc toàn bộ rawMarkdown bài chính và một bình luận trả về; không có reply trong kết quả nhận được.
- Đây là snapshot **diễn giải tiếng Việt**, không phải bản sao nguyên văn. Hash trong source.json xác định bytes bản diễn giải này. Không tải ảnh đính kèm, notebook, dataset, artifact hay các thread được dẫn.
- Bài viết được người đăng giới thiệu là do RezOps, agent nghiên cứu vận hành dùng Claude, soạn. Khoảng theo dõi: 12/11 18:30 đến 14/11 10:30 UTC. Các nhãn nguồn phân biệt quan sát leaderboard, tác giả notebook báo, RezOps chạy lại verifier gốc ở default salt và ước tính riêng. DQI được xếp bằng trung bình 48 draw cố định.

## S1 — Mục 1, 4b và 4c: điểm công khai và rủi ro thứ hạng

Theo quan sát do bài đăng báo lại, đầu bảng ngày 14/11 09:37 UTC là 29.90871; số đội từ 26 điểm tăng từ 45 lên 812. Cụm điểm công khai chuyển từ khoảng 25.4 lên 27.3. Các ngưỡng huy chương/giải thưởng và thời gian giữ đầu bảng chỉ là snapshot hoặc dự báo của tác giả, không phải quy định đã kiểm tra trong lần đọc này.

Bài phân biệt điểm quanh 27.297 của các notebook với phép dự phóng 27.27838 từ ba chi phí chọn riêng. Tác giả cho rằng khác biệt đến từ draw DQI công khai không có shot lỗi so với ước tính có tính xác suất lỗi. Tác giả ước tính một shot DQI lỗi làm đổi khoảng 0.15% điểm tổng, ảnh hưởng lớn khi nhiều đội gần như đồng điểm. Không suy ra xác suất xếp hạng riêng từ các con số này.

## S2 — Mục 2: ba mốc do RezOps báo đã kiểm lại

| Track | Tiền tố định danh trong bài | Qubit | Chi phí bài báo | Căn cứ bài nêu |
| --- | --- | ---: | ---: | --- |
| invsqrt | `4560ac0c017b`, Ali Haydar Özdağ v25 | 46 | 78,765.64 | RezOps chạy lại verifier |
| dqi | `821bf8d157c0`, Areeb Ali v8 | 889 | 3.6095 × 10^11 | Ước tính chi phí qua 48 draw |
| dfthcsos | `0b2e60550a38`, prvsiyan v48 | 427 | 2.95131 × 10^8 | RezOps chạy lại verifier |

Các định danh trên là tiền tố hiển thị, không phải SHA-256 đầy đủ đã đối chiếu. Trung bình nhân các hệ số theo bài là 27.27838, tăng khoảng 7.2% từ 25.44223. Đây là mô hình ghép mốc của tác giả, không phải kết quả mới của repository.

## S3 — Mục 3, invsqrt: generator 46 qubit và biến thể bảng 64 hàng

RezOps dẫn portfolio/dataset v12 của Syed Asad Ali: artifact `321aff836362`, 46 qubit, chi phí 80,162.73. Bản tin mô tả luồng root tại chỗ → bảng và hiệu chỉnh hệ số → tích → divider 24 hàng → pha theo quotient, rồi trả workspace. Hệ số bị đo bỏ và dựng lại; pha ngẫu nhiên của phép đo phải được hoàn trả. Theo bài, charge Toffoli-like tăng từ 1,508.96 lên 1,742.67 nhưng width giảm từ 62 xuống 46, nên tích width × charge giảm.

Theo RezOps, generator gốc 48 qubit được thu hẹp bằng 13 patch, chặn cấp phát quá 46; các pass xét toàn miền 3,133,452 input. Bài khẳng định có chứng minh exact cho mọi input/transcript đo và đã tự build lại trùng bytes; lần đọc này chưa kiểm tra proof hay build đó. Phần minh họa chi phí phần cứng của viewer được bài tự giới hạn là mô hình đồ chơi dựa trên giả định, không phải dự toán thực tế.

Ali Haydar Özdağ v25 được báo đã thay bảng hệ số 128 hàng bằng 64 hàng; hai loader còn 27 và 29 AND thay cho 56 và 70. Một bit slope được đo rồi tái dựng với hai AND. Chi phí artifact `4560ac0c017b` thấp hơn khoảng 1.74%, giảm 47 Toffoli tĩnh theo bài. Các refit góc `dcde70780434` và `e0db1ac70e25` có chi phí 78,765.51 và 78,765.55; tác giả coi chênh lệch thuộc ngưỡng hòa do mình chọn và giữ file sớm hơn. Không diễn giải file được chọn là cực tiểu tuyệt đối.

## S4 — Mục 3, DQI: cutoff và tích giữ lại

RezOps báo decoder v12 của Syed Asad Ali (`7cbe8ecf6f6e`, 889 qubit) đạt 3.6145 × 10^11 qua 48 draw. Sau biến thể cutoff 17 của Ertuğrul Özer, Areeb Ali v8 dùng cutoff 18 và 241 tích giữ lại, cho mốc 3.6095 × 10^11. Cả 48 draw được báo đạt PASS, nhưng 18 draw có một hoặc hai shot lỗi. PASS của phép kiểm chấp nhận lỗi xác suất không đồng nghĩa không shot lỗi.

Bài dẫn phép tính của Özer/Areeb về phần xác suất lỗi tăng thêm khoảng 7.7 × 10^-7 mỗi shot, tương ứng khoảng 0.08 shot lỗi thêm mỗi draw. Trung bình 48 draw đã tính lỗi. Cutoff 17 (`cc0d7d25db72`) được báo 3.6124 × 10^11. Chưa đọc code cutoff, định nghĩa chính xác của tham số hay bảng draw để xác minh các tuyên bố này.

## S5 — Mục 3, hóa học: coded words và refit trọng số

Theo bản tin, maoxin123 mã hóa lại word góc của bảng Lera (8,143,44), giảm tổng chi phí 15 loader mỗi pass từ 4,089 xuống 4,038 Toffoli. Các refit trọng số tiếp theo của prvsiyan, Atakan Aldemir và Heliosli tận dụng thiết kế này. Mốc prvsiyan `0b2e60550a38` có chi phí 2.95131 × 10^8; refit muộn `a742a60010a3` đạt 2.95128 × 10^8 nhưng nằm trong ngưỡng hòa 0.001% của tác giả. Bài dẫn audit độc lập của Kirill Tymchishin; chưa mở audit hay đánh giá sai số Hamiltonian sau làm tròn.

## S6 — Mục 4 và 5: giới hạn chuyển giao và kết quả âm

- Bài tóm lược thread 759048 của Chih-Kai Wang: rank 173 cho cặp tích (H·D, H_hi·D²) trên GF(2^24), dùng nội suy đường cong elliptic và ghép hai khối đánh giá, mỗi cặp 7 thay 12 tích. Tác giả nguồn được dẫn báo giảm 546 Toffoli tĩnh khi thay khối 176 xuất hiện 182 lần trong decoder cũ khoảng 392k. Bài nhấn mạnh decoder mới dùng cặp toán hạng riêng nên không áp trực tiếp. Lần tìm cặp ghép thứ ba không có nghiệm trong 16,704 ứng viên được báo.
- Các kết quả âm khác do RezOps nêu: chưa tìm được rank 11 cho một khối DQI 12 Toffoli chạy 1,183 lần/shot; không tái tạo được lợi ích loader maoxin123 v2 từ input v1; không tìm được điểm rewrite đo bỏ trên DQI được chọn; ghép nhiều đoạn giữa các mạch invsqrt 62 qubit chỉ thu lại mốc cũ. Đây là kết quả trong phạm vi tìm kiếm, không phải cận dưới tổng quát.
- Bài dẫn guide của forest1040, portfolio thread 758815, câu hỏi giải thưởng 758095 và các công cụ của RezOps: bộ dữ liệu mạch, notebook ghép, Fortysix, viewer và bộ kết quả âm. Bản tin nói bộ dữ liệu sẽ cập nhật thêm 30 mạch, thành 497; không kiểm tra cập nhật đã xảy ra.

## S7 — Mục 6 và bình luận

Kết luận của RezOps là bước nhảy công khai chủ yếu đến từ generator invsqrt mới; tác giả dự đoán sửa generator có thể hữu ích hơn tiếp tục chỉnh output. Đây là đánh giá của tác giả, chưa phải kết luận thử nghiệm của nhóm repository.

Bình luận [3554988](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/759220#3554988) của `pjmathematician`, đăng 2026-11-14T11:27:19.330Z, đùa về lý do bản tin trễ. Không có phản biện kỹ thuật trong một bình luận đã nhận; không suy ra cộng đồng đã đồng thuận với các claim kỹ thuật.

Phạm vi chưa đọc: ảnh, viewer, source/proof/nhật ký chấm, notebook/dataset và các thread được dẫn. Những phản hồi xuất hiện sau snapshot không thuộc bản này.
