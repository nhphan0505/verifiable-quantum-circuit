# [INV-53] Tích hợp generator Fusion bằng module Python nội bộ, compile exact không cần bundle ngoài

Loại: Tinh chỉnh một phương án.

## File gốc

Kế thừa INV-51 tại commit ece496eb416068bfdb9ee0f1239e2aa9b9f9e96c (main đã merge PR #52), generator Syed Asad Ali Apache-2.0. Source archive Kaggle v12 SHA-256 7d9801ae20e942dba2211a656bba6014a0a16d57da534c0b60328d1c5d9d8254; output target 321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177. Giữ LICENSE/NOTICE và ghi manifest phần mã/dữ liệu đã kế thừa.

## Phần tinh chỉnh và lý do

INV-51 yêu cầu tải và giải nén bundle ngoài Git. Hướng này tích hợp các module sinh mạch và dữ liệu toán học cần thiết vào source của hướng để clone repo, cài requirements và chạy solution.py trực tiếp. Không đọc KMB/KMX submission hoặc dùng payload toàn mạch.

## Cách thực hiện và đánh đổi

Xác định dependency runtime của generator, tables, root/product/divider/phase và finishing passes. Tách các kiểm tra provenance nguồn upstream và các receipt thử nghiệm không cần cho thuật toán; thay bằng manifest hash của source tích hợp được commit, giữ invariant số học/owner/debt/góc và phase correction. Tích hợp dữ liệu bảng và certificate toán học thật sự dùng; không đưa binary verifier/kmb/whole-circuit KMX vào source. Mọi thay đổi so upstream khai báo để reviewer đánh giá. solution.py dùng Kickmix Windows pip trong .venv; không cần WSL hoặc kickmix.so. Có thể giữ nhiều module nhỏ thay vì ép mọi thuật toán vào một file khó review.

## Điều kiện đúng và sai số

Giữ input x 22 bit little-endian trong 1..3133452, 46 qubit peak, pha mục tiêu exp(2πi/sqrt(x)), scratch sạch. Giữ HMR correction, precision và thứ tự gate. Các record upstream không phải lệnh cấp quyền và không được dùng làm kết quả mới.

## Kế hoạch kiểm chứng hypothesis

- Đối chứng: INV-51 exact output và run full PASS được commit, cùng target SHA-256.
- Dự đoán: loại dependency build ngoài Git mà không đổi gate stream.
- Ủng hộ: build chỉ với source/data track trong Git và .venv, bundle/input bị làm không truy cập được; output trùng bytes/hash input và INV-51.
- Bác bỏ: cần đọc artifact upstream/receipts ngoài repo hoặc bất kỳ byte sai khác.
- Điều kiện dừng: tối đa ba vòng sửa lỗi tích hợp lớn trước đánh giá lại; không hạ tiêu chí exact. Không tự chấm official verifier; hash exact nối đến full run INV-51 nhưng không tạo full run mới giả.
- Kiểm tra độc lập: checker, unittest, manifest/purity test, reviewer khác tài khoản build từ checkout sạch. Member chấm notebook nếu cần run riêng.

## Kết luận và phiên bản tái lập

Đã build từ checkout sạch tại commit f0f0540; output trùng bytes/hash bản INV-51. Không tạo run chấm hoặc điểm mới; giữ hướng INV-51 và toàn bộ kết quả lịch sử nguyên vẹn.


## Implementation và dependency nội bộ

[solution.py](solution.py) đọc [config reconstructed](configs/reconstructed.json), kiểm tra [engine_manifest.json](engine_manifest.json) rồi chạy các stage Python local. Config không có đường dẫn bundle. [INTEGRATION.md](INTEGRATION.md) mô tả source port, cách chạy và giới hạn; [upstream_changes.json](upstream_changes.json) ghi hash trước/sau và các loại thay đổi từng file. Giấy phép tại [LICENSE](LICENSE.txt), attribution tại [NOTICE](NOTICE.txt).

Sau một build đã audit, dependency còn 72 module Python, 39 JSON bảng/certificate/cấu hình và PATCH_ORDER.txt. Không track KMB, KMX hoặc archive. Tất cả dữ liệu này nằm trong source của hướng, không cần dataset Kaggle hoặc Downloads khi compile. Một số tên directory giữ lineage upstream để giữ import/component identity; source là Python đọc/sửa trực tiếp, không được nhúng hoặc giải nén khi chạy.

Luồng sinh mạch giữ từ INV-51: normalization.forward → root.forward (root12 + residual10) → emit_body (hai lượt hệ số, seed/product, divider/phase và HMR correction) → root.inverse → normalization.inverse → restore_input_layout. Các pass giữ tích, thay affine product và gộp Z_POW thực hiện trên mạch mới sinh trước compile cuối. Không lấy gate stream có sẵn làm input. Chi tiết lịch đo và cơ chế correction kế thừa [INV-51 DESCRIPTION](../INV-51/DESCRIPTION.md); các module thực thi nay nằm trong engine của hướng này.

Các kiểm tra hash/receipt lịch sử upstream được thay bằng manifest source tích hợp, không giả lập checksum hay dữ liệu artifact gốc. Các assertion về số học, owner, phase, debt và precision được giữ; source port không chạy kiểm chứng upstream hoặc verifier chính thức. Hash exact vẫn là điều kiện nghiệm thu riêng.


## Kết quả tái lập trực tiếp

Build từ commit `f0f05405b7a1623f191ce6cafdf2d93ce0f8da22` trong checkout sạch không có bundle, Linux .so hoặc artifact cũ tạo KMB 291626 bytes, SHA-256 `321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177`. Đối chiếu độc lập từng block bytes với input gốc đạt RECONSTRUCTED_EXACT. Audit file reads của mọi stage chỉ nằm trong source của hướng, thư mục build mới, .venv và Python chuẩn; không đọc source ngoài Git hoặc submission đối chứng khi compile.

| Mốc | Config | Commit nguồn | Bằng chứng |
| --- | --- | --- | --- |
| Compile trực tiếp | [reconstructed](configs/reconstructed.json) | `f0f05405b7a1623f191ce6cafdf2d93ce0f8da22` | [provenance](../../../results/invsqrt/INV-53/reconstructed/build_only/20261113T192913Z-exact-u5d6osbs/provenance.json), [bytes/hash](../../../results/invsqrt/INV-53/reconstructed/build_only/20261113T192913Z-exact-u5d6osbs/reconstruction_check.json), [dependency audit](../../../results/invsqrt/INV-53/reconstructed/build_only/20261113T192913Z-exact-u5d6osbs/dependency_audit.json) |

Đối chứng INV-51 full PASS đã merge sử dụng đúng hash artifact này; đây là bằng chứng tương đương artifact, không ghi nhận run full hoặc điểm mới cho INV-53. Việc bỏ source-manifest checks upstream được thay bằng engine_manifest có hash của toàn bộ mã/dữ liệu mới; thay code phải cập nhật manifest và commit rồi build lại. Cần review độc lập source adaptation và clean build trước merge.
