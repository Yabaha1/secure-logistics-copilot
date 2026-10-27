# Responsible AI Governance Policy — PortGuard AI

> **Operational, Compliance, and Human-in-the-Loop Framework for Maritime & Dry Port Documentation Desks**

---

## 👔 5-Minute Executive Brief (For Hiring Managers & Leadership)

### The Core Governance Principle
In shipping and port terminal management, **automation without accountability is an unacceptable operational risk**. If an AI system mistakenly authorizes an unauthorized cargo pickup or changes a freight wire account, the shipping line and terminal operator bear full financial and legal liability.

PortGuard AI operates under an ironclad governance principle:
> **"The AI Model Proposes; The Human Officer Disposes."**

PortGuard AI is an **advisory intelligence copilot**. It does the heavy lifting of reading documents, normalizing messy data, scrubbing private credentials, and drafting correspondence. But **it has zero executive agency**. 

No container can leave a port gate, no delivery address can be changed, and no bank account can be updated without verified signoff from a certified human documentation officer.

### Clear Chain of Custody & Accountability
Every action suggested by the AI, every flag intercepted, and every human approval or rejection is recorded in an **append-only, tamper-evident audit trail**. In the event of a dispute, management has a complete forensic timeline showing who reviewed the document, what the AI extracted, and why the decision was made.

---

## 👥 1. Operational Roles & Access Matrix

| Operational Role | System Permissions | Responsibilities |
|:---|:---|:---|
| **Tier 1: PortGuard Copilot (AI Engine)** | Read-only input parsing; zero execution authority. | Ingests untrusted documents, sanitizes Unicode, redacts PII, extracts structured facts, risk-scores actions, and drafts French/English replies. |
| **Tier 2: Documentation Clerk** | Approves routine, low-risk documentation extractions. | Reviews clean booking notes, verifies vessel schedules, and dispatches pre-drafted status communications to customers. |
| **Tier 3: Logistics Security Officer** | Authorizes high-risk operations escalated to the HITL Queue. | Sole authority permitted to approve `HIGH` and `CRITICAL` actions (bank detail changes, container gate-passes, delivery address diversions). Requires out-of-band verification. |
| **Tier 4: System Security Administrator** | Audit log inspection, security tuning, rate-limit management. | Reviews weekly audit logs, updates prompt injection signatures, and runs quarterly red-team benchmark suites. |

---

## 📋 2. Allowed vs. Prohibited Data Ingestion

### Allowed Data Ingestion
* Synthetic or customer-authorized bills of lading, booking notes, delivery orders, and packing lists.
* Standard commercial invoices and customs declarations.
* General logistics customer inquiries and status requests in French or English.
* Unclassified maritime entities: ISO 6346 container numbers, vessel names, UN/LOCODE port codes (`CIABJ`, `FRLEH`), and cargo gross weights.

### Strictly Prohibited Data Ingestion
* Unredacted government identity credentials (passports, national identity cards, driver's licenses) without prior Layer 2 masking.
* Live banking PINs, corporate credit card numbers, or online portal passwords.
* Classified port security emergency override codes or physical terminal gate master access keys.
* Unvetted third-party commercial contracts containing confidential pricing schedules.

---

## 🔒 3. Mandatory Human-in-the-Loop (HITL) Verification Rules

PortGuard AI enforces **three non-negotiable gates** where automated processing is physically halted until a human officer acts:

1. **Gate 1: Freight Disbursement Account Changes (`CHANGE_BANK_DETAILS`)**
   * **Trigger:** Any request to alter payout accounts, IBANs, or wire routing.
   * **Mandatory Action:** Requires two-party verbal verification (out-of-band telephone call to the shipper’s verified finance director) before updating billing records.
2. **Gate 2: Container Gate Release Authorization (`RELEASE_CONTAINER`)**
   * **Trigger:** Any suggested container release or gate-out pass.
   * **Mandatory Action:** Requires physical presentation and inspection of the original endorsed Bill of Lading (or electronic bill of lading cryptographic signature).
3. **Gate 3: Delivery Address Rerouting (`UPDATE_DELIVERY_ADDRESS`)**
   * **Trigger:** Any modification diverting cargo away from designated bonded terminal warehouses.
   * **Mandatory Action:** Requires verified customs authority clearance stamps and written consignee endorsement to prevent cargo diversion theft.

---

## 🚨 4. Security Incident Response Protocol

When an adversarial prompt injection or zero-width evasion attack is flagged by Layer 1 or Layer 5:

```text
[Adversarial Pattern Detected]
          │
          ▼
[1. Immediate Execution Halt] ────► Pipeline aborts; tags transaction as BLOCKED_INJECTION
          │
          ▼
[2. Immutable Audit Logging] ─────► Logs timestamp, SHA-256 input hash, and signature IDs to JSONL
          │
          ▼
[3. Security Officer Alert] ──────► Alerts Logistics Security Desk with originating Session ID
          │
          ▼
[4. Zero Privilege Retries] ──────► Attacker cannot bypass quarantine within active session window
```

---

## 📅 5. Review Cadence & Compliance Audits

* **Daily:** Automated monitoring of rejected transactions, high-risk flags, and rate-limit triggers.
* **Weekly:** Security Officer review of all HITL resolution logs and dual-authorization notes.
* **Quarterly:** Execution of the 28-case synthetic Red Team Benchmark Suite (`red_team_tests/runner.py`) to verify that defenses remain effective against evolving OWASP LLM vulnerabilities.

---

*© 2026 Developed by BAMBA Yabaha ( +225 07 77 61 47 11 ) , email id : bambayabahasolomarius@gmail.com*
