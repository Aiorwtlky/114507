import hmac
import hashlib
import secrets
import time

SECRET_KEY = b'my_super_secret_key'  # 自訂的密鑰，保持一致，自己改更安全

def generate_token(device_serial):
    random_part = secrets.token_hex(8)   # 16字亂碼
    timestamp = int(time.time())          # 現在時間
    raw = f"{device_serial}|{random_part}|{timestamp}"
    token = hmac.new(SECRET_KEY, raw.encode(), hashlib.sha256).hexdigest()
    return token, timestamp

def verify_token(token_timestamp, expire_seconds=900):
    current_time = int(time.time())
    return (current_time - token_timestamp) <= expire_seconds
