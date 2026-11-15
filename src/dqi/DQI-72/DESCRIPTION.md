# [DQI-72] Phục hồi decoder v7 889 qubit bằng emitter Python từ source archive, đối chiếu exact KMB

Loại: Tái dựng từ submission và mã nguồn đi kèm.

## Nguồn và đối chứng

Người dùng cung cấp archive chứa `dqi.kmb`, `dqi_source.zip` và thư mục source
đã giải nén. Bundle khai báo tác giả Syed Asad Ali, Apache-2.0; giữ LICENSE,
NOTICE và attribution khi trích source. Chưa có URL phát hành được xác minh.
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
Manifest sẽ chỉ rõ vai trò và nguồn từng file. Config dự kiến `reconstructed`,
j_min=15, scan_positions=4095, max_qubits=889; hoàn thiện trước commit nguồn.

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

Input đạt ROUNDTRIP_EXACT. Chưa build source phục hồi, chưa có source commit
được dựng hoặc provenance; chưa nghiệm thu RECONSTRUCTED_EXACT.

| Mốc | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Build phục hồi | Chưa tạo | Chưa có | Chưa build |
| Smoke | Chưa có | Chưa có | Chưa chấm |
| Full | Chưa có | Chưa có | Chưa chấm |

Điểm và các run: [SCORES.md](../SCORES.md).
