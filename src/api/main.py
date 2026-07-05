import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
from datetime import datetime, timedelta

# Add project root directory to path to allow absolute imports
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.ai_engine.fraud_detector import score_transaction
from src.quantum_security.encryption_demo import encrypt_transaction_with_telemetry, decrypt_transaction

app = FastAPI(
    title="Surakshify API",
    description="Autonomous Fraud Defense powered by Agentic AI + Quantum-Safe Cryptography",
    version="1.0.0",
)

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    merchant: str
    location: str
    timestamp: str
    device: str = "SBI_Netbanking_Portal"

class EncryptionRequest(BaseModel):
    data: str

class DecryptionRequest(BaseModel):
    encrypted_data: str

# Serve the HTML frontend directly at the root endpoint
@app.get("/", response_class=HTMLResponse)
def read_root():
    template_path = Path(__file__).resolve().parent / "templates" / "index.html"
    if not template_path.exists():
        # Fallback basic placeholder if file is not written yet
        return """
        <html>
            <body style="font-family: sans-serif; background: #0b0f19; color: #fff; text-align: center; padding-top: 100px;">
                <h1>Surakshify API Server Online 🛡️</h1>
                <p>Loading Dashboard assets, please wait...</p>
            </body>
        </html>
        """
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

@app.post("/api/v1/encrypt")
def encrypt_endpoint(payload: EncryptionRequest):
    try:
        res = encrypt_transaction_with_telemetry(payload.data)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/decrypt")
def decrypt_endpoint(payload: DecryptionRequest):
    try:
        decrypted = decrypt_transaction(payload.encrypted_data)
        return {"decrypted_data": decrypted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/evaluate")
def evaluate_transaction(transaction: Transaction):
    try:
        # 1. Package transaction string and run Post-Quantum (PQC) Encryption with Telemetry
        payload_str = f"id={transaction.transaction_id},amt={transaction.amount},usr={transaction.user_id},loc={transaction.location}"
        quantum_crypto = encrypt_transaction_with_telemetry(payload_str)
        
        # 2. Score transaction with Multi-Variable Agentic AI
        ai_analysis = score_transaction(transaction.model_dump())
        
        return {
            "transaction_id": transaction.transaction_id,
            "quantum_encryption": {
                "ciphertext": quantum_crypto["encrypted_data"],
                "telemetry": quantum_crypto["telemetry"]
            },
            "ai_evaluation": ai_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/simulate-feed")
def simulate_feed():
    """Generates 5 distinct simulation transactions to show the live detection flow."""
    now = datetime.utcnow()
    merchants = ["Amazon India", "Starbucks Mumbai", "SBI Atm Withdrawal", "unknown_merchant_proxy", "Luxe Jewelry Delhi"]
    locations = ["Mumbai", "Chennai", "Bhubaneswar", "London", "Delhi"]
    devices = ["SBI_Netbanking_Portal", "Pixel_9_Pro", "iPhone_15_Pro", "MacBook_Pro_M3", "Tor_Browser_Proxy"]
    
    users = ["usr_nupur_2026", "usr_shuveta_2026", "usr_rijul_2026"]
    
    simulated_transactions = []
    
    # 1. Clear Legitimate transaction
    simulated_transactions.append({
        "transaction_id": "TX_1001" + str(random.randint(10, 99)),
        "user_id": "usr_nupur_2026",
        "amount": 450.00,
        "merchant": "Starbucks Mumbai",
        "location": "Mumbai",
        "timestamp": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "device": "Pixel_9_Pro",
        "description": "Legitimate transaction from user's primary device and home location."
    })
    
    # 2. Amount Anomaly (Very High Transaction)
    simulated_transactions.append({
        "transaction_id": "TX_1002" + str(random.randint(10, 99)),
        "user_id": "usr_rijul_2026",
        "amount": 9500.00,
        "merchant": "Luxe Jewelry Delhi",
        "location": "Bhubaneswar",
        "timestamp": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "device": "MacBook_Pro_M3",
        "description": "Amount Anomaly: Transaction is ~12x the user's historical transaction average."
    })
    
    # 3. Location Mismatch (Geographical Anomaly)
    simulated_transactions.append({
        "transaction_id": "TX_1003" + str(random.randint(10, 99)),
        "user_id": "usr_shuveta_2026",
        "amount": 2500.00,
        "merchant": "unknown_merchant_proxy",
        "location": "London",
        "timestamp": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "device": "iPhone_15_Pro",
        "description": "Location Anomaly: Transaction originating from London, while user home location is Chennai."
    })
    
    # 4. Device Integrity Threat (Unknown User/Proxy Signature)
    simulated_transactions.append({
        "transaction_id": "TX_1004" + str(random.randint(10, 99)),
        "user_id": "usr_nupur_2026",
        "amount": 1800.00,
        "merchant": "Amazon India",
        "location": "Mumbai",
        "timestamp": now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "device": "Tor_Browser_Proxy",
        "description": "Device Security Anomaly: Transaction via unapproved anonymous Tor device."
    })
    
    # 5. Velocity Check Threat (Rapid successive transactions)
    # Generates a timestamp just 2 seconds after the first transaction
    rapid_time = now - timedelta(seconds=2)
    simulated_transactions.append({
        "transaction_id": "TX_1005" + str(random.randint(10, 99)),
        "user_id": "usr_nupur_2026",
        "amount": 750.00,
        "merchant": "Amazon India",
        "location": "Mumbai",
        "timestamp": rapid_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "device": "Pixel_9_Pro",
        "description": "Velocity Anomaly: Transaction triggered only 2 seconds after another transaction."
    })
    
    return simulated_transactions
