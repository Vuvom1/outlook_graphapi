from collections.abc import Generator
from typing import Any
import requests
import urllib.parse

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class UpdateMessageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Update an email message using Microsoft Graph API
        """
        try:
            # Get parameters
            email_id = tool_parameters.get("email_id", "")
            subject = tool_parameters.get("subject", "")
            body_content = tool_parameters.get("body_content", "")
            body_type = tool_parameters.get("body_type", "text")  # 'text' or 'html'
            
            # Validate required parameters
            if not email_id:
                yield self.create_text_message("Email ID is required.")
                return
            
            if not subject and not body_content:
                yield self.create_text_message("At least one of subject or body content must be provided.")
                return
            
            # Get access token from OAuth credentials
            access_token = tool_parameters.get("access_token")
            if not access_token:
                yield self.create_text_message("Access token is required in credentials.")
                return
            
            try:
                # Update email message
                result = self._update_email_message(access_token, email_id, subject, body_content, body_type)
                
                if isinstance(result, str):  # Error message
                    yield self.create_text_message(result)
                    return
                
                # Success
                yield self.create_text_message("Email updated successfully!")
                yield self.create_json_message(result)
                
            except Exception as e:
                yield self.create_text_message(f"Error updating email: {str(e)}")
                return
                
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
            return
    
    def _update_email_message(self, access_token: str, email_id: str, 
                              subject: str, body_content: str, body_type: str):
        """
        Update email message using Microsoft Graph API
        """
        try:
            url = f"https://graph.microsoft.com/v1.0/me/messages/{urllib.parse.quote(email_id)}"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "subject": subject,
                "body": {
                    "contentType": body_type,
                    "content": body_content
                }
            }
            
            response = requests.patch(url, headers=headers, json=data)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return "Authentication failed. Token may be expired."
            elif response.status_code == 403:
                return "Access denied. Check app permissions (Mail.ReadWrite required)."
            elif response.status_code == 404:
                return f"Email with ID '{email_id}' not found."
            else:
                return f"API error {response.status_code}: {response.text}" 
            
        except requests.exceptions.RequestException as e:
            return f"Network error: {str(e)}"
        except Exception as e:
            return f"Error updating email: {str(e)}"
        
update_message_tool = UpdateMessageTool(
    runtime=None,  # Set runtime when initializing the tool
    session=None,  # Set session when initializing the tool
)