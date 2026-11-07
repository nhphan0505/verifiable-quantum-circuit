# Kiểm tra trước PR

Từ root project, dùng Python 3.13:

```powershell
.\.venv\Scripts\python.exe scripts/check_repo.py
.\.venv\Scripts\python.exe -m unittest discover -s scripts/tests -v
```

Khi có Git, kiểm tra thêm diff với main đã fetch (thay đúng remote/branch):

```powershell
.\.venv\Scripts\python.exe scripts/check_repo.py --base origin/main --branch exp/INV-123-ten-huong
```

Check dùng thư viện chuẩn; không cần cài kickmix, tải dataset hoặc compile trên CI.
Workflow `.github/workflows/repo-checks.yml` chạy khi push/PR; PR có thêm kiểm tra
phạm vi dựa trên tên branch thật. Branch `exp/<ID>-...` chỉ được đổi thư mục source/results
của ID và dòng riêng trong EXPERIMENTS/SCORES. Nhánh hạ tầng không áp dụng giới hạn này;
reviewer vẫn phải xác nhận phạm vi và owner. Tên branch không thay thế quyền GitHub.

Check kiểm tra ID/title/index/link, cú pháp Python/docstring và notebook, JSON,
verifier gốc theo manifest, score PASS/đúng mode/khớp JSON, hệ số baseline/candidate
và profile dev. Khi có Git, check so hash source/config với snapshot commit,
kiểm tra commit còn là ancestor HEAD, file binary lớn bị track nhầm và phạm vi PR.
Đây là kiểm tra nhất quán; thuật toán, nội dung mô tả, chứng minh sai số, việc chấm
đủ điều kiện chính thức và danh tính/owner Issue vẫn cần review. Không gọi check này
là full verify. Chưa có Git thì bỏ qua snapshot/diff và báo rõ.

## Provenance cho run mới

Dùng [mẫu](../templates/run/provenance.json). Tất cả đường dẫn dưới đây là POSIX,
tương đối root (không ghi D:\... hoặc /content/...):

- `track`, `experiment_id`, `config_name`: khớp thư mục run.
- `source_commit`: SHA đầy đủ 40 ký tự của commit source/config đã dùng.
- `source_path`: `src/<TRACK>/<ID>/solution.py`.
- `source_sha256`: hash bytes source ở commit đó.
- `build_config_path`: `src/<TRACK>/<ID>/configs/<config>.json`.
- `build_config_sha256`: hash bytes JSON dựng mạch ở commit đó.
- `artifact_path`: `artifacts/<TRACK>/<ID>/<config>.kmb` hoặc `.zip`.
- `artifact_sha256`: hash file artifact thực tế; trùng `metadata.upload_artifact.sha256` khi chấm.
- `build_command`: lệnh thực tế; `environment`: phiên bản Python/package/OS.
- `build_run`: null với build_only; với run chấm là đường dẫn
  `results/<TRACK>/<ID>/<config>/build_only/<run_id>` đã ghi lúc dựng.

Sau commit, agent đối chiếu bytes source/config local với snapshot trước build;
phải bằng nhau để không gắn hash commit cho input khác. `.gitattributes` dùng LF cho
source/config và giữ nguyên bytes verifier/results. Nếu source/config local còn CRLF
sau commit đầu tiên, lưu lại thành LF rồi kiểm tra lại trước compile.
Run chấm phải khớp commit/hash với build_run, không suy ra từ HEAD hiện tại.
Các dependency/helper/data ngoài solution.py cũng cần được nêu trong environment
hoặc thông tin bổ sung; checker chưa chứng minh toàn bộ dependency closure.

Tám run cũ trong `scripts/legacy_runs.json` được miễn schema provenance mới, giữ nguyên
bằng chứng lịch sử. Đây là danh sách đường dẫn cố định, không miễn mọi run baseline.
Không thêm run mới vào danh sách để né check; thay đổi danh sách thuộc hạ tầng và cần review.

## Môi trường tái lập

Python hỗ trợ cho workflow này: **3.13**; `.python-version` ghi minor này.
Local baseline đã chạy Python 3.13.14: `requirements.txt` cố định kickmix 1.0.0,
NumPy 2.5.4, SciPy 1.18.1. Notebook local kiểm tra đúng kernel `.venv` và bộ
package này. Cài thêm requirements-notebook.txt để có giao diện notebook/dropdown.
Metadata của các run Colab lịch sử vẫn giữ nguyên Python/package thực tế; khi
so điểm với run local cần dùng baseline tương thích hoặc để hệ số trống.
CI kiểm tra records bằng Python 3.13; review/check bắt buộc do cấu hình GitHub quyết định.

## Bằng chứng chấm và tính bất biến

- Run full PASS phải dùng lệnh verifier chính thức. Check từ chối option làm đổi
  kích thước/dung sai/số mẫu; kiểm tra cả dạng `--option=value`, option trùng và
  tên viết tắt không xác định. Invsqrt cần 200540928 shots, DQI cần 102400 shots
  cùng m/n/degree/r/log2_delta chuẩn. DFTHC cần 64 shots/address; số shot trả về
  phải dương và chia hết cho 64. JSON DFTHC không chứa số địa chỉ độc lập, nên
  checker không tự chứng minh tổng số địa chỉ từ artifact bị ignore; phần đó
  vẫn dựa trên verifier chính thức và review, không gọi đây là chạy lại full.
