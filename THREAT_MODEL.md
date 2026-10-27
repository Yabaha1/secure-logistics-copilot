# Threat Model & STRIDE Analysis — PortGuard AI

> **Security & Threat Architecture for Port • Dry Port Logistics LLM Gateway**

---

## 👔 5-Minute Executive Brief (For Hiring Managers & Leadership)

### Why Maritime Logistics is a High-Value Target
A single ocean shipping container carrying premium export commodities (such as Ivorian cocoa beans, cashew nuts, or coffee) has an average declared value of **$65,000 to $120,000**. Ocean freight settlements frequently involve transactions exceeding **$50,000 per booking**.

When logistics companies adopt conversational AI to automate paperwork, sophisticated cyber-criminals exploit the AI's naive helpfulness:
* **The "Urgent Bank Change" Attack:** The attacker pretends to be the shipper's CFO, citing a "tax audit" or "system maintenance" to divert hundreds of thousands of dollars into an offshore account.
* **The "Cargo Reroute" Attack:** Fraudulent delivery amendment notes redirect high-value containers away from government-bonded port depots to private industrial warehouses for physical theft.
* **The "Gate Pass Bypass" Attack:** Clever prompt injection commands trick the AI into generating container pickup authorizations without physical original bills of lading.

### How PortGuard AI Protects the Organization
PortGuard AI views **every incoming email, attachment, and document as untrusted adversarial data**. It places 5 strict trust boundaries and 7 defense layers between incoming documents and terminal systems. 

**Most importantly:** PortGuard AI decouples "data extraction" from "action execution." The AI can read and extract data, but it is **physically impossible** for the model to authorize a payout or release a container without human officer physical signoff.

---

## 🏛️ 1. Critical Organizational Assets

| Asset Name | Business Value | Operational Impact of Compromise |
|:---|:---|:---|
| **Container Release Authority** | $65,000 – $120,000 / container | Physical theft of container cargo from terminal gate. |
| **Freight Disbursement Accounts** | $15,000 – $85,000 / transaction | Irrevocable wire fraud via compromised banking records. |
| **Shipper & Consignee Identity** | Regulatory Compliance | Fines under data protection frameworks for leaked PII. |
| **Bonded Customs Status** | Port License & Legal Standing | Cargo diversion evading customs inspection checkpoints. |
| **System Prompt Confidentiality** | Proprietary Business Logic | Exfiltration of company guardrail rules and parsing prompts. |
| **LLM Gateway Availability** | Operational Continuity | Denial of Service attacks exhausting terminal API quotas. |

---

## 🚪 2. Trust Boundaries & Data Flow

```text
[UNTRUSTED EXTERNAL WORLD]
    │  Unvetted emails, scanned bills of lading, customer messages, forwarder notes
────▼─────────────────────────────────────────────────────────────────────────────
[TRUST BOUNDARY 1: Ingestion & Input Sanitization]
    │  • Layer 1: Strips invisible Unicode (zero-width spaces, BOM, directional marks)
    │  • Layer 1: Length capping (max 8,000 characters)
    │  • Layer 1: Scans bilingual injection signatures (English & French)
────▼─────────────────────────────────────────────────────────────────────────────
[TRUST BOUNDARY 2: Privacy & Entity Isolation]
    │  • Layer 2: Masks sensitive PII (IBANs, credit cards, phones, IDs)
    │  • Layer 2: Preserves ISO 6346 container numbers
    │  • Layer 3: Encloses document inside explicit XML tags (<untrusted_shipping_document>)
────▼─────────────────────────────────────────────────────────────────────────────
[TRUST BOUNDARY 3: LLM Inference Sandbox]
    │  • Layer 4: Gemini Flash invocation in stateless mode
    │  • Layer 4: Response MIME = application/json, low temperature (0.1)
    │  • Layer 4: Inter-call pacing (4.0s) & SHA-256 local disk caching
────▼─────────────────────────────────────────────────────────────────────────────
[TRUST BOUNDARY 4: Schema & Policy Gate]
    │  • Layer 4: Rigid Pydantic v2 validation with extra="forbid"
    │  • Layer 5: Deterministic Policy Engine (risk-scores all proposed actions)
    │  • Layer 5: Mandates Human-in-the-Loop review for HIGH/CRITICAL operations
────▼─────────────────────────────────────────────────────────────────────────────
[TRUST BOUNDARY 5: Executive Authority & Terminal Operating System (TOS)]
    │  • Terminal Documentation Officer (Dual-authorization signoff)
    │  • Layer 6: Append-only immutable JSONL audit log
```

