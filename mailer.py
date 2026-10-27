# import smtplib
# import os
# from email.mime.text import MIMEText
# from dotenv import load_dotenv

# load_dotenv()

# def send_mail(to_email, subject, body):

#     sender = os.getenv("GMAIL_USER")
#     password = os.getenv("GMAIL_APP_PASSWORD")

#     msg = MIMEText(body)

#     msg["Subject"] = subject
#     msg["From"] = sender
#     msg["To"] = to_email

#     server = smtplib.SMTP("smtp.gmail.com", 587)

#     server.starttls()

#     server.login(sender, password)

#     server.sendmail(sender, to_email, msg.as_string())

#     server.quit()

import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_mail(to_email, subject, body):

    sender = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")

    # ---------------------------
    # CC EMAILS
    # ---------------------------
    cc_emails = [
        "fc@frellainternational.com",
        "sudath@frellainternational.com"
    ]

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    msg["Cc"] = ", ".join(cc_emails)

    # Combine TO + CC for sending
    recipients = [to_email] + cc_emails

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)

    server.sendmail(
        sender,
        recipients,
        msg.as_string()
    )

    server.quit()