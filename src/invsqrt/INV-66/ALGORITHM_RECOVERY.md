# INV-66: phục hồi thuật toán sau review

## Trạng thái nghiệm thu

Review [5909379196](https://github.com/nhphan0505/verifiable-quantum-circuit/pull/67#pullrequestreview-5909379196) của nhphan0505 trên commit 6c94828436f3deba8b92069e064afafeebc884fb yêu cầu phục hồi thuật toán số học gốc. Bản hiện tại chỉ đạt GATE_LEVEL_PYTHON. Build exact, full PASS và tests PP không đáp ứng thêm điều kiện mới này. Chưa xử lý xong yêu cầu review; không đề nghị approve/merge hoặc đổi nhãn recovery level.

## Kết quả truy nguồn đã xác minh

[Evidence](evidence/review_followup.json) ghi version, SHA-256 source notebook đã tải, review/commit và kết quả HTTP. Chỉ đọc source như dữ liệu, không chạy notebook tải về.

1. Notebook public ahoirg/qcc-submit-verify-and-package v25 xác định invsqrt 4560ac0c được dựng từ fork generator Syed Asad Ali với bảng 64 hàng, 6 bit địa chỉ, 13 bit intercept và 7 bit slope; hai loader được tổng hợp lại, S4 bị đo bỏ rồi dựng lại trước inverse product, hold pass xử lý interleaved chain. Source notebook chỉ tìm và đóng gói binary invsqrt_k6c.kmb từ input, không chứa generator của fork.
2. Generator được notebook đó dẫn là ahoirg/qcc-invk6-k6c. API public trả HTTP 403 khi kiểm tra. Không cố vượt quyền truy cập; chưa có source/data của fork này trong checkout.
3. Atakan Aldemir quantum-circuits-iso-gap-dqi-h5 v20 đưa bước refit 33 góc từ 4560ac0c sang dcde7078. Source ghi generator/proof riêng không được truy cập. Hai notebook Atakan và portfolio Alex Chilton v155 cung cấp binary/refit/attribution; chưa cung cấp generator số học 64 hàng có thể dùng để dựng từ đầu.
4. Notebook giải thích của sheroleg v10 dùng mạch đã compile và phép đo/profile để giải thích, không thay thế source generator.
5. Source INV-51 trong repo và bundle invsqrt_source_zip cũ là nguồn số học thật nhưng khác phiên bản: bảng A/S/stored_slope có 128 hàng, target 321aff83, không phải target e46d90c3 của INV-66. Không được đổi tên wrapper INV-51 thành INV-66 hoặc coi hai generator tương đương vì cùng 46 qubit.

Các đoạn source tải về và archive gốc chỉ nằm trong scratch ignored, không đưa nguyên bundle/notebook/base64/binary vào runtime hay Git. Evidence JSON chỉ giữ nguồn/hash và kết luận truy nguồn.

## Phục hồi độc lập từ artifact — cách 2

Đã bắt đầu phục hồi độc lập, không chờ quyền truy cập generator riêng.
[recovery_model.py](recovery_model.py) là model số học cổ điển mới viết từ
quan sát mạch, có bảng intercept/slope thật; không chứa chuỗi cổng hoặc đọc
artifact. Model chưa phải builder toàn mạch. Hai loader đã thay 2.977 lời gọi cổng trong `circuit.py` bằng [lookup_certificate.py](lookup_certificate.py) và [certificate GF(2)](data/lookup64_certificates.json).

Với x hợp lệ, các invariant đã kiểm tra:

- `k = floor((22 - bit_length(x))/2)`, `n = x * 4**k`.
- `R = floor(sqrt(16*n))`, `v = R - 4096`, `h = (n - floor(R*(R+1)/16) - 1) mod 1024`.
- Địa chỉ bảng `a = v >> 6`, tọa độ trong ô `t = v & 63`.
  Hai loader trả cùng intercept 13 bit và bốn bit thấp của stored slope.
  Slope đầy đủ có 7 bit; stored slope là `S >> 1`, có 6 bit.
- Hệ số C được cập nhật bằng sáu hàng cộng/trừ của S, với rounding khác nhau
  cho dấu dương/âm. Hàm `coefficient` ghi rõ công thức từng hàng; thay bằng
  một phép nội suy tuyến tính làm tròn cuối cùng sẽ cho kết quả khác.
- Seed 6 bit dùng ba hàng signed, cắt ở bit 11/10/9, trên các tọa độ Boolean
  tạm của v. Tích 15 bit dùng mười hàng signed trên residual, có carry phụ
  thuộc parity của C và carry alias ở hàng cuối.

Các biên operation dưới đây đếm từ 0, loại metadata; biên là exclusive:

| Biên | Trạng thái | Bằng chứng |
| --- | --- | --- |
| 609 | n, k sau normalize | Toàn bộ 3.133.452 x |
| 1638 | v12, h10 sau căn bậc hai | Toàn bộ 3.133.452 x |
| 2866 | Loader đầu trả A13, Hlow4 | Cả 64 địa chỉ; 27 CCX |
| 3283 | C13 sau sáu hàng coefficient | Cả 4.096 v và toàn miền x |
| 3404 | Seed6 | Cả 4.096 v và toàn miền x |
| 4407 | Product15 trước khi đo bỏ C | Toàn bộ 3.133.452 x |
| 15006 | Divider trả lại product trên owner mới | Toàn bộ 3.133.452 x |
| 16761 | Loader hai trả cùng A13, Hlow4 | Cả 64 địa chỉ; 29 CCX |
| 23877 | x phục hồi, scratch zero | Toàn bộ 3.133.452 x |

Loader hai tái sử dụng năm raw address bit 0..4 làm workspace. Chỉ giữ tọa
độ R-frame trên q44, thay vì lifecycle bảy bit của INV-51. Đây là khác biệt
thuật toán/allocation cần triển khai, không thể chỉ thay bảng 128 thành 64 hàng.

### Đối chiếu divider với INV-51

[evidence/divider_correspondence.json](evidence/divider_correspondence.json)
ghi ánh xạ dây và bốn đoạn khác nhau giữa raw INV-51 [6712,17303) và target
[4420,15006). Có 10.575 operation khớp sau khi đổi tên dây, bỏ qua ID bit đo
và giá trị góc quay. Bốn đoạn còn lại gồm tách/đo AND giữ lại, một feature pha
bị bỏ và một CSWAP chuyển thành HMR/CZ. Đây là correspondence tĩnh; chưa chứng
minh các rewrite đó từ source hoặc mọi measurement branch.

### Lặp lại kiểm tra phân tích

`validate_recovery.py` chỉ là công cụ kiểm chứng model, không được gọi từ
`solution.py` hoặc dùng làm đầu vào build. Nó nhận KMX tham chiếu tường minh,
kiểm hash trước khi diễn giải và không chạy verifier/engine:

```powershell
.\.venv\Scripts\python.exe src/invsqrt/INV-66/validate_recovery.py --reference-kmx <scratch>/circuit.kmx
```

[evidence/algorithm_recovery.json](evidence/algorithm_recovery.json) ghi hash
model/validator đã chạy, phạm vi kiểm tra và giới hạn. Kiểm tra thanh ghi toàn
miền dùng outcome HMR=0. Ngoài ra, 4.096 cặp input/measurement branch ngẫu nhiên
(512 input, tám trial, seed 660067) khôi phục x/scratch và khớp pha modulo hai
half-turn với nhánh outcome=0, dùng số hữu tỉ từ giá trị góc in trong KMX.
Đó là kiểm tra hữu hạn, không phải chứng minh mọi outcome, không phải điểm chấm
và không phải provenance của một source build mới.

## Phần chưa phục hồi và bước tiếp

1. Chứng minh cơ chế trả phase debt cho mọi outcome. Hai certificate đã phục hồi
   có 27/29 coordinate bậc hai, 40/44 ma trận đổi cơ sở affine và 10/15 phép đo.
   Emitter dùng Gaussian elimination GF(2), sinh khớp đúng toàn bộ 1.228/1.749
   operation lookup. Dữ liệu chỉ mô tả Boolean LUT sáu đầu vào, không chứa góc,
   ID bit đo, toàn mạch hoặc chuỗi opcode. Caller truyền owner dây/bit đo;
   phần cleanup cũ vẫn giữ trách nhiệm trả debt, chưa được phục hồi cấp cao.
2. Viết model quotient/pha của balanced divider và tham số refit 33 góc.
   Correspondence 10.575 operation không thay thế model pha số học.
3. Phục hồi inverse product, retire/rebuild slope S4, giải mã các address bit
   bị đo và cleanup. Kiểm tra x/scratch ở cuối không chứng minh cách dựng các khối.
4. Dựng lại từ helper số học, register có invariant và bảng/certificate đã track.
   Giữ các finishing/postprocessing ở module riêng, gồm PP-005; không đưa dữ liệu
   KMB/KMX hay toàn chuỗi cổng vào runtime.
5. Commit source trước build sạch từ commit đã push và môi trường mới, đối chiếu
   đúng 198590 bytes/SHA-256 e46d90c36d1beb3ce7731a3e0b5c3659b3cda7f5f290b73c6c34513d96c005b6.
   Không sửa run/receipt cũ hoặc hạ tiêu chí exact.
6. Chỉ sau khi các khối đã thành builder số học thật mới cập nhật reconstruction
   level và gửi review độc lập lại. Review hiện vẫn chưa được xử lý xong.

Không thiếu KMB hoặc receipt để tiếp tục cách 2. Source private sẽ hữu ích nếu
được cung cấp hợp lệ, nhưng không còn được coi là điều kiện bắt buộc để làm phân tích.


## Nghiệm thu build của bản phục hồi từng phần

Source dcb4794910d04a3b86a8d1b3a68bf9adfbab15d6 đã build từ clone GitHub sạch,
venv mới và cwd ngoài checkout. [Reconstruction check](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T100613Z-exact-8259a1b7/reconstruction_check.json)
ghi so bytes độc lập sau build: 198590 bytes và SHA e46d90c3…005b6. Audit ghi
Python/helper/certificate/PP đã khai báo, không có network/subprocess trong dựng.
Đây là nghiệm thu exact của bản builder từng phần, không phải nghiệm thu model
pha hoặc toàn bộ thuật toán cấp cao. Không có verifier run mới.
