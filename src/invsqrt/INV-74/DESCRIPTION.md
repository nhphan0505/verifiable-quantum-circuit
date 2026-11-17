# [INV-74] Tái dựng Fusion 44 qubit bằng Python và phục hồi số học từ KMX

Loại: Tái dựng từ submission; không coi thông tin điểm bên ngoài là kết quả local.

## Nguồn và mục tiêu

Input `invsqrt_x2763.kmb`, 200369 bytes, SHA-256 `47b318383a03c52e08a5c222c5600fd52e004b468f53fad038082fc0f26386ef`. Người dùng cung cấp attribution Syed Asad Ali, dataset `syed3000/vqcc-own-circuit-portfolio`, yêu cầu giữ attribution qua mọi lớp phái sinh. Chưa có source generator hay toàn văn notice/license của đúng artifact này; không tự suy giấy phép từ INV-51. Mục tiêu là Python độc lập dựng exact và phục hồi thuật toán tương tự INV-66, không chỉ wrapper hoặc opcode tape.

## Quan sát và đối chứng

Mạch có 44 qubit; register x là q0..q21. KMB trực tiếp và KMB qua KMX đều trùng bytes/hash. Có 24155 dòng KMX, 1379 CCX, 9 CCZ, 145 CSWAP, 1236 HMR, 39 Z_POW. Số lệnh là thống kê tĩnh, không phải chi phí thực thi. Đối chứng INV-66 tại source `f315c15b5828166e011e91388c2bdf97a54a77f9`, target `e46d90c36d1beb3ce7731a3e0b5c3659b3cda7f5f290b73c6c34513d96c005b6`, 46 qubit. 1635 dòng đầu hai KMX giống hệt; chưa suy phần còn lại giống thuật toán. INV-66 chưa merge nên không đưa dependency chưa có trên main vào build mà không track/push rõ ràng.

## Tái dựng và phục hồi thuật toán

Giữ thứ tự register, qubit, bit đo, PUSH/POP_CONDITION, HMR correction, exact rational angles và layout. Bắt đầu từ emitter Python rõ lệnh để khóa mục tiêu hash; sau đó thay từng khối bằng helper số học được đối chiếu instruction-for-instruction. Emitter không được đọc KMB/KMX gốc khi build, nhúng binary/archive hoặc toàn submission dưới dạng dữ liệu. Mức gate-level không đồng nghĩa phục hồi thuật toán và không phải kết luận cuối mong muốn.

Định vị normalize/consumed-root theo shared prefix và helper đã track của INV-51. Phân tích riêng lookup/address frame, bảng hệ số và rounding theo hàng, seed/product, divider, phase endpoint, inverse và HMR debt repayment. Chưa biết công thức của các khối mới thì ghi chưa biết; không thay bằng công thức INV-66 theo suy đoán. Với mỗi khối xác định input/output owner, width, modular arithmetic, carry/debt invariant và snapshot classical độc lập. Contract cuối là exp(2*pi*i/sqrt(x)) cho x=1..3133452, khôi phục x và toàn scratch; đúng hash không tự chứng minh mô tả thuật toán đúng.

## Kế hoạch kiểm chứng hypothesis

- Hypothesis tái lập: source/config/helper/data đã track và push đủ để dựng exact 200369 bytes với target hash; bác bỏ nếu khác một byte hoặc cần dữ liệu ngoài checkout/runtime.
- Config đầu tiên reconstructed, target cố định; package theo requirements của repo. Không chỉnh precision/góc/cấp phát trong giai đoạn exact.
- Build entry point từ checkout GitHub sạch, venv mới, cwd ngoài checkout; audit toàn read/import/subprocess, chỉ đọc checkout/runtime và intermediate vừa sinh. Ghi provenance và reconstruction_check build_only, giữ commit nguồn.
- Hai vòng sửa có căn cứ cho mỗi khối rồi đánh giá nguyên nhân nếu còn mismatch; không lặp quét tham số vô hạn. Không nghiệm thu arithmetic khi chỉ có emitter.
- Chấm notebook local là bước riêng; chưa có run mới, chưa xác nhận số liệu người dùng. Không sửa verifier, checker, notebook hoặc run cũ. Review độc lập và checks là điều kiện hoàn tất, không tự approve/merge.

## Hướng cải tiến hậu nghiệm cần kiểm chứng riêng

