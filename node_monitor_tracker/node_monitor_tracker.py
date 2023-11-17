import requests
from typing import List
from node_monitor.bot_email import EmailBot

class NodeMonitorTracker:
    def __init__(
            self, 
            email_bot: EmailBot, 
            recipients: List[str],
            node_monitor_url: str) -> None:
        self.email_bot = email_bot
        self.recipients = recipients
        self.node_monitor_url = node_monitor_url
        
    def send_notification(self) -> None:
        subject = "🚨 Node Monitor is Down 🚨"
        body = "Node Monitor is down. Restart required immediately!"
        self.email_bot.send_emails(self.recipients, subject, body)

    def check_node_monitor_status(self) -> bool:
        try:
            response = requests.get(self.node_monitor_url)
            data = response.json()

            if data['status'] == 'offline':
                self.send_notification()
            else:
                print('Server is online.')

        except Exception as e:
            self.send_notification()
            print(f"An error occurred: {e}")


