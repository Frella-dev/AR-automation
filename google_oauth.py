import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]

def login_google(client_id, client_secret):
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        },
        SCOPES,
    )

    # Opens browser automatically for Google login
    creds = flow.run_local_server(port=0)

    return creds


def save_token(creds, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        f.write(creds.to_json())


def load_token(path):
    if not os.path.exists(path):
        return None

    return Credentials.from_authorized_user_file(path, SCOPES)