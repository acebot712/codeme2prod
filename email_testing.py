import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import utils, encoders
import dkim
from dotenv import load_dotenv
load_dotenv()

URL="http://127.0.0.1:8000/"

# Helper function to send a verification email
def send_verification_email(email, token):
    sender = "info@codeme.site"
    recipient = email
    subject = "Verify your account"
    body_text = f"Please click on this link to verify your account: http://127.0.0.1:8000/verify/{token}"
    
    body_html = f"""
    <html>
        <body>
            <p>Please click on <a href="{URL}verify/{token}">this link</a> to verify your account.</p>
        </body>
    </html>
    """
    
    message = MIMEMultipart('alternative')
    message['From'] = f"CodeMe <{sender}>"
    message['To'] = recipient
    message['Subject'] = subject
    message['Date'] = utils.formatdate(localtime = 1)
    message['Message-ID'] = utils.make_msgid()

    # Add plain text version of the email
    message.attach(MIMEText(body_text, 'plain'))

    # Add HTML version of the email
    message.attach(MIMEText(body_html, 'html'))

    with smtplib.SMTP('smtp.zoho.in', 587) as server:
        server.starttls()

        # Login to the sender's email account
        server.login(sender, os.environ.get('PASSWORD', 'PASSWORD'))

        # Add a DKIM signature
        dkim_domain = 'codeme.site'
        dkim_selector = os.environ.get('DKIM_SELECTOR', 'default')
        dkim_private_key = os.environ.get('DKIM_PRIVATE_KEY','')
        dkim_signature = dkim.sign(
            message.as_bytes(),
            dkim_domain.encode(),
            dkim_selector.encode(),
            dkim_private_key.encode(),
        )
        message['DKIM-Signature'] = dkim_signature.decode().lstrip('DKIM-Signature:')
        # Send the email
        server.sendmail(sender, recipient, message.as_string())


if __name__ == '__main__':
    send_verification_email("abhijoy.sar@gmail.com","123")