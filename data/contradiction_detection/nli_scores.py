# MOCK_NLI_SCORES
# High scores (> 0.7) indicate the claims are discussing the same specific requirement
# but likely contain conflicting information.

MOCK_NLI_SCORES = {
    # (policy_claim_id, corpus_claim_id): score
    # Password Requirements
    ("p008", "c001"): 0.94,  # Min characters: 14 vs 8
    ("p010", "c002"): 0.89,  # Manager: 1Password vs LastPass
    ("p009", "c020"): 0.68,  # Password rotation (Threshold check: 12 cycles vs 60 days)
    # Endpoint Security
    ("p007", "c003"): 0.86,  # EDR: CrowdStrike vs Windows Defender
    ("p006", "c016"): 0.82,  # Encryption: Mandatory vs Recommended
    # VPN & Network
    ("p003", "c004"): 0.81,  # MFA: Mandatory vs Optional
    ("p002", "c006"): 0.90,  # VPN: Always vs Trusted Home Networks
    ("p004", "c008"): 0.92,  # Split Tunneling: Disabled vs Available
    # Device Enrollment
    ("p005", "c007"): 0.78,  # MDM: Mandatory for all vs AV-only for personal
    # Incident Response
    ("p011", "c011"): 0.77,  # Reporting: SOC vs Line Manager
    ("p011", "c012"): 0.84,  # Email: soc@ vs security@
    ("p012", "c014"): 0.88,  # Investigation: Do not vs Attempt basic remediation
    # Policy Exceptions
    ("p013", "c013"): 0.91,  # Windows: 90 days vs 180 days
}

# Neutral/Non-conflicting pairs typically return 0.15 - 0.40
