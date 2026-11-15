# [INV-66] Tái dựng mạch invsqrt e46d90c3 bằng Python cấp cổng từ KMX, giữ nguyên pha và sửa HMR/CZ

## Điều kiện nghiệm thu sau review

Review của nhphan0505 trên 6c94828 yêu cầu phục hồi thuật toán số học gốc. Bản hiện tại chỉ đạt GATE_LEVEL_PYTHON, chưa đáp ứng yêu cầu đó dù build exact và full PASS. Xem [kết quả truy nguồn và kế hoạch phục hồi](ALGORITHM_RECOVERY.md). Chưa xử lý xong review, chưa đủ điều kiện merge và không đổi nhãn mức phục hồi khi chưa có source/model thực tế.

Đã phục hồi độc lập model normalize/root, bảng 64 hàng, coefficient, seed và product; kiểm tra thanh ghi trên toàn miền đầu vào. Xem [model và giới hạn](ALGORITHM_RECOVERY.md). Builder số học và model pha divider vẫn chưa xong; mức bàn giao tiếp tục là GATE_LEVEL_PYTHON.

Loại: Tái dựng từ submission; phục hồi source Python cấp cổng, không nhận là thuật toán mới.

## Nguồn và mục tiêu

Artifact do người dùng cung cấp: submission_inv.zip, member invsqrt.kmb, 198590 bytes, SHA-256 e46d90c36d1beb3ce7731a3e0b5c3659b3cda7f5f290b73c6c34513d96c005b6. Receipt đi kèm khớp toàn bộ 18 member; chỉ xử lý invsqrt. Reference: https://www.kaggle.com/code/mizeroluckygall/quantum-circuits-one-toffoli-less-in-invsqrt . Notebook ghi credit asteriospanoras cho sửa dead-write HMR/CZ; precursor dcde7078 thuộc portfolio Alex Chilton/Atakan Aldemir, lineage Syed Asad Ali và Ali Haydar Özdağ. Code fix được notebook ghi Apache-2.0; điều khoản từng artifact upstream chưa được xác minh độc lập.

## Phạm vi tái dựng

Sinh cùng mạch bằng các lời gọi CircuitBuilder Python thông thường và vòng lặp có căn cứ; không nhúng KMB, KMX, archive, base64, chuỗi mã, hoặc bảng dữ liệu chứa toàn chuỗi cổng. Không đọc submission gốc, scratch, bundle hoặc cache trong entry point. KMB/KMX gốc chỉ là dữ liệu phân tích/đối chiếu riêng. Mức phục hồi là cấp cổng, không tuyên bố suy ra thuật toán số học gốc. Giữ nguyên 46 qubit, 387 bit, một register x 22 bit, thứ tự cổng, điều kiện, phép quay và serializer.

## Điều kiện đúng và sửa pha

Theo verifier repository: áp pha exp(2*pi*i/sqrt(x)), x=1..3133452; khôi phục x, scratch về zero, dung sai 2^-24/sqrt(x). HMR và conditional Z/CZ phải giữ transcript/pha nguyên bản. Quan sát tĩnh: 23877 operations; tại index 3292 có HMR q21 b61 rồi CZ q16 q20 if b61. Không tự khẳng định đúng từ thống kê. Hai đường KMB serialization và KMB-KMX-KMB đã exact trong bước 1-3; đây không phải verifier PASS hay independent build.

## So sánh nguồn và giới hạn

