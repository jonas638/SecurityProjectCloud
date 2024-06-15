 
import requests
import json

client_id = ""  # Application (Client) ID
tenant_id = ""  # Directory (Tenant) ID
client_secret = ""  # Client Secret (Replace with your actual client secret)
resource_uri = "https://graph.microsoft.com"  # Application ID URI

# Authentication
body = {
            "client_id": client_id,
                "client_secret": client_secret,
            "resource": resource_uri,
             "grant_type": "client_credentials"
        }
token_response = requests.post(f"https://login.microsoftonline.com/{tenant_id}/oauth2/token", data=body)
access_token = token_response.json()["access_token"]

headers = {
            "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
          }

# Query users
audit_logs_response = requests.get("https://graph.microsoft.com/v1.0/users", headers=headers)

response = requests.get(endpoint, headers=headers)

json_content = audit_logs_response.json()

if response.status_code == 200:
    users = response.json().get('value', [])
    for user in users:
        email = user.get('mail')
        if email:
            print(email)
else:
    print("Failed to retrieve users:", response.text)
