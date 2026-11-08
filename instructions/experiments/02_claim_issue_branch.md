# 02 — Nhận Issue và branch cho hướng đã chọn

Áp dụng [quy tắc chung và ngữ cảnh](../README.md), AGENTS.md, CONTRIBUTING.md và
[workflow thử nghiệm](../../docs/EXPERIMENT_WORKFLOW.md).
Lấy thông tin từ chat/project/GitHub; không yêu cầu điền lại form.

## Ràng buộc và quyền thao tác

Tạo/nhận Issue trong phạm vi được giao, tạo branch `exp/<ID>-<slug>` của owner từ nhánh chính; chỉ sửa `src/<TRACK>/<ID>/DESCRIPTION.md` và dòng của ID trong `src/<TRACK>/EXPERIMENTS.md`. Được commit/push, mở/cập nhật draft PR; chưa viết code/config hoặc compile.

## Yêu cầu thực hiện

Nếu chưa có Issue, tạo Issue thật cho hướng đã chọn, gán owner, tạo branch riêng,
commit mô tả/mục lục, push và mở draft PR. Không yêu cầu người dùng cấp Issue URL mới.
Nếu người dùng đã giao tiếp tục/nhận một Issue có sẵn, xác minh owner và phạm vi rồi
dùng đúng Issue/ID/branch đó; bỏ thao tác tạo mới, vẫn nghiệm thu các mục còn lại.
Không tự nhận Issue của người khác hoặc tạo trùng chỉ vì chưa được gửi URL.

Trước khi tạo, kiểm tra Issues mở/đóng và PR đang mở. Nếu đã có cùng phạm vi
hoặc một người đang làm hướng trùng, báo xung đột để thống nhất lại; không
vẫn tạo Issue trùng hoặc tự nhận Issue của người khác. Xác định đúng repo
và nhánh chính từ Git, giữ nguyên các thay đổi ngoài phạm vi.

TITLE BẮT BUỘC:
[<PREFIX>-<SỐ ISSUE THẬT>] <Thao tác/thành phần> bằng <phương pháp>, <phạm vi thử>
PREFIX: invsqrt → INV; dqi → DQI; dfthcsos → DFT.

Title phải tự đủ nghĩa: phần xử lý nào, định thay đổi bằng cách nào và phần
phạm vi giúp phân biệt với hướng khác. Viết thành câu dễ đọc; không giữ các
dấu <...>, không chỉ ghi tên file hoặc "tối ưu baseline", không bịa mức cải thiện.

Do chưa có số trước khi tạo Issue, làm theo thứ tự:
1. Đọc templates/experiment.md trước khi soạn; xác định loại hướng và chuẩn bị
   tên mô tả/nội dung Issue theo đúng phần template tương ứng.
2. Tạo Issue mới với title tạm [PREFIX] <Tên mô tả>, lấy số và URL trả về thật.
3. Đặt ID = PREFIX-<số Issue>, cập nhật title thành [ID] <Tên mô tả>.
4. Tạo branch exp/<ID>-<ten-huong> từ nhánh chính đã đồng bộ khi workspace an toàn.
5. BẮT BUỘC viết src/<TRACK>/<ID>/DESCRIPTION.md dựa trên templates/experiment.md.
   H1 đúng nguyên title cuối của Issue. Chỉ giữ phần template của loại hướng
   đã chọn, điền đầy đủ và xóa các placeholder/comment hướng dẫn.

   Viết thật chi tiết: một thành viên/agent mới chỉ đọc DESCRIPTION và các
   nguồn được dẫn phải có thể triển khai solution mà không cần hội thoại này.
   Không chỉ liệt kê ý tưởng, chép tên các mục hoặc viết vài câu định hướng.

   - Tinh chỉnh: link file gốc/phiên bản, chỉ đúng hàm hoặc khối xử lý sẽ sửa,
     hành vi trước/sau, lý do, cách sửa từng bước và phần giữ nguyên.
   - Kết hợp: link từng file gốc/phiên bản, lấy khối nào từ mỗi nguồn, thứ tự
     ghép, dữ liệu/thanh ghi trao đổi và xử lý từng điểm không tương thích.
   - Ý tưởng mới: mô tả đầy đủ input/output, biểu diễn, thuật toán từng bước,
     công thức, điều kiện đúng, sai số và tài nguyên dự kiến.

   Với phần thay đổi/mới, nêu cụ thể công thức hoặc pseudocode khi cần,
   ý nghĩa tham số/độ rộng/scale, invariant, overflow/làm tròn/cắt cụt,
   compute/uncompute/sửa pha và trường hợp biên liên quan. Phân tích phần chi
   phí dự kiến giảm/tăng và cách kiểm chứng giả thuyết; phân biệt suy luận
   với kết quả đã đo. Không cần chép lại phần không đổi đã dẫn nguồn.

   Giải thích vai trò và ràng buộc tham số; việc chọn JSON config đầu tiên
   thuộc giai đoạn 03, chưa compile hoặc khẳng định setting tối ưu ở đây.
   Giả định chưa được chứng minh phải ghi rõ cùng cách kiểm tra; không bịa
   bằng chứng hoặc kết quả để lấp chỗ còn chưa biết.
   Điền phần chung của template: mốc đối chứng, dự đoán, tiêu chí ủng hộ/bác bỏ,
   điều kiện dừng và kế hoạch kiểm tra độc lập ứng viên cuối. Chưa có config/run
   thì ghi rõ phần dự kiến để hoàn thiện ở 03; không bịa kết quả hoặc SHA.
