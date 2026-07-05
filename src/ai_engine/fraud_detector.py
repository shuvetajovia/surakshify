"""
Autonomous AI Agentic Fraud Detector.
Simulates a multi-variable agent reasoning pipeline evaluating transaction metadata
and generating decision logs, scoring distributions, and mitigation rules.
"""

import time
import random
from datetime import datetime

# Simulated database containing user historical patterns for context-aware scoring
USER_PROFILES = {
    "usr_nupur_2026": {
        "name": "Nupur Goswami",
        "home_location": "Mumbai",
        "avg_amount": 1500.0,
        "trusted_devices": ["SBI_Netbanking_Portal", "Pixel_9_Pro"],
        "last_transaction_time": "2026-07-05T21:40:00Z"
    },
    "usr_shuveta_2026": {
        "name": "A Shuveta Jovi",
        "home_location": "Chennai",
        "avg_amount": 3500.0,
        "trusted_devices": ["iPhone_15_Pro"],
        "last_transaction_time": "2026-07-05T21:45:00Z"
    },
    "usr_rijul_2026": {
        "name": "Rijul Raisa Beura",
        "home_location": "Bhubaneswar",
        "avg_amount": 800.0,
        "trusted_devices": ["MacBook_Pro_M3"],
        "last_transaction_time": "2026-07-05T21:30:00Z"
    }
}

def parse_iso_time(time_str: str) -> float:
    """Helper to parse ISO timestamp to epoch seconds."""
    try:
        # Standard formats
        for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.strptime(time_str, fmt).timestamp()
            except ValueError:
                continue
        return time.time()
    except Exception:
        return time.time()

