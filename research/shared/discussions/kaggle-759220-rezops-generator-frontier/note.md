# RezOps 759220 — Thu hẹp invsqrt, cutoff DQI và mã hóa word hóa học

Status: draft
Track: shared
Source: https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/759220
Version: snapshot 2026-11-14; bài 3554987 và bình luận 3554988

- Người đăng: `manwithacat`; bài tự nhận do agent RezOps dùng Claude soạn. Ngày đăng 14/11/2026, không coi đây là nguồn độc lập với hệ thống RezOps chạy các phép đo được báo.
- Từ khóa: giới hạn qubit, compute/measure/rebuild, table loader, extractor cutoff, retained products, coded angle words, phân phối lỗi.
- Bản nguồn đọc được: [snapshot diễn giải](source.md), [metadata và hash](source.json). Mọi dẫn S1–S7 dưới đây chỉ các mục của snapshot; chúng ghi rõ mục gốc trong [bài 3554987](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/759220#3554987).
- Đã đọc toàn bộ văn bản bài chính và một bình luận trả về từ API công khai. Không mở ảnh, viewer, notebook, dataset, proof hoặc log mà bài dẫn; không chạy chấm. Phản hồi sau thời điểm truy cập không thuộc coverage.

## Câu hỏi và bối cảnh

Bản tin theo dõi ba bài từ 12/11 18:30 đến 14/11 10:30 UTC: phần nào thực sự làm giảm tài nguyên, lợi ích nào chỉ nằm ở draw đang xét, và có thể chuyển kỹ thuật giữa các kiến trúc hay không? Bản tin nối tiếp [RezOps 757068](../kaggle-757068-rezops-public-frontier/note.md), nhưng các artifact/phiên bản đã đổi nên không dùng số cũ làm đối chứng mặc định.

Cần phân biệt bốn loại căn cứ trong bài: quan sát leaderboard của RezOps; kết quả tác giả notebook tự báo; kết quả RezOps nói đã chạy lại verifier gốc ở default salt; và ước tính trung bình 48 draw hoặc dự phóng điểm tổng. Chúng đều là **phát biểu nguồn bên ngoài**, trừ những kết quả project dẫn riêng bên dưới. Không lấy nhãn chạy lại verifier trong bài làm bằng chứng nhóm đã chạy lại.

Theo mục 2 ([S2](source.md#s2--mục-2-ba-mốc-do-rezops-báo-đã-kiểm-lại)), ba mốc là:

| Track | Artifact/phiên bản nguồn | Width Q | Chi phí nguồn báo | Giới hạn diễn giải |
| --- | --- | ---: | ---: | --- |
| invsqrt | Özdağ v25, `4560ac0c017b` | 46 | 78,765.64 | RezOps báo kiểm lại; chưa đối chiếu artifact/proof |
| dqi | Areeb Ali v8, `821bf8d157c0` | 889 | 3.6095 × 10^11 | Trung bình 48 draw của RezOps, có shot lỗi |
| dfthcsos | prvsiyan v48, `0b2e60550a38` | 427 | 2.95131 × 10^8 | RezOps báo kiểm lại; chưa đánh giá sai số/rounding |

Các hash trên chỉ là tiền tố do nguồn hiển thị. Dự phóng 27.27838 từ ba mốc không phải điểm leaderboard quanh 27.297. Các xếp hạng, ngưỡng huy chương, dự báo giải thưởng trong S1 là bối cảnh thời điểm chụp; không dùng làm căn cứ lựa chọn thuật toán hay xác nhận luật cuộc thi.

## Các phương án và lập luận

| Phương án | Cơ chế và lập luận nguồn | Điều kiện / phản biện / rủi ro | Căn cứ đã đọc |
| --- | --- | --- | --- |
| Generator invsqrt 46 qubit | Root tại chỗ, bảng hệ số, product/divider; đo bỏ các dây ở đỉnh width rồi dựng lại và trả pha. Đổi gate count lấy width thấp hơn. | Phải trả đúng input vật lý, scratch và pha mọi nhánh. Claim proof toàn miền/transcript do RezOps báo, chưa kiểm tra proof. | Mục 3 invsqrt; [S3](source.md#s3--mục-3-invsqrt-generator-46-qubit-và-biến-thể-bảng-64-hàng) |
| Bảng hệ số 64 thay 128 hàng | Hai loader được tổng hợp lại, còn 27 + 29 AND thay cho 56 + 70; đo/dựng lại một bit slope với hai AND. Nguồn báo giảm 47 Toffoli tĩnh và khoảng 1.74% chi phí. | Không suy ra độ chính xác của bảng mới từ số hàng/AND; cần proof sai số và phase cleanup đúng phiên bản. | Mục 3 invsqrt, Özdağ v25; S3 |
| DQI cutoff 18 và 241 tích giữ lại | Bỏ xử lý một số mẫu hiếm, đồng thời tái dùng tích để giảm Toffoli ở cùng width. | Tăng xác suất shot lỗi; kết quả draw cụ thể và chi phí kỳ vọng khác nhau. Cutoff là tham số của decoder nguồn, chưa có định nghĩa đủ để áp vào decoder khác. | Mục 3 DQI; [S4](source.md#s4--mục-3-dqi-cutoff-và-tích-giữ-lại) |
| Coded words và refit hóa học | Đổi cách mã hóa word góc để 15 loader/pass còn tổng 4,038 Toffoli thay 4,089; refit trọng số sau đó giảm chi phí. | Giảm loader chưa đủ: phải kiểm tra giải mã góc, precision, λ hiệu dụng và sai số Hamiltonian sau lượng tử hóa. Nguồn không đưa chứng minh đầy đủ trong thread này. | Mục 3 hóa học; [S5](source.md#s5--mục-3-hóa-học-coded-words-và-refit-trọng-số) |
| Rank 173 cho cặp tích GF(2^24) | Ghép đánh giá của hai tích có cấu trúc để thay khối rank/Toffoli 176, lặp 182 lần; nguồn dẫn báo giảm 546 Toffoli tĩnh. | Chỉ hợp cấu trúc toán hạng của decoder cũ khoảng 392k; chính bản tin nói decoder mới không có điều kiện đó. Tìm ghép thứ ba không có nghiệm trong 16,704 ứng viên. | Mục 4, tóm lược thread 759048; [S6](source.md#s6--mục-4-và-5-giới-hạn-chuyển-giao-và-kết-quả-âm) |

### Invsqrt: phân biệt width, charge và bằng chứng pha

Nguồn báo generator Ali v12 `321aff836362` có Q=46, charge Toffoli-like 1,742.67, chi phí 80,162.73; mốc cũ Q=62 có charge 1,508.96. Tính minh họa từ các số đã làm tròn cho `(46 × 1742.67)/(62 × 1508.96) ≈ 0.857`: giảm width có thể bù tăng charge. Đây là phép tính giải thích của nhóm, không phải chạy verifier mới hay công thức tổng quát cho mọi track.

Khung lý giải pha của nhóm: nếu dây phụ chứa `t=f(z)` và đo ở cơ sở X nhận bit `m`, nhánh còn lại có thừa số `(-1)^(m f(z))`. Dựng lại đúng giá trị cổ điển mà không hoàn trả thừa số này chưa đủ. Phải theo dõi cả thời điểm tái dựng, điều kiện phép sửa pha, quyền sở hữu dây và scratch. Bản tin nêu cơ chế này, còn chứng minh cụ thể phải theo generator/certificate của đúng artifact. Không dùng sự giống nhau về số qubit/cổng làm bằng chứng tương đương mạch.

Nguồn còn có refit góc với chi phí 78,765.51 và 78,765.55, thấp nhẹ hơn file được chọn 78,765.64; RezOps giữ file sớm theo ngưỡng hòa riêng. Vì vậy mốc trong bảng là lựa chọn của tác giả, không phải kết luận cực tiểu. Mô hình giá phần cứng trong viewer chỉ là minh họa theo giả định; không đưa vào kết luận tài nguyên của project.

### DQI: PASS, shot lỗi và kỳ vọng là ba khái niệm khác nhau

Nguồn báo cả 48 draw của cutoff 18 PASS, đồng thời 18 draw có một hoặc hai shot lỗi. Hai mệnh đề không mâu thuẫn khi verifier chấp nhận tỷ lệ lỗi dưới ngưỡng rồi phạt chi phí theo ước lượng lỗi. Nguồn đưa thêm xác suất lỗi khoảng `7.7 × 10^-7` mỗi shot, không phải tổng xác suất lỗi decoder. Với 102,400 shots/draw, phép nhân minh họa cho kỳ vọng **phần tăng thêm** là `0.078848` shot/draw; không dùng nó thay phân phối thực nghiệm của 48 draw.

Đối chiếu chỉ đọc [verifier DQI tại fe0169d](https://github.com/nhphan0505/verifiable-quantum-circuit/blob/fe0169da6404eac00149482b096b5ad9a692022d/verifiers/dqi/verify_submission_dqi.py): score có dạng `R(ε_plus) Q² T`, với `ε_plus` là cận Clopper–Pearson một phía từ shot lỗi, mức tin cậy theo `log2_delta`; `T` là chi phí Toffoli mà verifier dùng. Trong biểu thức của verifier, `R(ε)=ln(2)/[-ln(1/2+2√ε)]`, và điều kiện chấp nhận là `ε_plus < 1/16`. Vì thế thay cutoff có thể giảm T nhưng tăng hệ số phạt. Ở đây chỉ dùng để giải thích ngữ nghĩa; chưa đối chiếu 48 cấu hình/draw ngoài nguồn, chưa tính lại score cho artifact cutoff.

### Các kết quả âm và ý kiến chưa được xác nhận

Giữ nguyên giới hạn từ mục 5/S6: RezOps chưa tìm được rank 11 cho một khối DQI 12 Toffoli, chưa tái tạo được cải thiện loader v2 từ input v1 của maoxin123, không tìm được điểm đo-bỏ trên mạch DQI được chọn và không cải thiện bằng ghép nhiều đoạn các mạch invsqrt 62 qubit. Không có mô tả không gian tìm kiếm đủ để biến các thất bại này thành định lý bất khả thi.

Bình luận [3554988](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/759220#3554988) chỉ đùa về lý do bản tin trễ, không kiểm chứng hay phản bác kỹ thuật. Trong phạm vi một bình luận nhận được, không thấy tranh luận kỹ thuật; chưa có căn cứ gọi các nhận định của RezOps là đồng thuận cộng đồng. Kết luận mục 6 rằng sửa generator có triển vọng hơn sửa output là ý kiến định hướng của tác giả.

## Kết luận hiện tại

Nguồn có ích để phân biệt ba kiểu đánh đổi: width–charge của invsqrt, gate count–rủi ro thống kê của DQI, và loader–sai số/refit của hóa học. Bài cho mốc công khai và đường dẫn truy vết, nhưng không chứa đủ source/proof/log để tự tái lập các biến thể mới chỉ từ thread. Tuyên bố proof toàn input/transcript và 48-draw PASS giữ nhãn **nguồn báo**, không nâng thành kết quả project.

Liên hệ đã kiểm tra ở project: [INV-51 DESCRIPTION](../../../../src/invsqrt/INV-51/DESCRIPTION.md) và [full engine run lịch sử](../../../../results/invsqrt/INV-51/reconstructed/full/20261113T184831Z-local-full-b0043d/verifier.json) ghi 46 qubit, 80,162.73214111096 và hash đầy đủ `321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177`. Nó khớp tiền tố/chi phí Ali v12 trong bài; **không** xác nhận biến thể bảng 64 hàng `4560ac0c017b`. Đối chiếu ở main `fe0169da6404eac00149482b096b5ad9a692022d`; không tạo run mới trong lần đọc này.

## Hypothesis đề xuất và kiểm chứng tiếp

Các mục sau là suy luận của nhóm, chưa nhận Issue hoặc triển khai:

1. Nếu cùng generator INV-51 còn dư sai số, bảng 64 hàng có thể giảm tài nguyên loader. Trước nhận hướng, cần đọc source/certificate đúng version Özdağ, xác minh hash đầy đủ, so error budget và cleanup với INV-51. Đối chứng dùng cùng verifier/runtime/profile; chỉ ủng hộ nếu chi phí giảm và đủ bằng chứng độ chính xác/pha, không chỉ giảm static AND.
2. Cutoff DQI phải được đánh giá bằng chi phí có phạt trên draw độc lập chưa dùng chọn cutoff. Cần biết định nghĩa extractor cutoff, phân phối đầu vào và toàn bộ bảng failed shots; bác bỏ lợi ích nếu mean có phạt hoặc rủi ro xác nhận kém hơn đối chứng. Không áp trực tiếp rank 173 nếu thiếu quan hệ toán hạng được nêu trong S6.
3. Với hóa học, cần xác minh cả word decode lẫn refit sau làm tròn trước khi đo lợi ích coded-word loader. DFT-BASELINE hiện có chỉ là liên hệ thành phần; số 4,038 trong bài chưa phải điểm hay kế hoạch thay thế đã được nhóm chấp nhận.

Trước thực nghiệm phải kiểm tra lại [mục lục invsqrt](../../../../src/invsqrt/EXPERIMENTS.md), [DQI](../../../../src/dqi/EXPERIMENTS.md), [DFTHCSOS](../../../../src/dfthcsos/EXPERIMENTS.md) và Issues/PR hiện tại để không trùng hướng. Note này không cấp quyền thay đổi code.

## Liên kết triển khai và câu hỏi còn mở

- INV-51 đã có [Issue 51](https://github.com/nhphan0505/verifiable-quantum-circuit/issues/51) và [PR 55](https://github.com/nhphan0505/verifiable-quantum-circuit/pull/55); không tạo Issue/branch thuật toán mới trong bước tài liệu.
- Chưa biết hash đầy đủ và bằng chứng proof của bảng 64 hàng; chưa đọc chương trình tính xác suất cutoff, 48-draw salts/logs hay audit hóa học. Chưa kiểm tra guide, giải thưởng, viewer hoặc license từng notebook được bài dẫn. Bài nói các notebook/dataset liên quan Apache-2.0; không từ đó suy ra giấy phép của chính nội dung forum.
- Tự rà bước 3: đã đối chiếu số liệu/citation với bài chính và bình luận, tách rõ prefix/full hash, source claims/project results, PASS/shot lỗi và kỳ vọng/từng draw; kiểm tra metadata/coverage/hash và phạm vi file. Bước này chưa thay review độc lập bước 4. Giữ `Status: draft` tới khi reviewer độc lập kiểm tra trực tiếp nguồn và note.
