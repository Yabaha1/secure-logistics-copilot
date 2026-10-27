# Business Case & ROI Analysis — PortGuard AI

> **Assumptions-Based Economic Evaluation of AI-Driven Document Processing in Maritime & Dry Port Operations**
> 
> *Notice: All metrics, calculations, and labor estimates presented in this business case are **assumptions-based models** designed to evaluate operational feasibility. All assumptions are explicitly documented below.*

---

## 👔 5-Minute Executive Brief (For Hiring Managers & Leadership)

### The Bottom Line
Deploying PortGuard AI across a regional maritime documentation desk handling **1,200 shipping documents per day** delivers:
* **$1.40 Million in annual labor productivity savings** by reducing handling time per document from **18 minutes to 3 minutes** (-83.3%).
* **An estimated $200,000 to $600,000 in annual fraud and cargo theft avoidance** by intercepting wire transfer diversions and unauthorized container releases.
* **A Total Annual System Cost of ~$17,000**, representing an estimated **Net Return on Investment (ROI) exceeding 9,000%** with a financial payback period of **less than 10 business days**.

### The Problem Being Solved
Maritime documentation desks are overwhelmed with unstructured paperwork: PDF bills of lading, booking confirmations, customs transit passes, and customer inquiries across French and English. Human clerks spend their days manually reading documents, typing data into Terminal Operating Systems (TOS), and drafting acknowledgment emails. 

This manual workflow causes port congestion, delayed container gate-ins, and human fatigue errors. PortGuard AI automates the routine 83% of the workflow while establishing an automated security perimeter around high-risk transactions.

---

## 📊 1. Baseline Operational Assumptions

| Parameter | Baseline Value | Source / Operational Rationale |
|:---|:---:|:---|
| **Daily Document Volume** | 1,200 documents / day | Typical daily intake across container terminals and inland dry ports. |
| **Documentation Staff Size** | 15 full-time clerks | Dedicated documentation intake and customer service team. |
| **Fully Loaded Clerk Cost** | $18.00 / hour | Hourly salary, benefits, terminal overhead, and software seat costs. |
| **Manual Handling Time** | 18.0 minutes / doc | Reading document, verifying container IDs, manual TOS entry, drafting email. |
| **Copilot Review Time** | 3.0 minutes / doc | Verifying pre-extracted structured entities, 1-click reply dispatch. |
| **Working Days per Year** | 260 days / year | Standard annual operational work schedule. |

---

## ⏱️ 2. Productivity & Labor Savings Model

```text
[Manual Workflow]   18.0 min/doc  ════════════════════════════════════════►  $6,480 / day
[PortGuard AI]       3.0 min/doc  ════►  $1,080 / day (83.3% time savings)
                                         ─────────────────────────────────
                                         Net Savings: $5,400 / day (~$1.4M / year)
```

### Detailed Breakdown

| Metric | Manual Baseline | With PortGuard AI Copilot | Operational Delta |
|:---|:---:|:---:|:---:|
| **Average Handling Time per Document** | 18.0 minutes | 3.0 minutes | **-15.0 min (-83.3%)** |
| **Documents Processed per Clerk / 8h Shift** | ~26 documents | ~120 documents | **+361% capacity** |
| **Total Daily Labor Required (1,200 docs)** | 360 clerk-hours | 60 clerk-hours | **300 hours saved / day** |
| **Daily Operational Labor Cost** | $6,480 / day | $1,080 / day | **$5,400 saved / day** |
| **Annualized Operational Cost (260 days)** | $1,684,800 / year | $280,800 / year | **~$1,404,000 saved / year** |

---

## 🛡️ 3. Risk Reduction & Loss Avoidance Model (Assumptions)

In maritime supply chains, cyber fraud and cargo diversion represent catastrophic balance sheet risks:

### Scenario A: Intercepted Freight Wire Fraud
* **Assumptions:** 
  * Freight charges range between **$15,000 and $85,000 per booking**.
  * Business Email Compromise (BEC) attacks targeting payment accounts occur an estimated **2 to 4 times per year** at an unhardened terminal.
* **PortGuard AI Mitigation:** 
  * Layer 5 Policy Engine enforces non-negotiable out-of-band dual authorization for 100% of `CHANGE_BANK_DETAILS` requests.
* **Estimated Annual Loss Avoidance:** **$70,000 to $250,000 / year**.

### Scenario B: Container Diversion & Cargo Theft
* **Assumptions:** 
  * A 40ft High Cube container of export agricultural commodities (cocoa beans, cashew nuts) has a declared value of **$65,000 to $120,000**.
  * Social engineering attacks attempting to reroute containers away from bonded warehouses occur an estimated **1 to 3 times per year**.
* **PortGuard AI Mitigation:** 
  * `UPDATE_DELIVERY_ADDRESS` and `RELEASE_CONTAINER` are hard-quarantined to the Human-in-the-Loop review queue, requiring physical customs verification and original bill of lading surrender.
* **Estimated Annual Loss Avoidance:** **$130,000 to $360,000 / year**.

---

## 💰 4. Total Cost of Ownership (TCO) vs. Net ROI

| Cost Component | Annual Cost (Estimated) | Cost Basis & Assumptions |
|:---|:---:|:---|
| **Google Gemini API Inference** | ~$3,200 / year | 1,200 docs/day @ Gemini 2.5 Flash token pricing; local SHA-256 caching absorbs ~25% redundant queries. |
| **Cloud Hosting & Persistence** | ~$1,800 / year | Containerized Linux environment with append-only JSONL audit storage. |
| **Security Auditing & Maintenance** | ~$12,000 / year | Quarterly red-team benchmark runs, signature updates, and security officer training. |
| **Total Annual Investment (TCO)** | **~$17,000 / year** | Extremely lightweight footprint. |
| **Gross Financial Value Delivered** | **~$1,604,000 / year** | Labor savings ($1.40M) + fraud avoidance ($200k+). |
| **Net Financial Benefit** | **~$1,587,000 / year** | **Net ROI > 9,000%** (Payback period < 10 business days). |

---

*© 2026 Developed by BAMBA Yabaha ( +225 07 77 61 47 11 ) , email id : bambayabahasolomarius@gmail.com*
