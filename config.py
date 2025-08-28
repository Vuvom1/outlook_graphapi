"""
Configuration file for Outlook provider system credentials.
"""

import os
from typing import Any

# System credentials for Microsoft Graph API OAuth
SYSTEM_CREDENTIALS: dict[str, Any] = {
    # Azure AD Application credentials
    "client_id": os.getenv("AZURE_CLIENT_ID", "your-client-id-here"),
    "client_secret": os.getenv("AZURE_CLIENT_SECRET", "your-client-secret-here"),
    # Optional: Tenant ID (defaults to "common" for multi-tenant)
    "tenant_id": os.getenv("AZURE_TENANT_ID", "common"),
    # Optional: Custom scope (uses default if not specified)
    # "scope": "Mail.Read Mail.Send Mail.ReadWrite offline_access"
}

# Redirect URI for OAuth flow (automatically detects HTTPS/HTTP)
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://localhost:8000/client/callback")
