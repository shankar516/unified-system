import csv
import os
import hmac
import base64
import hashlib
import secrets
from datetime import datetime

USERS_CSV = "users.csv"

CSV_HEADERS = [
    "username",
    "email",
    "password_hash",   # base64
    "salt",            # base64
    "created_at"
]

def _ensure_users_file():
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def _pbkdf2_hash(password: str, salt: bytes, iterations: int = 120_000) -> bytes:
    # PBKDF2-HMAC-SHA256
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

def user_exists(username: str) -> bool:
    _ensure_users_file()
    username = username.strip().lower()
    with open(USERS_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("username", "").strip().lower() == username:
                return True
    return False

def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Returns (success, message)
    """
    _ensure_users_file()

    username = (username or "").strip()
    email = (email or "").strip()
    password = (password or "").strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if " " in username:
        return False, "Username must not contain spaces."
    if "@" not in email or "." not in email:
        return False, "Enter a valid email."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if user_exists(username):
        return False, "Username already exists."

    salt = secrets.token_bytes(16)
    pwd_hash = _pbkdf2_hash(password, salt)

    row = {
        "username": username,
        "email": email,
        "password_hash": base64.b64encode(pwd_hash).decode("utf-8"),
        "salt": base64.b64encode(salt).decode("utf-8"),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(row)

    return True, "Registration successful. Please login."

def verify_login(username: str, password: str) -> tuple[bool, str]:
    """
    Returns (success, message)
    """
    _ensure_users_file()

    username = (username or "").strip()
    password = (password or "").strip()

    if not username or not password:
        return False, "Enter username and password."

    with open(USERS_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("username", "").strip().lower() == username.lower():
                try:
                    salt = base64.b64decode(row["salt"])
                    stored_hash = base64.b64decode(row["password_hash"])
                except Exception:
                    return False, "Corrupted user record."

                check_hash = _pbkdf2_hash(password, salt)
                if hmac.compare_digest(stored_hash, check_hash):
                    return True, "Login successful."
                return False, "Invalid password."

    return False, "User not found."