Ưu tiên giải thích giảm peak owner từ 46 xuống 44 trước; chưa nhận là đã biết cơ chế. Sau exact có thể khảo sát dead-write CCX trước HMR theo guards control/owner và conditional CZ; hoặc gộp pha trên cùng Boolean feature bằng rational exact. Đây là đề xuất, chưa chọn hypothesis PP và chưa triển khai. Phải chứng minh input chưa qua PP tương ứng và kiểm từng phương pháp độc lập theo instructions/postprocessing, không lấy pipeline ghép làm bằng chứng. Bác bỏ nếu không có ứng viên hợp lệ, trả pha/scratch sai, hoặc full Q*C không cải thiện. Giới hạn một thay đổi có chứng minh rồi kiểm độc lập; không tự quét vô hạn.

## Giới hạn hiện tại

Bước tiếp nhận/khứ hồi/phân tích ban đầu đã có scratch bất biến. Đã viết source explicit cấp cổng trong circuit.py và CLI solution.py, config reconstructed; chưa build. Đây chưa phải phục hồi generator số học; clean build và grading mới chưa có. Thông tin cost/ratio từ người dùng được giữ ở manifest đầu vào, không đưa lên bảng điểm. Chưa khẳng định phục hồi source/search procedure gốc hoặc đủ điều kiện merge.

## Implementation ban đầu

[solution.py](solution.py) kiểm snapshot committed và môi trường, cấm network/subprocess khi dựng, chỉ đọc [circuit.py](circuit.py) cùng runtime đã pin. Source ban đầu sinh mỗi lệnh bằng lời gọi Python rõ ràng, chia hàm theo khoảng operation để kiểm tra; prefix hiện đã được thay bằng arithmetic_prefix.py; không chứa nguyên KMX/binary trong data và không đọc submission gốc. Đây là mốc GATE_LEVEL_PYTHON phục vụ phục hồi tiếp, chưa đáp ứng mục tiêu generator số học giống INV-66. Góc là decimal string exact half-turn, điều kiện từng lệnh và stack giữ riêng. [reconstruction.json](reconstruction.json) khai báo dependency và giới hạn; [NOTICE](NOTICE.txt) giữ attribution qua mọi lớp phái sinh.

## Manh mối phục hồi root và frame

Trên 2054 input (seed 74001), tại boundary operation 1649 không tính metadata, root q10..q21 khớp normalize_root của INV-66; residual q1..q9 giữ 9 bit cao còn q0 bằng zero. Hai cờ q24/q25 cùng XOR một bit t, hai cờ thấp không đổi. Tại operation 1612, t = h0 XOR 1 XOR v2 XOR v3 XOR v4 XOR temporary_q36; trên tập mẫu t bằng parity của normalized n. Đoạn mới 11 lệnh đưa t vào hai cờ rồi HMR q0 và conditional CZ(q24,q25). Đây là quan sát basis với outcome HMR zero, chưa chứng minh branch phase cho mọi outcome và chưa suy giảm 2 qubit chỉ từ đoạn này. Xem evidence/root_analysis.json.

## Phục hồi prefix bằng số học

[arithmetic_prefix.py](arithmetic_prefix.py) đã thay 1649 lời gọi cấp cổng đầu bằng normalization và consumed-root thật từ INV-51/circuit.py trên main. Chỉ nạp các primitive forward và patch narrow normalization; `_TABLES={}` để cấm fallback sang data/bundle INV-51. Bốn Z_POW exact tại normalization và frame/retire parity có guard theo owner/boundary compiler cố định. Phần lookup/coefficient/divider/phase/inverse vẫn explicit cấp cổng; không nhận đã phục hồi toàn generator. Thay đổi source cần build sạch lại trước nghiệm thu exact.

## Chứng minh phase cho parity frame

Vì n=x*4^k, n lẻ kéo theo k=0. Với k=0..10, code k không có đồng thời bit2 và bit3 bằng 1. Đổi code thành f=k XOR 12*p, p=n mod 2, cho f=12 khi p=1 và f=k khi p=0; ánh xạ (k,p)→f là đơn ánh trên miền hợp lệ, p=f2*f3, k=f XOR 12*p. HMR của q0=p sinh dấu (-1)^(m*p); CZ(f2,f3) dưới điều kiện m sinh cùng dấu, tích bằng 1 với cả hai outcome. Đó là lý do có thể retire q0 mà giữ coherence trên miền bài toán. Hai tests trong tests/test_parity_frame.py kiểm toàn bộ code hợp lệ và cả hai outcome. Công thức t=n mod 2 trước khi đo đã được kiểm exhaustively riêng; đây chưa phải chứng minh toàn bộ mạch hoặc điểm mới.

## Mốc build exact và kiểm tra thực tế

