from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin-Konfiguration für Custom User
    """
    list_display = ['email', 'fullname', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'fullname']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('fullname',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 
                      'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'fullname', 'password1', 'password2'),
        }),
    )