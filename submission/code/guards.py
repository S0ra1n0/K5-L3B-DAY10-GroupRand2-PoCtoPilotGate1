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
import re

from . import helpers as H
from .tools import Verdict


# Số ngày trễ khách tự khai ("trễ 9 ngày", "chỉ chậm 2 hôm", "late 5 days"): không phải nguồn sự thật.
_CLAIMED_DAYS = re.compile(r"\d{1,3}\s*(?:ngày|ngay|days?|hôm|hom)\b", re.I)


def pre_guard(ctx):
    policy = H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)
    if policy is None:
        return Verdict.escalate("không tìm thấy chính sách có hiệu lực")
    text = ctx.ticket.get("text") or ""
    cleaned = _CLAIMED_DAYS.sub("[số ngày do khách khai, hệ thống dùng tracking]", text)
    if cleaned != text:
        # Khai nhiều hơn hay ít hơn tracking đều sai tiền (hoàn dư / hoàn thiếu): bỏ con số trước khi model đọc.
        ctx.log("claimed_delay_removed", claims=_CLAIMED_DAYS.findall(text))
        return Verdict.rewrite("bỏ số ngày trễ khách tự khai; độ trễ lấy từ tracking", cleaned,
                               policy_id=policy["policy_id"])
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
        if parcel.get("status") == "DELIVERED" and not parcel.get("delivered_date"):
            ctx.log("delivered_without_date_escalate", parcel_id=parcel.get("parcel_id"))
            return Verdict.escalate("kiện đã giao nhưng thiếu ngày giao trong tracking: cần người duyệt")
        cause = parcel.get("delay_cause")
        if cause is None:
            return Verdict.escalate("tracking chưa ghi nguyên nhân trễ; cần người duyệt")
        # Không hoàn hai lần: lệnh ghi lặp của chính ticket này (agent ghi lại khi LLM confirm lỗi 429) thì bỏ;
        # đơn đã có khoản hoàn từ ticket khác (cờ refund_status chỉ cập nhật theo batch đêm) thì chuyển người.
        if ctx.tools.ledger_rows(ticket_id=action.get("ticket_id"), order_id=order["order_id"]):
            ctx.log("refund_duplicate_write_blocked", ticket_id=action.get("ticket_id"))
            return Verdict.deny("ticket này đã có khoản hoàn trong sổ cái: không ghi lặp")
        if ctx.tools.ledger_rows(order_id=order["order_id"]):
            ctx.log("refund_order_already_refunded", order_id=order["order_id"])
            return Verdict.escalate("đơn đã có khoản hoàn trong sổ cái: cần người duyệt trước khi hoàn thêm")
        delay = H.db_delay_days(parcel, ctx.as_of)
        allowed = H.entitlement_vnd(policy, order, delay, cause)
        changes = {}
        if action.get("payer", "LOGIX") != "LOGIX":
            # Chỉ chữ trong ticket / ghi chú đơn bảo "shop trả": không phải căn cứ để trừ tiền shop.
            ctx.log("refund_payer_reset", requested_payer=action.get("payer"))
            changes["payer"] = "LOGIX"
        if action["amount_vnd"] > allowed:
            ctx.log("refund_exceeds_tracking_entitlement", requested=action["amount_vnd"], allowed=allowed)
            if allowed <= 0:
                return Verdict.deny("số tiền yêu cầu vượt quyền lợi tính từ tracking và chính sách hiện hành")
            changes["amount_vnd"] = allowed
        amount = changes.get("amount_vnd", action["amount_vnd"])
        approval_id = action.get("approval_id")
        if approval_id and amount > policy["auto_limit_vnd"]:
            appr = next(iter(ctx.tools.lookup_approvals(approval_id=approval_id)), None)
            problem = None
            if appr is None:
                problem = "không tìm thấy phê duyệt"
            elif appr.get("status") != "valid":
                problem = f"phê duyệt ở trạng thái {appr.get('status')}"
            elif appr.get("expires_at") and appr["expires_at"] < ctx.as_of:
                problem = "phê duyệt đã hết hạn"
            elif appr.get("order_id") != order["order_id"]:
                problem = "phê duyệt thuộc đơn khác"
            elif amount > appr.get("max_vnd", 0):
                problem = "số tiền vượt mức phê duyệt"
            if problem:
                ctx.log("refund_approval_invalid", approval_id=approval_id, problem=problem)
                return Verdict.escalate(problem + ": cần người duyệt")
        elif approval_id:
            changes["approval_id"] = None          # đã về dưới hạn mức tự động: không gắn phê duyệt không cần thiết
        if changes:
            return Verdict.modify("điều chỉnh theo tracking, chính sách và người trả đúng", **changes)

    if tool == "file_carrier_fault":
        order = ctx.tools.lookup_order(action.get("order_id"))
        parcel = next((p for p in (order or {}).get("parcels", [])
                       if p["parcel_id"] == action.get("parcel_id")), None)
        if policy is None or parcel is None:
            ctx.log("carrier_fault_without_source_record", parcel_id=action.get("parcel_id"))
            return Verdict.deny("không tìm thấy chính sách hoặc kiện hàng trong nguồn sự thật")
        if parcel.get("status") == "DELIVERED" and not parcel.get("delivered_date"):
            ctx.log("carrier_fault_missing_delivered_date", parcel_id=parcel["parcel_id"])
            return Verdict.deny("kiện đã giao nhưng thiếu ngày giao: không tự ghi lỗi")
        delay = H.db_delay_days(parcel, ctx.as_of)
        if action.get("carrier_id") != parcel.get("carrier_id") or not H.carrier_at_fault(policy, parcel, delay):
            ctx.log("carrier_fault_not_supported_by_tracking", parcel_id=parcel["parcel_id"],
                    recorded_cause=parcel.get("delay_cause"))
            return Verdict.deny("tracking không xác nhận hãng và nguyên nhân chịu lỗi")
        carrier_id = action.get("carrier_id")
        faults_today = len(ctx.tools.fault_rows(carrier_id=carrier_id))
        max_faults = ctx.tools.ops_limits().get("max_auto_strikes_per_carrier_per_day", 2)
        if faults_today >= max_faults:
            ctx.log("carrier_fault_daily_cap_exceeded", carrier_id=carrier_id, faults_today=faults_today, cap=max_faults)
            return Verdict.deny(f"hãng {carrier_id} đã chạm trần {max_faults} lỗi tự động trong ngày: không ghi thêm tự động")
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
