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

Config `schur_rank42` đã BUILT từ source/config commit `a6a19f519f66bbc825ce79c9d6f72b857ac20f48` trên Python 3.13.14, kickmix 1.0.0, numpy 2.5.4, scipy 1.18.1. Source/config và hai helper được đối chiếu bytes với snapshot Git trước và sau build. Artifact local `artifacts/dqi/DQI-43/schur_rank42.kmb` có SHA-256 `af4962b7f4a94e9da1698d5d7498bd52f014c86c1a7e497e984a5fbb48637864`, dung lượng 1379816527 bytes.

[Build metrics](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/exp/DQI-43-schur-rank42/results/dqi/DQI-43/schur_rank42/build_only/20261110T063636Z-local-build/build.json), [provenance](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/exp/DQI-43-schur-rank42/results/dqi/DQI-43/schur_rank42/build_only/20261110T063636Z-local-build/provenance.json) và [component checks](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/exp/DQI-43-schur-rank42/results/dqi/DQI-43/schur_rank42/build_only/20261110T063636Z-local-build/component_validation.json) giữ bằng chứng thật. Q=900, T tĩnh=9859000, 148357628 instructions. Cả forward và reverse là 4036790 T, mỗi chiều 41930 lời gọi multiply-add; phase giữ 1785420 T và không gọi kernel mới. Peak đo được giữ 900, không phải dự đoán 903.

So với đối chứng tĩnh 11620060 T ở cùng Q, tiết kiệm 1761060 T và proxy Q²T giảm 15.1553%. Dự đoán trước build chỉ tính 78820 controlled call từ cleanup delta; bộ đếm build mới có tổng 83860 call, gồm thêm các call ngoài số suy từ cleanup có điều khiển. Chênh 5040 call giải thích phần tiết kiệm vượt dự đoán; không sửa dự đoán ban đầu thành số đã đo. Artifact tăng khoảng 24.369% so với 1109451887 bytes của schur_hmr; instructions/Clifford và kích thước là đánh đổi thực tế, chưa có timing simulator ứng viên.

Tại thời điểm bàn giao build chưa có score verifier; static Q²T và H1/H3 PASS không thay kết quả H4. Bộ 21 test repository đã đạt, không thay kiểm chứng thuật toán hoặc grading. Kết quả dev thực tế và điều kiện so sánh được ghi ở phần bước 04 dưới đây.

## Bàn giao chấm local

Trong notebook `notebooks/GQA_Grade_Submission.ipynb`, kernel `.venv`, chọn TRACK=dqi, MODE=dev_5min, EXPERIMENT_ID=DQI-43, OWNER=nhphan0505, CONFIG_NAME=schur_rank42. Giữ profile v1, seed 20261106, 4096 shots để đối chiếu; results tự lưu `results/dqi/DQI-43/schur_rank42/dev_5min/<run-id>/`. Chỉ một artifact cần chấm. Sau dev, ứng viên cuối cần full 102400 shots hoặc bộ seed giữ lại; weight35 và valuation jumps dài vẫn chưa được kiểm trong component decoder thu nhỏ. Agent dừng chờ thành viên chấm; không tự chạy verifier, approve hoặc merge.

## Kết quả dev và phân tích bước 04

Thành viên đã chấm [run dev 20261110T064752Z-local-dev_5min-adc82c](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/exp/DQI-43-schur-rank42/results/dqi/DQI-43/schur_rank42/dev_5min/20261110T064752Z-local-dev_5min-adc82c/verifier.json). Kết quả PASS, 4096 shots, value_errors=0, phase_errors=0, profile v1 và seed 20261106, m/n/degree/r=4095/70/12/2016, log2_delta=-128. Score dev là 23834759676363.117, Q=900, mean T=9858573.3671875, R=2.9847755992784792. Đây là dev, không phải full hoặc điểm chính thức của cuộc thi.

