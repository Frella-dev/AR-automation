import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build


def send_mail(creds, to_email, subject, body):

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    message = MIMEText(body)

    message["to"] = to_email
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()
