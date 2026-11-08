# [DQI-25] Tái sử dụng các tích lặp và tương đương Boolean/affine bằng product caching và xóa đo X, giữ decoder DQI-19

Loại: Tinh chỉnh một phương án.

## File gốc và phạm vi kế thừa

Kế thừa decoder [DQI-19 solution.py](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/c0cf9dfb45b62ba7eeb8588c87b0066409880046/src/dqi/DQI-19/solution.py) tại commit `c0cf9dfb45b62ba7eeb8588c87b0066409880046`, SHA-256 `3798b608825c8ca741aaf4cf1d7913d87b650f2be55242a35dc769b8cd47c298`, đã merge trong main `bb3a6311113217a69c64e88e9c3bb0513237a1f9`. Giữ attribution Apache-2.0 trong src/LICENSE.txt. Mốc so sánh ưu tiên là strategy `control_input`, [config](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/c0cf9dfb45b62ba7eeb8588c87b0066409880046/src/dqi/DQI-19/configs/rank42_control_input.json); lựa chọn config của hướng mới sẽ hoàn thiện ở bước 03, chưa tạo code/config hoặc artifact trong bước 02.

Chỉ tối ưu lịch tính và dùng lại các tích Boolean cục bộ trong decoder này. Giữ GF(2^12), m=4095, n=70, degree=12, EEA chính 222 vòng, Chien/Forney, runtime masks, số vòng và miền cam kết của verifier. Không nhập Bézout/reciprocal của [DQI-21](https://github.com/nhphan0505/verifiable-quantum-circuit/issues/21), không thay EEA bằng Schur/block-Wronskian của [DQI-23](https://github.com/nhphan0505/verifiable-quantum-circuit/issues/23). Mỗi hướng có branch/worktree riêng; không sửa source hay artifact của chúng. DQI-19 tối ưu tensor nhân và con trỏ; hướng này nghiên cứu reuse tích giữa các lần dùng, không tuyên bố tìm tensor mới.

Nguồn hình thành là kết hợp phân tích code với hai note ready đã merge tại main `bb3a6311113217a69c64e88e9c3bb0513237a1f9`:

- [Portfolio VQCC v11, §DQI](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-vqcc-own-circuit-portfolio/note.md): tác giả báo tái dùng cả tích cùng hàm Boolean trên dây rảnh; fingerprint chỉ sàng lọc.
- [Özer v23, DQI và What we measured](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/research/shared/discussions/kaggle-ozer-df-thc-group-compression-v23/note.md): tác giả báo bốn chuỗi tiết kiệm bốn Toffoli tĩnh, nhưng bảy tuyến có lỗi giá trị/pha; điều kiện affine dựa trên các hằng đã chứng minh và liveness là thiết yếu.

Chỉ dùng note, không đọc notebook/snapshot nguồn. Các số liệu và 61 hằng của nguồn không phải kết quả hay invariant của decoder repo. Không áp số bốn/bảy chuỗi hoặc số cổng nguồn làm dự đoán định lượng cho hướng này.

## Phần tinh chỉnh và lý do

Trong `_rank42_control_input`, mỗi term hiện tính `t = a AND b`, XOR t vào tập bit output rồi xóa ngay bằng `del_and`; parity a/b được thay đổi cho term kế. `_multiply_and_add_or_sub` gọi kernel trên các word khác nhau và có swap/điều khiển động. Đây là các cửa sổ khảo sát, chưa có chứng cứ term trong những cửa sổ này thực sự lặp. Cùng q_i, cùng chỉ số dây hay cùng tensor mask không đủ suy ra cùng hàm khi reg_a/mul/parity đã thay đổi. Cũng không mặc định hai term độc lập của một tensor rank 42 có thể nhập lại mà vẫn giữ đúng nhân field.

Giả thuyết: tồn tại hai lần tính tích có cùng hàm Boolean, hoặc chênh nhau bởi một hàm affine đã chứng minh, với khoảng sống đủ ngắn và có dây sạch rảnh trong peak Q hiện tại. Giữ tích trên dây đó có thể thay lần tính phi tuyến sau bằng CX/X và phần hiệu chỉnh pha Clifford, giảm T mà không tăng Q hoặc lỗi. Nếu không tìm được cặp thỏa mọi điều kiện, ghi kết quả âm thay vì ép cache.

## Cách thực hiện và đánh đổi

### Biểu diễn và chứng chỉ tương đương

Mỗi cửa sổ có input boundary gồm mọi qubit đang sống, classical bit/guard và trạng thái sạch đã chứng minh. Gán biến Boolean độc lập cho các đầu vào chưa biết. Với phép X/CX/SWAP và ràng buộc hằng đã được suy ra từ mạch ở boundary, theo dõi biểu thức affine trên F2: `a=c_a XOR sum a_i x_i`. Không suy hằng từ một mẫu mô phỏng, từ syndrome thường gặp hoặc từ mask runtime. Các bit mask E0..E4094 là dữ liệu cổ điển runtime tự do.

Ứng viên tích hai affine form là đa thức Boolean bậc tối đa 2; chuẩn hóa trong F2 với x_i^2=x_i và triệt tiêu hệ số chẵn. Dùng chính đa thức chuẩn hóa để so `f1=a1*b1` và `f2=a2*b2`; fingerprint chỉ giảm không gian tìm kiếm. Chấp nhận `f2 XOR f1=l(x)` khi đa thức chênh có bậc không quá 1 và có thể tổng hợp l trên các dây vẫn sống tại lần dùng thứ hai. Nếu dùng ràng buộc mạnh hơn hằng/affine, phải có chứng minh riêng theo miền reachable; phiên đầu bảo thủ bỏ qua. Dừng theo dõi hoặc tách cửa sổ ở phép phi tuyến không hỗ trợ, reset/measure không được mô hình hóa hoặc nhánh chưa chứng minh.

Chứng chỉ cho mỗi tuyến gồm boundary, instruction/mark hai điểm dùng, biểu thức f1/f2/l, danh sách giả định cùng nguồn chứng minh, guard, dây cache, khoảng sống, danh sách mọi truy cập xen giữa và lịch cleanup. ID dây không được xem là biến ổn định sau khi bị ghi. Đầu vào target tùy ý, không giả định target bằng zero khi là accumulate.

### Tái dùng và sửa pha qua đo X

Với cache c sạch, compute `c <- a1*b1` bằng một temporary AND. Tại lần dùng đầu, `target1 ^= c`; giữ c thay vì xóa. Tại lần sau, nếu `f2=f1 XOR l`, thực hiện `target2 ^= c XOR l` bằng CX/X. Fanout nhiều target áp cùng nguyên tắc, tính cả guard thật. Dùng c để copy không thay đổi c.

Đến cleanup, đo c theo cơ sở X, kết quả h, tạo pha cần bù `(-1)^(h*f1)`. Chỉ dùng `del_and(a1,b1,c)` khi hai factor vẫn đúng các giá trị lúc compute. Nếu factor đã đổi, phải có biểu diễn f1 bằng các affine form trên dây hiện còn sống và tổng hợp bù pha tương đương; nếu không chứng minh được thì tuyến không hợp lệ. Với factor affine, khai triển h*a*b thành các hằng/Z/CZ dưới classical h, xử lý cả thành phần tuyến tính do x_i^2=x_i. Hằng toàn cục có thể bỏ chỉ khi thực sự toàn cục ở nhánh đo; mọi pha phụ thuộc quantum/classical input phải được giữ đúng. Các gate hiệu chỉnh phải được kiểm theo semantics Kickmix, không coi inverse phép tính AND là CX tự do.

Với điều khiển quantum g, `target ^= g*f` có thể là bậc 3: không thay CCX bằng CX chỉ vì cache chứa f. Chỉ thay bằng CX nếu cache đã biểu diễn chính g*f hoặc guard đã được chứng minh và rewrite giữ cùng control; nếu vẫn cần CCX thì tính đúng chi phí và loại nếu không có lợi. Classical push_condition phải giống giữa các điểm hoặc có chứng minh sửa guard. Không đặt HMR dưới quantum control, không kéo phép đo qua nhánh khiến thiếu cleanup. Phiên đầu ưu tiên guard giống nhau và bỏ qua trường hợp không rõ.

### Dây rảnh, nhánh và lịch cấp phát

Dây cache phải là |0>, không entangled và không mang giá trị sống tại điểm bắt đầu. Không được đọc/ghi/đo/reset hoặc được allocator tái cấp phát cho công việc khác trong toàn khoảng giữ cache. Xây bảng liveness từ các alloc/free cùng invariant sạch và operation reads/writes, xét từng nhánh điều khiển có thể xảy ra. `builder.free` chỉ là thao tác quản lý tài nguyên, không tự chứng minh dây sạch. Dây dirty không thể dùng như cache sạch chỉ vì đang không được tham chiếu.

Bảo lưu dây trong allocator suốt tuyến; xác minh không đẩy nhu cầu scratch xen giữa vượt peak Q đối chứng. Với nhiều tuyến, xung đột khoảng sống phải được lập lịch theo dây sạch khả dụng tại mọi instruction và mọi nhánh, không chỉ tổng số tuyến. Từng tuyến bật riêng trước khi ghép; sau ghép phải kiểm lại tương tác liveness/pha và Q peak toàn decoder. Không cấu hình ép số tuyến vượt ngân sách. Chưa khẳng định repo có bốn dây/tuyến khả dụng.

### Thuật toán khảo sát và triển khai dự kiến bước 03

1. Khôi phục DQI-19 control_input và ghi hash source/helper/config. Trích các cửa sổ có product compute/copy/delete; giữ mark và guard. Phân tích trên IR/gate stream hoặc instrumentation riêng của implementation mới, không sửa Kickmix/verifier/hạ tầng chung.
2. Theo dõi affine boundary và liveness; tìm trùng đa thức bậc 2, xếp ứng viên theo T ròng tiết kiệm sau cleanup. Chưa có chứng chỉ thì chỉ là candidate, không bật.
3. Tạo một tuyến nhỏ với chứng chỉ đủ, dùng cache đúng khoảng rảnh. Chạy segment equivalence cả giá trị, pha và các dây boundary/workspace, gồm mọi kết quả đo trong cửa sổ nhỏ. Với boundary nhỏ, exhaustive truth table; với lớn, chứng minh biểu thức và kiểm độc lập kết hợp SAT/BDD nếu cần/khả dụng, không lấy random fingerprint làm chứng minh.
4. Bật lần lượt tuyến đã đạt; kiểm tương đương sau mỗi lần ghép. Đếm T_compute, T_copy, T_cleanup và Q peak, phân biệt static count với mean thực tế. Không giữ tuyến tăng Q hoặc phát sinh value/phase/workspace error.
5. Chỉ sau source/config commit mới build artifact đúng ID/config và ghi build_only provenance/hash. Thành viên chấm notebook local dev cùng profile, rồi agent phân tích ở bước 04. Bước 02 này không viết code/config hoặc compile.

Tham số dự kiến ở bước 03: danh sách chứng chỉ/tuyến được bật, giới hạn chiều dài cửa sổ và ngân sách cache theo liveness thực tế. m/n/degree vẫn chính thức. Tên config đầu tiên và giá trị cụ thể sẽ chốt trước commit nguồn, không chọn bằng cách sửa records sau khi thấy score. Không cần quét bảy tuyến chỉ vì note có số bảy.

## Điều kiện đúng, tài nguyên và rủi ro

Đây là rewrite chính xác trên F2, không làm tròn hay đổi dung sai. Mọi syndrome/mask hợp lệ và mọi nhánh đo phải giữ cùng phép tác động lên input/output và pha tương đối, ancilla sạch sau cleanup. Ca zero, trọng số thấp/35, control=0, pivot/termination và hai thứ tự forward/reverse là ca biên bắt buộc; rewrite không được dựa vào giả thiết input thông thường bỏ qua nhánh hiếm.

Verifier dùng `score=R(eps_plus)*Q^2*T`. Nếu Q và lỗi giữ nguyên, giảm T có lợi. Cache cần không tăng Q_max của circuit đối chứng; giữ dây lâu có thể đẩy peak dù không thêm alloc tại chỗ. Một tuyến lặp hai lần lý tưởng tiết kiệm một compute AND, nhưng chi phí mask, affine reconstruction, cleanup hoặc copy có quantum guard có thể bù hết. Chưa có số đo tiết kiệm cho repo; kết quả của note không được nhập vào bảng điểm. Chỉ giảm cổng tĩnh rất nhỏ có thể khó phân biệt từ score trung bình, nên segment proof và resource count là bằng chứng bắt buộc bên cạnh grader.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: DQI-19 source/config ở SHA nêu trên. [Dev đã có](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/results/dqi/DQI-19/rank42_control_input/dev_5min/20261108T122637Z-local-dev_5min-3fdc53/verifier.json), [provenance](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/bb3a6311113217a69c64e88e9c3bb0513237a1f9/results/dqi/DQI-19/rank42_control_input/dev_5min/20261108T122637Z-local-dev_5min-3fdc53/provenance.json): Python 3.13.7, kickmix 1.0.0, numpy 2.5.4, scipy 1.18.1, profile v1, seed 20261106, 4096 shots, Q=1893. Đối chiếu hash verifier/harness lần nữa trước so sánh. Full DQI-19 hiện là config rank42/source khác; không giả vờ đó là full control_input. Nếu cần full đối chứng cùng source/config/giao thức mà chưa có, bàn giao chấm phù hợp hoặc ghi giới hạn.
- Dự đoán trước thử: một hoặc nhiều tuyến có thể tiết kiệm T ròng tại Q_max không tăng; chưa có lower bound số tuyến hay mức cải thiện. Ưu tiên trùng hoàn toàn trước affine để giảm giả định. Không dự đoán thắng DQI-19 trước khi tìm được chứng chỉ.
- Ủng hộ: có ít nhất một tuyến được chứng minh segment equivalence, ghép không lỗi giá trị/pha/workspace, Q_max không vượt đối chứng, T toàn mạch giảm; dev PASS cùng profile và score giảm với giới hạn thống kê rõ. Bác bỏ tuyến ngay nếu liveness/pha không chứng minh được, Q tăng hoặc T ròng không giảm. PASS đơn lẻ không thay chứng minh liveness/segment.
- Điều kiện dừng: khảo sát tối đa hai phạm vi cục bộ (bên trong rank42 control_input và các cửa sổ lân cận trong multiply/add/control EEA); tối đa ba setting decoder ở vòng nghiên cứu ban đầu. Nếu không có tuyến chứng minh được hoặc không có lợi ròng thì kết thúc với kết quả âm, không mở rộng thành compiler optimizer toàn repo. Mỗi setting triển khai/chấm sau cần đúng bước được giao. Thiết kế tăng Q, thay EEA hoặc sửa verifier nằm ngoài phạm vi này, phải tách hypothesis.
- Kiểm tra ứng viên cuối: ca biên trọng số 0,1,35, control false/true và nhánh đảo; segment kiểm mọi outcome HMR khi khả thi; member chạy full chính thức hoặc bộ seed giữ lại chưa dùng chọn tuyến. Dev v1 cố định dùng để sàng lọc, không là xác nhận đầy đủ. Full defaults phụ thuộc artifact nên không gọi so sánh paired seed nếu không có seed chung thực tế. Nếu môi trường/hash không khớp baseline chính thức, cột gain giữ trống thay vì suy đoán provenance.

## Kết luận và phiên bản tái lập

Chưa triển khai hoặc chấm hypothesis này. Chứng cứ hiện có là code/contract repo và các kết quả do note tham khảo thuật lại; chưa chứng minh có product cache có lợi trên DQI-19. Stage 1 chọn hướng theo yêu cầu người dùng; stage 2 chỉ chuẩn bị mô tả, Issue/branch và draft PR. Cần giao stage 3 trước khi viết source/config, khảo sát có instrumentation hoặc compile.

| Mốc tốt nhất | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Dev | Chưa tạo | Chưa có | Chưa chấm |
| Full | Chưa tạo | Chưa có | Chưa chấm |

Điểm toàn track: [SCORES.md](../SCORES.md). Chưa thêm dòng score cho hướng chưa có run PASS.

## Triển khai bước 03 — control_cache

Config đầu tiên [control_cache.json](configs/control_cache.json) giữ m/n/degree=4095/70/12 và strategy control_input, bật duy nhất tuyến `eea_tail_pair`. [solution.py](solution.py) import DQI-19 read-only sau khi đối chiếu SHA-256 nêu trên; subclass chỉ thay lịch tail của `_synchronized_eea` cùng ba helper shift/metadata/swap. Không sửa source DQI-19. Hướng vẫn nằm trong phạm vi thứ hai đã chọn: control EEA lân cận multiply/add.

Khảo sát phạm vi đầu bằng đa thức chuẩn hóa trên hai input 12 bit độc lập cho tensor rank42: 42 quadratic signatures khác nhau trong 861 cặp; không có hai term chênh nhau chỉ bởi affine trong mô hình boundary này. Đây không là chứng minh không có cache trên mọi reachable input/cross-call; không mở rộng tìm kiếm sang compiler toàn mạch. Chọn tuyến control có chứng minh trực tiếp thay vì ép term tensor trùng.

### Chứng chỉ tuyến cache được bật

- Boundary: ngay trước nhóm shift → metadata → swap của forward, hoặc swap → metadata → shift của reverse. Multiply/add và update_flag ở ngoài khoảng giữ cache. Hai dây cache mới alloc sạch, giữ được allocator reserve trong toàn nhóm.
- Factor bất biến: `c0=ctrl[0]`, `c3=ctrl[3]`, `f=flag`. Ba khối chỉ đọc ctrl/flag; hai lần X(flag) dùng để compute/cleanup đều khôi phục ngay. Swap chỉ ghi các polynomial/metadata, không ghi ctrl/flag. Vì thế chứng chỉ áp cho cả thứ tự thuận/ngược, không suy từ trạng thái một mẫu.
- Compute hai bit `p=c0*(1+f)` và `q=c3*(1+f)`. Shift dùng p/q cho điều khiển cursor như bản gốc. Metadata dùng lại cùng p/q thay vì init_and mới. Swap dùng CX từ c3 và q vào scratch sạch, vì `c3 XOR q=c3*f`; đây là equivalence affine giữa hai tích dưới phép complement f, không dùng điều kiện one-hot để suy công thức.
- Sau khối cuối, X(flag), del_and với chính c0/c3 và complemented flag ban đầu, X(flag), free hai cache. Các factor không đổi nên HMR/CZ của del_and bù đúng `(-1)^(h*p)` và `(-1)^(h*q)` trên mọi nhánh đo. Không đo dưới quantum control. Không còn tuyến sống khi update_counter/update_halting_counter chạy.
- Bản gốc compute 2 AND ở shift, 2 ở metadata và 1 ở swap; bản mới compute 2 và tái dùng. Dự đoán tĩnh trước build: tiết kiệm 3 mỗi bước ×222×2=1332 Toffoli-like; T=5043561 so 5044893 của đối chứng, giảm khoảng 0.0264%. Dự đoán Q không tăng vì cache thay nf của shift; giữ chúng trong metadata/swap phải được full build xác nhận, không suy từ số alloc tại điểm compute.

### Kiểm tra component và tiêu chí build

`--validate-segments`: 73728 ca trên tail thu nhỏ, cả thứ tự thuận/ngược, it=0/2/221, ba seed HMR; input array tùy ý, các tổ hợp control one-hot-or-zero/flag và metadata nằm trong bound cursor kế thừa. Output từng dây khớp reference, pha khớp, workspace sạch; mỗi segment giảm đúng 3 T, Q=83 ở cả hai. Thử đầu với metadata tùy ý ngoài bound đã làm reference có workspace dư; vì thế không dùng miền ngoài contract helper làm bằng chứng correctness của rewrite. Không thay verifier hoặc che lỗi decoder; full syndrome domain cần grader thật.

Chứng chỉ Boolean độc lập được kiểm trên đủ 256 đầu vào (c0,c3,flag và năm target tùy ý), 32 seed HMR, tổng 8192 ca; không lỗi value/phase/workspace. Các seed chỉ lấy mẫu outcome, không gọi là đã ép mọi nhánh đo. Tính đúng trên mọi outcome dựa trên factor bất biến và identity del_and, kết hợp kiểm thực thi component. Các probe không phải dev/full submission PASS.

Compile phải từ source/config đã commit và khớp bytes, dùng Python .venv 3.13.7 cùng packages pin. Build từ chối nếu Q>1893 hoặc T tĩnh khác 5043561; khi đạt mới ghi artifact `artifacts/dqi/DQI-25/control_cache.kmb` và provenance/helper hash. Chưa có score hoặc run decoder cho config này. Dev bàn giao giữ profile v1/seed20261106/4096 shots để so DQI-19 control_input; gain formal với baseline toàn repo vẫn cần môi trường/provenance tương thích. Giữ nguyên điều kiện dừng và yêu cầu kiểm tra full/seed giữ lại đã nêu, không nâng dự đoán thành kết quả.

### Bàn giao BUILT bước 03

Source/config đã commit trước compile tại `755ead9c879fb2a426ce36f3c6a7c6e3946b1bcb`; bytes local khớp snapshot trước và sau build. [Build record](../../../results/dqi/DQI-25/control_cache/build_only/20261108T155840Z-local-build/build.json), [provenance](../../../results/dqi/DQI-25/control_cache/build_only/20261108T155840Z-local-build/provenance.json), [segment checks](../../../results/dqi/DQI-25/control_cache/build_only/20261108T155840Z-local-build/segment_validation.json), [tensor audit](../../../results/dqi/DQI-25/control_cache/build_only/20261108T155840Z-local-build/tensor_audit.json).

Artifact `artifacts/dqi/DQI-25/control_cache.kmb`, 895956444 bytes, SHA-256 `9aacc7e5ca5c4fb0e5c4cb247e407860a9e3395c8d792822dbc78b76f3cd6860`. Toàn mạch Q=1893, T tĩnh=5043561, 90582806 instructions; giảm đúng 1332 T (0.0264029%) tại Q không đổi. Đây là số build, chưa phải mean T/score hay PASS của grader. Các invariant toán học và component checks hỗ trợ rewrite, không thay kết quả decoder trên syndrome hợp lệ.

21 tests repo đạt; checker thường và scope đạt, không sửa verifier/notebook/SCORES hoặc raw run cũ. Build records và annotation sau build giữ local để gộp trong commit kết quả bước 04 tiếp theo; không push tùy chọn. Issue đồng bộ thiết kế kèm trạng thái source chưa công bố; draft PR vẫn chứa stage 2 trên remote. Các dòng “cần giao stage 3/chưa triển khai” phía trên là lịch sử kế hoạch, đã được phần triển khai/bàn giao này thay thế.

Thành viên mở notebook ở worktree **GQA-DQI-25**, kernel `.venv` Python 3.13.7, chọn TRACK=dqi, MODE=dev_5min, EXPERIMENT_ID=DQI-25, CONFIG_NAME=control_cache, OWNER=trng-hminh. Giữ profile v1/seed20261106/4096 shots; results tự lưu `results/dqi/DQI-25/control_cache/dev_5min/<run-id>/`. Sau dev có thể chạy full để bổ sung bằng chứng trước tổng kết; hai mode không so điểm trực tiếp. Agent dừng chờ kết quả thật trước bước 04, không tự chấm hoặc chuyển bước 05/06.


## Phân tích bước 04 — lợi ích nhỏ nhưng đo được

Thành viên đã chấm dev và full. Hai run đều PASS, hash artifact khớp build và source `755ead9c879fb2a426ce36f3c6a7c6e3946b1bcb`. Raw stdout bằng verifier JSON, metadata exit code 0, provenance/config/helper/verifier hashes và mode/shots đã đối chiếu. Giữ nguyên raw records; review sidecar ghi phép so sánh và giới hạn.

| Mode | Run / provenance / review | Score ↓ | Mean Toffoli-like | Q | Shots | Value/phase errors |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| dev_5min | [run](../../../results/dqi/DQI-25/control_cache/dev_5min/20261108T160148Z-local-dev_5min-397221/verifier.json), [provenance](../../../results/dqi/DQI-25/control_cache/dev_5min/20261108T160148Z-local-dev_5min-397221/provenance.json), [review](../../../results/dqi/DQI-25/control_cache/dev_5min/20261108T160148Z-local-dev_5min-397221/review.json) | 53941201474428.805 | 5043217.541015625 | 1893 | 4096 | 0/0 |
| full | [run](../../../results/dqi/DQI-25/control_cache/full/20261108T160249Z-local-full-a97a1a/verifier.json), [provenance](../../../results/dqi/DQI-25/control_cache/full/20261108T160249Z-local-full-a97a1a/provenance.json), [review](../../../results/dqi/DQI-25/control_cache/full/20261108T160249Z-local-full-a97a1a/review.json) | 21528568859278.418 | 5043211.755 | 1893 | 102400 | 0/0 |

### Vì sao mức cải thiện rất nhỏ

Dev so đúng DQI-19 control_input cùng Python 3.13.7/packages/verifier/harness/profile v1/seed 20261106/4096 shots: mean T từ 5044549.541015625 xuống 5043217.541015625, giảm đúng **1332**, tương đương **0.0264047%**. Score từ 53955448268222.56 xuống 53941201474428.805; hệ số DQI-19/candidate khoảng **1.00026412×**. Q=1893 và R=2.9847755992784792 không đổi, nên giảm score đến hoàn toàn từ T. Đây là lợi ích nhỏ đúng như dự đoán trước thử, không phải thất bại cleanup hoặc nhiễu score che mất một cải thiện lớn.

Toàn mạch còn khoảng 5.04 triệu Toffoli; tuyến này chỉ bỏ ba compute AND ở mỗi tail ×444 bước. Phần nhân field, nghịch đảo/division và các xử lý decoder còn lại giữ nguyên. Muốn giảm 1% T cần khoảng 50445 Toffoli, tức gần 38 lần mức tiết kiệm hiện tại; đây là phép định cỡ, không phải bằng chứng có thêm 38 tuyến.

Full PASS 102400 shots bổ sung kiểm tra ngoài dev: mean T=5043211.755, Q=1893, R=1.1912604648115832. So full incumbent DQI-19 rank42, score giảm khoảng 0.0263667%; đây không là full ablation control_input hoàn toàn giống source/config. Hai full defaults dùng seed phụ thuộc artifact nên không gọi paired common-seed. Không suy luận tốc độ thực từ wall time: dev mới khoảng 40.25 giây so 30.58 giây lịch sử nhưng không chạy cặp trên môi trường tải được kiểm soát, và hàm điểm không dùng elapsed_seconds.

Cột gain formal so baseline toàn repo giữ `—` vì metadata baseline chính thức khác Python patch/harness. Hệ số 1.00026412× ở đây là so DQI-19 tương thích, không đổi nghĩa thành gain so baseline. Không sửa baseline hoặc suy đoán provenance.

### Có config khác đáng chấm không?

**Chưa có config mới có cơ sở định lượng tốt hơn.** JSON hiện tại chọn một tuyến chứng minh được và implementation chỉ hỗ trợ tuyến đó; tăng cache budget/window hay số tuyến không tự tạo tích lặp. Hai tích p/q đã dùng cho shift và metadata, còn swap đã dùng quan hệ affine; không còn lần compute trùng trong nhóm ba khối để bỏ bằng một setting khác. Cache một trong hai tích riêng chỉ là ablation, tiết kiệm ít hơn; không đáng build/chấm thường lệ nếu không cần tách tác động.

Khảo sát tensor trong mô hình hai input độc lập không thấy quadratic signatures lặp/khác nhau bởi affine; tăng số cache ở chính tensor không có chứng chỉ mới. Điều này không chứng minh mọi cache qua nhiều call là bất khả thi. Cơ hội tiếp theo, nếu có, cần phân tích code/guard/dataflow rộng hơn để tìm product giữ nguyên qua các lần dùng, không thể suy từ cùng ID dây khi dữ liệu đã bị ghi. Đây là sửa implementation cần stage 05 được giao và chứng chỉ liveness/pha mới; chưa thực hiện.

Tại Q=1893, thêm chỉ một qubit làm Q² tăng khoảng 0.10568%, khoảng bốn lần lợi ích hiện tại. Một tuyến làm tăng Q cần tiết kiệm khoảng 5325 T chỉ để bù mức tăng đó ở T hiện tại; điều kiện của hướng vẫn nghiêm hơn: không tăng Q. Vì thế tăng dung lượng cache thiếu chứng chỉ rất dễ kém đi.

**Đề xuất:** giữ kết quả đúng và lợi ích nhỏ, kết thúc vòng tối ưu config thường lệ; chỉ mở vòng tiếp nếu tìm được tuyến mới có bound T ròng và Q rõ ràng. Không triển khai thêm config, không chuyển stage 06 hoặc ready/merge PR trong bước phân tích này. Chưa kết luận product caching không thể có lợi trên kiến trúc khác; kết luận chỉ áp cho phạm vi khảo sát hiện tại.

### Mốc tái lập tốt nhất

Cả dev và full hiện dùng config [control_cache.json](configs/control_cache.json), source `755ead9c879fb2a426ce36f3c6a7c6e3946b1bcb`, helper DQI-19 c0cf9df đúng hash trong provenance. Các run và provenance ở bảng trên là mốc tốt nhất duy nhất của ID này. Checkout source đó và chạy build command đã ghi trong provenance để tái lập; không dùng HEAD tương lai thay SHA nguồn. Full là bằng chứng thống kê độc lập với dev cố định, không chứng minh mọi syndrome.

Các ghi chú “chưa chấm/chờ bước 04” ở phần kế hoạch và bàn giao là trạng thái lịch sử, đã được phân tích này thay thế. Commit bước 04 lưu build records, hai raw runs, review sidecars, score và phân tích; giữ local theo yêu cầu không push tùy chọn của người dùng.


## Tổng kết bước 06

Sau phân tích, người dùng giao bước 05–06 và chấp nhận đề xuất kết thúc vòng config thường lệ. Không mở vòng build/chấm mới ở bước 05 vì chưa có tuyến cache mới có chứng chỉ/lợi ích định lượng; không coi config trùng hoặc ablation yếu hơn là một cải thiện mới. Chuyển trực tiếp từ kết quả bước 04 sang tổng kết bước 06, giữ nguyên source/config đã chấm.

Phạm vi nghiên cứu hữu hạn của hướng đã hoàn tất: tuyến reuse control có chứng minh, kiểm component và dev/full PASS; lợi ích nhỏ được báo đúng, chưa kết luận các kiến trúc product caching khác không có lợi. Gợi ý cho reviewer tiếp theo là tìm thêm tuyến cục bộ có factor bất biến hoặc tương đương affine có chứng chỉ và không tăng Q, trước khi cấp ngân sách build/chấm mới. Không có implementation cho gợi ý đó.

Bước 06 đồng bộ main bằng merge, giữ nguyên các SHA nguồn/run và mọi dòng hướng khác trong mục lục/score; push các commit source/kết quả đã lưu và chuẩn bị PR review. Những ghi chú “local/chưa push” ở các mốc trước là lịch sử tại thời điểm bàn giao, được bước công bố này thay thế sau push. Reviewer độc lập dùng bước 07/07b trên HEAD cuối; chưa approve, merge PR hoặc đóng Issue ở bước này.
