# [INV-66] Tái dựng mạch invsqrt e46d90c3 bằng Python cấp cổng từ KMX, giữ nguyên pha và sửa HMR/CZ

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

ROUNDTRIP_EXACT và RECONSTRUCTED_EXACT đã có bằng chứng riêng. Chưa chấm local. Receipt chỉ là bằng chứng bên ngoài, không chuyển thành run của repo. Mức phục hồi cấp cổng; chưa suy ra thuật toán số học gốc.

## Source cấp cổng và cách chạy

[solution.py](solution.py) là entry point; [circuit.py](circuit.py) chứa lời gọi CircuitBuilder trực tiếp, bảy hàm chia theo vùng quan sát và 136 vòng lặp sweep X. Không có parser KMX, tải binary, gate table, source string hay exec/eval trong generator. Góc quay là scalar decimal string chính xác truyền cho API, không qua float. Hai file Python và [configs/reconstructed.json](configs/reconstructed.json) là dependency runtime của hướng; requirements.txt khai báo package pin. [reconstruction.json](reconstruction.json) ghi nguồn/hash, vai trò file và mức phục hồi; [NOTICE.txt](NOTICE.txt) giữ attribution và giới hạn giấy phép.

Mức phục hồi là GATE_LEVEL_PYTHON: source rõ từng cổng và có thể sửa, nhưng chưa phục hồi phép tính số học cấp cao hoặc cách tác giả tìm mạch. Đây là đường triển khai được bước 05 cho phép, không phải source gốc. Input KMB/KMX chỉ được dùng để phân tích trước khi viết source và đối chiếu độc lập sau build.

```powershell
.venv/Scripts/python.exe src/invsqrt/INV-66/solution.py --config src/invsqrt/INV-66/configs/reconstructed.json
```

Chạy Python 3.13 và package pin. Config phải nằm trực tiếp trong configs của hướng; chỉ hỗ trợ reconstructed với target cố định. Output mới mặc định artifacts/invsqrt/INV-66/reconstructed.kmb, không ghi đè. Entry point kiểm tra checkout sạch, source/config khớp Git snapshot, rồi dựng trong bộ nhớ và ghi artifact mới. Audit chặn read ngoài source/runtime/output và network/subprocess trong construction; Git snapshot preflight và khởi động interpreter xảy ra trước audit. Native library OS reads không được CPython audit bao phủ; source generator chỉ gọi builder, serialization dùng BytesIO và file write qua Python.

Source commit `50f9c29b9ce7647e5e0f96ac7ccffc34cf1860d1` đã dựng từ clone GitHub mới, venv mới và cwd ngoài checkout; công cụ đối chiếu riêng xác nhận exact. Không chạy verifier. Working tree chính và thay đổi notebook của người dùng không bị sửa.

## Bằng chứng exact và giới hạn phục hồi

[Inventory](evidence/circuit_inventory.json) ghi register x=q0..q21, scratch q22..q45, classical bit capacity 387, điều kiện lồng tối đa hai mức. 23877 operation gồm 38 Z_POW (4 Clifford, 1 T, 33 generic); số cổng tĩnh không phải chi phí thực thi trung bình. Bản đồ vùng trong circuit.py chỉ mô tả vị trí quan sát, không gán tên thuật toán chưa chứng minh. [Round-trip](evidence/roundtrip.json) kiểm tra serializer trước khi viết source. [Receipt invsqrt](evidence/external_receipt_invsqrt.json) chỉ giữ phần liên quan từ receipt gốc có hash, không đại diện run local.

Hypothesis tái lập được ủng hộ ở mức source Python cấp cổng: KMB mới 198590 bytes, cùng SHA-256 mục tiêu và streamed bytes bằng input. Entry point không đọc file circuit gốc hoặc KMX. Không khẳng định phục hồi root/normalization/divider gốc hay cải thiện baseline. INV-51 chỉ là nguồn so sánh khác target, không phải dependency runtime.

| Mốc | Config | Commit source thực sự dùng | Bằng chứng |
| --- | --- | --- | --- |
| Build sạch exact | [reconstructed](configs/reconstructed.json) | `50f9c29b9ce7647e5e0f96ac7ccffc34cf1860d1` | [provenance](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T033727Z-exact-fe8b97b7/provenance.json), [so bytes/hash](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T033727Z-exact-fe8b97b7/reconstruction_check.json), [checkout/setup](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T033727Z-exact-fe8b97b7/clean_checkout.json), [audit](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T033727Z-exact-fe8b97b7/dependency_audit.json) |
| Smoke/full | Chưa chấm | Không có source/run chấm mới | Receipt bên ngoài không thay thế run repository |

Lần build đầu của source 92a1069 sinh target bytes nhưng không hoàn tất provenance vì platform.platform() gọi hostname bị audit chặn. Source 50f9c29 thay metadata platform bằng sys.platform rồi build sạch lại; không đổi circuit.py hoặc góc. Dữ liệu lần lỗi ở scratch riêng, không được gọi là build nghiệm thu. CPython audit không bao phủ mọi native OS read; generator chỉ có builder calls, serializer dùng BytesIO, file write qua Python. Source cache probe do importer thử mở không tồn tại sau build, không có cache cũ được chép vào checkout.

Attribution được giữ theo notebook và NOTICE; giấy phép của mọi component trong lineage chưa được xác minh độc lập. Cần reviewer kiểm tra giới hạn này trước công bố/merge. Chưa chạy verifier hoặc smoke/full, chưa có bằng chứng thử seed bổ sung. Bước tiếp theo là thành viên chấm notebook local ở bước 8 rồi review độc lập; không tự merge.
