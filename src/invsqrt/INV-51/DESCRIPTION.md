# [INV-51] Tái lập mạch invsqrt 46 qubit bằng source tác giả và đối chiếu KMX/KMB exact

Loại: Tái dựng từ submission.

Áp dụng phân loại riêng tại [instructions decompiler bước 04](../../../instructions/decompiler/04_claim.md); source tác giả đã được cung cấp cho bản này.

## File gốc

Kế thừa generator Fusion của Syed Asad Ali, Apache-2.0, trong gói `invsqrt_source` người dùng cung cấp. Giữ attribution tại [NOTICE](data/NOTICE.txt), [LICENSE](data/LICENSE.txt) và manifest `data/SHA256SUMS`. Gói chứa generator nền `src/work/c10`, 13 patch và các certificate/bảng dùng khi dựng. Nguồn discussion do người dùng xác nhận đã lấy source: [Kaggle discussion #758815](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/758815). Archive nguồn tải từ [dataset VQCC Own-Circuit Portfolio](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio), file `invsqrt_source_zip`; đổi tên thành `.zip` để giải nén. SHA-256 archive là `7d9801ae20e942dba2211a656bba6014a0a16d57da534c0b60328d1c5d9d8254` (2563106 bytes), đã kiểm tra manifest và toàn bộ 560 file bên trong. Đã tải lại [archive version 12 qua API công khai](https://www.kaggle.com/api/v1/datasets/download/syed3000/vqcc-own-circuit-portfolio/invsqrt_source_zip?datasetVersionNumber=12) không đăng nhập, HTTP 200 và hash trùng; dataset listing trả isPrivate=false, giấy phép Apache 2.0. Xem [bằng chứng nguồn](evidence/public_source.json). Cách cấp dependency nằm trong [DEPENDENCIES.md](DEPENDENCIES.md).

Submission đối chứng là `invsqrt.kmb`, 291626 byte, SHA-256 `321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177`. Source tác giả khai báo đúng hash này. Đây là phiên bản tốt nhất theo chi phí báo cáo trong các ảnh người dùng cung cấp; đã có phép chấm dev local trong hướng này, còn điểm full lịch sử chưa được xác nhận lại.

## Mục tiêu và phạm vi

Viết [solution.py](solution.py) đọc [configs/reconstructed.json](configs/reconstructed.json), dựng mạch bằng Python trong `.venv` Windows và xuất `artifacts/invsqrt/INV-51/reconstructed.kmb`. Giữ nguyên thuật toán, các bảng, góc quay, thứ tự patch và cấp phát qubit của bản nguồn. Tiêu chí là trùng toàn bộ bytes/hash với submission, không chỉ tương đương chức năng. Không đọc submission hay KMX đối chứng khi build.

Đây không phải một đề xuất tối ưu mới hoặc bản chỉnh sửa trực tiếp [INV-BASELINE](../INV-BASELINE/DESCRIPTION.md). Baseline repo dùng Horner bậc ba rồi Newton–Raphson; generator được cung cấp có luồng root/residual, bảng hệ số, seed, product, divider và phase endpoint riêng. Không gán lịch sử thuật toán của các ảnh bản cũ cho bản cuối nếu source không xác nhận.

## Thuật toán và biểu diễn

Bài toán là thực hiện `|x>|0> → exp(2πi/√x)|x>|0>` với x trong [1,3133452]. Register duy nhất tên `x` có 22 qubit little-endian. Mạch cuối dùng 46 qubit; 24 qubit còn lại là workspace được tái sử dụng theo giai đoạn.

Generator thực hiện các bước sau:

1. Cấp phát 22 qubit input và 4 cờ chuẩn hóa; chạy `normalization.forward`.
2. `root.forward` chuyển giá trị chuẩn hóa sang root 12 bit và residual 10 bit. Root/residual chiếm lại vùng dữ liệu, không giữ thêm bản sao nguyên input.
3. `emit_body` nạp bảng đầu từ các bit cao của root, tạo hệ số, xử lý metadata, dựng seed nghịch đảo và tích trung gian. Các giá trị không cần trong một đoạn được đo X rồi tái dựng ở thời điểm dùng lại, cùng khoản sửa pha tương ứng.
4. Luồng tiếp theo nạp bảng thứ hai, thực hiện divider và phase endpoint. Góc pha giữ dạng chính xác do generator/serializer cung cấp; không chuyển qua float để sinh lại góc.
5. Cleanup đảo các phép tính, trả lại root/residual và cờ. `root.inverse`, `normalization.inverse` và `restore_input_layout` khôi phục input về đúng qubit vật lý ban đầu. Sau đó gắn register `x` vào mạch.

Các patch trong `PATCH_ORDER.txt` thay callback của generator đã nạp, theo thứ tự cố định. Những thay đổi chính của bản 46 qubit gồm:

- Nạp hệ số bằng các chương trình Boolean có certificate, với giới hạn workspace riêng cho hai lượt. Địa chỉ và bit output giữ đúng giao diện của generator.
- Đo bỏ một số root bit ở đoạn endpoint, rồi tái dựng bằng chương trình AND đã khai báo. Root bit thứ hai dùng lại tích có sẵn từ lần tái dựng thứ nhất.
- Đo bỏ và tái dựng các history bit của divider để giảm đỉnh workspace. Sửa pha HMR được gắn với giá trị Boolean đã tái dựng, không chỉ khôi phục giá trị cổ điển.
- Tái dùng tích trung gian và thay cách phân bố pha ở postpass cuối.

Khi dùng temporary AND `t=a·b`, việc xóa bằng HMR có correction CZ(a,b) theo kết quả đo. Mọi scratch được đo/xóa phải có correction phù hợp với biểu thức thật của nó. Các trường hợp tái dựng phức tạp dùng bảng/certificate của source; hướng này giữ nguyên biểu thức, không tự suy ra một công thức thay thế có ít cổng hơn.

### Luồng dữ liệu và lịch đo/tái dựng trong thân mạch

Các tên dưới đây là vai trò logic trong source, không cố định vào một số qubit sau mọi bước. `v[0:12]` là root, `h[0:10]` là residual, `flags[0:4]` giữ lớp chuẩn hóa. Khi một vai trò bị đo và free, lần tái dựng có thể dùng qubit vật lý khác. Sau mỗi giai đoạn phải truyền danh sách owner hiện tại cho phần inverse.

`src/patches/patch_w47_body.py::emit_body` trong bundle đã pin mô tả lịch chính; bản cuối đặt `PACK=False`, `A6_EARLY=True`, `TAIL='donor'`:

| Giai đoạn | Dữ liệu và chuyển tiếp | Khoản đo/sửa pha phải xử lý |
| --- | --- | --- |
| Bảng đầu | Địa chỉ `v[5:]` nạp `D` và `Hlow`; dựng H3/H4, đổi root sang R-frame, chạy coefficient_forward | Đo sớm a6=`v[11]` sau H3; giữ outcome đến khi tái dựng. Xóa H qua table_debts; giữ snapshot hệ số |
| Seed và product | seed_forward dùng root và D; product_forward dùng D, seed và residual; từ word 16 bit giữ signed product P 15 bit | Tái dựng a6 từ D hiện tại; trả pha bằng Z(a6) khi outcome=1. Đo các bit D và giữ transcript `first_D` |
| Divider/phase | `compute_phase_cleanup(v,P,flags)` tạo trạng thái divider, thực hiện phase endpoint và đảo divider; trả lại P | Chỉ kết thúc ở 31 owner dữ liệu: root12+P15+flags4. Mọi carry/history debt phải trả trong cleanup |
| Bảng thứ hai | Chuyển root sang R-frame; nạp D/H từ lượt second. Bốn địa chỉ a0,a1,a2,a4 đã bị tiêu thụ; đo thêm a6 sau H3 | coefficient_forward tái tạo D để trả toàn bộ `first_D` bằng các Z có điều kiện; merge transcript hai lượt |
| Đảo product/seed | Tạo lại bit cao của word từ P14; product_inverse trả seed và residual, rồi seed_cleanup | Truyền owner root hiện tại và các dirty wire được phép dùng; giữ snapshot cho coefficient_inverse |
| Tail và hoàn nguyên | Replay T1 tái dựng a6/H3/H4; coefficient_inverse; replay T2 dựng lại bốn address bit và capture pha R; cleanup_joint18 | Xóa outcome a6, trả khoản pha R và table_debts; kiểm tra mọi row debt consumed, không còn measurement chờ, trả v12+h10+flags4 |

Ví dụ tái dựng a6 trong source: `a6 = D10 XOR D11 XOR D12 XOR ((D10 XOR a5) AND (D11 XOR a5))`, với a5=`v[10]`. Hai CX vào D10/D11 được đảo lại sau CCX. Z có điều kiện trên a6 mới trả đúng pha của lần HMR trước đó; khôi phục giá trị mà thiếu Z này chưa đủ đúng.

Divider lưu 24 row-debt và history của các hàng 12..24. `patch_hret_sat_s15k7a.py` đo bỏ sign12 và các history13/14/15 (15 có certificate SAT đã pin), giữ outcomes; khi đảo hàng thì tái dựng history cần dùng và trả pha trước khi tiêu thụ debt. Cuối cleanup phải quay về 31 owner, mọi debt được đánh dấu consumed. Các biểu thức history là dependency certificate, không suy ra từ tên hàng.

Endpoint trong `patch_endpoint_v9e2.py` gắn `agents/composer/p/w2core_e2.py`: route/walk trên ring26, các feature Boolean của lớp chuẩn hóa điều khiển phép quay chính xác modulo 2^50. Các tích E/F và đường route được giữ lại khi còn chỗ. Hai root bit v9/v10 bị retire qua endpoint; v9 được tái dựng theo `v9_form_e2.json`, v10 tái dùng gate g1 của chương trình đó khi hash form khớp. Giới hạn QMAX được đặt 46. Đây là mô tả từ source, không phải bằng chứng tự kiểm chứng toàn bộ correction.

Sau body_return, `root.inverse` và `normalization.inverse` chỉ chạy khi đã có đủ owner; `restore_input_layout` đưa register x về đúng thứ tự vật lý. Các assertion trong source kiểm tra số owner, debt và snapshot còn chờ; dev PASS hiện tại chưa chứng minh chúng cho mọi transcript đo.

## Các lượt hoàn thiện mạch

Sau generator, solution thực hiện đúng thứ tự build của tác giả:

1. Quét mạch để tìm quan hệ affine và các tích được tính lặp.
2. Giữ tích AND trên qubit rảnh khi lịch sống cho phép, dùng CX tại lần cần lại và HMR/correction khi kết thúc.
3. Tối đa bốn lượt tìm và thay Toffoli có tích nằm trong span affine của các dây đang sống; dừng sớm khi không còn findings.
4. Gộp các Z_POW tác động lên cùng hàm Boolean, giữ số học góc chính xác.
5. Compile, chạy postpass `relocate_cs2.py`, rồi compile KMB cuối.

Các audit này là một phần thuật toán dựng. Chúng không được ghi nhận thành official verifier PASS. Nếu serializer hoặc platform sinh bytes khác, build dừng và giữ output để điều tra.

## Điều kiện đúng, sai số và tài nguyên

Input phải được khôi phục, scratch phải về zero, không thêm register ngoài `x`. Verifier gốc cho tolerance `2^-24/√x` turns; phép tổng hợp rotation còn phải nằm trong phần ngân sách sai số dư. Hướng tái lập không thay precision, miền x hoặc dung sai.

Quan sát trực tiếp từ KMB: 46 qubit, 1297 HMR, 895 cặp PUSH_CONDITION/POP_CONDITION; số lệnh tĩnh là 1461 CCX, 9 CCZ, 129 CSWAP và 38 Z_POW. Các số tĩnh không bằng số cổng kỳ vọng thực thi mỗi shot. Báo cáo compiler từ bản dựng tính kỳ vọng 1511.5703125 Toffoli-like, 1 T và 33 generic rotations theo Boolean guards. Đây là kết quả đếm từ mạch với giả định HMR độc lập/công bằng, chưa phải điểm chấm. Vì vậy không tính score bằng tổng lệnh đơn giản. Inventory ở [evidence/circuit_inventory.json](evidence/circuit_inventory.json).

Đánh đổi của thiết kế là giảm số qubit bằng đo và tái dựng, có thể tăng một phần cổng/correction. Trong công thức score `Q × (Toffoli + T/4)`, chi phí tổng hợp rotation cũng góp vào T. Chưa có run tương thích thì không tính hệ số cải thiện so với baseline.

## Cách chạy và cấu hình

Dùng Python 3.13 trong `.venv` Windows, Kickmix 1.0.0, NumPy 2.5.4 và SciPy 1.18.1. Không dùng WSL. Config có ba trường: đường dẫn bundle nguồn tương đối root, hash mục tiêu và timeout 600 giây mỗi stage. Config phải nằm trong thư mục configs của hướng này; output lấy tên theo stem config. Output có sẵn sẽ không bị ghi đè. Provenance của các build mới ghi executable và lệnh chạy tương đối repo root bằng dấu `/`; build_only đặt build_run=null. Provenance lịch sử được giữ nguyên bytes.

[windows_runner.py](windows_runner.py) preload Kickmix Windows từ `.venv`. File Linux `.so` chỉ dùng để kiểm tra source pin, không thực thi. Adapter ghi rõ các yêu cầu Unix setrlimit không được enforce trên Windows; timeout subprocess vẫn có hiệu lực. Một assertion so sánh đường dẫn certificate được đổi sang so Path.resolve để xử lý dấu phân cách Windows; hash certificate không đổi. Các file generator nền đã pin giữ nguyên bytes.

Chạy lệnh trong [DEPENDENCIES.md](DEPENDENCIES.md). Build dùng bản nguồn đã commit, kiểm tra hash dependency rồi ghi provenance. Toàn bộ source tác giả là dependency ngoài Git, không phải source độc lập chỉ cần một file solution; người tái lập phải cấp đúng bundle. Source/config và metadata của adapter được version hóa trong hướng này.

## Kế hoạch kiểm chứng hypothesis

- Mốc đối chứng: hash submission ở trên, manifest 560 file của source và verifier gốc đúng data_manifest của repo. Hash xác định phiên bản, không dùng tên file hoặc ảnh làm bằng chứng PASS.
- Dự đoán: generator và các pass cố định chạy trên Windows tạo đúng bytes của bản tác giả.
- Ủng hộ: build từ source commit thật, hash trùng và công cụ độc lập so bytes toàn file đạt. Bác bỏ: bất kỳ sai khác byte nào hoặc thiếu dependency truy vết được.
- Điều kiện dừng: đạt exact hoặc sau ba lần sửa lỗi tích hợp phải đánh giá lại. Không vá KMB bằng input gốc; không hạ tiêu chí xuống tương đương chức năng.
- Kiểm tra độc lập ứng viên cuối: thành viên chạy notebook local dev_5min, sau đó full hoặc profile bổ sung phù hợp; reviewer khác tài khoản đánh giá source/provenance. Agent không tự chạy official verifier trong lượt decompiler này.

## Kết luận và phiên bản tái lập

Tiếp nhận và KMB/KMX roundtrip đã đạt, xem [roundtrip_check.json](evidence/roundtrip_check.json). Đã có dev_5min PASS trên 4096 input / 8192 shots; chưa có full. Build độc lập bằng .venv Windows đã đạt RECONSTRUCTED_EXACT: 291626 bytes trùng hoàn toàn với submission. Đã so từng block bytes và SHA-256 độc lập với builder. Exact chứng minh tái lập, không thay cho kết quả chấm hoặc full proof.

| Mốc | Config | Commit nguồn | Run / provenance |
| --- | --- | --- | --- |
| Build exact | [reconstructed](configs/reconstructed.json) | `bfe070108c6dd02649c6ba4ab3400b2f0ed50249` | [provenance](../../../results/invsqrt/INV-51/reconstructed/build_only/20261113T083955Z-exact-wopk8bm7/provenance.json), [đối chiếu](../../../results/invsqrt/INV-51/reconstructed/build_only/20261113T083955Z-exact-wopk8bm7/reconstruction_check.json) |
| Build sau review | [reconstructed](configs/reconstructed.json) | `48729436b421e7320d86e48cc0e451be0d84260e` | [provenance](../../../results/invsqrt/INV-51/reconstructed/build_only/20261113T160603Z-exact-8fe62qjo/provenance.json), [đối chiếu](../../../results/invsqrt/INV-51/reconstructed/build_only/20261113T160603Z-exact-8fe62qjo/reconstruction_check.json) |
| Dev | [reconstructed](configs/reconstructed.json) | `bfe070108c6dd02649c6ba4ab3400b2f0ed50249` | [run](../../../results/invsqrt/INV-51/reconstructed/dev_5min/20261113T084759Z-local-dev_5min-127a3b/verifier.json), [provenance](../../../results/invsqrt/INV-51/reconstructed/dev_5min/20261113T084759Z-local-dev_5min-127a3b/provenance.json) |
| Full | Chưa chấm | Chưa có | Chưa có |

Mã triển khai: [solution.py](solution.py). Cấu hình: [configs](configs/). Manifest: [reconstruction.json](reconstruction.json). Điểm và các run: [SCORES.md](../SCORES.md).


## Phân tích kết quả dev và quyết định

Run dev_5min ngày 13/11/2026 đạt PASS trên 4096 input, mỗi input 2 shots (8192 shots), seed 20261106, profile v1. Hash artifact khớp bản dựng exact và provenance nối đúng source commit, không lấy HEAD hiện tại làm nguồn dựng.

Mạch dùng 46 qubit, trung bình 1511.5113525390625 Toffoli-like, 1 T và 33 generic rotations trên các shots được chấm. Tỷ số sai số/dung sai lớn nhất là 0.7422629274647067 tại x=248, dưới ngưỡng 1. Sai số ở các input chưa lấy mẫu và các nhánh đo khác chưa được run này chứng minh.

So sánh với baseline local dev cùng Python, package, verifier/hash harness, profile, seed và hash tập input là hợp lệ; hệ số cải thiện được ghi trong SCORES. Score dev khác con số lịch sử trong ảnh vì profile lấy mẫu và ngân sách tổng hợp rotation phụ thuộc sai số quan sát được; không coi dev score là xác nhận điểm full của tác giả.

Hypothesis tái lập đúng bytes đã được ủng hộ bởi build exact. Run dev bổ sung bằng chứng chức năng trên mẫu đã chấm; chưa chứng minh toàn miền hay mọi transcript HMR. Dừng thay đổi implementation ở mốc exact này. Bước tiếp theo là thành viên chấm full hoặc profile bổ sung độc lập, rồi reviewer khác tài khoản kiểm tra trước merge. Không tối ưu thêm trong hướng tái lập hiện tại.

Bản build sau sửa review giữ nguyên hash/bytes của bản gốc; thay đổi ở code chỉ chuẩn hóa metadata provenance. Run dev trong bảng vẫn thuộc commit nguồn lịch sử bfe0701, không gán lại sang commit mới. Chưa chạy full; reviewer cần đánh giá lại HEAD mới trước merge.
