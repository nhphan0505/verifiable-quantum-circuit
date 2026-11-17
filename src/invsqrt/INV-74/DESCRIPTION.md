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

Bước tiếp nhận/khứ hồi/phân tích ban đầu đã có scratch bất biến. Chưa có source tái dựng, clean build hoặc grading mới. Thông tin cost/ratio từ người dùng được giữ ở manifest đầu vào, không đưa lên bảng điểm. Chưa khẳng định phục hồi source/search procedure gốc hoặc đủ điều kiện merge.
