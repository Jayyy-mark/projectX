import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(input_str: str):
    sender_email = "jaycoab2@gmail.com"
    password = "tmxdpsxeduimklat"  # App password, NOT Gmail login password

    # Parse the input string
    parts = dict(item.split("=", 1) for item in input_str.split(";") if "=" in item)
    parts = {k.strip(): v.strip() for k, v in parts.items()}  # Remove extra spaces
    
    receiver_email = parts.get("receiver_email")
    subject = parts.get("subject")
    body = parts.get("body")

    if not receiver_email or not subject or not body:
        return "Error: Missing required email parameters."

    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.send_message(msg)

    return f"Email sent successfully to {receiver_email}!"

# # Test
# print(send_mail("receiver_email=aungkyawgun21@gmail.com;subject=meeting;body=come and meet me at 1PM"))

