from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model
    
    Login erfolgt mit email statt username.
    fullname ersetzt first_name und last_name.
    """
    email = models.EmailField(
        unique=True,
        help_text="Email-Adresse für Login"
    )
    fullname = models.CharField(
        max_length=200,
        help_text="Vollständiger Name des Users"
    )
    
    # Login mit Email!
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.fullname} ({self.email})"