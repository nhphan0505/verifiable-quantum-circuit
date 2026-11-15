# INV-66 — thuật toán số học đã phục hồi

Generator số học đầy đủ đã thay source cấp cổng. Build sạch của source
f04c85e17d8114ec99a9a116da7f3ee44ba7e33c đạt RECONSTRUCTED_EXACT cho 198590 bytes,
SHA-256 e46d90c36d1beb3ce7731a3e0b5c3659b3cda7f5f290b73c6c34513d96c005b6.
Review cũ 5909379196 yêu cầu mức số học; implementation mới đã bổ sung các khối đó,
nhưng approval/review độc lập trên HEAD mới vẫn chưa có.

## Biểu diễn và luồng

```mermaid
flowchart LR
  X[Normalize x] --> R[Consumed root and residual]
  R --> C[64-row coefficient, seed, product]
  C --> D[Balanced m37 divider and phase]
  D --> I[Inverse product and coefficient]
  I --> E[Decode address and repay HMR debts]
  E --> U[Inverse root and normalization]
```

Số bit được ghi theo little-endian. Các word là phần tử modulo 2**width, không
tự suy ra signed/real value chỉ từ physical wire. Owner được đổi khi HMR/free;
token carry/debt phải được tiêu thụ đúng một lần.

1. Với x=1..3133452: k=floor((22-bit_length(x))/2), n=x*4**k.
2. R=floor(sqrt(16*n)), v=R-4096 (12 bit),
   h=(n-floor(R*(R+1)/16)-1) mod 1024 (10 bit).
3. Địa chỉ a=v>>6, tọa độ t=v&63. A[a] có 13 bit, S[a] có 7 bit;
   stored slope H=S>>1 có 6 bit. Hai loader trả A13 và Hlow4.

R-frame của địa chỉ là
`r = a5 xor a0 xor a1 xor a2 xor ((a0 xor a2) & a4)`.
Metadata mượn A11/A12 làm H4/H5 trong coefficient forward; R được frame thành
parity của S. Sau sáu hàng, metadata được đảo trước overflow update.

## Coefficient, seed và product

Coefficient không phải một phép nội suy rồi làm tròn ở cuối. Với mỗi i=0..5,
j=5-i, u=S>>(j+1): cộng u+S_j khi t_i=0, trừ u+S_(j-1) khi t_i=1;
S_-1=0. C là tổng đó với A, modulo 8192. Snapshot A7 và một window 8 bit giữ
đủ thông tin trả overflow/carry debt khi inverse.

Seed dùng ba tọa độ Boolean tạm của v: p0=v0 xor v2, p1=v1 xor v2,
p3=v3 xor v2 xor (p0&p1), rồi p0 xor= p1. Khởi tạo ba bit bằng 7; ba hàng
signed dùng C cắt/làm tròn ở 11/10/9 và thêm bit 1-p tương ứng, cho seed 6 bit.

Product bắt đầu từ seed6 nối h10 và sentinel ở bit 15. Mười hàng signed cộng
word 2*C đã dịch vào phần thấp đang lớn dần; carry dùng parity C7 và các bit
lân cận, hàng cuối có carry alias. Sentinel được trả/freed, còn P15 là word
modulo 32768 đi vào divider. `signed_product` trong recovery_model.py ghi đầy đủ
công thức bitwise và rounding, không thay bằng phép nhân real gần đúng.

## Balanced divider m37 và pha

Khởi tạo remainder 14 bit:
`U = (4094 - 3*v + P12 + P13 - 2*P14) mod 16384`.
Đây là dạng triangular code có thể HMR P13/P14 rồi dựng lại khi inverse.

Có 24 hàng j=12..35. Với 13 hàng đầu, prev=P_(24-j), cur=P_(23-j)
(cur=0 ở j=24), s=U13, v0=v&1. Carry Boolean:

```text
F = v0 xor prev xor (v0&prev) xor (v0&cur)
    xor (prev&cur) xor (prev&s) xor (cur&s)
T = ((U&8191) + (2*s-1)*((v>>1)+F+2048)) mod 8192
U = 2*T + (prev xor v0 xor s xor cur)
```

Lưu s vào history[j]. Các hàng j>=25 xoay U13 xuống bit 0; giữ phần thấp và
chỉ cập nhật phần cao có width 13-k bằng phép cộng/trừ tương tự, với k=0 ở
j=25..27, k=j-26 ở j>=28. Leading offset là 2**(11-k), carry là v_k.
`divider_forward` và `divider_inverse` là hai recurrence cổ điển độc lập với
CircuitBuilder; nghịch đảo dựng lại cả 15 bit P, kể cả hai bit cao đã đo.

Sigma25 frame và các XOR v0/v1 biến U/history thành 25 sign bit. Đảo các sign,
thêm một bit 1, được vòng 26 bit. Năm controlled reflection có centres
(2,6,24,0,25); controls từ các bit f_i của k:
(1 xor f2, f3, 1 xor f1 xor f2 xor f3, 1 xor f0 xor f1, 1 xor f0).
Slots là phép quay (21,22,23,24,25,0,...,20).

