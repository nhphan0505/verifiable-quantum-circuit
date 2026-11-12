# Instructions cho coding agent

Đọc AGENTS.md và CONTRIBUTING.md, chọn đúng luồng rồi đọc từng bước được giao.
Đây là instructions trong repository, không phải mẫu để chép vào chat hay điền form.
Các ký hiệu TRACK, OWNER, ID, PR, SOURCE_DIR dưới đây là tên thông tin cần xác định,
không phải tham số bắt buộc người dùng phải truyền trong mỗi tin nhắn.

| Luồng | Instructions | Branch được sửa | Issue |
| --- | --- | --- | --- |
| Thử nghiệm | [experiments](experiments/README.md) | `exp/<ID>-<slug>` của owner | Bắt buộc có Issue thật trước triển khai |
| Tái dựng submission | [decompiler](decompiler/README.md) | Scratch riêng bước 1–3; `exp/<ID>-<slug>` của owner từ bước 4 | Bắt buộc có Issue thật trước viết solution |
| Đọc paper | [papers](papers/README.md) | `research/<username>` của owner | Tùy chọn |
| Đọc discussion | [discussions](discussions/README.md) | `research/<username>` của owner | Tùy chọn |

Paper và discussion có chuỗi bước riêng; có thể cùng thuộc một đợt research/PR
của thành viên. Dùng chat/agent riêng giữa tài liệu và thử nghiệm, worktree riêng
khi đồng thời; không chuyển branch trong workspace đang có công việc chat khác.
Agent thử nghiệm chỉ đọc note ready đã merge; quyền đọc project không bỏ giới hạn này.
Templates trong `templates/research/`, `templates/experiment.md`, `templates/solution.py`
và `templates/run/` vẫn là mẫu đầu ra, không phải mẫu tin nhắn.

## Nhận lệnh ngắn và dùng ngữ cảnh

1. Với lệnh như **“thực hiện các bước 1 2 3”**, dùng luồng đang làm trong chat.
   Nếu chưa rõ luồng, hỏi chọn experiments, decompiler, papers hay discussions trước thao tác phụ thuộc.
   Số bước trong instructions là số để giao agent; 12 mục trong CONTRIBUTING.md là
   phần giải thích quy trình, không phải bảng số bước cho lệnh ngắn.
2. Lấy dữ kiện đã xác định từ chat trước; đối chiếu Git, file và GitHub thật trước
   khi dùng: repo/base branch, owner, track, hypothesis/Issue/ID/branch, nguồn/phiên bản,
   config/run, PR và review/SHA. Thông tin thật mới hơn phải được xử lý nếu mâu thuẫn chat.
   Không yêu cầu người dùng điền lại thông tin đã biết và còn đúng.
3. Tra thông tin thiếu bằng công cụ sẵn có: branch/remotes, DESCRIPTION, source.json,
   mục lục, results, tài khoản GitHub đăng nhập, Issue/PR liên quan. Tên/email Git
   không tự chứng minh GitHub username hoặc owner; không tự đổi danh tính/tài khoản.
4. Nếu không tra được hoặc có nhiều khả năng, hỏi ngắn đúng phần thiếu, ví dụ:
   “GitHub username của owner là gì?”, “Bạn muốn xử lý PR #7 hay #8?”, hoặc
   “Chọn hypothesis nào trong các đề xuất?”. Không đoán owner, PR, nguồn hay quyền.
   Vẫn làm phần đọc/kiểm tra độc lập an toàn trong lúc chờ, dừng thao tác phụ thuộc.
   Config, phạm vi đọc và track tài liệu thường lệ do agent tự chọn theo bước tương ứng.
5. Thực hiện các bước đã giao theo thứ tự, kiểm tra điều kiện đầu vào và nghiệm thu
   từng bước. Giao nhiều bước bao gồm quyền thao tác được liệt kê ở các bước đó;
   không hỏi lại quyền tạo Issue/branch, commit/push, PR hay merge đã được giao.
   Chỉ đọc instructions không cấp quyền thực hiện; không tự chạy bước chưa giao.
6. Nghiệm thu đạt thì chuyển bước kế tiếp đã giao, không dừng chỉ để xin xác nhận
   lại. Điểm cần dữ kiện/quyết định còn thiếu, chấm notebook local, reviewer độc lập,
   hoặc review/check chưa đạt vẫn là điều kiện chặn. Báo bước đã xong, đang chờ và
   còn lại; tiếp tục phần đã giao khi điều kiện được đáp ứng, không bỏ qua nghiệm thu.
   Tác giả không tự đóng vai reviewer độc lập dù được giao cả chuỗi bước.
7. Khi đổi chat/model, khôi phục từ repository/GitHub và thông tin bàn giao; không
   giả định chat mới nhớ chat cũ. Chỉ hỏi dữ kiện chưa thể khôi phục; không tạo lại
   Issue/PR/run đã có hoặc chạy lại công việc đã có bằng chứng phù hợp.

## Quy tắc và nghiệm thu chung cho mọi bước

- Trước sửa: xác minh branch/working tree/owner, giữ thay đổi của người dùng.
  Chỉ sửa file/phạm vi liệt kê trong bước; hướng dẫn/checker/verifier là hạ tầng,
  cần nhiệm vụ riêng. Không sửa log/run cũ, token, dữ liệu gốc hoặc công việc người khác.
- Trước nhận việc: kiểm tra Issues mở/đóng và PR mở để tránh trùng. Nếu không truy cập
  được GitHub, báo chưa xác minh, không khẳng định không trùng hoặc tạo số/URL giả.
- Điều kiện đầu vào không đạt: báo cụ thể, không đánh dấu bước hoàn tất. Chạy checks
  trước PR theo [REPOSITORY_CHECKS](../docs/REPOSITORY_CHECKS.md); không tuyên bố CI
  hoặc PASS nếu chưa có bằng chứng. Không bypass rule GitHub.
- Cuối lượt: liệt kê bước đã nghiệm thu/chưa xong, file có link thật, branch/commit/PR,
  checks thực sự đã chạy, giới hạn và bước tiếp. Giữ ngữ cảnh các giá trị đã xác minh
  trong chat để lệnh sau không cần lặp tham số; bằng chứng dài hạn nằm ở file/Git/GitHub.
