"""★ FILE ĐỘI SỬA (2/3): chỉ số theo dõi (monitor). Thêm ÍT NHẤT MỘT chỉ số bắt được sự cố của bàn.

Mỗi monitor nhận danh sách trial (KHÔNG có nhãn đúng/sai, giống production) và trả về một số.
Một trial = {"ticket_id", "seed", "day", "status", "amount_vnd", "ticket", "events", "ledger", "faults", "outbound",
             "arrive_min", "warehouse", "cost_vnd", "review_kind", "queue_wait_min", "queue_stuck"}
  "day"            một ngày vận hành giả lập: các ticket cùng "day" và cùng "seed" chạy nối nhau trên cùng một sổ cái
  "arrive_min"     phút ticket tới trong ca (0..480)          "warehouse"   kho của đơn
  "cost_vnd"       tiền LLM + nền tảng đã tốn cho ticket      "review_kind" None / "escalated" (trợ lý chuyển người) /
  "queue_wait_min" số phút chờ người duyệt (None nếu không vào hàng chờ)     "recheck" (nhân viên tự kiểm lại)
Chỉ số có thể là kỹ thuật (tỉ lệ model đè số trong ticket lên DB), vận hành (số ca cần người trong giờ đông nhất),
hay kinh doanh (tỉ lệ ticket trợ lý đọc xong vẫn phải chuyển người).

lab10.grade kiểm: monitor chạy không lỗi, và giá trị trên gói sự cố khác giá trị trên bộ nền,
tức là monitor "sáng đèn" khi sự cố xảy ra.
"""


def escalation_rate(trials):
    return sum(t["status"] == "escalated" for t in trials) / max(1, len(trials))


def model_override_delay_rate(trials):
    """Tỉ lệ ticket mà model đè số ngày trễ khách khai lên tracking DB (sự kiện model_override)."""
    if not trials:
        return 0.0
    count = sum(any(e.get("type") == "model_override" for e in t.get("events", [])) for t in trials)
    return round(count / len(trials), 4)


def carrier_fault_rate(trials):
    """Tỉ lệ ticket dẫn tới việc ghi lỗi hãng vận chuyển (bắt được việc dồn lỗi hãng)."""
    if not trials:
        return 0.0
    count = sum(bool(t.get("faults")) for t in trials)
    return round(count / len(trials), 4)


MONITORS = {
    "escalation_rate": escalation_rate,     # có sẵn; KHÔNG tính là metric mới của đội
    "model_override_delay_rate": model_override_delay_rate,  # chỉ số mới 1: bắt lỗi khách khai khống
    "carrier_fault_rate": carrier_fault_rate,                # chỉ số mới 2: bắt lỗi dồn hãng
}
STARTER_MONITORS = ("escalation_rate",)
