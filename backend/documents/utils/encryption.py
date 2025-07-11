from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.FERNET_KEY.encode())

def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()