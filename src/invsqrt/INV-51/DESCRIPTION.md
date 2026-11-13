# [INV-51] Tái lập mạch invsqrt 46 qubit bằng source tác giả và đối chiếu KMX/KMB exact

Loại: Tái dựng từ submission có source tác giả.


## Nguồn và bằng chứng

Input 291626 bytes, SHA-256 321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177.
Hai đường KMB→KMB và KMB→KMX→KMB đều trùng bytes/hash với Kickmix 1.0.0,
Python 3.13.14, NumPy 2.5.4. 560 entries của SHA256SUMS nguồn đều khớp.
Attribution theo gói: Syed Asad Ali, Apache-2.0. Chưa có URL phát hành độc lập.
Đây là bản tốt nhất theo chi phí được báo cáo trong các ảnh người dùng cung cấp;
chưa xác minh score bằng verifier trong phiên này.

## Bản đồ mạch quan sát trực tiếp

KMX có 34812 dòng. Dòng 1–22 gắn q0..q21 vào r0, dòng 23 đặt tên register x.
Tổng 46 qubit: input 22 bit little-endian, workspace tối đa 24 qubit khác.
Verifier yêu cầu x=1..3133452, pha exp(2πi/sqrt(x)), khôi phục x và scratch=0.
Có 1297 lệnh HMR và 895 PUSH_CONDITION/POP_CONDITION; số tĩnh:
1461 CCX, 9 CCZ, 129 CSWAP, 38 Z_POW. Các số tĩnh không bằng kỳ vọng mỗi shot.
Không gán ranh giới khối thuật toán vào final KMX khi chưa có cut-map sau rewrite.

## Bản đồ từ source

tools/build_variant.py: normalization.forward → root.forward → emit_body →
root.inverse → normalization.inverse → restore_input_layout → register x.
emit_body được patch bởi patch_w47_body.py, tổ chức bảng hệ số, metadata,
seed inverse, product, divider/phase và cleanup; giữ các callback từ module đã pin.
PATCH_ORDER.txt áp 13 patch, Q=46, rồi relocate_cs2.py.
pipeline.sh: audit_affine → audit_pairs → hold_pass → tối đa 4 vòng
audit_affine/postpass → merge_zpow → compile. Sau postpass cuối compile lại.
Phép đo HMR có sửa pha theo kết quả đo; không được bỏ điều kiện/metadata/góc.
Bản nền repo INV-BASELINE dùng Horner bậc ba và Newton; không coi bản nguồn này
là chỉnh sửa baseline đó. Không tuyên bố hệ số cải thiện khi chưa có run tương thích.

## Phương án triển khai

Tái lập từ source tác giả thay vì giải ngược chuỗi lệnh: giữ nguyên source dependency
và license/hash; Python adapter chỉ chuẩn bị đường dẫn, chạy generator và finishing
passes theo đúng thứ tự, rồi đối chiếu SHA-256. Không đọc KMB đầu vào hoặc KMX scratch
trong build. Lưu gói nguồn riêng ngoài Git cùng manifest từng file và hướng dẫn cấp lại.
Không đưa toàn KMB/KMX vào source dưới dạng bảng dữ liệu. Chỉ đọc các component KMX
nếu thực sự là dependency của source tác giả và khai báo rõ.
Môi trường repo Windows đã pin đủ; source tác giả yêu cầu Linux/Python 3.13 và
resource module. WSL Ubuntu hiện chỉ có Python 3.10.12. Cần runtime tương thích hoặc
adapter có kiểm chứng; không bỏ kiểm tra hash của nguồn và verifier để chạy được.
Giới hạn mỗi tiến trình build 10 phút, tối đa 3 lần sửa lỗi tích hợp trước đánh giá lại.
Không chạy official verifier/chấm tự động trong nhiệm vụ decompiler; bàn giao notebook.

## Nghiệm thu và giới hạn

Hypothesis: source + dependency pin dựng đúng bytes input. Chỉ nghiệm thu khi
build từ commit thật, so bytes/hash và provenance đúng schema. Hash khác là MISMATCH.
Exact không đồng nghĩa hiểu toàn bộ thiết kế hay PASS verifier. Chưa đo lại score.
GitHub đã xác minh owner nhphan0505, base main; đã đọc toàn bộ 50 Issue/PR và hai PR mở.
Không thấy hướng tái lập cùng input hash; INV-49 là tối ưu INV-41 của Reece1512,
khác phạm vi. Workspace DQI giữ nguyên; tạo worktree riêng từ origin/main.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: submission SHA-256 `321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177`; source supplied by user, Apache-2.0. Đây là đối chứng bytes, không lấy score ảnh làm run.
- Dự đoán: generator và các pass giữ nguyên sẽ tái tạo đúng artifact; adapter chỉ chuyển đường dẫn và điều phối, không thay số học.
- Ủng hộ: so sánh trực tiếp bytes và hash đều trùng, có source commit/config/dependency hashes thực tế. Bác bỏ: bất kỳ byte khác hoặc dependency không truy vết được.
- Điều kiện dừng: đạt exact hoặc sau ba vòng sửa tích hợp; không đổi tiêu chí để nhận một mạch tương đương. Không thay verifier, số bit hay góc quay.
- Kiểm tra độc lập: thành viên chạy notebook local dev_5min/full sau bàn giao; reviewer khác tài khoản kiểm tra provenance và phạm vi. Chưa có run chấm mới.

## Điều kiện đúng và sai số

Input x little-endian 22 bit, x trong [1,3133452]. Pha mục tiêu exp(2πi/sqrt(x)); tolerance theo verifier là 2^-24/sqrt(x) turns. Input phải trở về đúng các qubit ban đầu; mọi scratch phải sạch. HMR cần phase correction đúng từng nhánh. Không suy ra correctness toàn miền từ gate counts hoặc hash nguồn. Exact bytes với input chỉ chứng minh tái lập submission đó.

## Kết luận và phiên bản tái lập

Bước tiếp nhận và khứ hồi đã đạt trong scratch; chưa build độc lập từ source commit và chưa chấm. Config đầu tiên dự kiến tên reconstructed; triển khai adapter sau mốc mô tả này. Bằng chứng bước 1–3 sẽ được đưa vào thư mục của hướng cùng manifest.

| Mốc | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Build exact | Dự kiến reconstructed | Chưa có commit implementation | Chưa build |
| Dev | Chưa chấm | Chưa có | Chưa có |
| Full | Chưa chấm | Chưa có | Chưa có |
