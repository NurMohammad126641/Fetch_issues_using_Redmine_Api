import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from credentials import EMAIL_ADDRESS, EMAIL_PASSWORD, TO_EMAIL, EMAIL_CC_LIST

def send_email(html_content, attachments=[]):
    """Send an email with optional attachments."""
    msg = MIMEMultipart("mixed")
    msg["Subject"] = "📊 [PnE Report] Summary of pending customer's issues"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg["Cc"] = ", ".join(EMAIL_CC_LIST)
    msg.attach(MIMEText(html_content, "html"))

    for filepath in attachments:
        with open(filepath, "rb") as file:
            part = MIMEApplication(file.read(), Name=os.path.basename(filepath))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
            msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

    print("✅ Email sent successfully.")
