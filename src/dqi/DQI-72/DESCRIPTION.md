# [DQI-72] Phục hồi decoder v7 889 qubit bằng emitter Python từ source archive, đối chiếu exact KMB

Loại: Tái dựng từ submission và mã nguồn đi kèm.

## Nguồn và đối chứng

Người dùng cung cấp archive chứa `dqi.kmb`, `dqi_source.zip` và thư mục source
đã giải nén. Bundle khai báo tác giả Syed Asad Ali, Apache-2.0; giữ LICENSE,
NOTICE và attribution khi trích source. Nguồn công khai: [notebook của syed3000](https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook)
và [Kaggle dataset version 12](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio/versions/12).
Đã tải ẩn danh `dqi_source_zip` (8.486.126 byte), SHA-256 trùng hoàn toàn với
source ZIP người dùng cung cấp; LICENSE/NOTICE khớp bản giữ trong repo sau chuẩn hóa
xuống dòng. Xem [bằng chứng nguồn công khai](evidence/public_source.json).
Archive là bằng chứng nguồn gốc; build chỉ dùng source đã track trong checkout.
SHA-256 input: `7cbe8ecf6f6e9743529b574f019504bb1712ce06fbb570c719ce9d9e2c914cd9`,
455.590.024 byte. Source ZIP: `49e2b331d4008afb724985caf1038765b7a910f08838b590bf6e8fb692772763`.
430 file của bảng kê source khớp hash, gồm 425 file trong src và 5 file đóng gói.

Python 3.13.14/Kickmix 1.0.0 chuyển trực tiếp KMB→KMB và qua KMX đều trùng
bytes/hash. Quan sát từ artifact: 889 qubit, 53.911 classical bits, 52.930.855
lệnh; 364.619 CCX + 7.000 CCZ + 12.384 CSWAP = 384.003 Toffoli-like tĩnh;
không Z_POW. Đây là thống kê tĩnh, chưa phải kết quả verifier hay điểm số.
Đối chứng repo [DQI-39](../DQI-39/DESCRIPTION.md) dùng q26 từ nguồn khác;
không ghép code hoặc chuyển điểm của hướng đó sang bản phục hồi này.

## Thuật toán và biểu diễn

Thanh ghi quantum S0..S69 chứa syndrome GF(2^12), mỗi word 12 bit little-endian.
Thanh ghi classical E0..E4094 chứa mask M runtime. Theo verifier, phải khôi phục
syndrome và toàn bộ ancilla, đồng thời nhân pha bởi
`(-1)^sum_j popcount(e_j & M_j)`. Không được phát Z_POW.

Entry point upstream là integration_v7/build_v7.py, gọi v7_pipeline.configure/emit.
Lịch cố định gồm adaptive64 gauge; biến đổi syndrome; extraction GF(2^24)
với first-three retained-norm; synthesis locator/evaluator; converter transpose14
và gauge parking; projective finish infinity3; adaptive scan toàn chu kỳ 4095 vị
trí với 4026 point tests; reverse finish/converter/extraction; đóng gauge.
Các binding arithmetic, carry, deferred measurement masks và seam phải giữ nguyên.
Đây là mô tả đọc từ source; chưa phải chứng minh mọi khối đúng trên toàn miền.

## Cách phục hồi và dependency

Dùng emitter Python từ bundle để sinh lệnh, giữ thứ tự register, allocation,
compute/uncompute và sửa pha measurement. Bỏ bootstrap và hồ sơ audit lịch sử
khỏi đường build, thay bằng loader cố định dùng source đã track trong checkout.
Tối giản theo import/file-open audit: chỉ giữ helper và bảng thực sự cần, cùng
giấy phép và mapping hash upstream; không chép nguyên bundle hoặc nhúng tape.
100 module emitter/helper đã được tách vào `decoder/`, tổng 617.237 byte;
không giữ bootstrap, lịch sử gate hoặc bản mạch/KMX. Audit lượt dựng đầy đủ
loại thêm ba window module của các frame cũ không được gọi; các entrypoint
frame cũ báo lỗi rõ ràng, production cố định dùng transpose14_core.frame. Mapping path/hash và vai trò
từng module ở [reconstruction.json](reconstruction.json). Config [reconstructed](configs/reconstructed.json),
j_min=15, scan_positions=4095, max_qubits=889; cố định theo input. Chạy `python src/dqi/DQI-72/solution.py --config src/dqi/DQI-72/configs/reconstructed.json`.

Build không được đọc Downloads, submission/KMX gốc, cache hay thư mục source
ngoài checkout. Thư viện dùng pin requirements của repo. Cần build entry point
từ clone sạch của commit đã push bằng venv mới, cwd khác checkout và audit mọi
file đọc. Chỉ công cụ đối chiếu riêng sau build được mở artifact gốc.

## Điều kiện đúng, sai số và tài nguyên

Mục tiêu là tái tạo nguyên bytes, không đổi thuật toán hoặc chuẩn hóa lệnh.
Không có điều chỉnh precision; mọi phép GF và thứ tự mạch giữ theo upstream.
Nếu hash exact, chỉ kết luận tái lập artifact; tính đúng và chi phí runtime vẫn
cần chấm độc lập. Dự trù RAM trống 4 GB và đĩa 5 GB. Q và static T nêu trên
là số đo input, chưa phải bản dựng phục hồi.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: input KMB/hash và source ZIP/hash nêu trên; chưa có run chấm mới.
- Dự đoán: tách emitter khỏi audit/bootstrap vẫn sinh đúng toàn bộ bytes KMB.
- Ủng hộ: entry point từ clone sạch đã push sinh artifact trùng byte/SHA-256,
  audit chỉ đọc checkout/runtime và file mới tạo trong lần build.
