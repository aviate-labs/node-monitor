from email.message import EmailMessage
from smtplib import SMTP

from .load_config import gmailUsername, gmailPassword, plog


class NodeMonitorEmail(EmailMessage):
    def __init__(self, msg_content, msg_subject="Node Alert"):
        EmailMessage.__init__(self)
        self['Subject'] = msg_subject
        # self['To']      = "NA"
        self['From']    = "Node Monitor by Aviate Labs"
        self.set_content(msg_content)

    def send_to(self, recipient):
        self['To'] = recipient
        with SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(gmailUsername, gmailPassword)
            server.send_message(self)
            plog(f"Email Sent to {self['To']}")
        del self['To']

    def send_recipients(self, recipients):
        for recipient in recipients:
            self.send_to(recipient)