6. Thêm một dòng EXPERIMENTS.md: ID, title làm link tới DESCRIPTION, Issue URL.
   Đồng bộ body Issue từ phần dưới H1; đổi link tương đối thành URL thật.
7. Trước commit, đọc lại Issue từ GitHub và kiểm tra:
   - Prefix đúng TRACK; số trong ID đúng số Issue thật.
   - Title GitHub = H1 bỏ dấu '# ' = title hiển thị trong EXPERIMENTS.md.
   - Không còn placeholder; title nêu được thay đổi và phạm vi nhận việc.
   - Assignee đúng owner; link mô tả/Issue trỏ đúng hướng.
   - DESCRIPTION bám đúng loại trong templates/experiment.md, không còn
     placeholder; nêu đủ phần thay đổi, thuật toán, điều kiện đúng/đánh đổi
     để triển khai. Không bỏ phần mô tả chi tiết chỉ để tạo Issue nhanh.
   - Body Issue chứa đầy đủ nội dung DESCRIPTION dưới H1; không chỉ đăng
     một bản tóm tắt hoặc mỗi link tới file.
   Nếu sai, tự sửa rồi kiểm tra lại; không tuyên bố đã đồng bộ khi chưa đọc lại.
8. Commit phần mô tả/mục lục, push branch, mở draft PR liên kết Issue.

Chưa viết solution hoặc compile ở giai đoạn này. Kết thúc báo nguyên title
đã đọc lại, ID, owner, Issue URL, branch, draft PR URL, commit và phạm vi đã nhận.
Không merge hoặc đóng Issue. Nếu không tạo/đọc lại được qua GitHub, báo phần
chưa làm; không tạo số/URL giả và không khẳng định kiểm tra đã đạt.
Cuối lượt liệt kê file thực sự đã tạo/sửa kèm link thật để người dùng kiểm tra thủ công.

## Danh sách nghiệm thu

- [ ] Issue thật, ID/prefix/số/owner đúng; không trùng hướng đang có người nhận.
- [ ] Title Issue = H1 DESCRIPTION = title mục lục; body Issue đủ nội dung dưới H1, link GitHub thật đã đọc lại.
- [ ] DESCRIPTION đủ chi tiết để triển khai, có kế hoạch kiểm chứng/điều kiện dừng và nguồn kế thừa có phiên bản.
- [ ] Commit mô tả/mục lục, branch và draft PR thật đã được xác minh.

Ví dụ title cuối (số chỉ minh họa, không phải Issue đã tạo):

- `[INV-123] Giảm độ rộng tích Horner bằng precision riêng từng tầng, giữ nguyên bước Newton`.
- `[DQI-124] Giảm chi phí EEA bằng giới hạn số bước, đo tỷ lệ lỗi giải mã`.
- `[DFT-125] Giảm chi phí QROM bằng quét batch size, giữ bảng góc 12 bit và factorization`.
