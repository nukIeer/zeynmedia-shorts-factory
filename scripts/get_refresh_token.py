"""Bir kere lokalde çalıştır: YouTube refresh token'ı üretir.

Kullanım:
  pip install google-auth-oauthlib
  python scripts/get_refresh_token.py path/to/client_secret.json
"""
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

if len(sys.argv) != 2:
    sys.exit("Kullanım: python scripts/get_refresh_token.py client_secret.json")

flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

print("\nGitHub Secrets'a ekle:\n")
print(f"YT_CLIENT_ID      = {creds.client_id}")
print(f"YT_CLIENT_SECRET  = {creds.client_secret}")
print(f"YT_REFRESH_TOKEN  = {creds.refresh_token}")
