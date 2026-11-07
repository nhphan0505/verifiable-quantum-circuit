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
│   └── common/                       # Công cụ chấm phát triển dùng chung
├── artifacts/                        # File sinh ra để upload, không commit
│   ├── <TRACK>/
│   │   └── <EXPERIMENT_ID>/
│   │       ├── <CONFIG_NAME>.kmb      # Task 1–2
│   │       └── <CONFIG_NAME>.zip      # Task 3
│   └── colab/                        # ZIP verifier và dữ liệu tham chiếu
├── results/                          # Kết quả từng lần chạy
│   ├── <TRACK>/
│   │   └── <EXPERIMENT_ID>/
│   │       └── <CONFIG_NAME>/
│   │           └── <MODE>/            # smoke, dev_5min, full hoặc build_only
│   │               └── <run_id>/      # JSON, metadata, log và provenance
│   └── setup/                        # Biên bản setup/migration
├── verifiers/                        # Code và dữ liệu chấm gốc
├── sample_submission/                # Submission mẫu gốc
├── kickmix/                          # Binary Linux gốc; hiện dùng pip
├── notebooks/                        # Notebook upload/chấm/tải results
├── docs/                             # Hướng dẫn
├── templates/                        # Mẫu mô tả, source docstring và record run
├── .github/                          # Mẫu Issue và PR
└── .venv/                            # Môi trường Python local, không commit
```

## Làm việc

Dùng coding agent: yêu cầu đọc [AGENTS.md](AGENTS.md) trước khi bắt đầu. Chọn [prompt theo giai đoạn](templates/prompts/README.md) để giao việc.

1. Chuẩn bị workspace
2. Kiểm tra các hướng đã có
3. Tạo hoặc nhận GitHub Issue
4. Tạo branch cho hướng
5. Viết mô tả, implementation và config
6. Commit nguồn trước khi dựng và chấm
7. Dựng artifact và chấm thủ công trên Colab
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
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Dùng trực tiếp Python trong `.venv` như trên, không cần activate. Nếu không có
lệnh `py`, dùng `python --version` xác nhận đúng 3.13 rồi chạy `python -m venv .venv`.
Colab dùng bộ dependency riêng đã pin trong notebook và `requirements-colab.txt`.

**3. Bổ sung dữ liệu ban tổ chức:**

Lấy bộ dữ liệu gốc của cuộc thi hoặc từ người phụ trách nhóm, đặt theo [DATA.md](DATA.md).
Git không chứa dataset lớn, submission mẫu, `.venv` hoặc artifact đã compile.
Để tạo đủ hai ZIP Colab cần:

- `verifiers/dfthcsos/FeMoCo76o113e.fcidump`
- `verifiers/dfthcsos/FeMoCo76o113e.fixed_shifts.npz`

Dựng baseline task 3 còn cần `sample_submission/dfthcsos/submission.npz`.
Các file mạch mẫu dùng để đối chiếu khi cần; Windows dùng package pip Kickmix,
không cần binary Linux `kickmix.so` để compile.

**4. Tạo ZIP dùng cho Colab và kiểm tra workspace:**

```powershell
.\.venv\Scripts\python.exe scripts/prepare_colab.py
.\.venv\Scripts\python.exe scripts/check_repo.py
```

Lệnh đầu kiểm tra hash dữ liệu và tạo `gqa_verifiers.zip`, `dfthcsos_reference.zip`
cùng manifest trong `artifacts/colab/`. Nếu thiếu dữ liệu thì bổ sung đúng file
trước khi chạy lại. Checker có thể chạy riêng mà không cần dataset lớn.
Xem [hướng dẫn chấm Colab](docs/COLAB_GRADING.md) để sử dụng notebook và các ZIP này.

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
Bắt đầu bằng [prompt 01 — tìm hypothesis](templates/prompts/01_find_hypothesis.md),
sau đó làm theo [bộ prompt từng giai đoạn](templates/prompts/README.md).
Agent sẽ tạo branch, code/config và compile artifact khi được giao hướng;
người clone mới chưa có sẵn artifact baseline trong máy.

- [Invsqrt](src/invsqrt/README.md) · [DQI](src/dqi/README.md) · [DFTHC](src/dfthcsos/README.md)
- [Hướng dẫn Colab](docs/COLAB_GRADING.md) · [Cộng tác](CONTRIBUTING.md) · [Dữ liệu gốc](DATA.md)
- [Quy ước results](results/README.md)

Các record cũ đã chuyển về cấu trúc mới, giữ nguyên JSON/log. Đường dẫn lịch sử bên trong metadata vẫn là đường dẫn lúc chạy; xem results/setup/structure_migration.json để đối chiếu.

Kiểm tra trước PR: `.\.venv\Scripts\python.exe scripts/check_repo.py`. Xem [phạm vi check, provenance và phiên bản môi trường](docs/REPOSITORY_CHECKS.md). Dùng Python 3.13 và dependency đã pin; Colab dùng bộ riêng trong requirements-colab.txt.
