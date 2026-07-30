# Standard Operating Procedure: Cybersecurity Incident Response & Escalation

**Document ID:** SEC-SOP-108  
**Classification:** Internal Restricted  
**Last Revised:** April 15, 2026  
**Maintainer:** Security Operations Center (SOC)

---

## 1. Incident Classification Matrix

| Severity Level       | Definition & Criteria                                                                                                  | Required SLA Response Time | Lead Handler             |
| :------------------- | :--------------------------------------------------------------------------------------------------------------------- | :------------------------- | :----------------------- |
| **SEV-1 (Critical)** | Active data breach, ransomware explosion, core production system outage (>50% users affected), unauthorized DB access. | **< 15 minutes**           | CISO & Lead SOC Engineer |
| **SEV-2 (High)**     | Impairment of key non-production systems, confirmed targeted phishing campaign affecting high-privilege accounts.      | **< 1 hour**               | Senior Security Engineer |
| **SEV-3 (Medium)**   | Isolated malware detection on single workstation, minor policy violation, low-impact vulnerability discovery.          | **< 4 hours**              | Security Analyst         |
| **SEV-4 (Low)**      | General spam, failed baseline login attempts without lockout, security query.                                          | **< 24 hours**             | SOC Helpdesk Tier 1      |

---

## 2. Incident Handling Lifecycle

### Phase 1: Identification & Detection

- Any employee observing suspicious network activity, unapproved file modifications, or credential prompts must immediately notify `security-alert@company.com` or call internal emergency extensions `#7911`.
- Automatic alerts from SIEM (Splunk/Datadog) triggering a SEV-1 condition automatically initiate a Slack PagerDuty triage room (`#incident-sev1-[date]`).

### Phase 2: Containment Protocols

When a **SEV-1** or **SEV-2** system compromise is verified:

1. **Network Isolation:** Immediately isolate the affected virtual instance or host endpoint via the CrowdStrike Falcon admin console. Do **not** power off the machine (preserve RAM contents for forensic evaluation).
2. **Credential Revocation:** Force sign-out of all Active Directory / Okta sessions associated with compromised account user IDs and reset API keys across production environments.
3. **Firewall Lockdown:** Block external IP addresses involved in the breach perimeter at the Cloudflare WAF edge level.

### Phase 3: Eradication & Recovery

- Re-image compromised hosts using clean baseline infrastructure-as-code scripts (`Terraform`).
- Restore databases from validated cold backups performed prior to the documented point-of-compromise timestamp.
- Obtain explicit sign-off from the CISO prior to un-isolating systems and resuming public traffic.
