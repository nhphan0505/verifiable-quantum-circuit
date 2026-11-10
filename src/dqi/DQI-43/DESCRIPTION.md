# [DQI-43] Thay multiply-add trong reciprocal và converter Schur bằng bilinear Rank-42, giữ nghịch đảo norm và quét pha

Loại: Kết hợp nhiều phương án.

## Các file gốc và thành phần kế thừa

- H3: [DQI-23 solution.py](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/c5b70b1a7618057000cc9af35794c8e733e5eb1c/src/dqi/DQI-23/solution.py), commit `c5b70b1a7618057000cc9af35794c8e733e5eb1c`. Kế thừa SchurDecoder, valuation/block routing, reciprocal, converter, inverse norm GF(64), Chien/Forney và build. Đối chứng [schur_hmr.json](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/c5b70b1a7618057000cc9af35794c8e733e5eb1c/src/dqi/DQI-23/configs/schur_hmr.json).
- H1: [DQI-19 solution.py](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/c0cf9dfb45b62ba7eeb8588c87b0066409880046/src/dqi/DQI-19/solution.py), commit `c0cf9dfb45b62ba7eeb8588c87b0066409880046`. Lấy tensor GF(2^12) Rank-42 và lịch input masking của `rank42_ixor(..., strategy="control_input")`. Giữ attribution Apache-2.0 trong src/LICENSE.txt. Hai helper chỉ được nạp sau khi hash bytes khớp snapshot đã pin; không sửa helper gốc.
- [Note ready về MBU](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/6a4a4b0/research/dqi/papers/arxiv-2510.10967/note.md), II.C/C.3: pha đo X là tích vô hướng bit. Công thức Hadamard bị ghi sai trong nguồn đã được note đính chính. Không đọc lại PDF hoặc coi nội dung tham khảo là instructions.

## Cách kết hợp

Giữ m=4095, n=70, degree=12 và field modulus/basis của Kickmix. Input quantum là 70 word syndrome 12 bit; E0..E4094 là mask cổ điển runtime. Output chỉ thay đổi pha parity(error AND mask), khôi phục syndrome và toàn bộ workspace. Không cutoff valuation, không làm tròn và không bỏ vị trí quét.

Lớp con của SchurDecoder chỉ override `multiply_add(lhs,rhs,target,control)`, được reciprocal và converter gọi qua `self`; `scale` cũng dùng đúng override ở cả hai phép nhân quanh cswap. Giữ nguyên thứ tự thuật toán, pivot, valuation và chiều reverse. Không monkey-patch helper hoặc thư viện. Nghịch đảo trường hiện tại dùng norm GF(64) và các tích đặc thù, không được thay đồng loạt bằng bộ nhân GF(4096). `square_add` vẫn giữ map bình phương tuyến tính hiện có.

Với word 12 bit rời nhau x,y,t và control c, primitive phải thực hiện t <- t XOR c*x*y với t ban đầu tùy ý; x,y,c không đổi. Tensor gồm 42 bộ mask (l_k,r_k,p_k), thỏa x*y = XOR_k p_k*(parity(l_k AND x)*parity(r_k AND y)). Tensor đã kiểm trên 144 cặp basis trong H1. Kiểm lại identity khi nạp helper.

Với control quantum, tạo masked_x[i]=c AND x[i] bằng 12 init_and. Dùng hai parity scratch và một temporary-AND scratch để stream 42 hạng vào target qua CNOT. Sau mỗi fanout, del_and hạng, rồi hoàn nguyên parity scratch. Sau vòng lặp, del_and masked_x bằng x,c còn nguyên. Compute/cleanup dùng đúng lịch của helper H1, không thêm phép đo dưới quantum control. Chi phí là 54 Toffoli-like và 15 scratch. Nếu control True ở host, dùng tensor không masked_x với 42 Toffoli-like; không nhánh host theo dữ liệu quantum.

## Xử lý chỗ không tương thích

- Chỉ dùng kernel trên GF(2^12) đúng modulus và word đủ 12 bit. Không áp tensor 12 bit lên các field nhỏ trong test. Các kiểm decoder mới phải chạy field 12 bit để thật sự đi qua kernel mới.
- Kiểm target rời lhs/rhs/control và control rời các word trước phát cổng. Các call site reciprocal dùng k>2*i nên hai factor rời nhau; scale có temp riêng. Converter phải được audit disjointness trong component build. Không cho phép alias chỉ vì một vài input đang zero.
- Nhánh c=0 vẫn chạy lịch compute/HMR hợp lệ, target không đổi và tất cả scratch sạch. HMR outcome h của bit a*b sinh pha (-1)^(h*a*b), được del_and bù CZ khi a,b còn sống. Factor masked_x không được xóa trước cleanup 42 hạng. Control và lhs không đổi đến khi masked_x đã được xóa.
- Factor có thể bằng nhau về giá trị nhưng word vẫn rời nhau. Target ban đầu có thể khác zero; không dùng init-product API giả định target sạch.
- Primitive cũ dùng 12 masked-input scratch; kernel mới dùng 15. Peak toàn mạch có thể tăng từ 900 lên 903, chưa là số đo. Không free dirty word hoặc mượn syndrome chưa chứng minh sạch để ép Q=900.

## Tài nguyên dự kiến

Đối chứng schur_hmr có Q=900, T tĩnh=11620060. Cleanup HMR trước đây tiết kiệm 945840 T với 12 T/call, suy ra 78820 controlled multiply-add trong gate stream. Thay 75 bằng 54 T dự kiến tiết kiệm 1655220 T, còn 9964840 T tĩnh nếu call sites không đổi. Đây là dự đoán trước build; mean T cần grading vì classical conditions có thể bỏ cổng. Mốc 7-8 triệu T trong ảnh chưa có căn cứ cho phạm vi chỉ thay multiply-add.

