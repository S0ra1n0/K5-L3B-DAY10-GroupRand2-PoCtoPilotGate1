# Judge audit

Chạy (trong `src/`): `python -m lab9.judge --csv <file> --audit 5`. Lớp dương = **FAIL** (việc của judge là *tìm* reply lỗi).
Judge chạy ở chế độ replay: phán quyết đã lưu trong CSV, không gọi model.

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok (`judge_tone_public.csv`) | 100 | 0.757 | 0.857 | 0.800 | **Đạt** (exit 0) | **dùng**, chỉ để theo dõi giọng văn, không chặn tiền |
| helpful (`judge_helpful_public.csv`) | 100 | 0.375 | 1.000 | 0.300 | **Không đạt**: κ và R dưới sàn (exit 1) | **loại**, không được dùng làm gate |

Ma trận nhầm lẫn (FAIL = dương):

| | tp | fp | fn | tn | Tỉ lệ FAIL judge thấy | Sau Rogan-Gladen | Tỉ lệ FAIL thật (nhãn người) |
|---|---|---|---|---|---|---|---|
| tone_ok | 24 | 4 | 6 | 66 | 0.28 | 0.30 | 0.30 |
| helpful | 9 | 0 | 21 | 70 | 0.09 | 0.30 | 0.30 |

## ≥5 case audit thủ công

### tone_ok: 10 bất đồng (6 fn, 4 fp)

| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 1 | H-008 "Em đã hoàn tiền cho anh rồi nha…" | PASS | FAIL | **Người** | Xưng "em", gọi "anh", thêm "nha" là quá suồng sã với khách khiếu nại. Rubric thêm: *xưng hô bắt buộc "LogiX" – "anh/chị"; "em/bạn/anh" đơn lẻ = FAIL* |
| 2 | H-017 "Dạ, bạn ơi LogiX đã hoàn 25.000đ… rồi nha." | PASS | FAIL | **Người** | Cùng lỗi xưng hô: có "Dạ" nhưng vẫn gọi khách là "bạn". Rubric: *có từ lễ phép ("Dạ", "ạ") không bù được xưng hô sai*. Thêm H-008, H-017 làm ví dụ FAIL (few-shot) |
| 3 | H-029 "Dạ, vui lòng chờ… không cần nhắn thêm." | PASS | FAIL | **Người** | Judge bám vào cụm lịch sự ở đầu câu, bỏ qua ý ra lệnh/chặn khách. Rubric: *chấm cả câu; câu cấm khách liên hệ ("không cần nhắn thêm", "khỏi hỏi") = FAIL dù mở đầu lễ phép* |
| 4 | H-042 "Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ." | FAIL | PASS | **Người** | Judge tự thêm điều kiện "phải xin lỗi" mà rubric không có. Rubric: *ngắn gọn mà đủ ý (kết quả + thời gian) vẫn PASS; xin lỗi không bắt buộc* |
| 5 | H-051 "Dạ, LogiX đã refund 90.000đ…" | FAIL | PASS | **Người** | Style guide CS của LogiX cho phép từ "refund". Rubric: *đưa danh sách từ tiếng Anh được phép (refund, ship, voucher) vào prompt* |
| 6 | H-063 "…đã hoàn 20.000đ và sẽ hoàn thêm cho anh/chị ạ." | PASS | FAIL | **Người** (nhưng sai tiêu chí) | Giọng văn ổn; lỗi thật là **hứa tiền ngoài kết quả hệ thống**, là chuyện nội dung/tiền, không phải tone. Không sửa rubric tone; chuyển sang check code (FM-08: reply nêu số/cam kết không có trong ledger). Gắn lại nhãn tone = PASS sau khi tách tiêu chí |
| 7 | H-070 "…đã hoàn 90.000đ cho đơn O-909 ạ 😂😂" | PASS | FAIL | **Người** | Emoji cười trong ngữ cảnh khiếu nại là thiếu tôn trọng. Rubric: *không emoji trong reply CS* (đây là luật cứng, có thể kiểm bằng regex trước khi gọi judge) |
| 8 | H-081 "Dạ, đơn O-107 chưa đủ điều kiện hoàn… ạ." | FAIL | PASS | **Judge** | Ghi chú CSV: người đọc nhầm ticket khi gán nhãn. **Sửa nhãn người** (không sửa rubric), ghi lại vào changelog nhãn. Đã thử: đổi H-081 thành FAIL thì κ 0.757 → 0.784, P 0.857 → 0.893, R 0.800 → 0.806 (không sửa CSV công khai, chỉ tính lại) |
| 9 | H-088 "Dạ, dạ, LogiX đã hoàn 40.000đ… ạ." | FAIL | PASS | **Người** | Lặp "Dạ" là lỗi gõ, không phải thái độ. Rubric: *lỗi chính tả/lặp từ nhỏ không làm FAIL tone* |
| 10 | H-094 "Da, LogiX da hoan 40.000đ… xin loi vi su bat tien." | PASS | FAIL | **Người** | Mất dấu tiếng Việt (dịch máy) khiến khách khó đọc, trông thiếu chuyên nghiệp. Rubric: *reply tiếng Việt không dấu = FAIL* (cũng kiểm được bằng code) |

