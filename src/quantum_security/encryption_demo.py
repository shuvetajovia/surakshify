"""
Post-Quantum Cryptography (PQC) Ring Learning With Errors (Ring-LWE) Simulation.
This module simulates lattice-based key exchange and encryption (similar to ML-KEM/Kyber)
and generates mathematical telemetry for visualization on the dashboard.
"""

import random
import json
import base64

# Modulus q (standard prime for toy Kyber simulation)
MODULUS = 257
DIMENSION = 8  # Lattice dimension

# Default system keypair for background processes
_SYSTEM_KEYS = None

def get_system_keys():
    global _SYSTEM_KEYS
    if _SYSTEM_KEYS is None:
        _SYSTEM_KEYS = generate_lattice_keys()
    return _SYSTEM_KEYS

def generate_lattice_keys():
    """
    Generates a Ring-LWE public/private keypair.
    - Private Key: Secret vector s of small integers.
    - Public Key: Random matrix A, and vector t = (A * s + e) mod q, where e is error/noise.
    """
    q = MODULUS
    n = DIMENSION
    
    # 1. Private Key (s): Secret vector with small values (typically -1, 0, 1)
    s = [random.randint(-1, 1) for _ in range(n)]
    
    # 2. Public Key Matrix (A): Uniformly random integers mod q
    A = [[random.randint(0, q - 1) for _ in range(n)] for _ in range(n)]
    
    # 3. Error Vector (e): Gaussian noise vector (small integers)
    e = [random.randint(-1, 1) for _ in range(n)]
    
    # 4. Public Key Vector (t) = (A * s + e) mod q
    t = []
    for i in range(n):
        row_sum = sum(A[i][j] * s[j] for j in range(n))
        t.append((row_sum + e[i]) % q)
        
    return {
        "public_key": {
            "matrix_A": A,
            "vector_t": t,
            "modulus_q": q,
            "dimension_n": n
        },
        "private_key": {
            "vector_s": s
        }
    }

def encrypt_transaction_with_telemetry(data: str, public_key: dict = None) -> dict:
    """
    Encrypts a transaction string using lattice-based public key encryption.
    Returns the ciphertext AND the mathematical telemetry (steps, matrices, noise) for the UI.
    """
    if public_key is None:
        public_key = get_system_keys()["public_key"]
        
    A = public_key["matrix_A"]
    t = public_key["vector_t"]
    q = public_key["modulus_q"]
    n = public_key["dimension_n"]
    
    # 1. Convert text data to binary bits
    binary_data = ''.join(format(ord(char), '08b') for char in data)
    
    # 2. Generate random ephemeral secret vector r (small values)
    r = [random.randint(-1, 1) for _ in range(n)]
    
    # 3. Generate error vectors e1 (vector of size n) and e2 (scalar for payload coding)
    e1 = [random.randint(-1, 1) for _ in range(n)]
    e2 = random.randint(-1, 1)
    
    # 4. Compute public vector u = (A^T * r + e1) mod q
    # For a toy implementation, we do matrix-vector multiplication
    u = []
    for j in range(n):
        col_sum = sum(A[i][j] * r[i] for i in range(n))
        u.append((col_sum + e1[j]) % q)
        
    # 5. Encode binary bits into vector v.
    # In Kyber, we encode a message of n bits. We will take the first n bits of the data,
    # or pad it. To encrypt the whole text, we combine it with standard symmetric key AES,
    # or simply run this lattice coding on a hash/key. Here we will encrypt the actual data
    # by using v to hide the message bits, repeating as blocks if needed.
    # For a clean visualizer, we represent it as a polynomial encoding step:
    v = []
    # Encrypt blocks of size n
    blocks = [binary_data[i:i+n] for i in range(0, len(binary_data), n)]
    
    # Pad last block
    if blocks and len(blocks[-1]) < n:
        blocks[-1] = blocks[-1].ljust(n, '0')
        
    for block in blocks:
        block_v = []
        # Hide each bit: v_i = (t * r + e2 + bit * (q // 2)) mod q
        t_r_dot = sum(t[i] * r[i] for i in range(n))
        for bit_idx, bit in enumerate(block):
            bit_val = int(bit)
            coded_bit = (t_r_dot + e2 + bit_val * (q // 2)) % q
            block_v.append(coded_bit)
        v.append(block_v)
        
    # Create final packed ciphertext
    ciphertext_payload = {
        "u": u,
        "v": v
    }
    serialized_ciphertext = base64.b64encode(json.dumps(ciphertext_payload).encode()).decode()
    
    return {
        "encrypted_data": f"[PQC-LATTICE-CIPHER]:{serialized_ciphertext}",
        "telemetry": {
            "original_payload": data,
            "binary_bits": binary_data[:32] + "..." if len(binary_data) > 32 else binary_data,
            "ephemeral_vector_r": r,
            "error_noise_e1": e1,
            "error_noise_e2": e2,
            "vector_u": u,
            "matrix_ciphertext_v": v[:2],  # show first 2 blocks to avoid overwhelming UI
            "modulus": q,
            "algorithm": "Ring-LWE (Kyber Hybrid)"
        }
    }

def encrypt_transaction(data: str) -> str:
    """
    Standard backward-compatible wrapper that returns just the encrypted string.
    """
    res = encrypt_transaction_with_telemetry(data)
    return res["encrypted_data"]

def decrypt_transaction(encrypted_data: str, private_key: dict = None) -> str:
    """
    Decrypts the Ring-LWE ciphertext using the secret key vector s.
    - Decodes base64 payload.
    - Computes message_bit_estimation = (v - s * u) mod q.
    - Decodes bits back to character bytes.
    """
    if not encrypted_data.startswith("[PQC-LATTICE-CIPHER]:"):
        # Fallback if standard string was passed or old cipher format
        if encrypted_data.startswith("[QUANTUM-SAFE-ENCRYPTED]:"):
            return encrypted_data.replace("[QUANTUM-SAFE-ENCRYPTED]:", "")[::-1]
        return encrypted_data
        
    if private_key is None:
        private_key = get_system_keys()["private_key"]
        
    s = private_key["vector_s"]
    q = MODULUS
    n = DIMENSION
    
    try:
        # Decode base64 payload
        serialized = base64.b64decode(encrypted_data.replace("[PQC-LATTICE-CIPHER]:", "")).decode()
        payload = json.loads(serialized)
        u = payload["u"]
        v = payload["v"]
        
        binary_bits = ""
        # Decrypt each block
        for block_v in v:
            # Estimate: decryption_val = (v_i - s * u) mod q
            s_u_dot = sum(s[i] * u[i] for i in range(n))
            for val in block_v:
                decrypted_val = (val - s_u_dot) % q
                # If closer to q/2 (128) than 0 or q, it's a 1, otherwise it's a 0
                diff_to_half = min(abs(decrypted_val - q//2), abs(decrypted_val - q//2 - q), abs(decrypted_val - q//2 + q))
                diff_to_zero = min(abs(decrypted_val), abs(decrypted_val - q))
                if diff_to_half < diff_to_zero:
                    binary_bits += "1"
                else:
                    binary_bits += "0"
                    
        # Convert binary bits back to string
        chars = []
        for i in range(0, len(binary_bits), 8):
            byte = binary_bits[i:i+8]
            if len(byte) == 8:
                chars.append(chr(int(byte, 2)))
        return "".join(chars).rstrip('\x00')
    except Exception as e:
        # Return error explanation or fallback
        return f"Decryption Failed: {str(e)}"
