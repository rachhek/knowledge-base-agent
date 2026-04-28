# Information Security Policy — Remote Working
**Version:** 2.4 | **Owner:** Head of Information Security | **Review date:** 2026-06-01

---

## 1. Purpose

This policy sets out the requirements for employees and contractors who access company systems and data from locations outside of company-operated offices. It applies to all permanent staff, fixed-term employees, and third-party contractors with access to internal systems.

## 2. VPN and Network Access

All remote access to internal systems must be conducted exclusively over the company-approved VPN (GlobalProtect). Employees must ensure the VPN client is active before accessing any internal application or data store.

- VPN client download and setup instructions are available at: https://intranet.company.com/it/vpn-setup
- Multi-factor authentication (MFA) via Microsoft Authenticator is mandatory for all VPN sessions.
- Split-tunnel VPN is disabled; all traffic is routed through the corporate gateway.

For VPN provisioning or access issues, contact the IT Service Desk at it-support@company.com or call +358 9 4152 0300 (Monday–Friday, 08:00–18:00 EET).

## 3. Device Requirements

Only company-issued devices, or personally-owned devices formally enrolled in Mobile Device Management (MDM), may be used to access internal systems remotely.

- All devices must run an operating system version listed on the approved OS register (see Confluence: IT/Security/Approved-OS).
- Full-disk encryption must be enabled. For Windows devices, BitLocker is mandatory; for macOS devices, FileVault must be active.
- Endpoint Detection and Response (EDR) software (CrowdStrike Falcon) must be installed and reporting to the corporate console.

Requests to enrol a personal device must be submitted to the IT Service Desk via a service request at helpdesk.company.com.

## 4. Password and Authentication Standards

All accounts used to access company systems must meet the following minimum requirements:

- Minimum 14 characters, comprising uppercase, lowercase, numerals, and at least one symbol.
- Passwords must not be reused within the previous 12 cycles.
- All privileged accounts (admin, service accounts) must use a unique, system-generated 32-character password stored in CyberArk.

Employees must use the company-provided password manager (1Password Teams) for all non-privileged credentials. Licenses are provisioned automatically on day one. For access issues, contact it-support@company.com.

## 5. Incident Reporting

Any suspected security incident — including loss or theft of a device, credential compromise, or detection of unusual activity — must be reported immediately to the Security Operations Centre:

- **Email:** soc@company.com
- **Phone (24/7):** +358 9 4152 0911
- **Portal:** https://intranet.company.com/security/incidents

Do not attempt to investigate or remediate a suspected incident independently. Preserve all logs and artefacts in place and await guidance from the SOC team.

## 6. Policy Exceptions

Requests for exceptions to this policy must be submitted in writing to the Head of Information Security (security@company.com) and approved before the exception is enacted. Exceptions are valid for a maximum of 90 days and must be reviewed prior to expiry.

---

*This policy is reviewed annually or following any material change to the threat landscape or regulatory environment.*
