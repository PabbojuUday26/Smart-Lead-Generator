import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_email(sender, app_password, receiver, subject, body, attachment_path=None, link=None):
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject

    if link:
        body += f"\n\nHere is the link: {link}"

    msg.attach(MIMEText(body, "plain"))

    if attachment_path:
        try:
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                msg.attach(part)
        except Exception as e:
            print(f"Error attaching file: {e}")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, app_password)
            server.send_message(msg)
        print(f"[OK] Email sent to {receiver}")
    except Exception as e:
        print(f"[ERROR] Error sending to {receiver}: {e}")
        raise e  # Re-raise to let the caller handle it
