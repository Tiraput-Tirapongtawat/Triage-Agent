# Support Ticket Triage Policy (Checkpoint 1)

## 1) เป้าหมายของ Agent
- รับ ticket conversation (หลายข้อความ) + customer context
- ตัดสินใจ triage อย่างสม่ำเสมอและตรวจสอบย้อนกลับได้
- คืนผลลัพธ์ที่พร้อมส่งต่อทีมปฏิบัติการทันที

## 2) Output Contract (ฉบับที่ยึดใช้)
Agent ต้องคืนค่าเป็น JSON ตามฟิลด์ด้านล่าง:

```json
{
  "ticket_id": "string",
  "urgency": "critical|high|medium|low",
  "product": "string",
  "issue_type": "billing|outage|auth|bug|feature_request|how_to|other",
  "sentiment": "angry|frustrated|neutral|positive",
  "recommended_docs": [
    {
      "doc_id": "string",
      "title": "string",
      "reason": "string"
    }
  ],
  "next_action": "auto_respond|route_specialist|escalate_human",
  "route_team": "billing|sre|support|product|none",
  "confidence": 0.0,
  "rationale": "string"
}
```

## 3) Urgency Rubric
### `critical`
- ระบบใช้งานไม่ได้ในวงกว้าง/หลายผู้ใช้/ลูกค้าองค์กร
- กระทบรายได้หรือดีลในชั่วโมงเดียวกัน
- สัญญาณ outage, auth failure, error 5xx ระดับระบบ

### `high`
- ปัญหาเงิน/การคิดเงินซ้ำ/เข้าถึงแพ็กเกจไม่ได้
- ผู้ใช้ทำซ้ำหลายครั้งและกำลัง escalation (เช่น ขู่ chargeback)
- มี deadline เร่งด่วน (ภายในวันเดียว)

### `medium`
- บั๊กที่ยังมี workaround บางส่วน
- กระทบผู้ใช้รายเดียวหรือวงจำกัด
- ไม่ใช่ outage ระดับระบบ

### `low`
- คำถาม how-to / feature request / enhancement
- ไม่กระทบการใช้งานหลัก

## 4) Next Action Policy
- `critical` -> `escalate_human` + `route_team=sre`
- `high` -> `route_specialist` (เช่น billing) และส่ง acknowledgment อัตโนมัติทันที
- `medium` -> `route_specialist` หรือ `auto_respond` ตาม confidence ของ KB
- `low` -> `auto_respond`, ถ้าเป็นฟีเจอร์ขอเพิ่มให้ส่งต่อ `product`

## 5) Tool Usage Policy (ขั้นต่ำ 2 tools)
ลำดับการเรียก tool:
1. `customer_history_lookup`
  - คืน plan, tenure, previous_tickets, account_risk_flags
2. `knowledge_base_lookup`
  - คืน FAQ/docs ที่ตรงกับ issue_type และภาษา ticket
3. (เสริม) `system_status_lookup`
  - ใช้เมื่อพบ outage/auth/system error โดยเฉพาะที่ระบุ region

## 6) Language Policy
- ตรวจจับภาษา ticket (EN/TH)
- `rationale` และ auto-response ควรใช้ภาษาเดียวกับลูกค้า
- เก็บค่า taxonomy (`issue_type`, `urgency`) เป็นค่ามาตรฐานภาษาอังกฤษเสมอ

## 7) Failure & Guardrails
- ถ้า tool ล้มเหลว ให้ fallback ด้วยข้อมูลที่มีและลด `confidence`
- ถ้าความเชื่อมั่นต่ำกว่าเกณฑ์ (เช่น `< 0.55`) ให้ route ไป human/specialist
- ห้ามอ้างเอกสาร KB ที่หาไม่เจอจริงจาก tool result

## 8) Expected Decisions for Provided Sample Tickets
- Ticket #1 (Free -> Pro, duplicate charges, deadline 2 ชั่วโมง, tone โกรธ)
  - `urgency=high`
  - `issue_type=billing`
  - `sentiment=angry`
  - `next_action=route_specialist`, `route_team=billing`

- Ticket #2 (Enterprise 45 seats, TH region, error 500, หลายผู้ใช้, กระทบดีล)
  - `urgency=critical`
  - `issue_type=outage` (หรือ `auth` ถ้าตรวจแล้วเป็น login stack)
  - `sentiment=frustrated`
  - `next_action=escalate_human`, `route_team=sre`

- Ticket #3 (Dark mode question + possible bug + feature scheduling request)
  - `urgency=medium`
  - `issue_type=bug` + feature request side note
  - `sentiment=neutral`
  - `next_action=auto_respond` (docs/workaround) + route feedback to `product` when needed

## 9) Checkpoint 1 Exit Criteria
- มี output schema ชัดเจนและครบ requirement โจทย์
- มีกฎ urgency/next action ที่ deterministic
- มี expected outcome สำหรับ 3 sample tickets เพื่อใช้เทียบผลตอนทดสอบ
