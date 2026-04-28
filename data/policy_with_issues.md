# Information Security Policy — Remote Working
**Version:** DRAFT | **Owner:** [policy-owner] | **Review date:** TBD

---

## 1. Purpose

This policy sets out the requirements for employees and contractors who access company systems and data from locations outside of company-operated offices. It applies to all permanent staff, fixed-term employees, and third-party contractors with access to internal systems.

## 2. VPN and Network Access

All remote access to internal systems must be conducted exclusively over the company-approved VPN. Employees must ensure the VPN client is active before accessing any internal application or data store.

- VPN client download and setup instructions are available at: [vpn-setup-url]
- Multi-factor authentication (MFA) is mandatory for all VPN sessions.
- Split-tunnel VPN is disabled; all traffic is routed through the corporate gateway.

For VPN provisioning or access issues, contact the IT Service Desk at [it-support@company.com] or call [+358 XX XXX XXXX] during business hours.

## 3. Device Requirements

Only company-issued devices, or personally-owned devices formally enrolled in Mobile Device Management (MDM), may be used to access internal systems remotely.

- All devices must run an operating system version approved by the relevant IT team.
- Full-disk encryption must be enabled on all devices.
- The appropriate endpoint security software must be installed and active.

Requests to enrol a personal device should be submitted to the appropriate team.

## 4. Password and Authentication Standards

All accounts used to access company systems must meet the following minimum requirements:

- Minimum password length: {min_password_length} characters.
- Passwords must not be reused within the previous {reuse_window} cycles.
- All privileged accounts must use a unique, system-generated password stored in the approved secrets manager.

Employees must use the company-provided password manager for all non-privileged credentials. For access issues, contact TODO.

## 5. Incident Reporting

Any suspected security incident — including loss or theft of a device, credential compromise, or detection of unusual activity — must be reported immediately to the Security Operations Centre.

Contact details for the SOC are available from the relevant team. Response time expectations are defined in the SLA document.

Do not attempt to investigate or remediate a suspected incident independently.

## 6. Policy Exceptions

Requests for exceptions to this policy must be submitted in writing to the Head of Information Security and approved before the exception is enacted. Exceptions are valid for a maximum of ________ days and must be reviewed prior to expiry.

---

*This policy is reviewed annually or following any material change to the threat landscape or regulatory environment. Questions should be directed to the appropriate personnel.*