- Khi có `verify.stdout.txt` và `verifier.json`, hai JSON phải bằng nhau về nội dung
  (khác whitespace không ảnh hưởng). Stdout không phải JSON thì báo lỗi để review,
  không tự trích một đoạn rồi coi là kết quả gốc.
- Hệ số cải thiện yêu cầu cùng phiên bản Python patch, kickmix/numpy/scipy,
  toàn bộ bảng hash verifier và hash dev harness khi dùng dev. Thiếu bằng chứng
  so sánh thì để hệ số `—` và chấm đối chứng tương thích; không bổ sung hash suy đoán.
  Hệ số baseline tự so chính nó vẫn là 1.00×; không dùng ngoại lệ này cho ứng viên.
- Với `--base`, mọi file đã có trong thư mục run của nhánh gốc phải giữ nguyên bytes,
  kể cả raw results, provenance và review đã lưu. Áp dụng cả branch hạ tầng.
  Cho phép thêm sidecar mới như `review_v2.json`/provenance còn thiếu hoặc run mới;
  không ghi đè review/provenance cũ. CI PR tự truyền base, local cần truyền `--base`.
  Check đọc working tree nên bắt cả sửa/xóa chưa commit. Không có Git/base thì không
  thể đối chiếu tính bất biến. Tính nhất quán JSON không chứng minh dữ liệu mới là
  kết quả chạy thật: reviewer vẫn phải xem bằng chứng nguồn của run.

Notebook chạy local, đối chiếu EXPECTED_PACKAGES với requirements.txt. Xem [LOCAL_GRADING.md](LOCAL_GRADING.md).

## Chấm lại artifact được dựng trước Git

Run mới có thể dùng `provenance_type: pre_git_build`, source_commit/config build là
null, nếu nối được chính xác bằng hash artifact tới một build_only lịch sử có trong
legacy_runs.json. Phải ghi source_path/source_sha256 đúng biên bản cũ và limitations.
Checker đối chiếu hash upload với build cũ; không miễn kiểm tra run mới, không mở
ngoại lệ cho build mới hoặc tự thêm run vào allowlist. Mẫu provenance thông thường
vẫn bắt buộc SHA Git đầy đủ cho mọi build từ workflow hiện tại.

## Research notes và branch tài liệu

Note nằm tại research/<TRACK>/<papers|discussions>/<SOURCE_ID>/note.md.
Checker đối chiếu metadata Status (draft/ready), Track, Source, Version và source.json:
identity theo folder, title/version/ngày truy cập/coverage, đường dẫn nguồn cùng
thư mục và SHA-256 thật. Checker cấu trúc cho phép bản nháp; job CI research-notes yêu cầu mỗi thư mục nguồn có note.md không rỗng. Nguồn URL phải có URL
và phiên bản/ngày truy cập; không khai hash file local nếu không lưu file.

Branch research/<username> có thể sửa nhiều nguồn trong research/<TRACK>/<papers|discussions>/<SOURCE_ID>/
và các dòng bảng trong research/README.md. Không sửa research/AGENTS.md hay code/
config/results/templates. Chạy --base <base-ref> --branch research/<username> trước PR.
Checker chỉ kiểm tra hình thức username; quyền sở hữu và quyết định của nhóm được
xác minh qua GitHub và người dùng. Branch hạ tầng (ví dụ infra/...) dùng cho sửa workflow.

CI không chứng minh nội dung note đúng hoặc đã review/merge. Reviewer kiểm tra
nguồn trực tiếp; publisher xác nhận approval gắn HEAD cuối. Agent nghiên cứu chỉ
đọc note ready trên nhánh chính. Test fixture bao gồm research để kiểm tra link.

## CI bắt buộc note đi kèm resource

Job `Research resources require notes` trong .github/workflows/repo-checks.yml chạy
`python scripts/check_research_notes.py` trên PR, push và workflow_dispatch.
Mọi thư mục nguồn dưới bốn track/papers hoặc discussions phải có note.md chữ thường,
không rỗng, UTF-8 và không phải symlink. source.md, source.json hoặc PDF không thay thế note.
Tài nguyên đặt rời ngoài thư mục nguồn bị chặn; .gitkeep ở cấp papers/discussions được bỏ qua.
Check này áp dụng toàn kho, không miễn nguồn cũ và không phụ thuộc tên branch.

Check file không xác nhận chất lượng nội dung; reviewer phải đối chiếu nguồn.
Cần đặt job này là required check trong branch protection/ruleset để GitHub thực sự
chặn merge khi đỏ; chỉ có workflow không tự bật bảo vệ branch.

Nếu source.json có project_snapshot, hash phải lấy từ Git blob tại commit đã ghi,
không lấy từ checkout CRLF/LF. Checker đối chiếu với git show khi có Git.
