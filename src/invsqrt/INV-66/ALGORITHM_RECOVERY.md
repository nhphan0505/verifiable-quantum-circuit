# INV-66: phục hồi thuật toán sau review

## Trạng thái nghiệm thu

Review [5909379196](https://github.com/nhphan0505/verifiable-quantum-circuit/pull/67#pullrequestreview-5909379196) của nhphan0505 trên commit 6c94828436f3deba8b92069e064afafeebc884fb yêu cầu phục hồi thuật toán số học gốc. Bản hiện tại chỉ đạt GATE_LEVEL_PYTHON. Build exact, full PASS và tests PP không đáp ứng thêm điều kiện mới này. Chưa xử lý xong yêu cầu review; không đề nghị approve/merge hoặc đổi nhãn recovery level.

## Kết quả truy nguồn đã xác minh

[Evidence](evidence/review_followup.json) ghi version, SHA-256 source notebook đã tải, review/commit và kết quả HTTP. Chỉ đọc source như dữ liệu, không chạy notebook tải về.

1. Notebook public ahoirg/qcc-submit-verify-and-package v25 xác định invsqrt 4560ac0c được dựng từ fork generator Syed Asad Ali với bảng 64 hàng, 6 bit địa chỉ, 13 bit intercept và 7 bit slope; hai loader được tổng hợp lại, S4 bị đo bỏ rồi dựng lại trước inverse product, hold pass xử lý interleaved chain. Source notebook chỉ tìm và đóng gói binary invsqrt_k6c.kmb từ input, không chứa generator của fork.
2. Generator được notebook đó dẫn là ahoirg/qcc-invk6-k6c. API public trả HTTP 403 khi kiểm tra. Không cố vượt quyền truy cập; chưa có source/data của fork này trong checkout.
3. Atakan Aldemir quantum-circuits-iso-gap-dqi-h5 v20 đưa bước refit 33 góc từ 4560ac0c sang dcde7078. Source ghi generator/proof riêng không được truy cập. Hai notebook Atakan và portfolio Alex Chilton v155 cung cấp binary/refit/attribution; chưa cung cấp generator số học 64 hàng có thể dùng để dựng từ đầu.
4. Notebook giải thích của sheroleg v10 dùng mạch đã compile và phép đo/profile để giải thích, không thay thế source generator.
5. Source INV-51 trong repo và bundle invsqrt_source_zip cũ là nguồn số học thật nhưng khác phiên bản: bảng A/S/stored_slope có 128 hàng, target 321aff83, không phải target e46d90c3 của INV-66. Không được đổi tên wrapper INV-51 thành INV-66 hoặc coi hai generator tương đương vì cùng 46 qubit.

Các đoạn source tải về và archive gốc chỉ nằm trong scratch ignored, không đưa nguyên bundle/notebook/base64/binary vào runtime hay Git. Evidence JSON chỉ giữ nguồn/hash và kết luận truy nguồn.

## Bản đồ hiểu biết và phần còn thiếu

| Thành phần | Điều đã biết | Chưa đủ để phục hồi target |
| --- | --- | --- |
| Contract pha | Verifier yêu cầu exp(2*pi*i/sqrt(x)), khôi phục 22 bit x và scratch zero | Không suy ra được thuật toán chỉ từ contract |
| Normalize/root/residual | INV-51 có implementation số học, quản lý owner và HMR debt thật | Chưa chứng minh mapping và allocation của từng khối sang fork 64 hàng |
| Lookup coefficient | Fork được nguồn public mô tả là 64 hàng/6 address bits/13 intercept/7 slope | Giá trị đầy đủ, cách chọn/làm tròn và hai plan loader 27/29 AND chưa lấy được từ source fork |
| Product/inverse product | Lineage chỉ rõ retire/rebuild slope S4 với hai AND | Chưa có source cập nhật lifecycle, biểu thức Boolean và cleanup certificate của fork |
| Divider/phase | Có divider/phase source ở INV-51; target chứa 33 generic rotations | Chưa chứng minh các tham số/truncation/register của target giữ nguyên; cần model/correspondence |
| Finishing/refit | Refit góc Atakan và dead-write PP-005 đã nhận diện; PP-005 đã độc lập | Refit/PP không thay thế generator số học; hold-pass sửa cho interleaved chains chưa phục hồi |

Tên prefix/pre_phase/return_and_layout trong circuit.py hiện tại chỉ là vùng vị trí. Chưa được xem là hàm số học có invariant. Không sửa tên hoặc gom các dòng gate thành hàm để tự nhận ALGORITHM_RECOVERED.

## Kế hoạch làm lại và điều kiện chuyển tiếp

1. Nhận source/data fork 64 hàng có quyền sử dụng, hoặc phục hồi độc lập từng thành phần còn thiếu bằng phân tích dataflow/Boolean/số học. Không yêu cầu submission KMB mới; binary hiện có đã đủ cho đối chiếu.
2. Viết model số học cổ điển từ x đến pha: địa chỉ, hệ số, signed widths, phép nhân/chia, làm tròn/cắt cụt và thang fixed-point phải rõ. So model với execution trace và các điểm biên; không chỉ so cost/số qubit.
3. Viết builder từ các hàm số học và register có ý nghĩa, cộng helper/table thật sự cần. Giữ invariant input/output, measurement debt và correction; không dùng chuỗi cổng tuyến tính hoặc toàn mạch làm dữ liệu giả bảng hệ số.
4. Giữ finishing passes ở module PP tương ứng, pin source/data dependency trong checkout. Nếu cần PP mới, theo workflow PP và kiểm chứng độc lập, không chép implementation lẫn vào generator.
5. Commit source/config rồi build sạch từ đúng commit đã push, venv mới, cwd khác và audit dependency closure. Đối chiếu riêng toàn bộ 198590 bytes và SHA-256 e46d90c36d1beb3ce7731a3e0b5c3659b3cda7f5f290b73c6c34513d96c005b6. Không vá output bằng KMB gốc hoặc hạ tiêu chí khi mismatch.
6. Chỉ cập nhật reconstruction_level sau khi có generator/model/correspondence thực tế. Các run full cũ giữ source commit của chúng; mới build exact không được ghi thành run verifier mới. Sau đó mới gửi lại reviewer độc lập.

Hiện chưa có đầu vào để tái dùng trực tiếp fork 64 hàng; phục hồi độc lập từ low-level circuit vẫn là công việc chưa hoàn tất, không phải điều đã được chứng minh bất khả thi. Cần source public/được cung cấp của ahoirg/qcc-invk6-k6c để tránh tiếp tục suy đoán các thay đổi riêng chưa có căn cứ. PR giữ draft và trạng thái changes requested.
