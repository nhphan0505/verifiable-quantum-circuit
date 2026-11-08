# [DQI-10] Hợp nhất con trỏ unary iteration và thu gọn ancilla bằng điều khiển xung khắc, giữ 222 bước EEA

Loại: Tinh chỉnh một phương án.

## File gốc

Kế thừa [DQI-BASELINE/solution.py](../DQI-BASELINE/solution.py) và
[config baseline](../DQI-BASELINE/configs/baseline.json) tại commit
`e1463adcfcec61ed1c00d161ad40bc2ec64c10fc`. Giữ Apache-2.0 của
[src/LICENSE.txt](../../LICENSE.txt). Verifier gốc có SHA-256
`2b8e1b80a806157c333a7e308eaf2499ee09de499efbc05875202c327959959e`
trong [manifest](../../../data_manifest.json).
Cơ sở ý tưởng là mục tối ưu liveness/con trỏ của
[note ready đã merge](../../../research/dqi/papers/arxiv-2510.10967/note.md).
Không sử dụng PDF hoặc nguồn thảo luận chưa được review.

## Phần tinh chỉnh và lý do

Giữ m=4095 vị trí, n=70 syndrome, GF(2^12), Chien/Forney và
`default_n_iters(70)=222`; không xấp xỉ số học hoặc thay điều kiện dừng.
Tên m bên dưới chỉ độ dài mảng EEA, bằng n+3=73.
Trong `_multiply_and_add_or_sub.sweep_positions`, bốn cây unary iteration
trở thành hai cây nhờ c0_hc/c3_hc one-hot. Trong `_shift_b_array_right`,
ba cây thành hai cây bằng cách hợp nhất hai cây trên n_B.
Loại thanh ghi ratio tạm khi tích lũy thương. Thu hẹp n_A,n_B,n_a,n_b
về m.bit_length()=7; giữ n_q ở 8 bit cho tổng tạm n_q+n_a.

## Cách thực hiện và đánh đổi

Các điều khiển c0..c3 không thay đổi trong subroutine; OR của điều khiển
one-hot thực hiện bằng XOR vào một ancilla và được xóa đối xứng.

1. Con trỏ thương: trước sweep trừ 1 khỏi n_q khi c3, tạo điều khiển
   c0 XOR c3. Match tại i tương đương c0 AND old_n_q=i hoặc
   c3 AND old_n_q=i+1. Sau đóng cursor cộng lại 1 khi c3.
2. Con trỏ nhân: CSWAP n_a với n_A khi c0, rồi đổi n_a thành
   x=m-n_a khi c0 bằng complement bit và cộng m+1 modulo 2^w.
   Khi c3, x=n_a gốc. Trên miền bậc hợp lệ 0..m, điều khiển nhân là
   `c3 XOR ((c0 OR c3) AND x<=i)`.
   Vì vậy endpoint khởi tạo c3 rồi XOR các match 0..i; khi i dịch một
   vị trí, chỉ XOR match tại min(prev,i)+1. Endpoint cuối xóa mul;
   đóng cursor trước khi đảo cộng/complement/CSWAP.
   Không tái sử dụng upper bound cũ sau đổi tọa độ; quét miền 0..m
   để tránh loại nhầm biên. Giữ điều kiện multiplies của baseline.
3. Con trỏ dịch n_B: gọi g=ctrl_nB, h=c3_nf. Đổi x=n_B+h trước cursor,
   điều khiển chung g XOR h. Với k=m-i+1, hai nhánh cần
   `g AND x>=k` hoặc `h AND x<k`.
   Khởi tạo do_shift bằng g rồi XOR match x=0..k-1, cộng thêm
   predicate n_b>=i của c2 như baseline. Mỗi bước chỉ đổi một match
   ở x=m-max(prev,i)+1. Đóng cursor, hoàn tác n_B-=h, xóa control.
4. Tích lũy thương: init inverse_with_scaffold của reg_a[index],
   XOR tích reg_b[index]*inverse vào q_i dưới control rồi del inverse.
   Không tạo ratio 12 bit; dùng API nghịch đảo có sửa pha và dọn scaffold.
   Zero divisor theo quy ước thư viện cho inverse=0, giống phép chia gốc.
5. Metadata bậc nằm trong 0..m, phép cộng/trừ tạm được hoàn tác modulo
   2^7. Tổng n_q+n_a dùng 8 bit. Không thu hẹp halting_counter.

Mọi phép đổi địa chỉ có inverse rõ ràng, áp dụng cùng công thức ở cả
is_adjoint=False và True; thứ tự CSWAP/nhân trong sweep giữ nguyên.
Không thêm làm tròn hay cắt precision GF. Giả định miền bậc là invariant
của baseline; cần xác nhận bằng chấm giá trị, pha và ancilla.
Chi phí thêm gồm CSWAP metadata và cộng/trừ có điều khiển O(log m)
mỗi vòng; kỳ vọng ít cây unary và ít qubit hơn sẽ giảm Q²T.
Nhân có điều khiển khi tích lũy thương có thể tăng T: phải đo tổng,
không suy ra cải thiện chỉ từ số cursor hoặc kích thước artifact.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: source/config baseline tại commit ở trên;
  [run dev local](../../../results/dqi/DQI-BASELINE/baseline/dev_5min/20261107T092603Z-local-dev_5min-f901a5/verifier.json),
  [provenance](../../../results/dqi/DQI-BASELINE/baseline/dev_5min/20261107T092603Z-local-dev_5min-f901a5/provenance.json).
  Build baseline lịch sử có provenance pre-Git; không gán commit hiện tại cho nó.
- Dự đoán: Q<1893, T thấp hơn mốc 5725117.541015625 và Q²T giảm;
  đây là dự đoán trước chấm. Chọn config đầu tiên cùng (4095,70,12),
  không sweep tham số, để kiểm tra biến đổi cấu trúc.
- Kiểm chứng: kiểm tra đại số predicate và hoàn tác địa chỉ ở biên,
  kiểm tra source/config và build; bàn giao smoke trước dev_5min
  4096 shots, seed 20261106 cùng harness/môi trường baseline.
- Ủng hộ: value_errors=phase_errors=0 và Q²T giảm với profile tương thích;
  bác bỏ khi có lỗi hoặc Q²T không giảm. Chưa chấm thì chưa kết luận.
- Điều kiện dừng: một cấu hình ban đầu; nếu compile lỗi chỉ sửa lỗi triển khai
  trong hướng này. Sau BUILT chờ thành viên chấm, không tự chạy verifier.
- Kiểm tra ứng viên cuối: full hoặc seed chưa dùng chọn config; chú ý syndrome
  0, 1/35 lỗi, chuyển counter, thương bậc lớn và vùng padding chạm nhau.
  Dev không thay thế full.

## Kết luận và phiên bản tái lập

Chưa chấm; chưa xác nhận hypothesis. Config cụ thể và phiên bản build
sẽ được bổ sung ở giai đoạn triển khai trước compile.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa chấm | Chưa có build | Chưa chấm |
| Full | Chưa chấm | Chưa có build | Chưa chấm |

Điểm và các run: [SCORES.md](../SCORES.md).
