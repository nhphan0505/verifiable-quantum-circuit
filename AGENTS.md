# Hướng dẫn cho coding agent

Áp dụng cho toàn bộ repository. Đọc [CONTRIBUTING.md](CONTRIBUTING.md) trước khi làm việc; đó là quy trình đầy đủ. Làm trong phạm vi thành viên giao, không tự đổi hypothesis hoặc mở rộng sang hạ tầng chung. Nếu yêu cầu mới của người dùng thay đổi phạm vi, điều chỉnh công việc theo yêu cầu đó.

## 1. Xác định giai đoạn và quyền sở hữu

- Khi tìm hypothesis trên nhánh chính: chỉ đọc Issues, PR, EXPERIMENTS.md, DESCRIPTION, code và kết quả; đề xuất hướng rõ ràng, chưa sửa file.
- Trước khi nhận hướng, kiểm tra cả Issues mở/đóng và PR đang mở. Mục lục trên nhánh chính có thể chưa chứa hướng đang làm ở branch khác.
- Một Issue + một branch thuộc một owner. Không làm trùng hướng đã nhận hoặc sửa branch của người khác khi chưa thống nhất.
- Chỉ tạo/gán Issue, tạo branch, push, tạo PR hoặc merge khi giai đoạn đó đã được người dùng giao. Không yêu cầu xác nhận lại các thao tác đã được giao rõ ràng trong cuộc chat.
- Xác định TRACK, ID, owner và Issue từ yêu cầu hoặc GitHub. Không tự bịa số Issue, URL, tên nhánh chính hoặc danh tính thành viên. Nếu thiếu thông tin, tra nguồn có sẵn trước khi hỏi.
- ID: `INV-<số Issue>`, `DQI-<số Issue>`, `DFT-<số Issue>`. ID `*-BASELINE` dành riêng cho baseline gốc. Branch ví dụ: `exp/INV-123-horner-precision`.
- Trước khi sửa, kiểm tra branch và working tree. Giữ nguyên thay đổi của người dùng. Nếu nhiều chat chạy đồng thời trên cùng máy, dùng checkout/worktree riêng khi được giao; không tự chuyển branch của một workspace đang có công việc khác.

## 2. Cấu trúc bắt buộc

```text
src/<TRACK>/
  EXPERIMENTS.md
  SCORES.md
  <ID>/
    solution.py
    DESCRIPTION.md
    configs/<CONFIG_NAME>.json
artifacts/<TRACK>/<ID>/<CONFIG_NAME>.kmb  # invsqrt / dqi
artifacts/<TRACK>/<ID>/<CONFIG_NAME>.zip  # dfthcsos
results/<TRACK>/<ID>/<CONFIG_NAME>/<MODE>/<run_id>/
```

- TRACK là `invsqrt`, `dqi` hoặc `dfthcsos`. Một hướng có một implementation; các setting khác nhau dùng JSON khác nhau, không sao chép Python cho từng setting.
- Tên artifact trùng stem JSON config. Dùng tên config đơn giản gồm chữ/số/gạch ngang/gạch dưới để notebook nhận đúng tên.
- MODE: `smoke`, `dev_5min`, `full`; record dựng mạch dùng `build_only`. Mỗi run có ID mới, không ghi đè kết quả cũ.
- Mặc định chỉ sửa source, configs, mô tả, artifacts và results của ID được giao, cùng dòng của hướng đó trong hai bảng dùng chung.
- Verifier, dữ liệu gốc, notebook, `src/common/`, templates và hướng dẫn là hạ tầng chung. Chỉ sửa khi nhiệm vụ có phạm vi này; nên tách Issue/branch hạ tầng khỏi hướng thuật toán. Không sửa verifier để ứng viên được PASS.

## 3. Mô tả và title Issue

- Dùng [templates/experiment.md](templates/experiment.md). H1 của DESCRIPTION.md phải trùng title Issue và nội dung link hiển thị trong EXPERIMENTS.md.
- Title phải thể hiện thành phần, phương pháp và phạm vi, đủ để nhóm phân công; không chỉ ghi “tối ưu baseline”, “v2” hoặc tên file.
- EXPERIMENTS.md chỉ là mục lục: ID, title làm link tới DESCRIPTION.md, link Issue. Không thêm lịch sử chạy hoặc mô tả dài vào bảng.
- DESCRIPTION.md là bản chuẩn; phần dưới H1 dùng làm description Issue. Đồng bộ khi được giao cập nhật Issue; đổi link tương đối thành URL GitHub thật khi dán lên Issue.

| Loại | Nội dung bắt buộc |
| --- | --- |
| Tinh chỉnh | Link file gốc, phần sửa, lý do, cách thực hiện và đánh đổi |
| Kết hợp | Link từng nguồn, phần lấy từ mỗi nguồn, cách ghép và xử lý không tương thích |
| Ý tưởng mới | Thuật toán, công thức, điều kiện đúng, sai số và tài nguyên dự kiến |