---

## 🛡️ 3. STRIDE Threat Matrix for Maritime LLM Gateway

| Threat Category | Maritime Attack Scenario | OWASP ID | PortGuard AI Mitigation Implementation |
|:---|:---|:---:|:---|
| **Spoofing** | Attacker crafts email with forged carrier letterhead claiming port emergency waiver. | `LLM01` | Layer 1 scans injection signatures; Layer 3 encloses content in data tags; system instructions declare documents cannot issue commands. |
| **Tampering** | Adversary injects zero-width Unicode characters (`\u200b`, `\ufeff`) inside cargo description to hide prompt injection. | `LLM01` | Layer 1 regex strips all non-printable and zero-width Unicode characters prior to prompt construction. |
| **Repudiation** | Operator or carrier claims copilot automatically authorized an unauthorized cargo release. | `LLM08` | Layer 6 writes tamper-evident JSONL audit log with UTC timestamp, input SHA-256 digest, exact decision, and reasons. |
| **Information Disclosure** | Competitor attempts prompt injection to extract rival exporter shipping volumes or bank details. | `LLM02` | Model context is stateless across sessions; Layer 2 scrubs all personal and banking identifiers before model sees input. |
| **Denial of Service** | Flooding system with massive multi-megabyte payloads to exhaust Gemini rate limits and trigger HTTP 429. | `LLM04` | Layer 1 caps input at 8k chars; Layer 7 enforces sliding-window rate limits (10 req/min); SHA-256 disk cache absorbs duplicates. |
| **Elevation of Privilege** | Attacker coerces model to emit an automated `RELEASE_CONTAINER` gate pass with `risk_level="LOW"`. | `LLM06` | Layer 5 Policy Engine overrides model risk to `HIGH/CRITICAL`; model is strictly advisory; human approval is non-negotiable. |

---

## 🎯 4. OWASP Top 10 for LLM Applications Mapping

| OWASP ID | Threat Category | PortGuard AI Defensive Architecture |
|:---|:---|:---|
| **LLM01: Prompt Injection** | Direct & Indirect Injection | Strips zero-width evasion characters; encapsulates raw data inside `<untrusted_shipping_document>` tags; treats all text as passive data. |
| **LLM02: Sensitive Information Disclosure** | PII & Financial Leakage | PII redactor scrubs IBANs, cell numbers, emails, and passport/national IDs while preserving ISO 6346 shipping container IDs. |
| **LLM03: Supply Chain Vulnerabilities** | Dependency Compromise | Minimal, pinned dependencies in `requirements.txt` (`google-genai==1.5.0`, `pydantic==2.8.2`); no unvetted orchestration frameworks. |
| **LLM04: Data and Model Denial of Service** | Rate-Limit Exhaustion | Strict 8,000 character length cap; 4.0-second inter-call pacing; SHA-256 disk response caching; sliding-window rate limiting. |
| **LLM05: Improper Output Handling** | Unvalidated Model Generation | Outputs validated against rigid Pydantic v2 schemas (`extra="forbid"`). Malformed payloads or extra fields cause immediate rejection. |
| **LLM06: Excessive Agency** | Autonomous Execution | Model has zero execution privileges. It can only suggest structured JSON. High-risk actions are hard-quarantined to the HITL queue. |
| **LLM07: System Prompt Leakage** | Extraction of Confidential Rules | Bilingual injection scanner flags probe signatures (`reveal your instructions`); prompt boundary design prevents instruction regurgitation. |
| **LLM08: Vector & Embedding Weaknesses** | Vector Store Poisoning | N/A: System uses direct document parsing without persistent vector database retrieval. |
| **LLM09: Misinformation** | Hallucinated Logistics Data | Grounding via structured extraction strictly limited to entities present in the sanitized document payload. |
| **LLM10: Unbounded Consumption** | Uncontrolled API Spending | Exponential retry backoff on HTTP 429; sliding-window session rate limiter. |

---

*© 2026 Developed by BAMBA Yabaha ( +225 07 77 61 47 11 ) , email id : bambayabahasolomarius@gmail.com*
