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
