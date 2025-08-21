from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DeleteEmailTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Delete an email from Outlook using Microsoft Graph API
        """
        try:
            # Get parameters
            message_id = tool_parameters.get("message_id")

            if not message_id:
                yield self.create_text_message("Message ID is required.")
                return

            # Get access token from OAuth credentials
            access_token = tool_parameters.get("access_token")
            if not access_token:
                yield self.create_text_message("Access token is required in credentials.")
                return

            try:
                # Delete email
                response = self._delete_email(access_token, message_id)

                if isinstance(response, str):  # Error message
                    yield self.create_text_message(response)
                    return

                # Success: return confirmation message
                yield self.create_text_message(f"Email with ID {message_id} deleted successfully.")
                return
            except Exception as e:
                yield self.create_text_message(f"Error deleting email: {str(e)}")
                return

        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
            return

    def _delete_email(self, access_token: str, message_id: str):
        """
        Delete an email using Microsoft Graph API
        """
        try:
            url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
            headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

            response = requests.delete(url, headers=headers)

            if response.status_code == 204:
                return {"status": "success", "message": f"Email with ID {message_id} deleted."}
            else:
                return f"Failed to delete email: {response.text}"

        except requests.RequestException as e:
            return f"Network error during deletion: {str(e)}"


delete_message_tool = DeleteEmailTool(
    runtime=None,
    session=None,
)
