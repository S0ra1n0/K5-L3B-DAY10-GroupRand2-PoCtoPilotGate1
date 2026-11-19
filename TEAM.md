# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): `GroupRand2`
- Lớp: `L3B`
- Repo của bàn: `K5-L3B-DAY10-GroupRand2-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8): `S1`

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; bàn 3 người thì để trống dòng 4. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 | Nguyễn Lê Đăng Khoa | 2A202603847 | Kỹ sư cổng |        x     |
|   2 |           |      |     |             |
|   3 |  Nguyễn Minh Quang   |  2A202603791    | Kỹ sư cổng    |             |
|   4 | Nguyễn Ngọc Quang | 2A202603773 | Vận hành và pháp lý |             |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## HoVaTen-MSSV

### Phần việc phụ trách

Vai trong bàn; câu nào của đề, mục nào của phiếu A/B/C, file nào (`lab10/guards.py`, `config/operating_gates.json`, …).

### Đóng góp cụ thể

...

### Bằng chứng

Mã commit, mã lần chạy (`runs/<mã>`), dòng trong phiếu.

### Exit ticket

Một điều học được, một điều còn chưa chắc.

## NguyenLeDangKhoa-2A202603847

### Phần việc phụ trách

- **Vai:** Kỹ sư cổng (Gate Engineer), trưởng nhóm.
- **File/mục phụ trách chính:** vòng 1 `lab10/guards.py`; Phiếu B mục B7.1–B7.3 (câu 2.6–2.8); Phiếu C mục C6 (câu 3.4); tham gia chốt quyết định v1 tại Phiếu B mục B8.
- **Phạm vi đóng góp:** dựng phiên bản cổng phòng ngừa ban đầu và behavioral tickets; phân tích fault tree trước khi sửa cho thẻ S1. Các thay đổi code/monitor vòng 2 trong commit `dc150e9` do Nguyễn Minh Quang thực hiện.

### Đóng góp cụ thể

- Xây dựng bản cổng phòng ngừa đầu tiên cho các thao tác ghi: ghim chính sách hiệu lực, đối chiếu hoàn tiền với tracking, xác minh ghi lỗi hãng và giới hạn trường thông báo cho hãng.
- Hoàn thiện Phiếu B mục B7.1–B7.3: mô tả các cổng, ghi hai bước tránh rò rỉ dữ liệu khi chỉnh trên bộ chấm, và thiết kế hai ticket hiểm để kiểm tra lời khai ngày trễ so với tracking cùng dữ liệu người nhận quà gửi cho hãng.
- Lập fault tree trước sửa cho S1 ở Phiếu C mục C6: phân tích ba nhánh gồm khách khai đè tracking, tracking thiếu `delivered_date` dù kiện đã giao, và lỗi của GHSH dồn vượt giới hạn vận hành.
- Cùng bàn so sánh bằng chứng của mốc prepared với tiêu chí đã ký và chốt quyết định v1 là **Thu hẹp**, giới hạn pilot ở HN/CT và để ca không xác định được kho/đơn đi theo quy trình làm tay.
- **Sử dụng AI:** có dùng Copilot hỗ trợ đọc trace, soạn nội dung và phác thảo cổng. Commit ban đầu có thêm test vào `tests/test_public.py`; sau đó file test đã được khôi phục về bản gốc và không nằm trong thay đổi cuối cùng.

### Bằng chứng

- **Commit:** `bd26298` (câu 2.6–2.8); `713287a` (fault tree câu 3.4); `f2b57ec` (chốt v1).
- **Mã lần chạy:** baseline `R-base-before-20261119-161158-bde05c`; mốc prepared S1 `R-S1-prepared-20261119-171919-159538`. Bản tự kiểm tra sau đó ghi `R-S1-grade-20261119-195313-a25689`; phần code vòng 2 và monitor thuộc đóng góp của Quang.
- **Vị trí:** Phiếu B mục B7.1–B7.3 và B8; Phiếu C mục C6.

### Exit ticket

- **Một điều học được:** cổng trước thao tác ghi cần đối chiếu với nguồn dữ liệu có thẩm quyền và giới hạn quyền của agent; chỉ nhìn câu trả lời của model không đủ để bảo vệ khách hàng và đối tác.
- **Một điều còn chưa chắc:** nếu tracking thiếu hoặc sai ngày giao, cần cơ chế đối soát với hãng và quy trình cập nhật dữ liệu nào để vừa tránh ghi lỗi oan vừa không từ chối các khoản hoàn hợp lệ?

## NguyenMinhQuang-2A202603791

### Phần việc phụ trách

- **Vai:** Kỹ sư cổng (Gate Engineer).
- **File chính phụ trách:** `lab10/guards.py`, `lab10/monitors.py`.
- **Mục phiếu phụ trách:**
  - Vòng 1: Phiếu B mục B0 & B1 (câu 2.1 - chạy mốc base, phân tích tự chặn vs người duyệt), mục B2 (câu 2.2 - dò trace T-002@55, phân loại lỗi chìm, tìm nguồn và hướng xử lý), mục B6 (câu 2.5 - pre-mortem 4 lăng kính).
  - Vòng 2: Phiếu C mục C0 (nhật ký lần chạy vòng 2), mục C7 (câu 3.5 - thiết kế và code cổng sửa các nhánh của fault tree), mục C8 (câu 3.6 - xây dựng telemetry monitor production).

### Đóng góp cụ thể

1. **Vòng 1 (Khối 2A):**
   - Chạy và phân tích kết quả mốc baseline `R-base-before-20261119-161158-bde05c`, phát hiện các rủi ro vi phạm an toàn tài chính và đối tác (hoàn sai 20.000đ, phạt oan 1 lỗi cho hãng VNX).
   - Dò trace chi tiết ca `T-002@55`: xác định chính xác đây là "lỗi chìm" do model đặt sai trọng số, lấy số ngày khách tự khai (5 ngày) đè lên tracking DB (2 ngày) kích hoạt `model_override`.
   - Đóng góp phân tích Pre-mortem 4 lăng kính (kỹ thuật, kinh doanh, con người/vận hành, pháp lý), nhận diện trước các nguy cơ vỡ ngân sách bồi hoàn, quá tải hàng chờ CSKH, và nguy cơ đình chỉ tuyến đối tác vận chuyển.
2. **Vòng 2 (Khối 3 - Sự cố S1):**
   - Đo mốc prepared khi nhận thẻ S1, phân tích nguyên nhân lỗi ghi oan cho hãng GHSH: kiện thiếu `delivered_date` dù `status: DELIVERED` (O-2120, O-2121), khách khai khống ngày trễ (S1-03), và dồn lỗi vượt trần 2 lỗi/ngày của hãng (S1-40..S1-43).
   - Trực tiếp lập trình bổ sung trong `lab10/guards.py`:
     - Nhánh `issue_refund`: dùng `Verdict.modify` ép số tiền hoàn về `amount_vnd=allowed` theo tracking DB thay vì từ chối cả khoản (sửa thành công ca `S1-03` đạt hoàn 30.000đ); phát hiện `status: DELIVERED` nhưng thiếu `delivered_date` thì `Verdict.escalate` chuyển người duyệt, ngăn hoàn tiền khống.
     - Nhánh `file_carrier_fault`: kiểm tra thiếu `delivered_date` thì `Verdict.deny` không tự ghi lỗi; đếm số lỗi trong ngày của hãng qua `fault_rows`, chạm trần 2 lỗi/ngày thì `Verdict.deny` từ chối tự ghi thêm.
   - Trực tiếp lập trình và đăng ký trong `lab10/monitors.py` 2 chỉ số theo dõi production: `model_override_delay_rate` (đo tần suất model override ngày trễ) và `carrier_fault_rate` (đo tỉ lệ ticket ghi lỗi hãng), cả 2 đều sáng đèn rõ rệt ở mốc before và after.
   - Hoàn thiện chi tiết các mục C0, C7, C8, C9 trong Phiếu C ([templates/form-c-incident.md](templates/form-c-incident.md)).
   - Chạy kiểm thử hồi quy và tự kiểm tra bằng `lab10.grade --incident S1`, đưa kết quả đạt `PASS-VISIBLE` tuyệt đối (pass_rate 1.0 trên S1 và bộ nền, 0 lỗi oan, 0 hoàn sai).

### Bằng chứng

- **Mã commit Git:**
  - `4951cac`: `docs:add Phieu B 2A (baseline run and T-002 triage)`
  - `f2b3e88`: `docs: finish 2A`
  - `dc150e9`: `feat: hoàn thành 3.5 và 3.6 (guards, monitors, Phiếu C C7-C9 cho S1)`
- **Mã lần chạy (`runs/<mã>`):**
  - Mốc base ban đầu: `R-base-before-20261119-161158-bde05c`
  - Mốc prepared sự cố S1: `R-S1-prepared-20261119-171919-159538`
  - Mốc after sự cố S1 (sau sửa code): `R-S1-after-20261119-184342-30d810`
  - Báo cáo tự kiểm tra đạt chuẩn: `R-S1-grade-20261119-184716-a25689` / `R-S1-grade-20261119-195313-a25689` (`PASS-VISIBLE`, 1 integrity ✅, 2 criteria ✅, 3 visible ✅, 5 regression ✅, 6 monitor ✅)
  - Kiểm tra regression bộ nền: `R-base-after-20261119-184337-30d810` (pass_rate 1.0)
- **Dòng trong phiếu:**
  - Phiếu B: Mục B0 (dòng 1), B1 (câu 2.1), B2 (bảng soát lỗi T-002), B6 (pre-mortem).
  - Phiếu C: Mục C0 (nhật ký 4 lần chạy), C7 (bảng 3.5 cho 3 nhánh), C8 (bảng thông số 3.6), C9 (fault tree sau sửa).

### Exit ticket

- **Một điều học được:** Cổng cấp hệ thống (system-level write gates) nằm ngoài prompt và model là phòng tuyến quyết định sống còn; các lỗi model override hay dữ liệu tracking mâu thuẫn hoàn toàn có thể được ngăn chặn triệt để khi write gate đối chiếu với nguồn sự thật (Single Source of Truth) và trần vận hành (ops limits).
- **Một điều còn chưa chắc:** Trong môi trường triển khai thực tế (pilot thật), nếu bản thân dữ liệu tracking DB bị nhập bù sai lệch hoặc có độ trễ đồng bộ từ tài xế bên ngoài, write gate vẫn có thể bị "mù" nếu chỉ coi DB là chân lý tuyệt đối mà không có kênh đối soát độc lập thời gian thực.

## NguyenNgocQuang-2A202603773

### Phần việc phụ trách

- **Vai:** Vận hành và pháp lý.
- **File chính:** `config/operating_gates.json` (mục `operations`, `legal`), `submission/submission.json`.
- **Mục phiếu:** Phiếu A câu 1.2, 1.4; Phiếu B mục B4, B5 (HAZOP) và câu 2.10 (runbook, cổng vận hành); Phiếu C header, câu 3.1, 3.3, mục C10, C11 và C12 (quyết định v2, ba dòng bắt buộc).

### Đóng góp cụ thể

- Phiếu A: viết câu 1.2 và 1.4.
- Phiếu B: làm HAZOP ở B4, B5 (guideword PERTURBED, INCAPABLE); câu 2.10: điền `operations` (PIC NV-TUNG, người duyệt NV-HANH, 1 người trực, 6 ca/giờ, chờ tối đa 60 phút, các điều kiện dừng, kênh `#logix-refund-pilot-alerts`) và `legal` (chặn `recipient_contact`, `customer_note` gửi hãng; bắt buộc có nguyên nhân trong tracking khi ghi lỗi hãng) trong `config/operating_gates.json`; cập nhật runbook theo phạm vi v1.
- Phiếu C (S1): câu 3.1, 3.3; Risk register và runbook ở C10, C11; C12: chạy lại `lab10.grade --incident S1` trên code cuối, chọn **Thu hẹp** (chỉ kho HN), ghi ba dòng bắt buộc và điền `submission/submission.json`.
- Sửa lỗi toàn vẹn: khôi phục `tests/test_public.py` về bản gốc, giữ các file đã ký/chốt đúng từng byte (CRLF) bằng `.gitattributes`.
- Sau review: thêm cổng trong `lab10/guards.py` (bỏ số ngày khách tự khai ở `pre_guard`; chặn hoàn lặp, đặt lại người trả về LOGIX, kiểm phê duyệt ở `issue_refund`) và cập nhật C7, C9, C12 cho khớp.
- **Sử dụng AI:** có dùng Claude Code hỗ trợ đọc report, review code, sửa cổng, soạn C12 và kiểm bài nộp; bàn đã xem lại số liệu trong report.

