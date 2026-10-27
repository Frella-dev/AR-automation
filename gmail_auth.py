import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

TOKEN_PATH = os.path.join("tokens", "gmail_token.json")


def _get_client_config():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in environment."
        )

    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                "http://localhost:8501/"
            ],
        }
    }


def load_token():
    """
    Load existing Gmail OAuth token
    """

    if not os.path.exists(TOKEN_PATH):
        return None

    creds = Credentials.from_authorized_user_file(
        TOKEN_PATH,
        SCOPES
    )

    # Refresh expired token automatically
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds


def login_google():
    """
    Run OAuth login flow
    """

    flow = InstalledAppFlow.from_client_config(
        _get_client_config(),
        SCOPES
    )

    creds = flow.run_local_server(
        host="localhost",
        port=8501,
        prompt="consent",
        authorization_prompt_message="Please authorize Gmail access"
    )

    os.makedirs("tokens", exist_ok=True)

    with open(TOKEN_PATH, "w") as token:
        token.write(creds.to_json())

    return creds