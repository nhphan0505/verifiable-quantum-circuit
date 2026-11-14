# Quy trình cộng tác từ ý tưởng đến hoàn thành

**Luồng chấm hiện tại:** dùng kickmix-engine 0.6.0, chỉ có `smoke` và `full`.
Notebook tự nhận diện OS; Windows dùng WSL. Các mục/run `dev_5min` bên dưới
là hồ sơ của luồng cũ, không còn là lựa chọn cho lượt chấm mới. Xem docs/LOCAL_GRADING.md từ root repo.

Một hướng nghiên cứu tương ứng một GitHub Issue, một branch và một thư mục source. Một hướng có thể thử nhiều config và nhiều lần chấm. Quy trình khép kín:

**Chuẩn bị → kiểm tra hướng cũ → nhận Issue → tạo branch → mô tả/code/config → commit nguồn → dựng/chấm → lưu và phân tích → commit kết quả → thử tiếp hoặc PR → review/merge → đóng Issue.**

Instructions cho coding agent: [instructions/README.md](instructions/README.md).

## Hai luồng cộng tác

- **Tái dựng submission (decompiler):** [instructions](instructions/decompiler/README.md).
  Lối vào luồng thử nghiệm từ KMB/ZIP, dùng KMX để phân tích, kiểm tra exact bằng
  bytes/SHA-256 rồi viết Python/DESCRIPTION. Không cần hypothesis ban đầu; dùng
  số bước riêng và giữ các điều kiện Issue, provenance, chấm local, review.
- **Nghiên cứu thử nghiệm:** [agent](docs/EXPERIMENT_WORKFLOW.md),
  [instructions](instructions/experiments/README.md); thực hiện 12 bước bên dưới.
- **Đọc tài liệu:** [agent](research/AGENTS.md), [paper](instructions/papers/README.md) và [discussion](instructions/discussions/README.md).
  Tạo/tiếp tục branch `research/<username>` → thêm nhiều resource → viết note →
  review độc lập bước 04 → tác giả hoàn thiện và merge PR vào main ở bước 05. Issue cho nguồn
  là tùy chọn; không có yêu cầu một nguồn một branch/Issue.
- Dùng agent/chat riêng, worktree/workspace riêng khi chạy đồng thời. Branch research
  thuộc một thành viên, chỉ sửa tài nguyên và mục lục research; hạ tầng cần nhiệm vụ riêng.
  Workflow experiment vẫn một Issue/branch/owner và không phụ thuộc việc nhóm đang đọc tài liệu.
- Note ready đã review và merge là điểm nối. Agent nghiên cứu chỉ đọc note trong
  research, vẫn tự phân tích code/verifier/results; không đọc nguồn hoặc tự viết note.
- Agent tài liệu được đọc nguồn nhưng không sửa thí nghiệm, điểm hoặc chạy chấm.
  Luồng tài liệu không cần compile/provenance build. Review bước 04 đủ làm căn cứ để
  tác giả merge khi checks đạt; không cần họp nhóm hoặc đăng approval GitHub riêng.
  Vẫn tuân thủ rules GitHub thực tế, không bypass nếu repo yêu cầu approval.
- CI yêu cầu mỗi thư mục resource có note.md không rỗng; PDF/link-only chỉ lưu nháp,
  chưa được merge. Chạy scripts/check_research_notes.py trước bàn giao PR.

Giao agent bằng số bước theo [instructions](instructions/README.md), ví dụ
“thực hiện các bước 1 2 3” trong luồng đang làm; không cần chép prompt hay truyền lại
tham số đã biết. Agent tra chat/project/GitHub, chỉ hỏi phần thiếu hoặc mơ hồ.
Mỗi bước có ràng buộc file/branch/quyền, yêu cầu đầu ra và danh sách nghiệm thu.
Các mục 1–12 dưới đây giải thích quy trình experiment; số dùng trong lệnh giao việc
là số ở instructions của luồng tương ứng.