- Ghi commit/permalink hoặc hash nguồn kế thừa. Giữ giấy phép và attribution. Không kể lại toàn bộ baseline khi chỉ thay một phần.
- Mọi file Python phải có docstring đầu file giải thích chi tiết solution, giả định, kiểm soát sai số, compute/uncompute/sửa pha, đánh đổi và cách chạy; dùng [templates/solution.py](templates/solution.py).
- Trước khi thử, DESCRIPTION phải ghi mốc đối chứng (source/config/phiên bản và run nếu có), dự đoán, tiêu chí ủng hộ/bác bỏ hypothesis và điều kiện dừng. Hoàn thiện setting cụ thể trước compile/chấm; nếu đổi tiêu chí sau khi xem results phải ghi lý do.
- Owner, trạng thái và thảo luận nằm trên Issue. Kết luận kỹ thuật cập nhật vào DESCRIPTION.md; điểm nằm trong SCORES.md; log gốc nằm trong results.

## 4. Commit nguồn, dựng mạch và ghi provenance

- Với công việc thử nghiệm đã được giao: commit mô tả/code/config trước khi dựng/chấm; lấy SHA nguồn thực tế. Thay source/config sau đó thì commit và dựng lại trước lần chấm mới.
- Chạy Python 3.13 trong `.venv`, dùng package pip đã pin theo requirements.txt (Colab dùng requirements-colab.txt). Không dùng binary Linux `kickmix.so` để dựng trên Windows.
- `solution.py` suy ra TRACK/ID từ vị trí file, đọc `--config` là JSON ngay trong `configs/` của hướng sau khi resolve đường dẫn, và mặc định xuất artifact vào đúng TRACK/ID. Chỉ ghi đè artifact khi đang chủ động dựng lại; không sửa hoặc ghi đè run cũ.
- Task 3: ZIP có `submission.npz` và toàn bộ `angle_k_0.kmb`, `angle_k_1.kmb`, ... liên tục từ 0 ở gốc ZIP, không có thư mục con/file thừa.
- Dùng schema [templates/run/provenance.json](templates/run/provenance.json) và [quy tắc check](docs/REPOSITORY_CHECKS.md); source/config local phải khớp bytes snapshot commit trước build.
- Sau compile, agent tự lưu record `results/<TRACK>/<ID>/<CONFIG_NAME>/build_only/<run_id>/provenance.json`: TRACK/ID/config, SHA nguồn, đường dẫn và SHA-256 config, hash artifact, lệnh dựng, phiên bản môi trường. Ghi thêm record trạng thái BUILT nếu cần; không tạo điểm verifier cho build_only.
- Nếu chưa có Git hoặc thao tác commit bị chặn, ghi rõ điều đó và dùng hash source/config để nhận diện tạm; không bịa SHA hoặc tuyên bố đã commit. Báo giới hạn này khi bàn giao.
- Không commit artifacts lớn, `.venv`, token hoặc thông tin đăng nhập. Không amend/rebase làm mất dấu commit đã được run tham chiếu.

## 5. Bàn giao chấm Colab — điểm dừng bắt buộc của thử nghiệm

Thành viên tự chấm thủ công. Sau khi dựng artifact và kiểm tra phù hợp, cung cấp:

1. Đường dẫn artifact và SHA-256.
2. TRACK, EXPERIMENT_ID, tên config và mode đề xuất.
3. Hướng dẫn mở notebook, upload ZIP verifier và đúng một artifact; task 3 nạp thêm ZIP dữ liệu tham chiếu nếu cần.
4. Hướng dẫn tải results và giải nén ZIP vào root project.

Sau đó dừng và chờ kết quả. Không tự mở browser, chạy Colab, theo dõi runtime hay dùng MCP để chấm thay, trừ khi người dùng yêu cầu rõ ràng cho lượt đó.

Notebook tự lấy CONFIG_NAME từ tên artifact. Task 1–2 chỉ nhận một `.kmb`; task 3 chỉ nhận một ZIP submission. Không yêu cầu upload JSON build. Xem [docs/COLAB_GRADING.md](docs/COLAB_GRADING.md).

## 6. Khi người dùng đã tải results

