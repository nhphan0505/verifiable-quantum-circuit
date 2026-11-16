# [INV-66] Tái dựng generator invsqrt 64 hàng với divider m37 và cleanup HMR

Loại: tái dựng độc lập thuật toán từ submission, dùng lại primitive số học đã track.
Mức source hiện tại: `ARITHMETIC_GENERATOR`. Generator đầy đủ đã build sạch exact;
cần review độc lập lại trên HEAD mới, chưa merge và không tự nhận approval.

## Kết quả và phạm vi

Đã thay phần liệt kê khoảng 20.000 dòng cổng bằng generator số học: normalize,
consumed root/residual, lookup 64 hàng, coefficient có rounding từng hàng,
seed/product, balanced divider m37, 33 feature pha, inverse product/coefficient,
giải mã địa chỉ và trả HMR debt, inverse root/normalization. Chi tiết công thức,
invariant và chứng minh cleanup ở [ALGORITHM_RECOVERY.md](ALGORITHM_RECOVERY.md).

Target cố định: `invsqrt.kmb`, 198590 bytes,
SHA-256 `e46d90c36d1beb3ce7731a3e0b5c3659b3cda7f5f290b73c6c34513d96c005b6`.
Input/output vẫn là x 22 bit, x=1..3133452, 46 qubit; pha theo contract
exp(2*pi*i/sqrt(x)), khôi phục x và scratch zero. Đây không phải tối ưu mới.

## Nguồn và attribution

Artifact/receipt do người dùng cung cấp, lineage và notebook refit được lưu trong
[reconstruction.json](reconstruction.json) và [evidence/review_followup.json](evidence/review_followup.json).
Reference walkthrough: mizeroluckygall/quantum-circuits-one-toffoli-less-in-invsqrt;
precursor thuộc lineage Syed Asad Ali/Ali Haydar Özdağ, Alex Chilton và Atakan
Aldemir; asteriospanoras cung cấp sửa dead-write HMR/CZ. Xem [NOTICE.txt](NOTICE.txt).

Source private `ahoirg/qcc-invk6-k6c` chưa được cung cấp. Implementation hiện tại
phục hồi độc lập từ semantics của artifact và primitive Apache-2.0 trong INV-51;
không coi wrapper INV-51 là INV-66. Bảng hệ số, certificate Boolean và tham số pha
là dữ liệu toán học đã khôi phục; không nhận đã tìm lại quy trình tối ưu/thử góc gốc.
Receipt bên ngoài chỉ là evidence, không phải local-run/source-build provenance.

## Source và dependency

| File | Vai trò |
| --- | --- |
| [solution.py](solution.py) | CLI, snapshot Git, package pins, audit và provenance |
| [circuit.py](circuit.py) | Generator số học và inverse với owner/carry-debt tokens |
| [arithmetic_helpers.py](arithmetic_helpers.py) | Chọn primitive normalize/root/add/divider từ [INV-51](../INV-51/circuit.py) đã track |
| [lookup_certificate.py](lookup_certificate.py) | Compiler quadratic/affine GF(2), sinh hai loader 27/29 AND |
| [cleanup.py](cleanup.py) | Decoder 8 AND, inverse R-frame, trả debt và erasure với tám bank Boolean |
| [recovery_model.py](recovery_model.py) | Model cổ điển độc lập và bảng A64/S64 |
| [finishing.py](finishing.py) | Adapter gọi PP riêng và giữ đúng tọa độ khi chain đan xen |
| data/lookup64_certificates.json | Hai plan Boolean sáu đầu vào; không chứa toàn mạch |
| data/cleanup64.json | Decoder nhỏ và lịch retirement/bank; không chứa phase opcode list |
| data/arithmetic_helpers.json | 16 đối tượng toán học/compatibility cần để khởi tạo helper cũ, khoảng 19 KB |
| data/phase_parameters.json | 33 hệ số pha dyadic và thứ tự feature |

Không chạy generator, loader hay replay cũ của INV-51; không đọc INV-51/tables.json.
Mọi file cần để build được track/pin trong checkout. KMB/KMX gốc, notebook, bundle,
cache cũ và dữ liệu scratch không phải input runtime. KMX trung gian chỉ do lần
build hiện tại mới sinh trong work directory riêng dưới artifacts.

Finishing vẫn tách khỏi thuật toán: gọi nguyên implementation PP-001..PP-004 rồi
PP-005 trong src/invsqrt/postprocessing. Adapter truyền từng hold-chain cho PP-001
và remap tọa độ chain chưa xử lý sau insert/replace; không sửa method của owner khác.
PP-005 giữ module riêng và rewrite đúng site 3292. Các dependency được pin SHA-256.