## 1. Chuẩn bị workspace

Nếu đã có workspace, đồng bộ nhánh chính khi working tree an toàn; giữ nguyên thay đổi chưa commit. Khi vừa clone, làm các bước sau.


Mỗi thành viên dùng một workspace riêng. Chuẩn bị Git, Python **3.13** và quyền
truy cập repo. Các lệnh dưới đây chạy bằng **PowerShell trên Windows**.

**1. Clone và mở thư mục project** (nếu đã clone thì chỉ mở thư mục đó):

```powershell
git clone https://github.com/nhphan0505/verifiable-quantum-circuit.git GQA
cd GQA
```

**2. Tạo môi trường Python và cài dependency local:**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
.\.venv\Scripts\python.exe -m pip check
```

Dùng trực tiếp Python trong `.venv` như trên, không cần activate. Nếu không có
lệnh `py`, dùng `python --version` xác nhận đúng 3.13 rồi chạy `python -m venv .venv`.
Notebook local dùng cùng bộ dependency trong requirements.txt và các package giao diện trong requirements-notebook.txt.

**2b. Cài engine chấm (bắt buộc để chạy notebook):**

Giữ `kickmix==1.0.0` trong `.venv` để compile; chấm dùng `kickmix-engine==0.6.0`.
Notebook tự nhận diện OS và chỉ có hai mode `smoke`/`full`.

- **Windows:** giữ kernel `.venv` Windows. Nếu chưa có WSL Ubuntu, mở PowerShell
  Administrator và chạy `wsl --install -d Ubuntu`, mở Ubuntu để hoàn tất tạo tài khoản,
  rồi chọn `wsl --set-default Ubuntu`. Trong terminal Ubuntu, vào cùng project
  (ví dụ `cd /mnt/d/GQA`), tạo `.venv-engine` bằng Python 3.13 Linux và cài requirements
  cùng wheel Linux của engine. Không dùng `.venv` Windows từ WSL.
- **Linux/macOS:** tạo `.venv` bằng `python3.13 -m venv .venv`, cài
  `requirements-notebook.txt` và wheel engine phù hợp vào chính `.venv`; notebook dùng
  kernel này. Wheel phát hành hỗ trợ Linux x86_64 và macOS Apple Silicon; macOS Intel
  cần build và kiểm thử riêng. Từng generator có thể có giới hạn OS, xem hướng dẫn của ID.

Lệnh cài Python trong WSL, wheel cố định phiên bản, kiểm hash và `doctor` nằm trong
[hướng dẫn chấm local](docs/LOCAL_GRADING.md#engine-chấm-mặc-định).
Notebook báo lỗi nếu thiếu WSL/engine, không quay về trình chấm cũ.

**3. Bổ sung dữ liệu ban tổ chức:**

Lấy bộ dữ liệu gốc của cuộc thi hoặc từ người phụ trách nhóm, đặt theo [DATA.md](DATA.md).
Git không chứa dataset lớn, submission mẫu, `.venv` hoặc artifact đã compile.
Để chấm task 3 local cần:

- `verifiers/dfthcsos/FeMoCo76o113e.fcidump`
- `verifiers/dfthcsos/FeMoCo76o113e.fixed_shifts.npz`

Dựng baseline task 3 còn cần `sample_submission/dfthcsos/submission.npz`.
Các file mạch mẫu dùng để đối chiếu khi cần; Windows dùng package pip Kickmix,
không cần binary Linux `kickmix.so` để compile.

**4. Kiểm tra workspace và mở notebook local:**

```powershell
.\.venv\Scripts\python.exe scripts/check_repo.py
```

Mở `notebooks/GQA_Grade_Submission.ipynb` trong VS Code/Jupyter, chọn kernel
`.venv`. Chọn TRACK, MODE (`smoke` hoặc `full`), EXPERIMENT_ID, CONFIG_NAME trong dropdown, điền OWNER rồi chạy cell chấm; artifact được đọc
từ project và results lưu đúng chỗ. Xem [chấm local](docs/LOCAL_GRADING.md).

**5. Chuẩn bị coding agent để bắt đầu nghiên cứu:**

Mở workspace trong coding agent, yêu cầu đọc [AGENTS.md](AGENTS.md) và quy trình trong tài liệu này. Kiểm tra Git đã có tên/email commit của chính
thành viên và công cụ GitHub của agent đã đăng nhập đúng tài khoản, có quyền
thao tác repo. Không dùng chung tài khoản tác giả/reviewer.

```powershell
git config user.name
git config user.email
git status --short --branch
```

Nếu thiếu tên/email, cấu hình danh tính Git của mình trước khi commit.
Bắt đầu bằng [bước 01 — tìm hypothesis](instructions/experiments/01_find_hypothesis.md),
sau đó làm theo [instructions từng bước](instructions/experiments/README.md).
Agent sẽ tạo branch, code/config và compile artifact khi được giao hướng;
người clone mới chưa có sẵn artifact baseline trong máy.

## 2. Kiểm tra các hướng đã có

Chọn TRACK: `invsqrt`, `dqi` hoặc `dfthcsos`. Đọc `src/<TRACK>/EXPERIMENTS.md`, các DESCRIPTION liên quan, SCORES.md và cả GitHub Issues đang mở/đã đóng.

Xác định mình đang tinh chỉnh một hướng, kết hợp các hướng hay đề xuất ý tưởng mới. Kiểm tra cả những hướng đã thất bại để không lặp lại. Nếu chỉ khác setting trong cùng phạm vi, phối hợp trên Issue hiện có thay vì tự tạo hướng trùng. Nếu phạm vi giao nhau với người đang làm, thống nhất ranh giới trước khi code.

## 3. Tạo hoặc nhận GitHub Issue

Nếu chưa có Issue cho hướng, tạo bằng [mẫu Issue](.github/ISSUE_TEMPLATE/experiment.md), nêu giả thuyết và phạm vi dự kiến. Nếu Issue đã có nhưng chưa ai nhận, nhận chính Issue đó. Gán một owner chính và chuyển sang `claimed` trên Issue/project board.

ID lấy theo số Issue: `INV-123`, `DQI-124`, `DFT-125`. Sau khi có số, đổi title thành `[<ID>] <Tên hướng>`. Không tự cấp số khi đã dùng GitHub; `*-BASELINE` dành riêng cho các baseline gốc.

Tiêu đề phải đọc là hình dung được phần xử lý, phương pháp và phạm vi thử để nhóm phân công. Ví dụ:

- `[INV-123] Giảm precision các tích Horner, giữ nguyên bước Newton và đa thức baseline`.
- `[DQI-124] Giảm số bước EEA và đo đánh đổi giữa Toffoli với tỷ lệ lỗi giải mã`.
- `[DFT-125] Quét batch size QROM, giữ nguyên bảng góc 12 bit và factorization`.

Không dùng title chung như “tối ưu baseline”, “cải tiến v2”, tên file đơn lẻ hoặc mức cải thiện chưa đo. Các ví dụ trên chỉ minh họa cách đặt tên, không phải Issue đã tạo.

Khi nhóm chưa đưa dự án lên GitHub, thống nhất ID và người phụ trách trực tiếp; cột Issue ghi “Chưa tạo”, không tự tạo URL giả.

## 4. Tạo branch cho hướng

Tạo branch từ nhánh chính đã đồng bộ, ví dụ `exp/INV-123-horner-precision`. Một thành viên không tự sửa source/config của hướng đang có người khác phụ trách nếu chưa thống nhất.

Có thể push branch và mở draft PR sớm, liên kết Issue để nhóm thấy đang có người làm. Push/commit không có nghĩa đã hoàn thành hoặc đã merge; để Issue mở trong lúc thử nghiệm.

## 5. Viết mô tả, implementation và config

Tạo cấu trúc:

```text
src/<TRACK>/
  EXPERIMENTS.md
  SCORES.md
  <ID>/
    DESCRIPTION.md
    solution.py
    configs/
      <config-name>.json