Raw stdout khớp verifier JSON, exit_code=0; metadata/config/provenance khớp ID và mode. Hash artifact trong metadata/verifier/provenance và file local đều khớp build `af4962b7f4a94e9da1698d5d7498bd52f014c86c1a7e497e984a5fbb48637864`. Source/config và hai helper khớp snapshot SHA/hash đã pin. Không sửa raw records hoặc provenance notebook; [review sidecar](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/exp/DQI-43-schur-rank42/results/dqi/DQI-43/schur_rank42/dev_5min/20261110T064752Z-local-dev_5min-adc82c/review.json) lưu checks, hash raw files và phép so sánh; [provenance run](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/exp/DQI-43-schur-rank42/results/dqi/DQI-43/schur_rank42/dev_5min/20261110T064752Z-local-dev_5min-adc82c/provenance.json) nối đúng build/source thay vì suy từ HEAD.

### Đối chứng và đánh đổi

- DQI-BASELINE dev `20261107T092603Z-local-dev_5min-f901a5` có score 61234661450380.1. Hai phía khớp Python 3.13.14, packages, toàn bộ verifier hashes, dev harness hash, profile/version/seed, shots và spec. Vì vậy baseline/candidate = **2.5691327406630573×**, giảm score khoảng **61.0764%**, đủ điều kiện điền cột gain dev. Baseline lịch sử này khác baseline recheck Python 3.13.7 trong mô tả H1/H3; không sửa bằng chứng hoặc mapping của các hướng khác.
- So H3 schur_hmr dev, mean T giảm đúng 1761060 và Q giữ 900. Tỷ số score số học là 1.178632336993238×, giảm 15.1559%. Profile/seed/shots/packages/verifier hashes và R khớp nhưng Python patch (3.13.7 so với 3.13.14) và dev harness hash khác. Do đó đây là so sánh mô tả; chưa gọi gain formal so H3 hoặc thí nghiệm ghép có đối chứng môi trường hoàn toàn đồng nhất. Static counts độc lập với grading cũng hỗ trợ phần tiết kiệm 1761060 T.
- Runtime verifier quan sát là 256.6156 giây trong giới hạn 300 giây. Instruction count tăng 115232928 lên 148357628 so với H3, artifact tăng 24.3692%. Timing H3 48.2998 giây ở môi trường khác không đủ để quy mức tăng thời gian cho riêng kernel, nhưng cho thấy tiết kiệm Toffoli không đồng nghĩa giảm overhead mô phỏng.

### Quyết định

Correctness được ủng hộ trên kernel/component và dev đã kiểm; Q không tăng, static và mean T giảm đúng hướng dự đoán. H4 đạt dev PASS và cải thiện 2.5691× so baseline tương thích. Kết quả chưa đạt mục tiêu tham khảo 7-8 triệu T hoặc 3-3.5× trong ảnh. Không tự mở config hoặc đổi inverse norm để đuổi mục tiêu đó. H4 cũng chưa là ứng viên tốt nhất repo: DQI-39 có dev score thấp hơn, thuộc kiến trúc khác.

Sau dev, đã đề nghị giữ nguyên `schur_rank42` để thành viên chấm full 102400 shots trước quyết định kết thúc/review. Tại mốc dev chưa có full hoặc seed giữ lại độc lập; phần full và quyết định sau cùng được ghi bên dưới. Không mở vòng 05 hoặc tự chấm.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | [schur_rank42](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/a6a19f519f66bbc825ce79c9d6f72b857ac20f48/src/dqi/DQI-43/configs/schur_rank42.json) | `a6a19f519f66bbc825ce79c9d6f72b857ac20f48` | [verifier](../../../results/dqi/DQI-43/schur_rank42/dev_5min/20261110T064752Z-local-dev_5min-adc82c/verifier.json) · [provenance](../../../results/dqi/DQI-43/schur_rank42/dev_5min/20261110T064752Z-local-dev_5min-adc82c/provenance.json) |
| Full | [schur_rank42](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/a6a19f519f66bbc825ce79c9d6f72b857ac20f48/src/dqi/DQI-43/configs/schur_rank42.json) | `a6a19f519f66bbc825ce79c9d6f72b857ac20f48` | [verifier](../../../results/dqi/DQI-43/schur_rank42/full/20261110T070438Z-local-full-2f5a6e/verifier.json) · [provenance](../../../results/dqi/DQI-43/schur_rank42/full/20261110T070438Z-local-full-2f5a6e/provenance.json) |

