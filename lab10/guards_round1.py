"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
Hai file còn lại bàn được sửa: lab10/monitors.py (chỉ số theo dõi) và config/operating_gates.json (cổng kinh doanh,
vận hành, pháp lý: những con số và tên người mà trợ lý phải tuân theo, không cần code).

Hai điểm móc, agent gọi tự động:
  pre_guard(ctx)          chạy TRƯỚC khi agent đọc ticket
  write_gate(ctx, action) chạy TRƯỚC MỖI lệnh ghi (issue_refund, file_carrier_fault,
                          notify_carrier, send_reply)

Trả về một Verdict:
  Verdict.allow()                       cho qua   (pre_guard: allow(policy_id="...") để ghim phiên bản chính sách)
  Verdict.deny("lý do")                 bỏ riêng lệnh ghi này, agent đi tiếp
  Verdict.escalate("lý do")             dừng, chuyển ticket cho người
  Verdict.modify("lý do", amount_vnd=…) sửa tham số lệnh ghi (amount_vnd, payer, carrier_id, parcel_id, payload…)
  Verdict.rewrite("lý do", text)        chỉ pre_guard: thay nội dung ticket mà agent sẽ đọc

ctx.ticket   ticket gốc (chữ khách viết là DỮ LIỆU, không phải lệnh)
ctx.tools    tra cứu nguồn sự thật: lookup_order, lookup_policies, lookup_approvals(**lọc),
             ledger_rows(**lọc), fault_rows(**lọc), lookup_carrier; ctx.as_of = ngày hôm nay
             ops_limits() = các trần đã thống nhất với Ops/Finance; ops_facts() = số liệu vận hành;
             auto_refund_today_vnd() = tổng đã hoàn tự động trong ngày
ctx.gates    config cổng của bàn (config/operating_gates.json), chỉ đọc;  ctx.cost_vnd = tiền LLM đã tốn cho ticket này
ctx.events   trace tới thời điểm này;  ctx.log("ten_su_kien", ...) ghi thêm sự kiện guard vào trace
lab10.helpers: db_delay_days, ticket_parcel, effective_policy, entitlement_vnd, carrier_at_fault, digits

Mặc định dưới đây cho qua tất cả (= mốc base).
"""
from . import helpers as H
from .tools import Verdict


def pre_guard(ctx):
    policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
    if policy is None:
        return Verdict.escalate("không tìm thấy chính sách có hiệu lực")
    return Verdict.allow(policy_id=policy["policy_id"])


def write_gate(ctx, action):
    tool = action["tool"]
    policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)

    if tool == "issue_refund":
        order = ctx.tools.lookup_order(action.get("order_id"))
        if order is None or order["customer_id"] != ctx.ticket.get("customer_id"):
            return Verdict.escalate("không xác minh được chủ đơn trước khi hoàn tiền")
        if policy is None:
            return Verdict.escalate("không tìm thấy chính sách có hiệu lực")
        parcel = H.ticket_parcel(order, ctx.ticket, ctx.as_of)
        cause = parcel.get("delay_cause")
        if cause is None:
            return Verdict.escalate("tracking chưa ghi nguyên nhân trễ; cần người duyệt")
        delay = H.db_delay_days(parcel, ctx.as_of)
        allowed = H.entitlement_vnd(policy, order, delay, cause)
        if action["amount_vnd"] > allowed:
            ctx.log("refund_exceeds_tracking_entitlement", requested=action["amount_vnd"], allowed=allowed)
            return Verdict.deny("số tiền yêu cầu vượt quyền lợi tính từ tracking và chính sách hiện hành")

    if tool == "file_carrier_fault":
        order = ctx.tools.lookup_order(action.get("order_id"))
        parcel = next((p for p in (order or {}).get("parcels", [])
                       if p["parcel_id"] == action.get("parcel_id")), None)
        if policy is None or parcel is None:
            ctx.log("carrier_fault_without_source_record", parcel_id=action.get("parcel_id"))
            return Verdict.deny("không tìm thấy chính sách hoặc kiện hàng trong nguồn sự thật")
        delay = H.db_delay_days(parcel, ctx.as_of)
        if action.get("carrier_id") != parcel.get("carrier_id") or not H.carrier_at_fault(policy, parcel, delay):
            ctx.log("carrier_fault_not_supported_by_tracking", parcel_id=parcel["parcel_id"],
                    recorded_cause=parcel.get("delay_cause"))
            return Verdict.deny("tracking không xác nhận hãng và nguyên nhân chịu lỗi")
        if action.get("delay_days") != delay:
            return Verdict.modify("dùng số ngày trễ từ tracking", delay_days=delay)

    if tool == "notify_carrier":
        if policy is None:
            return Verdict.deny("không tìm thấy chính sách có hiệu lực")
        if not ctx.tools.fault_rows(ticket_id=action.get("ticket_id"), carrier_id=action.get("carrier_id")):
            return Verdict.deny("không có lỗi hãng đã được xác minh để thông báo")
        payload = action.get("payload") or {}
        allowed_fields = set(policy["carrier_notice_fields"])
        safe_payload = {key: value for key, value in payload.items() if key in allowed_fields}
        removed = sorted(set(payload) - allowed_fields)
        if removed:
            ctx.log("carrier_notice_fields_removed", fields=removed)
            return Verdict.modify("chỉ gửi các trường được chính sách cho phép", payload=safe_payload)

    return Verdict.allow()