Tổng kết tone: 8/10 người đúng, 1/10 judge đúng (H-081, lỗi nhãn), 1/10 là sai tiêu chí (H-063). FN của judge dồn vào
một kiểu lỗi: **bị đánh lừa bởi từ lễ phép bề mặt** ("Dạ", "vui lòng") mà bỏ qua xưng hô/ý ra lệnh. FP dồn vào **tự đặt luật không có trong rubric** (xin lỗi, cấm tiếng Anh, lỗi gõ).

### helpful: 21 bất đồng, tất cả là fn (người FAIL, judge PASS)

| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 11 | HL-015 "Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ." (ledger 40.000đ) | PASS | FAIL | **Người** | Judge chỉ thấy reply, **không thấy ledger**, nên không thể biết số tiền sai. Không sửa được bằng rubric. Chuyển sang grader code FM-08 (so số trong reply với `snapshot.refund_vnd`) |
| 12 | HL-016 reply xin lỗi 3 câu dài, "hoàn 55.000đ cho đơn O-404" (ledger 35.000đ) | PASS | FAIL | **Người** | Cùng lỗi sai tiền, cộng thêm **thiên vị độ dài/xin lỗi**: reply càng nhiều câu xin lỗi càng dễ được PASS. 13/18 case "sai tiền" là reply dài kiểu này |
| 13 | HL-043 "…rất tiếc… đã hoàn 35.000đ cho đơn O-202…" (ledger 20.000đ) | PASS | FAIL | **Người** | Đúng mẫu FM-08 trong `probe_misreport C-008` (reply 35.000, ledger 20.000). Bằng chứng: tiền phải chấm bằng code |
| 14 | HL-047 "Ok bạn, đơn O-515 xử lý rồi nhé." | PASS | FAIL | **Người** | Sai xưng hô và không nói kết quả cụ thể (hoàn bao nhiêu). Rubric helpful: *phải nêu kết quả (số tiền hoặc lý do từ chối) + bước tiếp theo*; xưng hô thuộc tiêu chí tone |
| 15 | HL-091, HL-097 "Ok bạn, đơn O-xxx xử lý rồi nhé." | PASS | FAIL | **Người** | Cùng mẫu với #14 (3/3 case "sai xưng hô" đều bị bỏ qua) |

Recall của helpful theo từng loại lỗi người gán: *sai tiền* 0/18, *sai xưng hô* 0/3, *giọng cụt* 4/4, *không hỏi lại mã đơn* 3/3, *lạc đề* 2/2.
Judge chỉ bắt được lỗi **lộ ra trên bề mặt văn bản**; mọi lỗi cần đối chiếu với dữ liệu ngoài reply thì nó bỏ sót toàn bộ.

## Kết luận

- **tone_ok: dùng được** (κ=0.757, P=0.857, R=0.800, đạt cả 3 sàn). Chỉ dùng làm metric theo dõi chất lượng giọng văn, không đặt
  blocking cho tiền/approval. Sửa rubric theo #1–#5, #7, #9, #10 rồi calibrate lại trên tập nhãn mới; sửa nhãn H-081.
- **helpful: loại, không được làm gate.** κ=0.375 < 0.6 và R=0.300 < 0.7, dù P=1.000. Ma trận nhầm lẫn: fn=21, fp=0. Judge này
  *không bao giờ báo nhầm* nhưng **bỏ sót 70% reply lỗi**, đúng loại lỗi đắt nhất (18 reply nói sai số tiền, 0 bị bắt). Nếu dùng nó
  làm gate, một PR làm agent nói sai tiền (FM-08) vẫn được merge. Precision cao ở đây không nói lên gì: judge càng ít khi dám nói
  FAIL thì P càng dễ đạt 1.0, còn R mới cho biết nó bắt được bao nhiêu lỗi.
- **Rogan-Gladen không cứu được helpful.** Tỉ lệ lỗi quan sát 0.09 hiệu chỉnh thành 0.30, khớp tỉ lệ thật. Nhưng hiệu chỉnh chỉ
  đúng cho *tỉ lệ tổng* trên tập đã calibrate; gate cần biết *trial nào* lỗi và Δ giữa hai phiên bản trên cùng item. Với R=0.3,
  một regression làm tăng lỗi sai tiền gần như không làm đổi phán quyết của judge, nên Δ ≈ 0 và gate không chặn.
- **Hành động:** chấm "reply nói đúng số tiền" bằng grader code (metric FM-08, M3), không bằng judge. Tách rubric helpful thành:
  (a) phần đối chiếu dữ liệu → code; (b) phần "nêu kết quả + bước tiếp theo" → judge, calibrate lại riêng.
- **Rủi ro còn lại:** judge chỉ được kiểm trên dữ liệu replay đã công khai (100 dòng mỗi tiêu chí, có thể đã bị "học thuộc" khi
  sửa rubric); cần bộ nhãn người mới, held-out, để biết κ/P/R thật. Nhãn người cũng có lỗi (H-081), nên cần ≥2 người gán nhãn
  và đo κ giữa người với người trước khi coi nhãn người là chuẩn.
