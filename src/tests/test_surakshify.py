"""
Unit tests for the Surakshify Platform Core.
Verifies Ring-LWE Lattice Encryption accuracy and AI Agent scoring consistency.
Run with: python -m unittest src/tests/test_surakshify.py
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.quantum_security.encryption_demo import encrypt_transaction, decrypt_transaction, generate_lattice_keys
from src.ai_engine.fraud_detector import score_transaction

class TestSurakshifyCore(unittest.TestCase):
    
    def test_quantum_encryption_decryption(self):
        """Verifies that lattice-based encrypt -> decrypt is lossless."""
        original_payload = "TX_ID:99201;AMOUNT:5420.00;USER:usr_nupur_2026"
        
        # Encrypt
        encrypted = encrypt_transaction(original_payload)
        self.assertTrue(encrypted.startswith("[PQC-LATTICE-CIPHER]:"))
        
        # Decrypt
        decrypted = decrypt_transaction(encrypted)
        self.assertEqual(decrypted, original_payload)

    def test_ai_scoring_legitimate(self):
        """Test scoring of standard transactional logs (low risk)."""
        tx = {
            "transaction_id": "TX_TEST_01",
            "user_id": "usr_shuveta_2026",
            "amount": 100.0,
            "merchant": "Regular Tea Stall",
            "location": "Chennai",  # Matches home location
            "device": "iPhone_15_Pro"  # Matches trusted device
        }
        res = score_transaction(tx)
        self.assertEqual(res["action"], "APPROVE")
        self.assertLess(res["score"], 0.45)

    def test_ai_scoring_location_anomaly(self):
        """Test scoring when geolocation is mismatched (escalate/freeze)."""
        tx = {
            "transaction_id": "TX_TEST_02",
            "user_id": "usr_shuveta_2026",
            "amount": 100.0,
            "merchant": "International Retailer",
            "location": "London",  # Mismatched location
            "device": "iPhone_15_Pro"
        }
        res = score_transaction(tx)
        # Location anomaly adds 0.3 * 0.85 = 0.25 risk score
        # Let's verify it gets evaluated
        self.assertIn("location_risk", res["metrics"])
        self.assertGreater(res["metrics"]["location_risk"], 0.7)

    def test_ai_scoring_amount_anomaly(self):
        """Test scoring when amount is significantly above average (freeze)."""
        tx = {
            "transaction_id": "TX_TEST_03",
            "user_id": "usr_rijul_2026",
            "amount": 10000.0,  # Average is 800.0, this is ~12x average
            "merchant": "Luxury Watch Store",
            "location": "Bhubaneswar",
            "device": "MacBook_Pro_M3"
        }
        res = score_transaction(tx)
        self.assertEqual(res["action"], "FREEZE")
        self.assertGreater(res["score"], 0.75)

if __name__ == "__main__":
    unittest.main()
