"""Watchdog Script

This script monitors the status of a Node Monitor service and 
sends email notifications if the service goes offline or is unreachable.

Usage:

1. Set the check interval in seconds (CHECK_INTERVAL_SECONDS) 
   based on the desired frequency of monitoring. 
   The default is 900 seconds (15 minutes).

2. Define an instance of the EmailBot class with the required email credentials,


Note:
- The `start()` method runs indefinitely, so make sure to interrupt 
  the script manually (^C) when needed.

- It is recommended to customize the email notification content 
  in the `send_notification()` method based on your specific requirements.

- This script assumes the existence of the 'EmailBot' and 'load_config' modules, 
  which should be available in the specified import paths.
"""

import requests
import time
from typing import List

import node_monitor.load_config as c
from node_monitor.bot_email import EmailBot

CHECK_INTERVAL_SECONDS = 900

class Watchdog:
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

    def is_node_monitor_online(self) -> bool:
        try:
            response = requests.get(self.node_monitor_url)
            response.raise_for_status()
            data = response.json()
            if data['status'] == 'online':
                return True
            return False
        except Exception as e:
            return False
            
    def start(self) -> None:
        while True:
            if not self.is_node_monitor_online():
                self.send_notification()
            time.sleep(CHECK_INTERVAL_SECONDS)

email_bot = EmailBot(c.EMAIL_USERNAME, c.EMAIL_PASSWORD)
watchdog = Watchdog(email_bot, c.EMAIL_ADMINS_LIST, c.NODE_MONITOR_URL)

assert watchdog.is_node_monitor_online() == True

if __name__ == "__main__":
    watchdog.start()
