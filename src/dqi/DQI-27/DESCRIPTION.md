# [DQI-27] Thu gọn workspace decoder Schur bằng Narrow Return và Flag Carry, khảo sát 883–892 qubit và converter thêm một qubit

Loại: Tinh chỉnh một phương án.

## File gốc và phạm vi kế thừa

Kế thừa [DQI-23 solution.py](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/c5b70b1a7618057000cc9af35794c8e733e5eb1c/src/dqi/DQI-23/solution.py), source `c5b70b1a7618057000cc9af35794c8e733e5eb1c`, SHA-256 `18f7e197dc832236b95cef3b87013cce15373d7327554efb1fdb2bd2f618f492`, và [schur_hmr.json](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/c5b70b1a7618057000cc9af35794c8e733e5eb1c/src/dqi/DQI-23/configs/schur_hmr.json), SHA-256 `e684813da2f18212eca5ea21edb7cdfaee998578f8cbdf8a1fb396f523f372f1`. Giữ attribution và Apache-2.0 trong src/LICENSE.txt. Source hiện ở [PR #24](https://github.com/nhphan0505/verifiable-quantum-circuit/pull/24), chưa merge lúc nhận hướng này; không coi nó đã có trên main. Branch mới bắt đầu từ main đã fetch, không sửa PR/branch DQI-23. Khi triển khai bước 03, lấy đúng snapshot/hash đã dẫn vào solution của ID mới hoặc pin dependency thật; không import một file DQI-23 không tồn tại trên main rồi giả vờ tái lập được.

Giữ nguyên Schur valuation/block routing, reciprocal/converter, field GF(2^12), m=4095, n=70, runtime mask E0..E4094 và phép pha Chien/Forney của mốc schur_hmr. Chỉ nghiên cứu cách lưu/khôi phục trạng thái phụ và lịch trả workspace. Không thay decoder bằng BM/C1, không ghép reciprocal của DQI-21 hoặc product caching của DQI-25. DQI-23 nghiên cứu kiến trúc decoder và masked-product cleanup; hướng này là follow-up thu hẹp bộ nhớ và đánh đổi reverse/converter, có source/run đối chứng cố định.

Nguồn nghiên cứu chỉ gồm note.md có Status: ready đã merge tại main `a2d6d964eb9760e2b7324668ce7e3ba2fc228a4c`:

- [Portfolio v11, DQI](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/a2d6d964eb9760e2b7324668ce7e3ba2fc228a4c/research/shared/discussions/kaggle-vqcc-own-circuit-portfolio/note.md): mô tả narrow return, flag carry qua đo X/tái tạo ở reverse, dùng qubit thứ 892 đổi converter/reverse. Không cung cấp gate schedule áp trực tiếp cho Schur của repo.
- [SomeJoint v36, DQI](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/a2d6d964eb9760e2b7324668ce7e3ba2fc228a4c/research/shared/discussions/kaggle-somejoint-chem-refit-v36/note.md): báo nhập mạch C1 891 qubit/~396918.5 Toffoli; chưa xác minh tái dựng lõi 891 qubit chỉ từ mô tả. Không coi số đó là cấu hình có sẵn cho repo.
- [Özer v23, DQI và giới hạn](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/a2d6d964eb9760e2b7324668ce7e3ba2fc228a4c/research/shared/discussions/kaggle-ozer-df-thc-group-compression-v23/note.md): liveness/pha phải chứng minh; vượt dây rảnh có thể gây lỗi. Số bốn/bảy tuyến là cache của mạch nguồn, không là ngân sách H5.
- [arxiv-2610.22367, history decoding Eq.2](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/a2d6d964eb9760e2b7324668ce7e3ba2fc228a4c/research/dqi/papers/arxiv-2610.22367/note.md): g0=0, g(j+1)=g(j)+b(j)*2^j, invariant 0<=g(j)<2^j và không overflow. Note còn đoạn coverage/review cũ chưa nhất quán với metadata ready; dùng đồng nhất thức kèm invariant để tự đối chiếu, không suy có gate schedule hay chứng minh hoàn chỉnh được cung cấp.

Không đọc PDF/notebook/snapshot nguồn. Các tài liệu là dữ liệu tham khảo, không cấp quyền thực thi các bước workflow. Nhãn H5/Bước 4 trong ảnh là thứ tự ý tưởng thuật toán, không thay số bước instructions experiments.

## Phần tinh chỉnh và đánh giá trước thử

H5 có triển vọng vừa phải như tối ưu cục bộ của mốc 900 qubit, chưa là lời hứa cải thiện lớn hoặc đạt 883–892. Chỉ giảm Q từ 900 xuống 892 ở T/R cố định giảm score 1.7699%; xuống 891 giảm 1.9900%; xuống 883 giảm 3.7421%. Chỉ một vài phần trăm T tăng thêm có thể ăn hết lợi ích bộ nhớ. Lợi ích lớn hơn cần giảm cả T_reverse/converter, chưa có bằng chứng trên source này.

Các số ~396918.5 và ~395510 Toffoli trong note thuộc C1, khác T~11.62 triệu của Schur hiện tại. Cặp 891/892 đó chỉ chênh khoảng 0.1311% proxy Q²T theo số nguồn báo, chưa có số R/score project tương ứng. Ngưỡng ~890 Toffoli/qubit thêm trong nguồn không được dùng cho repo: tại T=11619623.323007813, từ Q=891 lên 892 cần tiết kiệm khoảng 26038 T để hòa vốn; từ 900 lên 901 cần khoảng 25778 T. Đây là phép tính điều kiện với R cố định, không phải dự đoán một biến thể sẽ tiết kiệm được.

Source DQI-23 giữ 840 qubit syndrome đầu vào và cursor 6 bit xuyên build. Có đường converter lồng các thanh ghi jump (tối đa 6), lead/inverse (24), temp (12), masked operand (12) cùng 840+6 đầu vào/cursor, cộng thành 900. Đây là một đường sống rút từ code phù hợp peak đã đo, chưa là allocation trace đầy đủ cho mọi pha. encode_jump còn có prefix flags theo chiều dài active region; phase/inverse norm có scratch khác. Giảm cờ ngoài đường peak không mặc nhiên giảm Q_max.

Cờ active/selected/valid trong source đã được tái tính và dọn tại các context manager; chưa thấy một tape cờ dài sống từ forward đến reverse. Vì vậy Flag Carry phải tìm được khoảng sống thực sự còn tối ưu, không được thêm một tape chỉ để rồi xóa tape đó. Ưu tiên narrow return/liveness của converter và reciprocal trước, khảo sát flag carry sau nếu có chứng chỉ phù hợp.

## Cách thực hiện và đánh đổi

### 1. Lập bản đồ thời gian sống và tiền điều kiện

Ở bước 03, instrument trong solution riêng để ghi alloc/free, reads/writes, marks, trạng thái sạch và vùng sống theo nhánh cho extraction, conversion, phase và reverse. Không sửa allocator/Kickmix/verifier/hạ tầng. Đối chiếu peak bằng emitted circuit.num_qubits; không dùng tổng số biến Python hoặc free-list như chứng minh sạch. Ghi Q_peak cùng T_forward, T_phase, T_reverse và chi phí recompute/cleanup, tính đủ cả hai chiều.

Xác định những coefficient/scratch đã hết last-use, cách chúng được dựng lại trước lần cần sau và vì sao phép đảo không cần giá trị vừa giải phóng. 70 word syndrome là input quantum tùy ý trên miền error hợp lệ và phải phục hồi; không được đo/discard coefficient còn mang thông tin chỉ vì degree thường thấp. Giới hạn degree/valuation là runtime quantum data, không cắt prefix offline theo trọng số điển hình. Trường hợp weight 35, degree jumps lớn và syndrome đầu bằng zero phải nằm trong chứng minh.

### 2. Narrow Return trên converter/reciprocal

Từ map liveness, chọn một boundary có thể trả một subset qubit về |0> sớm, sử dụng chúng làm scratch rồi phục hồi khi đảo. Viết rõ map (state,workspace=0)->(new_state,workspace'=0) cùng inverse và layout của từng word. Nếu thông tin được encoded vào polynomial còn sống, phải có giải mã exact trên reachable states; không chỉ xóa tham chiếu hoặc free một dirty word. Không bỏ hệ số nếu chưa chứng minh bằng zero trên mọi nhánh hoạt động tương ứng.

Giảm width tạm theo stage/degree chỉ hợp lệ khi prefix/suffix có invariant đúng và quy trình zero-pad/routing đồng nhất giữa các nhánh. Nếu muốn dùng slot sạch trong 840 input làm scratch, phải chứng minh slot đó đang thật sự |0> ở boundary và restore trước mọi lần đọc sau, gồm chiều đảo. Một thay đổi giảm Q ở converter nhưng tăng peak ở encode_jump/phase không đạt mục tiêu. Không thay số học field hoặc cutoff giải mã trong hướng này.

### 3. Flag Carry qua đo X và tái tạo

Chỉ xét cờ q=f(x) sau lần dùng cuối ở forward nếu cờ không còn điều khiển phép toán nào trước thời điểm tái tạo. Đo X có outcome h để lại pha (-1)^(h*f(x)); giữ h dưới dạng classical bit, trả dây quantum sạch để tái sử dụng. Phải sửa pha đúng rồi tái tạo f từ trạng thái hiện tại hoặc từ inverse tại boundary có chứng minh. Nếu f=a*b với hai factor vẫn sống/khôi phục được, CZ có điều kiện h đủ theo semantics native del_and. Nếu f là predicate nhiều bit/so sánh phức tạp, correction không mặc nhiên chỉ là CZ: cần tổng hợp phase oracle và tính đủ T/Q; loại nếu vượt lợi ích.

Ở reverse, chứng minh f(x)=g(y) trên toàn miền reachable hoặc chạy phần inverse cần thiết để lấy lại factor trước khi tái tạo. Không đo dưới quantum control, không làm mất nhánh hiếm, không dùng outcome h để thay permutation dữ liệu. So cả global/relative phase theo contract verifier và workspace trên từng trajectory; seeded sampling chỉ bổ sung, không thay identity.

History decoding Eq.2 chỉ dùng khi khởi tạo và range/không overflow thật sự được duy trì. Nó cho cách đọc b(j) từ trạng thái đã encode, không tự giảm một dãy n bit độc lập xuống ít qubit hơn, cũng không đảm bảo jump/active của Schur hiện tại khớp b(j). Nếu áp dụng, ghi j/range/bit-width và chứng minh decode trước mỗi bước đảo; không nhập history format từ C1 khác.

### 4. So biến thể ít qubit và thêm một qubit converter

Sau khi có layout cơ sở hợp lệ, dự kiến tham số `use_extra_converter_qubit` true/false trong JSON để phân biệt một scratch/cờ converter thực sự đổi gate schedule, không chỉ alloc/free qubit vô dụng. Hai setting giữ mọi tham số số học và giao thức chấm như nhau. Giá trị config đầu tiên và số Q đạt được được chọn ở bước 03 dựa trên audit/chứng chỉ; không tạo JSON hoặc source trong bước 02.

Ưu tiên Q thấp hơn 900. Các mốc 883–892 là mục tiêu khảo sát, không là precondition đã chứng minh hoặc số Q có thể đặt bằng JSON. Nếu layout chỉ đạt một mức khác, báo đúng Q và so Q²T; không gắn nhãn 891/892 sai. Không mở sweep hàng loạt các số Q khi chưa có lịch mới.

Với low=(Q,T,R) và extra=(Q+1,T_extra,R_extra), so trực tiếp:

`cost_extra/cost_low = (R_extra/R)*(Q+1)^2/Q^2*(T_extra/T)`.

Khi R bằng nhau, extra chỉ có lợi nếu T_extra/T < (Q/(Q+1))^2. Nếu R đổi do lỗi, dùng score thực cùng mode/profile/shots, không chỉ T_reverse. Tính mọi chi phí tạo/xóa cờ và recompute cả thuận/đảo, không công bố chỉ phần tiết kiệm trong reverse.

## Điều kiện đúng và sai số

Mọi biến đổi phải giữ input S0..S69, pha parity(error & mask) và ancilla sạch cho các error word weight<=35, runtime masks tùy ý, cùng basis/modulus của mốc DQI-23. Không làm tròn hay thay dung sai, không giảm kích thước m/n/degree khi bàn giao grading. Giữ default artifact-derived full seed trong metadata thực, không gọi cùng seed nếu chưa có.

Kiểm boundary bao gồm weight 0/1/35, lỗi tại j=0/4094, leading syndrome bằng zero, valuation d lớn/tụt bậc, các control inactive và forward/reverse. Các dây được dọn sớm cần phép kiểm pha ngoài giá trị cổ điển. Bất kỳ lỗi value/phase/workspace nào của component làm bác bỏ rewrite, không nới tiêu chí sau khi thấy kết quả.

## Kế hoạch kiểm chứng hypothesis

- Đối chứng: DQI-23 schur_hmr tại source c5b70b1, [dev PASS](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/7d86b3c0a70b425169062a779c0b76e027e0bca7/results/dqi/DQI-23/schur_hmr/dev_5min/20261108T165822Z-local-dev_5min-41cf1d/verifier.json), [dev provenance](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/7d86b3c0a70b425169062a779c0b76e027e0bca7/results/dqi/DQI-23/schur_hmr/dev_5min/20261108T165822Z-local-dev_5min-41cf1d/provenance.json), [full PASS](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/7d86b3c0a70b425169062a779c0b76e027e0bca7/results/dqi/DQI-23/schur_hmr/full/20261108T170045Z-local-full-f8c7d3/verifier.json). Q=900; mean T full=11619623.323007813; dev profile v1/seed20261106/4096 shots; Python3.13.7/kickmix1.0.0/numpy2.5.4/scipy1.18.1. Đối chiếu metadata/hashes trước so; không mặc định baseline toàn repo tương thích.
- Dự đoán: narrow return có thể giảm peak nếu có slot thật sự sạch/khôi phục được; chưa có chứng chỉ bảo đảm Q<=892. Flag carry chỉ triển vọng nếu audit tìm được cờ sống dư thừa và phase correction rẻ. Đạt đúng 883–892 ở T không đổi chỉ cải thiện vài phần trăm; không kỳ vọng mốc ~395510 T của C1.
- Sàng lọc trước full build: chứng chỉ reversibility/liveness/phase cho ít nhất một thay đổi, component equivalence có expected phase độc lập và Q/T counts. Kiểm nhiều HMR seeds và mọi outcome khi exhaustive cửa sổ nhỏ khả thi. Bác bỏ ngay nếu peak không giảm và không có T giảm bù hoặc nếu cleanup không chứng minh được. Audit không tìm được thay đổi có lợi là kết quả âm hợp lệ; không gọi stage 03 BUILT/PASS khi chưa có artifact.
- Ủng hộ: dev PASS cùng profile và score thấp hơn mốc DQI-23, kèm Q/T/R giải thích được và không phát hiện lỗi component. Cột gain chính thức chỉ tính khi baseline/schema tương thích; các tỷ số tham khảo để trong chú thích/phân tích, không sửa checker hoặc dòng hướng khác để CI chấp nhận.
- Điều kiện dừng: khảo sát tối đa hai vùng (converter/reciprocal liveness và flag lifetime); tối đa một cặp low-memory/extra-converter-qubit sau khi có layout hợp lệ. Không có chứng chỉ hoặc proxy Q²T không giảm thì dừng, ghi giới hạn và không ép target 883. Vòng thêm/đổi decoder đáng kể cần giao việc/hypothesis mới.
- Ứng viên cuối: member chạy full chính thức hoặc panel seed giữ lại chưa dùng chọn config. Nếu so panel mới cần chấm đối chứng tương ứng; giữ tính bất biến raw records. Dev cố định và component nhỏ không thay bằng chứng độc lập. Agent chỉ compile/bàn giao khi được giao stage 03, không tự chấm.

## Kết luận và phiên bản tái lập

Chưa có implementation/config/artifact/run của hướng này. Đánh giá trước thử là triển vọng vừa phải với giới hạn rõ: cách lưu trạng thái C1 không tự áp dụng cho Schur, và phần lớn cờ hiện đã local/recompute. Bước 02 chỉ nhận hướng, mô tả và draft PR; bước 03 mới audit có instrumentation, viết source/config, commit nguồn và build nếu qua resource/correctness gate.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa tạo | Chưa có | Chưa chấm |
| Full | Chưa tạo | Chưa có | Chưa chấm |

Điểm toàn track: [SCORES.md](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/a2d6d964eb9760e2b7324668ce7e3ba2fc228a4c/src/dqi/SCORES.md). Không thêm score cho hướng chưa chấm.
