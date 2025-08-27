from msal import ConfidentialClientApplication
import os
import time
from datetime import datetime

client = ConfidentialClientApplication(
    client_id=os.getenv("AZURE_CLIENT_ID"), client_credential=os.getenv("AZURE_CLIENT_SECRET")
)

if not os.getenv("AZURE_CLIENT_ID") or not os.getenv("AZURE_CLIENT_SECRET"):
    raise ValueError("Please set the AZURE_CLIENT_ID and AZURE_CLIENT_SECRET environment variables.")

_SCOPES = ["User.Read", "Mail.Read", "Mail.Send", "Mail.ReadWrite"]

# code = "M.C510_SN1.2.U.f95b3020-3ab7-d1d9-88fa-54b9d31bc2f5"

# creds = client.acquire_token_by_authorization_code(
#             code=code, scopes=_SCOPES, redirect_uri=os.getenv("REDIRECT_URI", "https://cloud.dify.ai/console/api/oauth/plugin/langgenius/outlook/outlook/tool/callback")
# )

# print(creds)

def display_accounts():
    """Display cached accounts with timestamp"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n=== Account Check at {current_time} ===")
    
    accounts = client.get_accounts()
    print(f"Accounts found: {len(accounts)}")
    
    if accounts:
        print("Cached accounts:")
        for i, account in enumerate(accounts, 1):
            username = account.get('username', 'Unknown')
            home_account_id = account.get('home_account_id', 'Unknown')
            print(f"  {i}. Username: {username}")
            print(f"     Home Account ID: {home_account_id}")
            
            # Try to get token silently to check if account is still valid
            try:
                result = client.acquire_token_silent(_SCOPES, account=account)
                if result:
                    expires_in = result.get('expires_in', 0)
                    print(f"     Token Status: ✅ Valid (expires in {expires_in}s)")
                else:
                    print(f"     Token Status: ❌ Invalid or expired")
            except Exception as e:
                print(f"     Token Status: ❌ Error: {str(e)}")
    else:
        print("No accounts found in cache")
    
    print("=" * 50)

# Initial account check
display_accounts()

# Display accounts every 7 seconds
print("\nStarting account monitoring every 7 seconds...")
print("Press Ctrl+C to stop")

try:
    while True:
        time.sleep(7)
        display_accounts()
except KeyboardInterrupt:
    print("\n\nAccount monitoring stopped by user")
    print("Final account check:")
    display_accounts()


