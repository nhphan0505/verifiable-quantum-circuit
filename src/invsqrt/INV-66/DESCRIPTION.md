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

Đã có ROUNDTRIP_EXACT ngoài Git; chưa có source build, chưa có provenance build hoặc run chấm local. Receipt là bằng chứng bên ngoài, không chuyển thành run của repo. Config dự kiến reconstructed. Bước 5-6 sẽ ghi mapping commit/config/build thật; bước 7 hoàn thiện giới hạn phục hồi cấp cổng.

## Source cấp cổng và cách chạy

[solution.py](solution.py) là entry point; [circuit.py](circuit.py) chứa lời gọi CircuitBuilder trực tiếp, bảy hàm chia theo vùng quan sát và 136 vòng lặp sweep X. Không có parser KMX, tải binary, gate table, source string hay exec/eval trong generator. Góc quay là scalar decimal string chính xác truyền cho API, không qua float. Hai file Python và [configs/reconstructed.json](configs/reconstructed.json) là dependency runtime của hướng; requirements.txt khai báo package pin. [reconstruction.json](reconstruction.json) ghi nguồn/hash, vai trò file và mức phục hồi; [NOTICE.txt](NOTICE.txt) giữ attribution và giới hạn giấy phép.

Mức phục hồi là GATE_LEVEL_PYTHON: source rõ từng cổng và có thể sửa, nhưng chưa phục hồi phép tính số học cấp cao hoặc cách tác giả tìm mạch. Đây là đường triển khai được bước 05 cho phép, không phải source gốc. Input KMB/KMX chỉ được dùng để phân tích trước khi viết source và đối chiếu độc lập sau build.

```powershell
.venv/Scripts/python.exe src/invsqrt/INV-66/solution.py --config src/invsqrt/INV-66/configs/reconstructed.json
```

Chạy Python 3.13 và package pin. Config phải nằm trực tiếp trong configs của hướng; chỉ hỗ trợ reconstructed với target cố định. Output mới mặc định artifacts/invsqrt/INV-66/reconstructed.kmb, không ghi đè. Entry point kiểm tra checkout sạch, source/config khớp Git snapshot, rồi dựng trong bộ nhớ và ghi artifact mới. Audit chặn read ngoài source/runtime/output và network/subprocess trong construction; Git snapshot preflight và khởi động interpreter xảy ra trước audit. Native library OS reads không được CPython audit bao phủ; source generator chỉ gọi builder, serialization dùng BytesIO và file write qua Python.

Mốc source hiện tại chưa build; không có provenance hoặc run local mới. Bước 6 phải chạy entry point từ cwd khác trong checkout sạch của commit đã push và môi trường mới, sau đó so bytes/hash bằng công cụ riêng. Không dùng working tree có thay đổi của chat khác.
