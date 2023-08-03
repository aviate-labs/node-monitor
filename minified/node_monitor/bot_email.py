from email.message import EmailMessage
from smtplib import SMTP


class EmailBot():
    def __init__(self, gmail_username: str, gmail_password: str):
        self.gmail_username = gmail_username
        self.gmail_password = gmail_password
    
    def send_email(self, recipient: str, subject: str, body: str) -> None:
        # Not Yet Implemented
        pass