```

### Mô tả ý tưởng

Viết DESCRIPTION.md theo [mẫu mô tả](templates/experiment.md), đủ chi tiết để thành viên khác có thể triển khai ý tưởng. H1 trùng nguyên văn title GitHub Issue. Phần dưới H1 dùng làm description của Issue, với nội dung theo loại:

| Loại | Nội dung cần viết |
| --- | --- |
| Tinh chỉnh một phương án | Link file gốc, sửa phần nào, vì sao sửa, cách thực hiện và đánh đổi |
| Kết hợp nhiều phương án | Link từng file gốc, lấy phần nào từ mỗi phương án, cách ghép và xử lý chỗ không tương thích |
| Ý tưởng mới | Mô tả đầy đủ thuật toán, công thức, điều kiện đúng, sai số và tài nguyên dự kiến |

Với hướng kế thừa, tập trung vào phần thay đổi thay vì chép lại toàn bộ baseline. Dẫn link source và commit/permalink hoặc hash để xác định phiên bản. Baseline gốc có hash tại data_manifest.json; giữ attribution và giấy phép khi kế thừa code.

Thêm một dòng vào EXPERIMENTS.md gồm ID, title làm link trực tiếp tới DESCRIPTION.md và link Issue. File mô tả trong repo là bản chuẩn; đồng bộ title và nội dung Issue khi thiết kế thay đổi. Khi dán description lên Issue, đổi link tương đối thành URL GitHub tương ứng để người đọc mở được file. Không cần lặp H1 trong body Issue.

Trước khi thử, điền phần kế hoạch kiểm chứng trong DESCRIPTION: mốc đối chứng
source/config/commit và run có điểm nếu đã có; dự đoán; tiêu chí ủng hộ/bác bỏ
hypothesis; điều kiện dừng hoặc giới hạn số vòng/tài nguyên. Hoàn thiện tham số ở
giai đoạn triển khai trước compile/chấm. Nếu đổi tiêu chí sau khi thấy kết quả,
ghi lý do để phân biệt với dự đoán ban đầu.

### Implementation và setting

Viết solution.py theo DESCRIPTION.md. Đầu mỗi file Python có docstring chi tiết theo [mẫu](templates/solution.py), giải thích implementation, cách chạy, điều kiện đúng và sai số. Giữ nguyên verifier và submission mẫu của ban tổ chức.

Tham số được đọc từ `configs/<config-name>.json` ngay trong thư mục của hướng; đường dẫn được resolve để từ chối config của hướng khác hoặc symlink ra ngoài. TRACK/ID và output mặc định suy ra từ vị trí `solution.py`, không hard-code ID baseline. Một setting là một JSON; không tạo file Python mới chỉ để đổi precision, batch size hoặc tham số khác trong cùng hướng. Nên dùng tên config ổn định, dễ phân biệt như `balanced`, `low_precision`; nếu đổi nội dung cùng tên phải có commit mới để phân biệt phiên bản.

## 6. Commit nguồn trước khi dựng và chấm

**Commit DESCRIPTION.md, solution.py, JSON config và mục lục liên quan trên branch của hướng trước khi dựng artifact.** Ví dụ commit: `INV-123: implement Horner precision sweep`.

Lấy SHA nguồn:

```powershell
git rev-parse HEAD
```

Dựng mạch từ đúng phiên bản đã commit. Nếu có thay đổi chưa commit ảnh hưởng implementation/config thì commit lại, lấy SHA mới và dựng lại trước khi chấm. Không gán SHA của phiên bản cũ cho artifact sinh từ code mới.

Giữ SHA đã được run tham chiếu; tránh amend/rebase làm mất dấu các commit đó. Có thể commit/push từng phần trước khi tới mốc này, nhưng phải có một commit xác định đầy đủ code/config thực tế dùng cho lần dựng.

## 7. Dựng artifact và chấm bằng notebook local

Chạy solution.py bằng Python trong `.venv`, truyền `--config`. Artifact phải cùng tên config và ở đúng vị trí:

```text
artifacts/<TRACK>/<ID>/<config-name>.kmb   Task 1–2
artifacts/<TRACK>/<ID>/<config-name>.zip   Task 3
```

Task 3 phải đóng gói `submission.npz` và `angle_k_0.kmb`, `angle_k_1.kmb`, ... liên tục từ 0 ở gốc ZIP. Nếu đổi setting, dùng artifact tương ứng; không chấm nhầm file của lần dựng trước. Nếu chủ động dựng lại cùng tên, dùng tùy chọn ghi đè của solution và đối chiếu hash artifact mới.

Mở [notebook local](notebooks/GQA_Grade_Submission.ipynb), chọn kernel `.venv`,
chạy cell setup/form, chọn TRACK, MODE, EXPERIMENT_ID, CONFIG_NAME và điền OWNER, rồi chạy cell chấm theo
[hướng dẫn local](docs/LOCAL_GRADING.md). File trong artifacts được đọc trực tiếp.

Dùng smoke để kiểm tra cơ bản, dev_5min để so sánh các phương án trong cùng cấu hình chấm. Full chạy khi cần xác nhận đầy đủ hoặc trước mốc nộp quan trọng, không bắt buộc cho mọi config. Điểm dev không tương đương full; DQI còn có hệ số phạt phụ thuộc số mẫu.

## 8. Tải results và gắn phiên bản nguồn

Sau khi chấm, kết quả tự nằm trong
`results/<TRACK>/<ID>/<config-name>/<mode>/<run-id>/`; không tải/giải nén ZIP.

Mỗi run là một thư mục riêng. Không ghi đè run cũ, không sửa JSON verifier hoặc metadata gốc để làm đẹp kết quả. Giữ config.json, metadata.json, verifier.json (nếu có), stdout/stderr và dữ liệu lỗi khi chạy thất bại. `config.json` từ notebook là cấu hình chấm; config dựng mạch nằm trong source ở bước 5.

Thêm `provenance.json` vào thư mục run, ghi ít nhất: SHA commit nguồn ở bước 6, đường dẫn và hash JSON config dựng, hash artifact, lệnh dựng thực tế. Đối chiếu hash artifact với hash submission mà notebook ghi. Notebook tự nối provenance khi có đúng một build khớp hash; agent đối chiếu và bổ sung khi thiếu/mơ hồ, không suy đoán commit từ HEAD.

Không commit token hay thông tin bí mật. Dữ liệu JSON/log nhỏ trong results được commit; artifact lớn vẫn ở ngoài Git. Xem thêm [quy ước results](results/README.md).

## 9. Phân tích và cập nhật điểm

Kiểm tra PASS/FAIL/TIMEOUT, tham số chấm, số mẫu và hash trước khi kết luận. TIMEOUT không chứng minh mạch sai và không có điểm hợp lệ. Smoke/FAIL/TIMEOUT giữ trong results, không ghi điểm vào bảng.

Ghi full PASS hoặc dev_5min PASS vào SCORES.md: mỗi hướng một dòng, hai cột điểm riêng, kèm link run tốt nhất tương ứng. Hai chế độ có thể chọn ra hai config khác nhau. Chỉ đánh dấu full khi đúng kích thước bài, dung sai và số shot chính thức.

Cải thiện (lần) = `baseline_score / candidate_score`. Baseline là `1.00×`; lớn hơn 1 là tốt hơn (ví dụ `2.00×` nghĩa là chi phí còn một nửa baseline), nhỏ hơn 1 là kém hơn. Chi phí/score gốc càng thấp càng tốt; hệ số cải thiện càng cao càng tốt.

Có điểm PASS hợp lệ của cùng bài là được so sánh và tính hệ số, không yêu cầu trùng phiên bản Python/package, verifier/harness, môi trường, profile, seed hoặc số mẫu. Chỉ tính với chi phí hữu hạn, lớn hơn 0; chưa có điểm baseline/candidate thì để `—`. Bảng điểm giữ score gốc và hai hệ số full/dev riêng theo baseline tương ứng; khi so khác mode trong phân tích phải ghi rõ mode. Giữ metadata/provenance và nêu khác biệt bối cảnh, không sửa JSON verifier gốc hoặc bắt chấm lại chỉ để khớp phiên bản.

Ứng viên cuối cần kiểm tra bổ sung độc lập (mẫu/seed chưa dùng để chọn config,
kiểm tra biên phù hợp) hoặc full trước khi khẳng định chất lượng. Bộ dev cố định
có thể bị chọn quá phù hợp sau nhiều vòng thử. Nếu so điểm trên profile bổ sung,
ghi rõ profile của các run; không bắt chấm lại đối chứng chỉ để được so điểm. Thành viên vẫn tự chạy notebook local. Chưa có kiểm tra bổ sung
thì có thể tổng kết/merge với giới hạn rõ ràng, không tuyên bố đã xác nhận đầy đủ.

Trong DESCRIPTION, ghi config/run tốt nhất của từng mode kèm SHA nguồn thực tế,
link provenance và cách lấy source/config tại commit đó. Khi sửa solution.py,
giữ mapping mốc tốt cũ: JSON cũ chạy với implementation mới không nhất thiết tái lập
kết quả cũ. Không sửa provenance/run cũ theo HEAD mới.

Bổ sung kết luận kỹ thuật vào DESCRIPTION.md: giả thuyết nào đúng/sai, đánh đổi, giới hạn và phần chưa thử. Không chép log upload, cài đặt hoặc bảng điểm vào mô tả; EXPERIMENTS.md chỉ giữ mục lục. Đồng bộ Issue nếu giải thích hoặc phạm vi thay đổi.

## 10. Commit kết quả và quyết định thử tiếp

**Commit results của run, provenance.json, SCORES.md và phân tích trong DESCRIPTION.md sau khi chấm.** Ví dụ commit: `INV-123: record balanced dev_5min result`.

Sau mỗi vòng, chọn một trong các nhánh:

- **Thử setting khác cùng ý tưởng:** quay lại bước 5, thêm/sửa JSON; commit nguồn/config ở bước 6 rồi dựng và chấm lại. Ghi profile chấm để người đọc hiểu bối cảnh so điểm.
- **Cần sửa implementation trong cùng hướng:** cập nhật mô tả và code ở bước 5; tạo commit mới trước khi dựng/chấm.
- **Đổi sang ý tưởng đáng kể hoặc nằm ngoài phạm vi đã nhận:** quay lại bước 2–3, tạo/nhận Issue mới và link hướng gốc.
- **Đã thử đủ:** sang bước 11, kể cả khi không cải thiện điểm.
- **Tạm dừng/bỏ hướng:** cập nhật trạng thái Issue, ghi kết luận và phần có thể bàn giao; commit công việc/kết quả cần giữ để người khác không thử lại từ đầu.

Mỗi vòng có hai mốc: **commit code/config → dựng/chấm → commit kết quả/phân tích**. Không đợi tới cuối toàn bộ hướng mới commit.

## 11. Hoàn thiện PR và review

Push các commit lên branch của hướng, chuyển draft PR sang sẵn sàng review. Dùng [mẫu PR](.github/pull_request_template.md), dẫn Issue và mô tả vấn đề, giải pháp cuối cùng, kết quả, config tốt nhất, giới hạn và cách tái lập. Thêm `Closes #<số Issue>` cho hướng đã hoàn tất.

