from email.message import EmailMessage
import smtplib
from typing import List


class EmailBot:
    def __init__(
            self, email_username: str, email_password: str, 
            smtp_server: str = 'smtp.gmail.com', smtp_port: int = 587) -> None:
        """Create an EmailBot object that can send emails from the given
        email account. The default SMTP server is gmail, but this can be
        changed if desired."""
        self.email_username = email_username
        self.email_password = email_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port


    def send_emails(self, 
            recipients: List[str], subject: str, body: str) -> None:
        """Send an email to each recipient with the given subject and body.
        Logs in and out of the SMTP server only once even if multiple 
        recipients are specified."""
        email_message = EmailMessage()
        email_message['Subject'] = subject
        email_message['From'] = "Node Monitor"
        email_message['To'] = 'will-be-overwritten'
        email_message.set_content(body)
        # # # #
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.email_username, self.email_password)
            # Note: You can pass a list to 'To'
            # I chose not to do this to keep recipients mutually blind:
            for recipient in recipients:
                del email_message['To']
                email_message['To'] = recipient
                server.send_message(email_message)
