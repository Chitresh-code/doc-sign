from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.SECRET_KEY[:32].encode())  # ensure it’s 32-byte

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()