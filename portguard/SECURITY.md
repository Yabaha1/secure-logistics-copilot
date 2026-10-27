# Security Policy & Vulnerability Disclosure — PortGuard AI

> **Responsible Security Reporting & Supply Chain Cyber-Defense Standards**

---

## 👔 5-Minute Executive Brief (For Hiring Managers & Leadership)

### Our Cybersecurity Commitment
Maritime ports, shipping lines, and inland dry port terminals form the backbone of national and international commerce. A security vulnerability in terminal software can lead to supply chain disruption, cargo theft, and financial wire fraud.

PortGuard AI is built from the ground up on **secure-by-design and defense-in-depth engineering principles**. We maintain an active, transparent vulnerability disclosure process and commit to investigating and resolving all reported vulnerabilities rapidly.

---

## 📬 1. How to Report Security Vulnerabilities

If you discover a security vulnerability, prompt injection bypass, PII leakage flaw, or logic defect in PortGuard AI:

* **Primary Security Contact:** **BAMBA Yabaha**
* **Direct Email:** [bambayabahasolomarius@gmail.com](mailto:bambayabahasolomarius@gmail.com)
* **Direct Phone / WhatsApp:** +225 07 77 61 47 11

> **⚠️ Critical Notice:** Please **DO NOT** create public GitHub issues, pull requests, or social media posts for undisclosed security vulnerabilities. Always use the private security channels above.

---

## 📋 2. Information to Include in Your Report

To help us triage and reproduce the issue rapidly, please provide:
1. **Target Vulnerability Category:** Specify the relevant OWASP Top 10 for LLM Applications ID (e.g., `LLM01: Prompt Injection`, `LLM02: Sensitive Information Disclosure`, `LLM06: Excessive Agency`).
2. **Exact Adversarial Payload:** The precise input string, text document, or email payload that triggered the bypass.
3. **Reproduction Steps:** Step-by-step instructions to reproduce the issue in both `BASELINE` and `HARDENED` modes using `red_team_tests/runner.py` or the Streamlit dashboard.
4. **Observed vs. Expected Behavior:** Details on how the defense was bypassed (e.g., did an injection avoid Layer 1 detection, or did a high-risk action avoid Layer 5 policy quarantine?).

---

## ⏱️ 3. Response & Remediation Timelines

| Stage | Committed SLA Timeline |
|:---|:---|
| **Initial Acknowledgment** | Within **24 hours** of report receipt. |
| **Triage & Reproduction** | Within **48 hours** with status confirmation. |
| **Fix Development & Testing** | Within **3 to 5 business days** for high/critical vulnerabilities. |
| **Public Advisory & Patch Release** | Coordinated disclosure following verified patch deployment. |

---

## 🎯 4. Scope of Testing

### In-Scope Vulnerabilities
* Novel prompt injection or jailbreak techniques that bypass Layer 1 input sanitization without triggering quarantine.
* Evasion techniques using zero-width characters, homoglyphs, or obfuscated multilingual syntax that deceive the gateway.
* PII extraction patterns that cause the LLM to output unredacted personal, banking, or passport details.
* Policy engine logic flaws that allow `CHANGE_BANK_DETAILS`, `RELEASE_CONTAINER`, or `UPDATE_DELIVERY_ADDRESS` actions to execute without human approval.

### Out-of-Scope
* Distributed Denial of Service (DDoS) attacks directed against external Google Gemini API infrastructure.
* Attacks requiring physical access to the host server running the application.
* Social engineering targeting human operational clerks outside the software gateway.

---

*© 2026 Developed by BAMBA Yabaha ( +225 07 77 61 47 11 ) , email id : bambayabahasolomarius@gmail.com*