Nếu b_i là bit tại slot i, pha tính bằng half-turn, modulo 2:

```text
sum(i=0..25, alpha_i*b_i)
+ sum(j=0..6, beta_j*[k>=j+1]*b_j)
+ (1/4)*[k>=8]*b7 + (1/2)*[k>=9]*b8 + f1*f3
```

33 alpha/beta là số dyadic trong data/phase_parameters.json, denominator tới
2**63. Các giá trị đã được khôi phục, không giả là đã lặp lại search góc upstream.
Term overflow-8 có giá trị khác 0 ở 13 input nhỏ; PP-004 chuyển implementation
của nó về normalization, không được bỏ term đó khỏi model. Tất cả 33 generic
feature và fixed phase đã khớp trên cả 3.133.452 x.

## Inverse arithmetic và S4

Sau divider cleanup, P trở lại đúng word cũ trên owner mới. Loader hai tái sử
dụng năm address owner 0..4, chỉ giữ R-frame. Coefficient thứ hai tái tạo C;
conditional Z trả 13 outcome đã đo C lần đầu và XOR các carry transcripts.

Đo S4 (H3), mượn owner đó cho high product bit. Inverse product đi ngược mười
hàng, trả mọi CarryDebt bằng inverse adder có borrowed dirty wires; đo ba root
bit 0/1/3 để có workspace. Inverse seed dựng lại chính ba root bit đó, trả pha
đo tương ứng và khôi phục h10.

Inverse coefficient đảo overflow trước, release snapshot, dựng H5 từ A10..12,
rebuild S4 bằng hai AND trên A/Hlow và H5, dựng H4 bằng một AND nữa, frame parity
trong R, rồi đảo sáu hàng coefficient. H4/H5 được HMR với quadratic correction;
snapshot outcome được trả bằng A7 đã phục hồi. S4 outcome được hoãn sang cleanup.

## Decoder và cleanup: chứng minh mọi outcome

Decoder tám AND trên A13/Hlow4/R trả đúng cả sáu bit địa chỉ trên 64 codewords.
R-frame được uncompute và release bằng biểu thức quadratic đã biết. Sau đó
chart raw6+A13+Hlow4 có quadratic rank 64, biểu diễn được mọi Boolean function
của địa chỉ, kể cả cả 30 debt từ hai loader, Hlow lần đầu và S4.

Với mỗi debt m của function f(a), codebook giải polynomial p trên chart hiện
tại, kiểm p(a)=f(a) cho cả 64 địa chỉ rồi áp (-1)**(m*p). Dấu HMR
(-1)**(m*f) triệt tiêu cho mọi m; không cần chọn một measurement sample.

Retirement lần lượt xóa 17 table outputs. Tám bank trung gian có functions
a1*a2, a4*a5, a3*a4, a0*a1, a0*a2, a0*a1*a2, a3*a5, a3*a4*a5 giữ đủ span cho
các erasure tiếp theo. Mỗi bank/output được HMR và giải lại polynomial trên
chart còn sống. Cuối cùng xóa tám bank theo thứ tự nghịch, chỉ còn raw6.
Không lưu phase opcode list: polynomial được solver dựng từ truth vectors.

Test giữ 55 outcome như các biến ký hiệu độc lập, theo dõi hệ số pha 64 bit cho
từng biến; mọi hệ số đều zero. Điều này bao phủ đồng thời mọi tổ hợp 2**55 outcome
trong native Boolean cleanup. Các PP sau đó vẫn là module/phép kiểm riêng.
Sau cleanup chỉ còn v12+h10+flags4, đủ chạy inverse root/normalization và layout.

## Kiểm chứng và dependency

[evidence/algorithm_recovery.json](evidence/algorithm_recovery.json): toàn miền x,
cả 4096 v, cả 64 địa chỉ, model chia thuận/nghịch và pha. Công cụ phân tích chỉ
đọc reference ngoài solution để đối chiếu, không được runtime builder gọi.
[Tests](tests/test_arithmetic_recovery.py) kiểm symbolic cleanup và các boundary
chia/hold-coordinate. [Build exact](../../../results/invsqrt/INV-66/reconstructed/build_only/20261115T112732Z-exact-b6c89817/reconstruction_check.json)
và dependency audit ghi source f04c85e, checkout GitHub sạch, venv mới, cwd khác.

Helper số học chia sẻ chỉ đọc INV-51/circuit.py và 16 math/compatibility objects
đã chọn trong data/arithmetic_helpers.json; không chạy entry point/gate replay
hoặc đọc INV-51/tables.json. Finishing gọi PP-001..PP-004, sau đó PP-005 riêng;
adapter remap tọa độ chain đan xen, không sửa implementation PP của owner khác.

Không còn khối số học/cleanup để lại dưới dạng liệt kê toàn chuỗi cổng.
Source private và quy trình fit/search tham số không được nhận là đã lấy lại.
Không có lượt verifier mới hoặc analytic error bound mới; provenance full PASS
lịch sử vẫn gắn đúng source cũ. Review độc lập HEAD mới còn phải thực hiện.
