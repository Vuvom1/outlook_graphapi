"""
Services package for the Outlook service.
Contains business logic and external service integrations.
"""

from .auth_service import AuthService
from .email_service import EmailService

__all__ = ["EmailService", "AuthService"]