Đồng bộ nhánh chính bằng merge vào branch thử nghiệm và xử lý conflict trước merge PR; không rebase/amend các commit đã được run tham chiếu. Với EXPERIMENTS.md và SCORES.md, giữ đủ các hướng của thành viên khác, tránh ghi đè dòng của họ.

Trước PR, agent chạy `.\.venv\Scripts\python.exe scripts/check_repo.py`, bộ test trong `scripts/tests`, và check diff `--base/--branch` khi có Git. Xem [schema provenance và check CI](docs/REPOSITORY_CHECKS.md).

Reviewer kiểm tra mô tả/Issue đã đồng bộ, code đọc config, commit nguồn/provenance, hash và bằng chứng chấm, điểm đúng cột và link kết quả mở được. Các kiểm tra nhỏ hoặc CI chỉ chạy nếu phù hợp; không tuyên bố full PASS khi chỉ có dev. Hướng thất bại vẫn có thể merge để lưu tri thức, nhưng phải ghi kết luận rõ.

Phân công review: tác giả dùng bước 06 chuẩn bị PR; teammate dùng phiên agent
riêng chạy [07](instructions/experiments/07_review_pr.md), ghi findings và SHA đã review.
Tác giả sửa/push nếu cần; teammate kiểm tra lại commit mới rồi dùng
[07b](instructions/experiments/07b_publish_review.md) để đăng Approve hoặc Request changes.
Tài khoản reviewer phải khác tác giả. CI đang chờ thì chưa approve; thiếu approval
không phải lỗi check kỹ thuật. Findings trong chat chưa thay thế review GitHub.
Nếu HEAD đổi sau review, teammate review lại phần mới và đăng approval cho HEAD đó,
kể cả khi thay đổi chỉ để xử lý conflict. Tác giả dùng bước 08 để merge sau cùng.

