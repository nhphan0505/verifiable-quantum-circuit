| Experiment | Full score ↓ | Dev_5min score ↓ | Cải thiện full (lần) ↑ | Cải thiện dev (lần) ↑ | Run full | Run dev |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| DQI-BASELINE | 24439463583672.93 | 61234661450380.1 | 1.00× | 1.00× | [20261107T094931Z-local-full-5ed1c6](../../results/dqi/DQI-BASELINE/baseline/full/20261107T094931Z-local-full-5ed1c6/verifier.json) | [20261107T092603Z-local-dev_5min-f901a5](../../results/dqi/DQI-BASELINE/baseline/dev_5min/20261107T092603Z-local-dev_5min-f901a5/verifier.json) |
| DQI-10 | — | 61648121312893.56 | — | 0.9933× | — | [20261108T052816Z-local-dev_5min-619295](../../results/dqi/DQI-10/merged/dev_5min/20261108T052816Z-local-dev_5min-619295/verifier.json) |
| DQI-19 | — | 53955451017897.38 | — | 1.1349× | — | [20261108T110610Z-local-dev_5min-9b8900](../../results/dqi/DQI-19/rank42/dev_5min/20261108T110610Z-local-dev_5min-9b8900/verifier.json) |

Ghi chú cho DQI-19: **1.1349×** là tỷ số số học giữa baseline dev lịch sử `61234661450380.1` và ứng viên `53955451017897.38`, được điền theo yêu cầu người dùng. Chưa xác nhận cải thiện trong điều kiện tương thích: Python patch và hash dev harness khác nhau; checker comparison hiện báo lỗi cho ô này. Xem [phân tích](DQI-19/DESCRIPTION.md).
