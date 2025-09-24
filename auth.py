import os
import hmac
import hashlib


def _get_secret() -> bytes:
	secret = os.environ.get("APP_SECRET_KEY", "streamlit-bolos-secret")
	return secret.encode("utf-8")


def hash_password(password: str) -> str:
	secret = _get_secret()
	digest = hmac.new(secret, password.encode("utf-8"), hashlib.sha256).hexdigest()
	return digest


def verify_password(password: str, password_hash: str) -> bool:
	calc = hash_password(password)
	return hmac.compare_digest(calc, password_hash)
