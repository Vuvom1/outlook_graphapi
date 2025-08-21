import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.entities.oauth import ToolOAuthCredentials
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from msal import ConfidentialClientApplication


class OutlookProvider(ToolProvider):
    _SCOPES = ["User.Read", "Mail.Read", "Mail.Send", "Mail.ReadWrite"]
    client = ConfidentialClientApplication(
        client_id=os.getenv("AZURE_CLIENT_ID"), client_credential=os.getenv("AZURE_CLIENT_SECRET")
    )

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """Validate access token by calling Microsoft Graph API."""
        if not credentials.get("access_token"):
            raise ToolProviderCredentialValidationError("Microsoft Graph access token is required.")

        # Create request with authentication header
        req = urllib.request.Request(
            "https://graph.microsoft.com/v1.0/me", headers={"Authorization": f"Bearer {credentials['access_token']}"}
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.getcode() != 200:
                    raise ToolProviderCredentialValidationError("Invalid or expired access token.")
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise ToolProviderCredentialValidationError("Invalid or expired access token.")
            else:
                raise ToolProviderCredentialValidationError(f"Failed to validate credentials: {e}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Network error during validation: {e}")

    def _oauth_get_authorization_url(self, redirect_uri: str, system_credentials: Mapping[str, Any]) -> str:
        """Generate OAuth authorization URL."""
        # tenant_id = system_credentials.get("tenant_id", "common")
        # auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"

        authorization_url = self.client.get_authorization_request_url(
            scopes=self._SCOPES,
            redirect_uri="https://cloud.dify.ai/console/api/oauth/plugin/langgenius/outlook/outlook/tool/callback",
        )
        if not authorization_url:
            raise ToolProviderCredentialValidationError("Failed to generate authorization URL.")

        return authorization_url

    def _oauth_get_credentials(
        self, redirect_uri: str, system_credentials: Mapping[str, Any], code: str
    ) -> ToolOAuthCredentials:
        """Exchange authorization code for access token."""

        if not code:
            raise ToolProviderCredentialValidationError("No authorization code provided")

        credentials = self.client.acquire_token_by_authorization_code(
            code=code, scopes=self._SCOPES, redirect_uri=os.getenv("REDIRECT_URI", redirect_uri)
        )

        if not credentials.get("access_token"):
            raise ToolProviderCredentialValidationError("Failed to obtain access token from authorization code.")

        if not credentials.get("refresh_token"):
            raise ToolProviderCredentialValidationError("Failed to obtain refresh token from authorization code.")

        return ToolOAuthCredentials(
            credentials={"access_token": credentials["access_token"], "refresh_token": credentials["refresh_token"]},
            expires_at=credentials.get("expires_in", 3599) + int(time.time()),
        )

    def oauth_refresh_credentials(
        self, redirect_uri: str, system_credentials: Mapping[str, Any], credentials: Mapping[str, Any]
    ) -> ToolOAuthCredentials:
        """Refresh OAuth credentials."""
        refreshed_credentials = self.client.acquire_token_by_refresh_token(
            refresh_token=credentials.get("refresh_token"),
            scopes=self._SCOPES,
        )

        access_token = refreshed_credentials.get("access_token")
        refresh_token = refreshed_credentials.get("refresh_token")

        if not access_token or not refresh_token:
            raise ToolProviderCredentialValidationError("No access token or refresh token in response")

        return ToolOAuthCredentials(
            credentials={"access_token": access_token, "refresh_token": refresh_token},
            expires_at=refreshed_credentials.get("expires_in", 3599) + int(time.time()),
        )


outlook_provider = OutlookProvider()
