from django.urls import path

from .views import EmailCheckView, LoginView, RegistrationView

"""
URL configuration for the authentication and user management endpoints.

This module defines the mapping between URL paths and their corresponding 
class-based views (CBVs) for user registration, authentication, and validation.
"""

urlpatterns = [
    # Endpoint for creating a new user account
    path("registration/", RegistrationView.as_view(), name="registration"),
    # Endpoint for authenticating a user and obtaining a token or session
    path("login/", LoginView.as_view(), name="login"),
    # Endpoint to verify if an email address is already in use or is valid
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
]
