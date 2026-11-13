# Compile trực tiếp INV-51

Cài requirements.txt của repo vào .venv Windows Python 3.13. Generator và dữ liệu nằm sẵn trong engine/; không cần tải bundle tác giả, Linux .so hoặc verifier để build.

Từ repo root:

```powershell
.venv/Scripts/python.exe src/invsqrt/INV-51/solution.py --config src/invsqrt/INV-51/configs/reconstructed.json
```

Output: artifacts/invsqrt/INV-51/reconstructed.kmb. Output có sẵn không bị ghi đè; lưu bản cũ trước khi build lại. engine_manifest.json kiểm tra file tích hợp. Xem INTEGRATION.md và upstream_changes.json để review source port. Các source commit và run lịch sử vẫn được giữ nguyên.

Nguồn lineage upstream: [Kaggle dataset version 12](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio/versions/12), archive invsqrt_source_zip SHA-256 7d9801ae20e942dba2211a656bba6014a0a16d57da534c0b60328d1c5d9d8254. Đây là nguồn phát triển/attribution; không phải dependency tải về lúc compile.
