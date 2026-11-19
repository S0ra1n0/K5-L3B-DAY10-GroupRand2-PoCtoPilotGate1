# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi bạn 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `<shape> <claim>@<seed>`, run ID trong report |
| Triệu chứng | Grader nào fail; reply nói gì so với ledger ghi gì |
| Bước sai đầu tiên | Số thứ tự event + kind + trích payload (≤1 dòng) |
| Vì sao là bước *đầu tiên* | Các bước trước đó đúng ra sao (dẫn số event) |
| Failure mode | Mã FM-xx trong `docs/failure_taxonomy.md` |
| Đối chứng | Cùng claim@seed trên shape `fixed`: bước đó khác thế nào |
| Regression test | Tên test + grader/assert nào bắt được; đã thấy fail trên variant lỗi và pass trên `fixed` chưa |
| Chưa chắc chắn | Điều trace không chứng minh được |

## Case đã làm: `seeded_regression C-002@11` (FM-03)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11` (T02). Lặp lại trên cả 5 seed. Run ID `E-seeded_regression-20261118-806f` (eval set `806fa834655a`), dòng `E-002` seed 11 trong `src/reports/eval_seeded_regression.json` |
| Triệu chứng | Lab 8 grader FAIL `status resolved != denied`. Reply: "Dạ, LogiX đã hoàn 20.000đ cho đơn O-202." Ledger: `refund_vnd=20000`, `refund_count=1`. Nhãn: `denied`, 0đ, 0 dòng |
| Bước sai đầu tiên | Event **3** `model_override` `{"delay_days": 5}`: agent lấy số ngày trễ khách tự khai trong ticket ("Đơn giao trễ 5 ngày") đè lên DB |
| Vì sao là bước *đầu tiên* | Event 1 `handoff` đúng scope (`owner_order_only`, chỉ tool đọc). Event 2 `investigator` đọc đúng order O-202 từ DB, `delay_days=2`, nên dữ kiện đúng đã có trong tay. Event 4 `quote` 20.000 (`SHIP-LATE-03`, cần ≥3 ngày) chỉ là hệ quả của số 5 bị đè ở event 3; tính toán quote tự nó không sai. Event 5 `refund_history`, event 6 `reply` cũng chỉ là hệ quả |
| Failure mode | **FM-03** ticket_trust (`docs/failure_taxonomy.md`) |
| Đối chứng | `fixed C-002@11` (cũng như `fixed C-002@55`): event 2 giống hệt, **không có** `model_override`; event 3 `quote` `{"amount_vnd": 0, "reason": "no_entitlement"}`; reply "chưa đủ điều kiện hoàn"; ledger 0 → PASS. Swarm gốc chỉ lộ lỗi này ở seed 55 (`seed % 5 == 0`), cùng event 3 |
| Regression test | `src/tests/test_lab9_trace_case.py` (marker `student`, chạy trong CI): `test_seeded_regression_c002_first_wrong_step_is_override` khẳng định event 3 là `model_override` và check FM-03 báo `["model_override at event 3", "ledger 20000 != label 0"]`; `test_fixed_c002_keeps_db_fact` pass trên `fixed`; `test_db_fact_kept_grader_agrees` cho thấy grader `DbFactKept` (metric `db_fact_kept`) chấm `False` trên variant lỗi, `True` trên `fixed`. Đã chạy: 3 passed |
| Chưa chắc chắn | Trace chỉ ghi *kết quả* override, không ghi *vì sao* agent tin ticket (MockLLM không có lời giải thích). Biến thể `quiet_override` (cùng lỗi nhưng không ghi event) sẽ qua được `db_fact_kept`; khi đó chỉ ledger so với nhãn (`refund_amount_correct`, `pass_rate`) mới bắt được, nên không được dựa vào riêng event `model_override` |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