## Phạm vi PR và dependency PP-005 sau review

Theo review của nhphan0505 và Reece1512, PR67 không sửa checker, test policy hoặc
REPOSITORY_CHECKS để mở rộng phạm vi experiment. Các file hệ thống đã được trả
về bản trusted main. PP-005 thuộc Issue #70 và [PR71](https://github.com/nhphan0505/verifiable-quantum-circuit/pull/71),
không nộp chung thay đổi method/catalog trong diff INV-66.

PR67 tạm đặt base `pp/PP-005-dead-write-hmr` để thể hiện dependency chưa merge.
PR71 cần review/merge vào main trước; sau đó mới đổi base PR67 về main và kiểm
scope/checks lại. CI trên base dependency không có nghĩa dependency đã có trên
main hoặc PR67 đủ điều kiện merge. Không tự merge hoặc tự approve dependency.

Source/helper/data build giữ nguyên bytes của source f04c85e đã nghiệm thu exact;
việc hoàn tác policy và tài liệu không tạo một lượt build/chấm mới.

## Hypothesis tái lập và nghiệm thu

Hypothesis: các hàm số học, typed cleanup và dữ liệu toán học đã track đủ sinh đúng
artifact, với package/serializer pin, không cần nạp binary gốc. Bác bỏ khi khác
bytes/hash hoặc audit có input ngoài checkout/runtime/newly-generated work.
Không vá output và không hạ tiêu chí exact.

Source **f04c85e17d8114ec99a9a116da7f3ee44ba7e33c** đã clone mới từ GitHub và build
bằng venv mới, Python 3.13.7, kickmix 1.0.0, NumPy 2.5.4, SciPy 1.18.1, cwd ngoài
checkout. Đối chiếu bytes độc lập sau build đạt toàn bộ 198590 bytes và SHA trên.
[Build record](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T112732Z-exact-b6c89817/reconstruction_check.json)
ghi provenance, audit, setup, construction cuts và stage logs thực tế.
Audit kiểm 19 input source/data against Git; không đọc KMB/receipt/notebook gốc,
không đọc INV-51/tables.json, không network/subprocess trong construction.
CPython audit không bao phủ mọi OS read bên trong native package; giới hạn này giữ rõ.

Kiểm tra đã chạy:

- Model/register/phase features trên cả 3.133.452 x; divider nghịch trả đúng product.
- Cả 4096 v và 64 địa chỉ cho mỗi loader; 33 generic feature và fixed phase khớp.
- Symbolic cleanup trên 64 codewords với 55 outcome độc lập: mọi phase coefficient
  triệt tiêu; kết quả giữ đúng sáu bit địa chỉ và không còn owner/debt thừa.
- Sáu tests mới (cleanup, divider boundaries/random, remap chain đan xen) và 49 tests
  hạ tầng qua; repository checker 0 lỗi. CI trên HEAD cuối cần xanh trước review.

Lặp lại model: `python src/invsqrt/INV-66/validate_recovery.py --reference-kmx <scratch>/circuit.kmx`.
Công cụ phân tích này không được solution gọi. Lặp lại component proof:
`python -B -m unittest discover -s src/invsqrt/INV-66/tests -v`.

## Build và quan hệ với kết quả chấm

Từ checkout sạch, dùng Python 3.13 và requirements.txt của repo:

```powershell
.\.venv\Scripts\python.exe src/invsqrt/INV-66/solution.py --config src/invsqrt/INV-66/configs/reconstructed.json
```

Output mặc định artifacts/invsqrt/INV-66/reconstructed.kmb không bị ghi đè.
Có thể dùng --output tới subdirectory mới của artifacts, cùng tên reconstructed.kmb.
Entry point audit toàn bộ arithmetic và finishing trong cùng process, chặn read/write
ngoài source/runtime/work mới và lưu build_only provenance với source commit thật.

Không có verifier run mới. Full PASS lịch sử vẫn thuộc source 50f9c29 và run
20261115T042258Z-local-full-7feec4; score 78719.52914734723 và hệ số 26.3819× là
kết quả lịch sử trong SCORES, không chuyển provenance sang f04c85e. Các build cấp
cổng trước vẫn giữ nguyên records. Chưa nhận được review độc lập cho generator mới;
không nhận có analytic error bound hoặc quy trình search parameter mới.