def score_transaction(transaction: dict) -> dict:
    """
    Evaluates a transaction using a multi-agent routing simulation.
    Analyzes Location Anomaly, Amount Anomaly, Velocity, and Device integrity.
    
    Args:
        transaction (dict): Details of the current transaction.
        
    Returns:
        dict: Evaluation results, scores, and detailed agent reasoning steps.
    """
    tx_id = transaction.get("transaction_id", "TX_" + str(random.randint(100000, 999999)))
    user_id = transaction.get("user_id", "usr_unknown")
    amount = float(transaction.get("amount", 0.0))
    location = transaction.get("location", "Unknown")
    merchant = transaction.get("merchant", "Merchant")
    device = transaction.get("device", "SBI_Netbanking_Portal")
    tx_time_str = transaction.get("timestamp", datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
    
    # 1. Retrieve profile context or create a dynamic baseline
    profile = USER_PROFILES.get(user_id)
    is_new_user = False
    if not profile:
        is_new_user = True
        profile = {
            "name": f"User {user_id.split('_')[-1] if '_' in user_id else user_id}",
            "home_location": location,
            "avg_amount": 1000.0,
            "trusted_devices": [device],
            "last_transaction_time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        }
    
    agent_logs = []
    agent_logs.append(f"[Agent Core] Initializing transaction audit pipeline for transaction {tx_id}...")
    agent_logs.append(f"[Context Service] Retriving history profile for user '{profile['name']}'...")
    agent_logs.append(f"[Context Service] Profile loaded. Registered Home Location: '{profile['home_location']}', Avg Transaction Size: ₹{profile['avg_amount']}")

    # 2. Risk Metrics Initialization
    location_risk = 0.0
    amount_risk = 0.0
    velocity_risk = 0.0
    device_risk = 0.0
    
    # --- Agent Tool 1: Location Analyzer ---
    agent_logs.append("[Location Agent] Comparing transaction origin with home profile...")
    if location.lower() != profile["home_location"].lower():
        # High mismatch
        location_risk = 0.85
        agent_logs.append(f"[Location Agent] WARNING: Location mismatch! Transaction originating from '{location}', but home location is '{profile['home_location']}'. Anomaly weight: High.")
    else:
        agent_logs.append(f"[Location Agent] OK: Transaction originating from home base '{location}'.")

    # --- Agent Tool 2: Amount Analyzer ---
    agent_logs.append("[Amount Agent] Comparing transaction volume with historical averages...")
    deviation = amount / profile["avg_amount"]
    if deviation > 5.0:
        amount_risk = 0.95
        agent_logs.append(f"[Amount Agent] ALERT: Severe volume anomaly! Transaction amount ₹{amount:.2f} is {deviation:.1f}x the user's typical transaction size (₹{profile['avg_amount']:.2f}). Anomaly weight: Critical.")
    elif deviation > 2.0:
        amount_risk = 0.50
        agent_logs.append(f"[Amount Agent] WARNING: Moderate deviation! Transaction amount ₹{amount:.2f} is {deviation:.1f}x the user's typical transaction size (₹{profile['avg_amount']:.2f}). Anomaly weight: Medium.")
    else:
        agent_logs.append(f"[Amount Agent] OK: Amount ₹{amount:.2f} is within normal parameters.")

    # --- Agent Tool 3: Velocity Analyzer ---
    agent_logs.append("[Velocity Agent] Checking time gap between successive transactions...")
    t1 = parse_iso_time(tx_time_str)
    t0 = parse_iso_time(profile["last_transaction_time"])
    time_diff = abs(t1 - t0)
    
    if time_diff < 15:  # Less than 15 seconds
        velocity_risk = 0.90
        agent_logs.append(f"[Velocity Agent] ALERT: Rapid succession warning! Current transaction initiated just {time_diff:.1f}s after previous transaction (Threshold: 15s). Indicates card testing or bot automation. Anomaly weight: Critical.")
    elif time_diff < 60:  # Less than 1 minute
        velocity_risk = 0.40
        agent_logs.append(f"[Velocity Agent] WARNING: High frequency transfer. Time delta is {time_diff:.1f}s. Anomaly weight: Medium.")
    else:
        agent_logs.append(f"[Velocity Agent] OK: Standard time interval between transactions ({time_diff:.1f}s).")

    # --- Agent Tool 4: Device Fingerprinter ---
    agent_logs.append("[Device Agent] Verifying requesting browser/device signature...")
    if device not in profile["trusted_devices"]:
        device_risk = 0.70
        agent_logs.append(f"[Device Agent] WARNING: Untrusted device signature detected: '{device}'. Profile trusted devices: {profile['trusted_devices']}. Anomaly weight: High.")
    else:
        agent_logs.append(f"[Device Agent] OK: Device signature matched trusted device '{device}'.")

    # 3. Decision Matrix
    # Weights: Location (30%), Amount (35%), Velocity (20%), Device (15%)
    weighted_score = (
        (location_risk * 0.30) +
        (amount_risk * 0.35) +
        (velocity_risk * 0.20) +
        (device_risk * 0.15)
    )
    
    # 4. Generate Actions
    action = "APPROVE"
    reason = "Low risk profile"
    
    if weighted_score > 0.75:
        action = "FREEZE"
        reason = "Autonomous lock: High combined anomaly index across Location, Amount, and Velocity checks."
        agent_logs.append(f"[Action Engine] CRITICAL: Combined Anomaly Index is {weighted_score:.2f} (Threshold: 0.75). Auto-triggering lockdown block on card/account.")
    elif weighted_score > 0.45:
        action = "ESCALATE"
        reason = "Human review: Moderate risk profile. Escalating for Multi-Factor Authentication challenge."
        agent_logs.append(f"[Action Engine] WARNING: Anomaly Index is {weighted_score:.2f}. Route selected: Challenge/Escalate (MFA/Human-in-the-loop audit required).")
    else:
        agent_logs.append(f"[Action Engine] OK: Anomaly Index is {weighted_score:.2f}. Transaction pre-approved.")

    # 5. Update cache details if not a fake transaction simulation
    if not is_new_user and weighted_score < 0.75:
        USER_PROFILES[user_id]["last_transaction_time"] = tx_time_str
        
    return {
        "action": action,
        "score": round(weighted_score, 4),
        "reason": reason,
        "metrics": {
            "location_risk": location_risk,
            "amount_risk": amount_risk,
            "velocity_risk": velocity_risk,
            "device_risk": device_risk
        },
        "agent_reasoning": agent_logs
    }
