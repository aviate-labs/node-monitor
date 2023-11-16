from typing import List
from node_monitor.bot_email import EmailBot

class NodeMonitorTracker:
    def __init__(self, email_bot: EmailBot, recipients: List[str]) -> None:
        self.email_bot = email_bot
        self.recipients = recipients
        
    def send_notification(self) -> None:
        subject = "🚨 Node Monitor is Down 🚨"
        body = "Node Monitor is down. Restart required immediately!"
        self.email_bot.send_emails(self.recipients, subject, body)

    def check_server_status(self) -> bool:
        raise NotImplementedError


