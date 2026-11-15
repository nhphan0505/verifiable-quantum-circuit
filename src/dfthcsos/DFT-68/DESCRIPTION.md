# [DFT-68] Tái dựng 15 loader DFTHC bằng plan Boolean và dữ liệu factorization cố định

Loại: Tái dựng từ submission; owner nhphan0505.

## Nguồn và mục tiêu
Kế thừa compiler của Syed Asad Ali, Apache-2.0, từ bundle dfthcsos_source.zip (SHA-256 a3e5747c6211c465cc211df4608beab59898e806d1dbddc5624b674dae8d3fea), thuộc [VQCC Own-Circuit Portfolio](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio). Người dùng cung cấp 15 angle_k_0..14.kmb và submission.npz dưới tên dfthcsos__*. Notebook tác giả kiểm hash từng thành phần rồi đóng ZIP chung cả ba bài; không có ZIP DFTHC gốc để so container. Mục tiêu là khớp bytes từng thành phần và tạo ZIP DFTHC ổn định theo tiện ích chung; không tuyên bố hash ZIP gốc đã khớp.

## Thuật toán và phạm vi
Phục hồi loader từ các plan explicit_products đã đóng băng, không chạy lại randomized matching/search. Bảng angle_words có 1220 địa chỉ x 75 word, 8 bit/word; chia 15 batch, 5 word/batch. Selection 11 qubit, 5 register word 8 bit. Compiler hoàn tất 12 địa chỉ padding, phân rã Boolean low/high và các product GF(2), phát CNOT/Toffoli, HMR với CZ sửa pha rồi xóa cache. ANGLE_0 dùng lịch low-cache tám bit sống; ANGLE_8 dùng high-subspace cache; các batch còn lại dùng full high-cache. Giữ kiểm chứng algebra và phase correction của nguồn. Điều kiện loader là hai endpoint hợp lệ theo tác giả, chưa nhận đã chứng minh toàn Hilbert space.

NPZ gồm U(float64,8x143x76), W(float64,8x143x44), H2_I(float64,8x44), H1_I(float32 scalar), Hsym_lower(float32,2926), tree_edges(int64,75x2), angle_words(int64,1220x75). Lưu mảng dưới dạng dữ liệu số text có dtype/shape, dựng lại NPY và NPZ với metadata ZIP xác định. Đây là dữ liệu fitting cuối, không nhận đã phục hồi quá trình tìm factorization. Không tạo postprocessing.py theo yêu cầu người dùng; không tối ưu hay đổi dữ liệu.

## Implementation và dependency
Dự kiến solution.py điều phối, circuit.py gom các hàm compiler thực sự dùng, data.json chứa mảng số/plan/lịch cần thiết; config reconstructed.json và reconstruction.json/hash manifest khai báo nguồn. Giữ LICENSE/NOTICE. Không bê nguyên research/bundle hoặc KMB/KMX vào Git, không dùng local Downloads/scratch làm đầu vào build. Gọi src/common/package_submission.py để đóng gói, không nhân bản logic ZIP. Windows Python 3.13, kickmix 1.0.0 và NumPy 2.5.4 theo requirements, không WSL/so của tác giả.

## Kế hoạch kiểm chứng hypothesis
Hypothesis tái lập: Python phát 15 KMB và NPZ khớp bytes/hash công bố; không phải giả thuyết tối ưu mới. Đã kiểm chuyển trực tiếp và KMB-KMX-KMB cho cả 15 file: tất cả exact. Đã kiểm serialization lại các mảng NPY/NPZ: NPZ khớp SHA-256 6418ec8e10b1a8da967ee26278434f9ac950474741185f4d61363e17a03da77f sau cố định metadata Unix. Source/config phải commit và push trước build; build lại entry point từ checkout GitHub sạch với venv mới, cwd khác, audit input-file reads. So bytes mọi thành phần và NPZ/NPY; đóng ZIP hai lần kiểm determinism. Lưu provenance source/config/helper/data/package/environment/hashes và records mới. Nếu mismatch thì tìm nguyên nhân, commit lại, không vá từ KMB gốc. Thiếu dữ liệu thì báo blocker.

## Tài nguyên, baseline và giới hạn
Manifest tác giả ghi tổng 4074 Toffoli mỗi pass của ANGLE và điểm lịch sử 296635967.5935997; đây là công bố nguồn, chưa phải chấm của repo. Baseline DFT-BASELINE là QROM batch 8; không suy điểm cải thiện chỉ từ khác batch hoặc gate count. Chưa có grading mới và không sửa SCORES. Giữ data cuối nguyên bytes; fitting/refit thiếu đầu vào v18 không nằm trong build này. Không claim original ZIP exact; chỉ nghiệm thu component-exact cho tập đầu vào đã cung cấp, container mới deterministic.

## Kết quả và tái lập
Chưa build solution hoặc chấm. Sau build sẽ bổ sung mapping source commit/config -> records. Chờ thành viên chấm theo instructions sau nghiệm thu build, rồi review độc lập; không tự merge.