## 12. Merge và hoàn thành Issue

Sau khi review được chấp nhận và các yêu cầu của repository đạt, merge PR vào nhánh chính bằng **merge commit** để giữ các SHA nguồn đã được run tham chiếu trong lịch sử main. Không dùng squash merge hoặc rebase merge cho PR thử nghiệm. Nếu repository không cho phép merge commit, báo để cấu hình repository được điều chỉnh; không tự chuyển phương thức hoặc bypass rule. Xác nhận Issue được đóng qua `Closes #...`; nếu không tự đóng thì đóng sau khi merge và dẫn PR đã merge. Chuyển trạng thái hướng sang `completed` trên Issue/project board. Không đóng Issue chỉ vì đã commit hoặc push xong.

Nếu chỉ merge phần bàn giao mà hướng còn dang dở, giữ Issue mở hoặc chuyển giao; không đánh dấu completed. Sau khi hoàn tất, đồng bộ nhánh chính trên máy để bắt đầu hướng tiếp theo từ bước 2.

## Nơi lưu thông tin

| Nơi | Nội dung |
| --- | --- |
| GitHub Issue / project board | Owner, phạm vi nhận việc, trạng thái và thảo luận |
| EXPERIMENTS.md | ID, title trùng Issue, link Issue và link DESCRIPTION |
| <ID>/DESCRIPTION.md | Thiết kế, nguồn kế thừa, điều kiện đúng, đánh đổi và kết luận kỹ thuật |
| <ID>/solution.py | Implementation và docstring giải thích chi tiết |
| <ID>/configs/ | Các setting dựng mạch dùng lại |
| SCORES.md | Điểm full/dev tốt nhất theo hướng, link run tương ứng |
| results/ | Cấu hình chấm, metadata, JSON/log và provenance của từng run |
| artifacts/ | Mạch/ZIP sinh ra, không commit thông thường |

Trạng thái đề xuất: `proposed → claimed → running → in_review → completed`; thêm `paused` hoặc `abandoned` khi cần. Mô tả trong repo là bản chuẩn, đồng bộ với Issue. Khi chưa có GitHub thì theo dõi phân công trực tiếp trong nhóm, giữ nguyên các nguyên tắc ID, source/config và kết quả.

Chấm local theo [hướng dẫn](docs/LOCAL_GRADING.md); không cần tạo ZIP verifier hoặc tải results về máy.
