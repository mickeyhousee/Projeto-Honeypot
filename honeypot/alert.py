import smtplib
from email.mime.text import MIMEText

# Email configuration
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USER = 'your_email@example.com'
SMTP_PASS = 'your_password'
SENDER = 'your_email@example.com'
RECIPIENT = 'recipient@example.com'


def send_email_alert(subject, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = SENDER
        msg['To'] = RECIPIENT

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SENDER, [RECIPIENT], msg.as_string())
        print(f"[ALERT] Email sent: {subject}")
    except Exception as e:
        print(f"[ALERT] Failed to send email: {e}") 