Base repository a6ec810060d35d1fb53cc86c1cc0e8f0db631241. INV-BASELINE dùng Horner/Newton. INV-51 là đối chiếu lineage 46-qubit nhưng target 321aff83 khác e46d90c3; không sửa code của INV-51 hoặc coi nó sinh cùng mạch. Không quét tham số/tối ưu.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: KMB/hash bất biến nêu trên và verifier repository tại base commit.
- Dự đoán: Python cấp cổng với API pin Kickmix 1.0.0 có thể tái tạo đúng 198590 bytes, không cần nạp artifact trong build.
- Ủng hộ: source/config đã commit và push, checkout sạch/môi trường mới, entry point chạy từ cwd khác; audit read chỉ thuộc checkout/runtime/output mới; SHA-256 và streamed bytes bằng input.
- Bác bỏ/dừng: serializer/API làm đổi bytes chưa khắc phục được, hoặc phải giấu toàn mạch trong data/đọc binary gốc để dựng. Không vá output từ input, không hạ tiêu chí exact.
- Kiểm tra cuối: checks/tests/scope phù hợp và đối chiếu exact độc lập. Chấm smoke/full do thành viên chạy sau bàn giao riêng, không tự chạy trong bước 4-7.

## Kết luận và phiên bản tái lập

ROUNDTRIP_EXACT và RECONSTRUCTED_EXACT có bằng chứng riêng; smoke và full local đã PASS với cùng artifact/hash và source commit dựng. Receipt vẫn là bằng chứng bên ngoài, không chuyển thành run của repo. Mức phục hồi cấp cổng; chưa suy ra thuật toán số học gốc.

## Source cấp cổng và cách chạy

[solution.py](solution.py) là entry point; [circuit.py](circuit.py) chứa builder của precursor, bảy vùng quan sát và 136 vòng lặp sweep X, cùng adapter nạp PP-005. Không có artifact/KMX nhúng, tải binary, gate table, source string hay exec/eval. PP-005 chỉ parse KMX vừa serialize từ circuit trong bộ nhớ để áp rule; không đọc KMX gốc từ đĩa. Góc quay là scalar decimal string chính xác truyền cho API, không qua float. Runtime của hướng dùng `solution.py`, `circuit.py`, [lookup_certificate.py](lookup_certificate.py),
[hai certificate lookup](data/lookup64_certificates.json), module [PP-005](../postprocessing/PP-005/solution.py)
và [configs/reconstructed.json](configs/reconstructed.json); requirements.txt khai báo package pin. [reconstruction.json](reconstruction.json) ghi nguồn/hash, vai trò file và mức phục hồi; [NOTICE.txt](NOTICE.txt) giữ attribution và giới hạn giấy phép.

Mức phục hồi là GATE_LEVEL_PYTHON: source rõ từng cổng và có thể sửa, nhưng chưa phục hồi phép tính số học cấp cao hoặc cách tác giả tìm mạch. Đây là đường triển khai được bước 05 cho phép, không phải source gốc. Input KMB/KMX chỉ được dùng để phân tích trước khi viết source và đối chiếu độc lập sau build.

```powershell
.venv/Scripts/python.exe src/invsqrt/INV-66/solution.py --config src/invsqrt/INV-66/configs/reconstructed.json
```

Chạy Python 3.13 và package pin. Config phải nằm trực tiếp trong configs của hướng; chỉ hỗ trợ reconstructed với target cố định. Output mới mặc định artifacts/invsqrt/INV-66/reconstructed.kmb, không ghi đè. Entry point kiểm tra checkout sạch, source/config khớp Git snapshot, rồi dựng trong bộ nhớ và ghi artifact mới. Audit chặn read ngoài source/runtime/output và network/subprocess trong construction; Git snapshot preflight và khởi động interpreter xảy ra trước audit. Native library OS reads không được CPython audit bao phủ; precursor dùng builder, compiler/certificate lookup và adapter PP-005 đã khai báo; PP serialize circuit mới trong bộ nhớ, KMB dùng BytesIO và file write qua Python.

Source commit `50f9c29b9ce7647e5e0f96ac7ccffc34cf1860d1` đã dựng từ clone GitHub mới, venv mới và cwd ngoài checkout; công cụ đối chiếu riêng xác nhận exact. Không chạy verifier. Working tree chính và thay đổi notebook của người dùng không bị sửa.

## Bằng chứng exact và giới hạn phục hồi

