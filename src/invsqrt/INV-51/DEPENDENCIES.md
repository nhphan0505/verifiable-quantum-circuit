# Dependency runtime

Cài requirements.txt của repo vào .venv Windows Python 3.13. Chỉ cần source trong repo: solution.py, circuit.py, tables.json và configs/reconstructed.json. Không cần tải bundle tác giả, thư mục engine, Linux .so hoặc verifier để compile.

```powershell
.venv/Scripts/python.exe src/invsqrt/INV-51/solution.py --config src/invsqrt/INV-51/configs/reconstructed.json
```

Output: artifacts/invsqrt/INV-51/reconstructed.kmb. Lưu bản output cũ trước khi chạy lại; không tự ghi đè. engine_manifest.json kiểm tra source/data. LICENSE.txt và NOTICE.txt giữ attribution Apache-2.0. Chi tiết refactor ở INTEGRATION.md; nguồn lineage công khai ở DESCRIPTION.md.
