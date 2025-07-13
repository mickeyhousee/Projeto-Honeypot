import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.backends import default_backend
import base64
import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), '../logs/honeypot.log')
KEY_FILE = os.path.join(os.path.dirname(__file__), 'logkey.bin')
PRIV_KEY_FILE = os.path.join(os.path.dirname(__file__), 'private_key.pem')
PUB_KEY_FILE = os.path.join(os.path.dirname(__file__), 'public_key.pem')

backend = default_backend()

# Generate or load symmetric key for encryption
def get_symmetric_key():
    if not os.path.exists(KEY_FILE):
        key = os.urandom(32)
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return key

# Generate or load RSA key pair for signing
def get_rsa_keys():
    if not os.path.exists(PRIV_KEY_FILE):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=backend
        )
        with open(PRIV_KEY_FILE, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        with open(PUB_KEY_FILE, 'wb') as f:
            f.write(private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
    else:
        with open(PRIV_KEY_FILE, 'rb') as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None, backend=backend)
    with open(PUB_KEY_FILE, 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read(), backend=backend)
    return private_key, public_key

symmetric_key = get_symmetric_key()
private_key, public_key = get_rsa_keys()

# Encrypt log entry
def encrypt_log_entry(entry):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(symmetric_key), modes.CFB(iv), backend=backend)
    encryptor = cipher.encryptor()
    ct = encryptor.update(entry.encode()) + encryptor.finalize()
    return base64.b64encode(iv + ct).decode()

# Sign log entry
def sign_log_entry(entry):
    signature = private_key.sign(
        entry.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

# Log event to encrypted, signed file
def log_event(service, ip, timestamp, data):
    entry = f"[{service}] {timestamp} - {ip} - {data}"
    encrypted_entry = encrypt_log_entry(entry)
    signature = sign_log_entry(entry)
    with open(LOG_FILE, 'a') as f:
        f.write(f"{encrypted_entry}||{signature}\n")

# Export logs (returns decrypted entries)
def export_logs():
    if not os.path.exists(LOG_FILE):
        return []
    entries = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            if '||' not in line:
                continue
            encrypted_entry, signature = line.strip().split('||')
            # Decrypt
            raw = base64.b64decode(encrypted_entry)
            iv = raw[:16]
            ct = raw[16:]
            cipher = Cipher(algorithms.AES(symmetric_key), modes.CFB(iv), backend=backend)
            decryptor = cipher.decryptor()
            entry = decryptor.update(ct) + decryptor.finalize()
            # Verify signature
            try:
                public_key.verify(
                    base64.b64decode(signature),
                    entry,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                entries.append(entry.decode())
            except Exception as e:
                entries.append(f"[INVALID SIGNATURE] {entry.decode()}")
    return entries 