[Inventory](evidence/circuit_inventory.json) ghi register x=q0..q21, scratch q22..q45, classical bit capacity 387, điều kiện lồng tối đa hai mức. 23877 operation gồm 38 Z_POW (4 Clifford, 1 T, 33 generic); số cổng tĩnh không phải chi phí thực thi trung bình. Bản đồ vùng trong circuit.py chỉ mô tả vị trí quan sát, không gán tên thuật toán chưa chứng minh. [Round-trip](evidence/roundtrip.json) kiểm tra serializer trước khi viết source. [Receipt invsqrt](evidence/external_receipt_invsqrt.json) chỉ giữ phần liên quan từ receipt gốc có hash, không đại diện run local.

Hypothesis tái lập được ủng hộ ở mức source Python cấp cổng: KMB mới 198590 bytes, cùng SHA-256 mục tiêu và streamed bytes bằng input. Entry point không đọc file circuit gốc hoặc KMX. Không khẳng định phục hồi root/normalization/divider gốc; so sánh chi phí baseline dựa trên run full thật bên dưới, không phải tuyên bố tối ưu mới của bước tái dựng. INV-51 chỉ là nguồn so sánh khác target, không phải dependency runtime.

| Mốc | Config | Commit source thực sự dùng | Bằng chứng |
| --- | --- | --- | --- |
| Build sạch exact | [reconstructed](configs/reconstructed.json) | `50f9c29b9ce7647e5e0f96ac7ccffc34cf1860d1` | [provenance](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T033727Z-exact-fe8b97b7/provenance.json), [so bytes/hash](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T033727Z-exact-fe8b97b7/reconstruction_check.json), [checkout/setup](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T033727Z-exact-fe8b97b7/clean_checkout.json), [audit](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T033727Z-exact-fe8b97b7/dependency_audit.json) |
| Build sạch với PP-005 | [reconstructed](configs/reconstructed.json) | `a9b0dd06833c364fbc53687799f4cf30a127f7f1` | [provenance](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T052208Z-exact-86967189/provenance.json), [so bytes/hash](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T052208Z-exact-86967189/reconstruction_check.json), [checkout/setup](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T052208Z-exact-86967189/clean_checkout.json), [audit](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T052208Z-exact-86967189/dependency_audit.json) |
| Smoke PASS | [reconstructed](configs/reconstructed.json) | `50f9c29b9ce7647e5e0f96ac7ccffc34cf1860d1` | [run](../../../results/invsqrt/INV-66/reconstructed/smoke/20261115T042039Z-local-smoke-4371a2/verifier.json), [provenance](../../../results/invsqrt/INV-66/reconstructed/smoke/20261115T042039Z-local-smoke-4371a2/provenance.json) |
| Full PASS | [reconstructed](configs/reconstructed.json) | `50f9c29b9ce7647e5e0f96ac7ccffc34cf1860d1` | [run](../../../results/invsqrt/INV-66/reconstructed/full/20261115T042258Z-local-full-7feec4/verifier.json), [provenance](../../../results/invsqrt/INV-66/reconstructed/full/20261115T042258Z-local-full-7feec4/provenance.json), [analysis](../../../results/invsqrt/INV-66/reconstructed/full/20261115T042258Z-local-full-7feec4/analysis.json) |

Lần build đầu của source 92a1069 sinh target bytes nhưng không hoàn tất provenance vì platform.platform() gọi hostname bị audit chặn. Source 50f9c29 thay metadata platform bằng sys.platform rồi build sạch lại; không đổi circuit.py hoặc góc. Dữ liệu lần lỗi ở scratch riêng, không được gọi là build nghiệm thu. CPython audit không bao phủ mọi native OS read; precursor dùng builder, adapter chỉ nạp PP-005 đã khai báo, serializer KMB dùng BytesIO và file write qua Python. Source cache probe do importer thử mở không tồn tại sau build, không có cache cũ được chép vào checkout.

Attribution được giữ theo notebook và NOTICE; giấy phép của mọi component trong lineage chưa được xác minh độc lập. Cần reviewer kiểm tra giới hạn này trước công bố/merge. Smoke và full đã được thành viên chạy; chưa có lượt salt/seed bổ sung. Bước tiếp theo là review độc lập theo bước 9; không tự merge.

