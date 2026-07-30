# IT Knowledge Base: Global VPN Access & Okta SSO Troubleshooting Guide

**Document ID:** IT-KB-204  
**Category:** IT User Support / Connectivity  
**Last Updated:** February 10, 2026

---

## 1. Connecting to Global Network VPN (GlobalProtect)

### Standard Connection Procedure

1. Open the **Palo Alto GlobalProtect** client on your system tray (Windows) or menu bar (macOS).
2. Enter the portal address: `vpn.global.company.com`.
3. Click **Connect**. When prompted, log in with your Okta Single Sign-On (SSO) credentials.
4. Verify Multi-Factor Authentication (MFA) on your Okta Verify mobile app.

---

## 2. Common Errors and Resolutions

### Issue A: "Gateway Not Responding" or Connection Timeout

- **Root Cause:** Stale DNS entries or local network blocking UDP port 4500 (IPsec).
- **Resolution Steps:**
  1. Open Terminal (Mac) or Command Prompt as Admin (Windows).
  2. Flush local DNS cache:
     - **macOS:** `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
     - **Windows:** `ipconfig /flushdns`
  3. In GlobalProtect settings, switch the connection protocol under **Preferences > Connection** from `IPsec` to `SSL`.
  4. Retry connection.

---

### Issue B: Okta Push Notifications Not Arriving on Mobile Phone

- **Root Cause:** Device clock desynchronization or background data throttling.
- **Resolution Steps:**
  1. Verify your mobile device's system time is set to **Automatic / Network-Provided Time**. A time drift of even 30 seconds will break TOTP tokens.
  2. Open the Okta Verify App manually to check for pending authentication requests.
  3. If issues persist, clear app cache or select **"Enter Code Manually"** on the Okta web browser prompt to input the 6-digit rolling OTP code.

---

## 3. IT Helpdesk Escalation Contact Information

If your issue is not resolved after following the self-service steps:

- **Slack Channel:** `#it-helpdesk` (Monitored 24/7)
- **Email:** `support@company.com`
- **Phone (Emergency Line):** +1 (800) 555-0199 (Ext 4)