## Kết quả full và kết luận cuối

Thành viên đã chạy verifier chính thức, defaults đầy đủ và chỉ thêm `--max-workers 1`. Run `20261110T070438Z-local-full-2f5a6e` PASS **102400 shots**, value_errors=0, phase_errors=0; m/n/degree/r=4095/70/12/2016 và log2_delta=-128. Score full **9512735649563.273**, Q=900, mean T=9858564.464101562, R=1.1912604648115832. Source/config và artifact giữ đúng bản đã chấm dev; không sửa implementation hoặc thêm config.

Raw stdout bằng verifier JSON, metadata exit_code=0, mode/command đúng full, hash artifact trong file local/metadata/verifier/provenance khớp build. Source/config/dependency snapshots và verifier hashes đã đối chiếu. [Review full](../../../results/dqi/DQI-43/schur_rank42/full/20261110T070438Z-local-full-2f5a6e/review.json) lưu kiểm tra và hash raw files; giữ nguyên raw records/provenance notebook và mọi run cũ. Full là kiểm chứng thống kê bổ sung ngoài dev, không chứng minh mọi syndrome hoặc mọi nhánh phép đo.

Baseline full lịch sử `20261107T094931Z-local-full-5ed1c6` có score 24439463583672.93; khớp Python 3.13.14, packages, verifier hashes, full spec và 102400 shots. **Baseline/candidate=2.569130950758096×**, giảm score khoảng **61.0763%**. Cột full gain đủ điều kiện điền 2.5691×. Verifier dùng default seed suy từ hash từng mạch, nên hai bên full có mẫu khác nhau; không gọi paired common-seed experiment.

So schur_hmr full lịch sử, score giảm số học 15.1559% (tỷ số 1.1786323825663332×), Q giữ 900 và mean T giảm khoảng 1761058.859. Python patch/platform khác nên giữ giới hạn so sánh như dev. Dev/full có score khác nhau chủ yếu do R phụ thuộc số shots; không so trực tiếp score hai mode để suy cải thiện thuật toán.

**Chốt hướng sau một config:** kết hợp Rank-42 với Schur đạt dev/full PASS trên các lượt đã lưu, giảm T cả thuận/đảo và giữ peak 900 qubit. Kết quả ủng hộ phạm vi tối ưu multiply-add đã chọn; chưa đạt mục tiêu tham khảo 7-8 triệu T hoặc 3-3.5× trong ảnh. Artifact và instruction overhead tăng, không có benchmark timing lặp độc lập. DQI-39 vẫn có score tốt hơn; H4 lưu một phép ghép có kiểm chứng và bằng chứng tài nguyên, không tuyên bố là ứng viên tốt nhất repo.

Không mở thêm config hoặc thay inverse/routing trong hướng này. Hoàn tất phân tích bước 04 và chuẩn bị PR ở bước 06, giữ các SHA nguồn và dependency. Reviewer độc lập cần kiểm điều kiện disjointness của các call site, phase correction của input masking, mapping source/build/run, điểm/gain hai mode và phạm vi diff. Merge/đóng Issue chỉ sau approval teammate khác tài khoản tác giả trên đúng HEAD và các check thực tế đạt; tác giả không tự approve.

Tái lập: checkout source/config tại `a6a19f519f66bbc825ce79c9d6f72b857ac20f48`, giữ hai helper đúng hash/commit trong provenance, dùng Python 3.13 và packages pin, chạy `python src/dqi/DQI-43/solution.py --config src/dqi/DQI-43/configs/schur_rank42.json`. Build record gắn source SHA gốc; không thay provenance theo HEAD tài liệu sau cùng.