Source `36553eb7800dfa7afd1185aaf924297219642dc3` đã được clone từ GitHub vào checkout sạch, tạo venv mới và cài requirements pin. Entry point chạy từ cwd ngoài checkout; output trùng toàn bộ 200369 bytes và SHA-256 target. Audit ghi các source/helper thực sự đọc, gồm shared INV-51/circuit.py; không đọc submission gốc hoặc data/bundle/cache máy tác giả. So bytes với input được thực hiện riêng sau build. Xem [clean checkout build](../../../results/invsqrt/INV-74/reconstructed/build_only/20261117T112724Z-exact-4e8c34e8/clean_checkout_build.json) và [byte comparison](../../../results/invsqrt/INV-74/reconstructed/build_only/20261117T112724Z-exact-4e8c34e8/byte_comparison.json). Config reconstructed → source `36553eb7800dfa7afd1185aaf924297219642dc3` → run `20261117T112724Z-exact-4e8c34e8`. Thay đổi tài liệu/manifest sau đó không thay SHA nguồn của run.

Đã kiểm root/frame trên toàn miền x=1..3133452 với outcome HMR zero: v và h cao khớp công thức, q0 zero, flags=k XOR 12*(n mod 2), scratch q26 trở lên zero tại boundary 1649. Xem evidence/exhaustive_root.json. Kiểm thêm 141 input biên/ngẫu nhiên, seed 74002, mỗi input có nhánh zero và bốn luồng outcome HMR ngẫu nhiên: x khôi phục, scratch zero, pha exact modulo hai half-turn khớp nhánh zero. Xem evidence/branch_analysis.json. Đây là phân tích semantics, không phải verifier run hoặc chứng minh synthesis error/score.

Checker và diff scope ban đầu đạt 0 lỗi. Bộ scripts/tests ban đầu chạy 34 tests, một lỗi fixture do đường dẫn Windows dài; chạy lại toàn nhóm test_check_repo với core.longpaths=true đạt 14/14. Hai tests parity-frame đạt. Không sửa checker/tests hạ tầng hoặc kết quả cũ.

## Khảo sát cải tiến và phần chưa phục hồi

Quét chỉ đọc theo toàn bộ guard conservative dead-write CCX→HMR/CZ của INV-66 cho 0 ứng viên. Không rewrite hoặc áp PP, không khẳng định có thể giảm thêm Toffoli bằng rule đó. Pipeline tạo input gốc chưa biết nên chưa thể xác nhận input chưa qua PP. Bằng chứng ở evidence/pp_guard_scan.json. Thử nghiệm PP mới phải chọn hypothesis và quản lý độc lập theo instructions/postprocessing; không tự tích hợp nhiều PP vào bản exact.

Hai hướng còn có căn cứ khảo sát: (1) mở rộng cách dùng code chuẩn hóa dư để giữ metadata và giảm peak owner ở lookup/coefficient, với điều kiện encoding đơn ánh và trả toàn debt; (2) so sánh Boolean features pha để tìm phép gộp exact có lợi cho chi phí tổng, không gộp chỉ vì cùng dây tại thời điểm khác. Đây là đề xuất hậu nghiệm, chưa đo lợi ích hoặc triển khai. Dừng nếu không chứng minh được owner/phase invariant; không thay artifact exact âm thầm.

Mục tiêu phục hồi generator số học đầy đủ như INV-66 **chưa hoàn tất**. Prefix đã dùng thuật toán số học nhưng lookup/address frame, coefficient rounding, seed/product, divider/phase và inverse/cleanup vẫn ở mức explicit gate-level. Không dùng bảng/công thức INV-66 để thay khối mới khi chưa có mapping owner và kiểm chứng. Bước tiếp theo là giải các truth table/frame của loader mới và recurrence coefficient từ snapshots độc lập, rồi thay từng khối và build sạch lại. Draft PR giữ trạng thái chưa sẵn sàng nghiệm thu toàn generator; không có review độc lập, grading mới hoặc merge.

## Chạy lại từ checkout mới

Tại root checkout của source commit ở trên, dùng Python 3.13 tạo `.venv`, chạy `.venv/Scripts/python.exe -m pip install -r requirements.txt`. Có thể chạy từ bất kỳ cwd với đường dẫn tuyệt đối tới `src/invsqrt/INV-74/solution.py` và `--config` trỏ vào `src/invsqrt/INV-74/configs/reconstructed.json` của checkout đó. Working tree phải sạch; output mặc định là `artifacts/invsqrt/INV-74/reconstructed.kmb`, không ghi đè output có sẵn. Records mới được tạo trong results/invsqrt/INV-74/reconstructed/build_only. Chưa có run full/smoke để ghi vào SCORES.