### Bằng chứng

- **Commit:** `07c508b` (1.2, 1.4), `e608035` (B4, B5), `fcf5e00` (2.10), `a709e15` (header Phiếu C, runbook), `8d40c10` (3.1, 3.3, C10, C11), `d02eb26` (khôi phục file khoá).
- **Mã lần chạy:** report tự kiểm tra `R-S1-grade-20261119-222152-2a0891` (PASS-VISIBLE); base `R-S1-before-20261119-222152-2a0891`, prepared `R-S1-prepared-20261119-222152-2a0891`, after `R-S1-after-20261119-222152-2a0891`.
- **Vị trí:** Phiếu A câu 1.2, 1.4; Phiếu B B4, B5, B7.5–B7.6; Phiếu C 3.1, 3.3, C10–C12.

### Exit ticket

- **Một điều học được:** cổng con số và con người (người duyệt, điều kiện dừng, phạm vi pilot) quan trọng ngang cổng code; report cho phép "Tiếp tục" chưa có nghĩa là nên mở rộng khi độ phủ chỉ khoảng 38%.
- **Một điều còn chưa chắc:** với 1 người trực, 6 ca/giờ, hàng chờ có đủ khi tracking thật hay thiếu ngày giao làm tỉ lệ chuyển người duyệt tăng vượt 0,25 không.
