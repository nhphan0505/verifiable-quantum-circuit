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

## Chạy nhanh

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/invsqrt/INV-BASELINE/solution.py --config src/invsqrt/INV-BASELINE/configs/baseline.json
```

Artifact baseline hiện đã có; thêm `--overwrite` nếu chủ động dựng lại. `--output` cho phép đổi thư mục đích nhưng vẫn phải giữ tên theo config.

- [Invsqrt](src/invsqrt/README.md) · [DQI](src/dqi/README.md) · [DFTHC](src/dfthcsos/README.md)
- [Hướng dẫn Colab](docs/COLAB_GRADING.md) · [Cộng tác](CONTRIBUTING.md) · [Dữ liệu gốc](DATA.md)
- [Quy ước results](results/README.md)

Các record cũ đã chuyển về cấu trúc mới, giữ nguyên JSON/log. Đường dẫn lịch sử bên trong metadata vẫn là đường dẫn lúc chạy; xem results/setup/structure_migration.json để đối chiếu.

Kiểm tra trước PR: `.\.venv\Scripts\python.exe scripts/check_repo.py`. Xem [phạm vi check, provenance và phiên bản môi trường](docs/REPOSITORY_CHECKS.md). Dùng Python 3.13 và dependency đã pin; Colab dùng bộ riêng trong requirements-colab.txt.
