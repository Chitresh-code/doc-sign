from django.contrib.auth.models import AbstractUser
from django.db import models
from django_cryptography.fields import encrypt

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('signer', 'Signer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    email = encrypt(models.EmailField(unique=True))
    first_name = encrypt(models.CharField(max_length=150, blank=True))
    last_name = encrypt(models.CharField(max_length=150, blank=True))

    def __str__(self):
        return self.username
