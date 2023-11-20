import requests
import schedule
import time
import node_monitor.load_config as c
from typing import List
from node_monitor.bot_email import EmailBot

# CHECK_INTERVAL = 15*60
CHECK_INTERVAL = 5

class Watchdog:
    def __init__(
            self, 
            email_bot: EmailBot, 
            recipients: List[str],
            node_monitor_url: str) -> None:
        self.email_bot = email_bot
        self.recipients = recipients
        self.node_monitor_url = node_monitor_url
        self.jobs = [
            # schedule.every(15).minutes.do(self.check_node_monitor_status)
            schedule.every(5).seconds.do(self.check_node_monitor_status)
        ]
        
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

        except Exception as e:
            self.send_notification()
            
    def start(self) -> None:
        while True:
            schedule.run_pending()
            time.sleep(CHECK_INTERVAL)

email_bot = EmailBot(c.EMAIL_USERNAME, c.EMAIL_PASSWORD)
watchdog = Watchdog(email_bot, c.EMAIL_ADMINS_LIST, c.NODE_MONITOR_URL)

if __name__ == "__main__":
    watchdog.start()