- Bác bỏ/chưa đủ: khác bytes, thiếu dependency hoặc cần bundle ngoài GitHub;
  không dùng số cổng giống nhau để thay thế exact.
- Dừng: đạt exact và dependency closure, hoặc tối đa ba vòng build khi còn
  sai khác chưa giải quyết; không hạ tiêu chí và không vá bằng tape gốc.
- Ứng viên cuối: bàn giao notebook smoke/full cho thành viên; không tự chấm
  trong phạm vi này. Không dùng tuyên bố điểm trong archive làm kết quả mới.

## Kết luận và phiên bản tái lập

Input đạt ROUNDTRIP_EXACT; bản dựng phục hồi đạt **RECONSTRUCTED_EXACT**.
Commit nguồn thực sự dựng: `9d899c2fe708135ee86f43473084f8288b5865ab`. Entry point được chạy từ cwd ngoài
checkout sạch lấy từ GitHub, venv mới với requirements pin. Toàn bộ 100 module
decoder có trong manifest đều được đọc; không có module decoder dư hoặc dependency
source/bundle bên ngoài checkout. Không có subprocess trong build.

Artifact 455.590.024 byte trùng từng byte và SHA-256 với input. Số đo bản dựng:
889 qubit, 53.911 classical bits, 52.930.855 lệnh, 384.003 Toffoli-like tĩnh.
Đối chiếu chạy riêng sau build, không cấp input gốc cho solution.
Xem [báo cáo exact](../../../results/dqi/DQI-72/reconstructed/build_only/20261115T083137Z-clean-build/reconstruction_check.json),
[audit dependency](../../../results/dqi/DQI-72/reconstructed/build_only/20261115T083137Z-clean-build/dependency_audit.json),
[checkout sạch](../../../results/dqi/DQI-72/reconstructed/build_only/20261115T083137Z-clean-build/clean_checkout.json) và
[provenance](../../../results/dqi/DQI-72/reconstructed/build_only/20261115T083137Z-clean-build/provenance.json).

Lượt dựng trước khi hoàn thiện audit đã cho hash exact nhưng phần ghi metadata
Windows gọi shell và bị chặn; đã thay bằng metadata không subprocess. Audit lượt
tiếp theo cho phép loại ba module fallback không dùng. Bản cuối nêu trên đã dựng
lại sau thay đổi source, không lấy hash của phiên bản cũ để nghiệm thu phiên bản mới.
Các module tiền nhiệm còn lại cung cấp helper/binding cho production; không phải
config thử nghiệm bổ sung. Các hồ sơ kiểm chứng lịch sử upstream không được chuyển
thành PASS hay điểm của hướng này.

Đây là phục hồi mạch, không có hypothesis tối ưu thuật toán mới hoặc thay đổi
miền đúng/sai số. Hypothesis tái lập được ủng hộ bằng build exact và lượt full
102.400 shots không ghi nhận lỗi value hoặc phase. Full dùng kickmix-engine 0.6.0,
Python 3.13.18 trên WSL2, kernel avx2, mặc định m=4095, n=70, degree=12, r=2016,
log2_delta=-128; không đặt seed/salt riêng. Seed được engine suy ra theo mặc định
từ artifact; metadata không lưu giá trị seed cụ thể nên không suy đoán.

Hash artifact trong full, metadata và build provenance khớp. Verifier JSON khớp
nguyên nội dung JSON stdout. Số qubit giữ 889; trung bình Toffoli-like/shot
383.156,2908886719, max 384.003. Không lỗi trên lượt này không chứng minh đúng
tuyệt đối trên toàn miền; không chuyển các tuyên bố điểm lịch sử từ archive sang
kết quả mới. Chưa có smoke hoặc full bổ sung với salt độc lập.

Run/config full hiện tại là mốc duy nhất của hướng, cùng commit nguồn
`9d899c2fe708135ee86f43473084f8288b5865ab` đã dựng exact. Xem [full verifier](../../../results/dqi/DQI-72/reconstructed/full/20261115T094523Z-local-full-502791/verifier.json)
và [provenance full](../../../results/dqi/DQI-72/reconstructed/full/20261115T094523Z-local-full-502791/provenance.json). Score và tỷ số baseline được
ghi trong SCORES; so sánh dùng full baseline có trước trên engine 0.6.0,
giữ nguyên metadata khác môi trường/mẫu. Mục tiêu phục hồi exact và chấm full
đã đạt; dừng vòng phục hồi và chuyển review độc lập. Không chỉnh mạch để tối ưu
trong phạm vi hướng này.

| Mốc | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Build exact | [reconstructed](configs/reconstructed.json) | `9d899c2fe708135ee86f43473084f8288b5865ab` | [provenance](../../../results/dqi/DQI-72/reconstructed/build_only/20261115T083137Z-clean-build/provenance.json) |
| Smoke | reconstructed | Chưa chấm | Chưa có |
| Full | [reconstructed](configs/reconstructed.json) | `9d899c2fe708135ee86f43473084f8288b5865ab` | [full provenance](../../../results/dqi/DQI-72/reconstructed/full/20261115T094523Z-local-full-502791/provenance.json) |

Mã triển khai: [solution.py](solution.py). Cấu hình: [configs](configs/).
Điểm và các run: [SCORES.md](../SCORES.md).