## Phân tích chấm local (bước 8)

Run smoke kiểm tra 4096 input với một shot/input; run full kiểm tra toàn bộ 3133452 input với 64 shot/input, tổng 200540928 shots. Cả hai PASS, exit code 0, stderr rỗng; JSON trong stdout khớp verifier.json. Hash artifact, hash verifier và provenance khớp record build sạch; source thực tế vẫn là 50f9c29, không suy ra từ HEAD của commit phân tích. Không sửa raw JSON/log hoặc metadata của run.

Full xác nhận 46 qubit, mean Toffoli 1479.7500405453395, Toffoli-equivalent 1711.2941118988529, một T gate và 33 generic rotations. Worst error/tolerance 0.9986660009092673 tại x=159, còn khoảng 0.1334% dung sai trước khi chạm ngưỡng. Đây là biên hẹp; không có cơ sở giảm precision hoặc thay góc trong phạm vi tái dựng exact. Smoke chỉ dùng kiểm tra nhanh, không có điểm dev hoặc dòng điểm riêng.

Chi phí full thấp hơn baseline INV-BASELINE khoảng 26.3819 lần (baseline/candidate), theo hai run full PASS được dẫn trong SCORES. Đây là lợi thế của mạch public đã tái dựng, không phải cải thiện mới do decompilation. Hai lượt dùng cùng Python 3.13.18, Kickmix 1.0.0, NumPy 2.5.4, SciPy 1.18.1 và engine 0.6.0; baseline dùng glibc2.35/1 thread, candidate glibc2.39/4 threads. So sánh được phép theo chính sách repo, giữ nguyên metadata bối cảnh. Build xảy ra trên Windows Python 3.13.7; chấm xảy ra trên WSL Linux Python 3.13.18. Hai môi trường được ghi riêng, không thay môi trường build trong provenance bằng môi trường chấm.

Giá trị cost/error full khớp phần invsqrt trong receipt bên ngoài, nhưng kết luận local dựa trên log mới của thành viên. Cùng artifact/hash và không override salt/seed có nghĩa các lượt dùng policy seeded mặc định; không gọi đây là kiểm chứng bằng seed độc lập so với receipt. Full không liệt kê mọi transcript đo có thể xảy ra.

Hypothesis tái lập exact được ủng hộ bởi build sạch và đối chiếu bytes; tính đúng theo bộ kiểm tra chính thức được xác nhận bằng full PASS trong điều kiện ghi lại. Mục tiêu exact ban đầu đã đạt ở mức phục hồi cấp cổng. Review tiếp theo yêu cầu mức thuật toán cao hơn, hiện chưa đạt; cần làm lại generator trước khi gửi lại review. Kiểm tra salt bổ sung chỉ là việc có thể giao riêng; không tự chạy hoặc mở hướng tối ưu mới.

## Tách postprocessing PP-005

Bản refactor mới sinh precursor dcde7078 bằng builder, giữ CCX gốc tại operation 3292 và HMR ở vị trí muộn ban đầu. Sau đó adapter nạp [PP-005](../postprocessing/PP-005/DESCRIPTION.md) bằng đường dẫn và gọi rewrite tại đúng site 3292. Không còn hard-code hai cổng đã sửa trong generator. PP nằm trên branch riêng, có Issue riêng #70; PR INV-66 phụ thuộc branch PP, không sửa checker để bỏ giới hạn scope.

PP-005 đã được kiểm chứng riêng trên raw INV-BASELINE + identity harness với hai lượt smoke cùng seed, không dùng frontier đã hậu xử lý như đối chứng chưa PP. Kết luận PP và số đo riêng không gộp thành run/results experiment. API dùng generated in-memory circuit, không đọc artifact gốc. Source/config hash, dependency PP và audit phải được khóa lại ở build sạch mới. Các run smoke/full lịch sử tiếp tục gắn source 50f9c29; không thay provenance hoặc diễn giải như run chấm mới của refactor.