- Tìm run mới trong project trước khi hỏi lại vị trí. Đối chiếu TRACK/ID/config/mode, trạng thái, số mẫu, profile/seed và hash mạch/verifier.
- Nối kết quả với record build_only bằng hash artifact, không chỉ dựa vào tên file. Bổ sung provenance.json cho run chấm, dẫn SHA nguồn/config/lệnh dựng đã ghi lúc compile. Nếu không xác định được bản build, ghi rõ thiếu provenance; không suy đoán từ HEAD hiện tại.
- Giữ nguyên config.json, metadata.json, verifier.json và stdout/stderr tải về. File đã có trong run của nhánh gốc (kể cả provenance/review) không được sửa/xóa; bổ sung bằng sidecar mới. Không tự tạo PASS hoặc số điểm thiếu. Review/bổ sung thông tin ở file riêng như review.json hoặc provenance.json.
- Chỉ gọi full khi đúng kích thước bài, dung sai và số shot chính thức. Dev PASS không chứng minh full PASS; TIMEOUT không chứng minh mạch sai.
- SCORES.md: mỗi hướng một dòng; full/dev_5min là hai cột, link run tốt nhất tương ứng. Hai mode có thể chọn ra hai config khác nhau.
- Khi tính cải thiện, môi trường Python/package và hash verifier/dev harness phải khớp đối chứng theo checker; thiếu bằng chứng thì để `—`, không suy đoán hash hoặc sửa metadata gốc.
- Cải thiện (lần) = `baseline_score / candidate_score`; baseline `1.00×`, cao hơn tốt hơn. Chỉ so baseline cùng mode/profile/seed/số mẫu. Chưa có baseline phù hợp thì để `—`. Chỉ tính với PASS và chi phí hữu hạn, lớn hơn 0.
- Smoke/FAIL/TIMEOUT chỉ lưu results và kết luận cần thiết, không ghi điểm vào bảng. Không lấy điểm dev so trực tiếp với full.
- Chọn ứng viên cuối cần kiểm tra bổ sung độc lập (mẫu/seed chưa dùng chọn config, kiểm tra biên phù hợp) hoặc full; không khẳng định chất lượng chỉ từ nhiều lần tối ưu trên cùng bộ dev. So điểm ở profile mới cần đối chứng tương ứng; vẫn bàn giao để thành viên tự chấm Colab. Chưa có bằng chứng bổ sung thì ghi rõ giới hạn, không gọi đã xác nhận full.
- DESCRIPTION ghi mapping config/run tốt nhất của từng mode với SHA nguồn và link provenance/permalink. Khi sửa solution.py, giữ đúng phiên bản của mốc tốt cũ; JSON cùng tên chạy với code mới không bảo đảm tái lập run cũ. Không thay SHA của run cũ bằng HEAD mới.
- Phân tích giả thuyết, đánh đổi, rủi ro còn lại và đề xuất thử tiếp hay dừng. Cùng ý tưởng thì thêm config/sửa implementation theo phạm vi giao; đổi hypothesis đáng kể phải quay lại bước nhận hướng.
- Commit kết quả, provenance, bảng điểm và phân tích sau chấm. Khi tiếp tục, lặp: commit nguồn/config → compile → bàn giao chấm → commit kết quả/phân tích.

## 7. PR, conflict và merge

- Khi được giao hoàn tất hướng, push branch và tạo/cập nhật PR theo [mẫu](.github/pull_request_template.md). Nêu giải pháp cuối, bằng chứng, giới hạn và cách tái lập; dùng `Closes #<số>` nếu hướng thực sự hoàn tất.
- Đồng bộ nhánh chính bằng merge vào branch thử nghiệm, không rebase các commit đã được run tham chiếu. Với conflict ở EXPERIMENTS.md/SCORES.md, giữ đủ dòng của các hướng khác; chỉ cập nhật dữ liệu của mình. Không chấp nhận toàn bộ một phía để bỏ mất thay đổi của nhóm.
- Trước PR chạy `python scripts/check_repo.py`, `python -m unittest discover -s scripts/tests -v` bằng `.venv`, và `--base <base-ref> --branch <branch>` để kiểm tra diff khi có Git. Không thêm run mới vào danh sách legacy để né provenance.
- Kiểm tra link mô tả/results, score khớp JSON, cấu trúc/config, provenance và thay đổi ngoài phạm vi. Chạy các check có sẵn phù hợp; không tuyên bố có CI/branch protection nếu repository chưa cấu hình chúng.
- PR thử nghiệm dùng **merge commit** để giữ SHA nguồn trong lịch sử nhánh chính; không squash/rebase merge. Nếu repository không cho phép merge commit, báo điều kiện còn thiếu và dừng merge, không tự đổi phương thức hoặc bypass rule.
- Tác giả dùng prompt 06/08; teammate với phiên agent riêng dùng 07 để review và ghi SHA, 07b để đăng kết luận bằng tài khoản GitHub khác tác giả. Chỉ đăng review khi được giao bước 07b; approval phải gắn với HEAD hiện tại và còn hiệu lực. HEAD đổi thì cần review/approval lại; không lấy kết luận chat thay cho approval GitHub.
- Merge chỉ khi đã được người dùng giao quyền merge cho công việc này, review và các check bắt buộc của repository đã đạt. Không tự bỏ qua check, force-push nhánh chính hoặc merge khi conflict chưa xử lý.
- Đóng Issue sau merge khi phạm vi hoàn tất. Nếu chỉ bàn giao một phần thì giữ Issue mở hoặc chuyển giao; không đánh dấu completed cho phần chưa xong.
- Hướng không cải thiện vẫn giữ code/config, kết quả và kết luận cần thiết qua PR để tránh lặp lại nghiên cứu.

## 8. Báo cáo khi kết thúc lượt

Nêu ngắn gọn: đã đổi gì, ID/branch/commit liên quan, kiểm tra thực sự đã chạy, kết quả và việc còn lại. Khi bàn giao Colab, đưa đúng artifact và bước tiếp theo. Phân biệt rõ dự kiến, BUILT, dev PASS, full PASS và kết quả chấm chính thức. Không tự tạo Issue/commit/PR/điểm hoặc tuyên bố hoàn tất khi chưa có bằng chứng.
