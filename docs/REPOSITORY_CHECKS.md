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
NumPy 2.5.4, SciPy 1.18.1. Colab full baseline đã chạy Python 3.13.18:
`requirements-colab.txt` cố định kickmix 1.0.0, NumPy 2.4.6, SciPy 1.16.3.
Notebook cài đúng bộ Colab và chặn minor Python khác; nếu runtime không còn cung cấp
Python 3.13, cần kiểm chứng môi trường mới và chấm lại baseline đối chứng trước khi đổi.

Metadata lịch sử giữ nguyên phiên bản thực tế. Hai bộ dependency được giữ riêng vì
đã có bằng chứng chạy khác nhau, chưa khẳng định chúng cho điểm giống nhau mọi bài.
So ứng viên/baseline cùng mode/profile và môi trường chấm; nếu đổi dependency, ghi rõ
và chạy lại đối chứng. CI chỉ kiểm tra records bằng Python 3.13, không xác nhận khả năng
cài hoặc chạy package Colab. Workflow sẽ hoạt động khi push lên GitHub; việc đặt nó
thành required check và yêu cầu reviewer phải cấu hình trên GitHub sau khi tạo repo.

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
