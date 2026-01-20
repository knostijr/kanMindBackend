# Standardbibliothek
# (keine benötigt)

# Drittanbieter (Third-party)
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom User Manager
    
    Überschreibt create_user und create_superuser
    um mit email statt username zu arbeiten.
    """
    def create_user(self, email, fullname, password=None, **extra_fields):
        """
        Erstellt normalen User
        """
        if not email:
            raise ValueError('Email ist erforderlich')
        if not fullname:
            raise ValueError('Fullname ist erforderlich')
        
        email = self.normalize_email(email)
        
        # Username automatisch aus Email generieren
        username = email.split('@')[0]
        base_username = username
        counter = 1
        
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = self.model(
            email=email,
            username=username,
            fullname=fullname,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, fullname, password=None, **extra_fields):
        """
        Erstellt Superuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser muss is_staff=True haben')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser muss is_superuser=True haben')
        
        return self.create_user(email, fullname, password, **extra_fields)


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
    
    # Custom Manager verwenden
    objects = UserManager()
    
    # Login mit Email!
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.fullname} ({self.email})"