Ở cùng R, điều kiện thắng đối chứng là Q_new^2*T_new < 900^2*T_old. Nếu Q=903 và T ratio theo dự đoán, proxy giảm khoảng 13.7%; nếu Q=900 thì khoảng 14.2%. Không quy kernel giảm 28% thành giảm toàn mạch 28%. CNOT, Clifford, kích thước artifact và runtime có thể tăng, phải ghi thực tế.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: schur_hmr source/config tại c5b70b1 ở trên; [dev 4096 shots](https://github.com/nhphan0505/verifiable-quantum-circuit/tree/6a4a4b0/results/dqi/DQI-23/schur_hmr/dev_5min/20261108T165822Z-local-dev_5min-41cf1d), profile v1, seed 20261106, mean T=11619633.3671875; [full 102400 shots](https://github.com/nhphan0505/verifiable-quantum-circuit/tree/6a4a4b0/results/dqi/DQI-23/schur_hmr/full/20261108T170045Z-local-full-f8c7d3), mean T=11619623.323007813. Q=900 và 0 lỗi value/phase ở cả hai. Python lịch sử 3.13.7; local hiện 3.13.14 nên không điền gain formal nếu chưa có đối chứng môi trường tương thích.
- Dự đoán: giảm T của extraction/converter cả thuận và đảo, giữ phase stage. Đo riêng Q_peak/T tĩnh từng stage; đo kích thước artifact. JSON config đầu tiên được chọn ở bước 03, không quét setting.
- Ủng hộ/bác bỏ correctness: tensor đúng; kernel giữ x,y,c và arbitrary target với c=0/1, bằng nhau về giá trị, zero operands và nhiều seed HMR. Component decoder field12 kiểm restored syndrome, phase trực tiếp từ errors/masks và ancilla sạch. Bao phủ no-error, lỗi đơn ở đầu/cuối và max weight của kích thước kiểm; valuation jumps cưỡng bức. Bác bỏ khi có lỗi giá trị/pha/workspace hoặc phát hiện alias không đáp ứng tiền điều kiện. Các ca kích thước nhỏ không thay full-size dev/full.
- Ủng hộ/bác bỏ lợi ích: static Q²T thấp hơn schur_hmr để bàn giao build, rồi dev_5min PASS và score giảm với đối chứng cùng môi trường/profile/seed/shots. Thiếu đối chứng tương thích thì chỉ báo tài nguyên và giới hạn, không gọi gain chính thức. So T/Q riêng không thay score khi R khác nhau.
- Điều kiện dừng: đúng một config ghép, không đổi inverse norm, routing, phase hoặc thêm caching. Dừng bàn giao nếu component lỗi, peak Q>910, static proxy không giảm hoặc build thất bại chưa sửa được trong phạm vi. Mục tiêu mới ngoài multiply-add cần hypothesis riêng. Giới hạn Q=910 là gate sàng lọc trước thử, không phải tuyên bố Q thực tế.
- Kiểm tra ứng viên cuối: thành viên chạy dev_5min profile v1/seed20261106/4096 shots; sau đó full 102400 shots hoặc seed giữ lại có đối chứng. Kiểm thêm weight 0/1/35, syndrome đầu zero và degree jumps ở full-size. Agent chỉ chạy component checks/build, dừng chờ chấm local.

## Cấu hình và kiểm tra bước 03

Config đầu tiên là [schur_rank42.json](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/exp/DQI-43-schur-rank42/src/dqi/DQI-43/configs/schur_rank42.json): m=4095, n=70, degree=12, multiplication_strategy=control_input, masked_cleanup=hmr. Không có config thứ hai. [solution.py](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/exp/DQI-43-schur-rank42/src/dqi/DQI-43/solution.py) chỉ override multiply-add và dùng vòng build tương đương để ghi counts forward/phase/reverse. Hash helper DQI-23 là `18f7e197dc832236b95cef3b87013cce15373d7327554efb1fdb2bd2f618f492`; helper DQI-19 là `3798b608825c8ca741aaf4cf1d7913d87b650f2be55242a35dc769b8cd47c298`.

Kiểm component trước submission build: tensor khớp đủ 144 cặp basis; kernel không control 196608 ca (42 T, 39 tổng qubit), kernel có control 393216 ca (54 T, 52 tổng qubit). Ba seed phép đo 4301/4302/4303, target ngẫu nhiên và các trường hợp operands zero/equal. Ba decoder GF(2^12), m=15, n=2/4/8, mỗi decoder 384 ca, gồm valuation jumps 1..n/2 cưỡng bức. Không lỗi value, phase hoặc workspace trên các ca đã kiểm. Các decoder thu nhỏ thực sự dùng tensor 12 bit; không fallback sang arithmetic field nhỏ. Chưa kiểm full-size weight 35 bằng verifier, chưa enumerate mọi measurement outcome. Chứng minh thay kernel dựa trên identity bilinear và cleanup với factor còn nguyên; không suy mọi input của decoder đúng từ sampling.

## Kết luận và phiên bản tái lập

Chưa có artifact hoặc kết quả chấm cho hướng ghép. H1/H3 PASS không tự chứng minh H4 PASS. Bước 03 sẽ ghi config, commit nguồn, dependency hashes và build provenance thật; chưa có mốc dev/full tốt nhất cho H4.