Build tích hợp PP-005 đã đạt RECONSTRUCTED_EXACT từ clone GitHub sạch của source a9b0dd06833c364fbc53687799f4cf30a127f7f1 và venv mới, chạy entry point từ cwd ngoài checkout. Precursor mới sinh có SHA-256 dcde70780434501912c5cc032c6dfad25ac694d50da4e8e45cdb65115baa81b2; PP-005 rewrite đúng một site, output 198590 bytes khớp streamed bytes/hash e46d90c3 của artifact đã full PASS. Provenance mới khóa thêm source/hash PP-005 và report precursor; không đọc binary/KMX gốc trong build.

Không có lượt verifier experiment mới sau refactor. Full PASS lịch sử vẫn gắn source 50f9c29, không được đổi sang a9b0dd0. Kết quả smoke riêng PP chỉ nằm trong phần mô tả phương pháp/chat; thư mục build_only mới này là bằng chứng build integration theo luồng decompiler, không phải run chấm PP. Có nhiều build cùng hash; nếu chấm lại cần đối chiếu source/build cụ thể khi notebook báo provenance mơ hồ, không tự chọn HEAD.

Theo yêu cầu gộp PR của người dùng, PP-005 và tích hợp INV-66 được nộp chung trong PR #67 hướng về main; PR #71 được đóng vì toàn bộ commit đã nằm trong #67. Mã PP vẫn tách trong src/invsqrt/postprocessing/PP-005 và Issue #70 vẫn quản lý phương pháp. Theo nhiệm vụ sửa CI được giao sau khi gộp PR, checker xác minh PP dependency theo manifest đã commit và SHA-256 của module; chỉ folder PP đó và dòng catalog tương ứng được phép đi kèm. Tests chặn PP/track/experiment khác và declaration chưa commit. Phạm vi bootstrap checker/tests/docs được giới hạn cho base còn policy cũ; không tắt kiểm tra scope hoặc đổi tên branch. Chưa merge; cần review độc lập HEAD mới. Sau khi PP đổi hoặc resolve conflict cần build/review lại HEAD liên quan.


## Phục hồi số học độc lập — tiến độ cách 2

Đã phục hồi model normalize/root, bảng 64 hàng A13/S7, sáu hàng coefficient,
seed và mười hàng signed product. `validate_recovery.py` đối chiếu thanh ghi trên
toàn miền 3.133.452 x; kiểm tra riêng cả 4.096 v, cả 64 địa chỉ cho mỗi loader và
4.096 nhánh đo ngẫu nhiên. Xem [bằng chứng và giới hạn](evidence/algorithm_recovery.json).
Hai loader đã thay 2.977 lệnh tĩnh bằng compiler GF(2) và certificate toán học
(27/29 coordinate bậc hai, các ma trận affine khả nghịch); certificate chỉ là
lookup sáu đầu vào, không phải toàn mạch hay payload KMB/KMX.

Source dcb4794910d04a3b86a8d1b3a68bf9adfbab15d6 đã được clone mới từ GitHub và
build bằng venv mới, cwd ngoài checkout, package pin của repo. Run
`results/invsqrt/INV-66/reconstructed/build_only/20261115T100613Z-exact-8259a1b7`
ghi provenance/audit và đối chiếu bytes độc lập: 198590 bytes,
SHA-256 e46d90c36d1beb3ce7731a3e0b5c3659b3cda7f5f290b73c6c34513d96c005b6.
PP-005 vẫn là module riêng và rewrite đúng một site. Không chấm lại; các run/receipt
lịch sử giữ nguyên nguồn và provenance.

Đây là phục hồi từng thành phần, chưa phải generator số học toàn mạch.
Model quotient/pha divider, inverse product và cleanup cấp cao vẫn còn thiếu;
`GATE_LEVEL_PYTHON` và trạng thái review chưa được xử lý xong vẫn giữ nguyên.
