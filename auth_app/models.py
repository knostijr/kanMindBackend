from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom User Manager
    
    overrides create_user and create_superuser
    to use email instead of username
    """
    def create_user(self, email, fullname, password=None, **extra_fields):
        """
        create normal user
        """
        if not email:
            raise ValueError('Email ist erforderlich')
        if not fullname:
            raise ValueError('Fullname ist erforderlich')
        
        email = self.normalize_email(email)
        
        # delete username from extra_fields, if exists
        extra_fields.pop('username', None)
        
        user = self.model(
            email=email,
            fullname=fullname,
            **extra_fields
        )
        
        # generate username from email
        username = email.split('@')[0]
        base_username = username
        counter = 1
        
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user.username = username
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, password=None, **extra_fields):
        """
        create superuser
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

    Custom User model where email is the primary identifier for login.
    The fullname field is used in place of separate first_name and last_name fields.
    """
    email = models.EmailField(
        unique=True,
        help_text="Email-Adresse für Login"
    )
    fullname = models.CharField(
        max_length=200,
        help_text="Vollständiger Name des Users"
    )
    
    # usw Custom Manager 
    objects = UserManager()
    
    # Login with Email!
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.fullname} ({self.email})"