# Google Quantum AI - Verifiable Quantum Circuit Compilation

## Cấu trúc

```text
GQA/
├── src/                              # Code và tài liệu các hướng thử
│   ├── <TRACK>/                      # invsqrt, dqi hoặc dfthcsos
│   │   ├── EXPERIMENTS.md             # Mục lục, title và link Issue/mô tả
│   │   ├── SCORES.md                  # Điểm full/dev_5min và link run
│   │   └── <EXPERIMENT_ID>/
│   │       ├── solution.py            # Implementation của hướng
│   │       ├── DESCRIPTION.md         # H1 = title Issue; nội dung = description
│   │       └── configs/
│   │           └── <CONFIG_NAME>.json # Setting dùng lại của cùng hướng
│   └── common/                       # Bộ chạy kickmix-engine dùng chung
├── artifacts/                        # File sinh ra để upload, không commit
│   ├── <TRACK>/
│   │   └── <EXPERIMENT_ID>/
│   │       ├── <CONFIG_NAME>.kmb      # Task 1–2
│   │       └── <CONFIG_NAME>.zip      # Task 3
├── results/                          # Kết quả từng lần chạy
│   ├── <TRACK>/
│   │   └── <EXPERIMENT_ID>/
│   │       └── <CONFIG_NAME>/
│   │           └── <MODE>/            # smoke/full/build_only; dev_5min lịch sử
│   │               └── <run_id>/      # JSON, metadata, log và provenance
│   └── setup/                        # Biên bản setup/migration
├── verifiers/                        # Code và dữ liệu chấm gốc
├── sample_submission/                # Submission mẫu gốc
├── kickmix/                          # Binary Linux gốc; hiện dùng pip
├── notebooks/                        # Notebook chấm local bằng engine
├── research/                         # Mục lục paper, ghi chú và thảo luận
├── docs/                             # Hướng dẫn
├── templates/                        # Mẫu mô tả, source docstring và record run
├── .github/                          # Mẫu Issue và PR
└── .venv/                            # Môi trường Python local, không commit
```

## Làm việc

Dùng coding agent: yêu cầu đọc [AGENTS.md](AGENTS.md) trước khi bắt đầu. Chọn [instructions theo bước](instructions/experiments/README.md) để giao việc.

1. Chuẩn bị workspace
2. Kiểm tra các hướng đã có
3. Tạo hoặc nhận GitHub Issue
4. Tạo branch cho hướng
5. Viết mô tả, implementation và config
6. Commit nguồn trước khi dựng và chấm
7. Dựng artifact và chấm bằng notebook local
8. Tải results và gắn phiên bản nguồn
9. Phân tích và cập nhật điểm
10. Commit kết quả và quyết định thử tiếp
11. Hoàn thiện PR và review
12. Merge và hoàn thành Issue

Chi tiết: [CONTRIBUTING.md](CONTRIBUTING.md).

## Setup workspace sau khi clone

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

Mở workspace trong coding agent, yêu cầu đọc [AGENTS.md](AGENTS.md) và
[CONTRIBUTING.md](CONTRIBUTING.md). Kiểm tra Git đã có tên/email commit của chính
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

- [Invsqrt](src/invsqrt/README.md) · [DQI](src/dqi/README.md) · [DFTHC](src/dfthcsos/README.md)
- [Hướng dẫn chấm local](docs/LOCAL_GRADING.md) · [Cộng tác](CONTRIBUTING.md) · [Dữ liệu gốc](DATA.md)
- [Quy ước results](results/README.md)

Các record cũ đã chuyển về cấu trúc mới, giữ nguyên JSON/log. Đường dẫn lịch sử bên trong metadata vẫn là đường dẫn lúc chạy; xem results/setup/structure_migration.json để đối chiếu.

Kiểm tra trước PR: `.\.venv\Scripts\python.exe scripts/check_repo.py`. Xem [phạm vi check, provenance và phiên bản môi trường](docs/REPOSITORY_CHECKS.md). Dùng Python 3.13 và dependency đã pin.

Kho tài nguyên: [paper và thảo luận nghiên cứu](research/README.md).

## Hai luồng dùng agent

| Luồng | Hướng dẫn | Instructions |
| --- | --- | --- |
| Nghiên cứu thử nghiệm | [Workflow](docs/EXPERIMENT_WORKFLOW.md) | [experiments](instructions/experiments/README.md) |
| Đọc paper thành note | [Agent tài liệu](research/AGENTS.md) | [papers](instructions/papers/README.md) |
| Đọc discussion thành note | [Agent tài liệu](research/AGENTS.md) | [discussions](instructions/discussions/README.md) |

Dùng chat và workspace riêng khi chạy đồng thời. Agent tài liệu xuất bản note;
agent nghiên cứu chỉ dùng note ready đã review và merge. Chấm notebook local vẫn
thực hiện thủ công. Xem [điểm vào chung](instructions/README.md).

Luồng tài liệu: mỗi thành viên thêm nhiều nguồn/note trên `research/<username>`,
mở PR cho đợt; sau review độc lập bước 04 và checks đạt, tác giả được merge ở
bước 05 theo research/AGENTS.md. Issue nguồn là tùy chọn.
Workflow experiment vẫn dùng `exp/<ID>-...` như trước.

Trong chat đã xác định luồng, chỉ cần nói “thực hiện các bước 1 2 3”. Agent đọc
instructions, dùng lại ngữ cảnh và tra project/GitHub; chỉ hỏi thông tin chưa biết
hoặc chưa rõ, không yêu cầu chép prompt/điền lại tham số. Xem [quy tắc giao việc](instructions/README.md).
