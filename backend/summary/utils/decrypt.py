from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.FERNET_KEY.encode())

def decrypt_value(value: str) -> str:
    try:
        return fernet.decrypt(value.encode()).decode()
    except Exception:
        return value  # fallback if not encrypted or error