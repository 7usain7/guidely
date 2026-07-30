# Corporate Policy: AI & Machine Learning Acceptable Use Policy
**Document ID:** SEC-POL-099  
**Effective Date:** March 1, 2026  
**Owner:** Information Security & AI Governance Board  
**Applies To:** All Software Engineers, Product Managers, and Data Employees  

---

## 1. Approved Third-Party AI Models & Tooling

### 1.1 Tier 1 Approved Enterprise Tools
Employees are permitted to use the following enterprise-contracted AI platforms for work-related code generation, document summarization, and data analysis:
* **Claude (via Anthropic API / Claude Code):** Approved for internal codebases, architecture analysis, and standard technical documentation.
* **GitHub Copilot Enterprise:** Approved for inline code completion within company-managed IDEs.
* **Enterprise ChatGPT (Dedicated Tenant):** Approved for drafting emails, blog posts, and internal non-sensitive slide decks.

### 1.2 Strictly Prohibited Commercial Tools
* Public consumer tiers of AI chatbots (e.g., free ChatGPT, public Claude Web UI, Gemini Free) are **strictly prohibited** for any work-related task or code input.
* Storing or processing corporate source code in unapproved browser extensions or local open-source LLMs without explicit CISO approval is grounds for immediate termination.

---

## 2. Data Classification Rules for Model Prompts

| Sensitivity Level | Examples | Permitted LLM Processing |
| :--- | :--- | :--- |
| **Public Data** | Published marketing copy, open-source code, public PR releases. | Any Tier 1 approved tool. |
| **Internal Data** | Internal technical documentation, non-sensitive Slack logs, team SOPs. | Enterprise-tier LLMs with zero data retention enabled. |
| **Restricted / PII Data** | Customer PII, SSNs, credit card numbers, production API keys, HR payroll records. | **STRICTLY PROHIBITED** from all external LLM prompts. |

---

## 3. Human-in-the-Loop Verification Requirements

### 3.1 Code Review Mandate
* 100% of AI-generated code must undergo mandatory manual review by a peer engineer prior to merging into `main`.
* Autonomously generated pull requests that lack unit test coverage or security scans will be automatically rejected by CI/CD pipelines.

### 3.2 Intellectual Property & Copyright Notice
* Employees must verify that third-party code snippet completions do not output licensed GPL/AGPL code verbatim without attribution.
