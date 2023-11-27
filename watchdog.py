#!/usr/bin/env python3

## Watchdog Script
##
## This script monitors the status of a Node Monitor service and
## sends email notifications if the service goes offline or is unreachable.
## You can run this in GNU Screen or another multiplexer/background process manager.
##
##
## Usage:
##   1. Set the check interval in seconds (CHECK_INTERVAL_SECONDS)
##   2. Instantiate an EmailBot with the desired username, password, and (optional) SMTP server
##   3. Instantiate class Watchdog
##   4. Call the mainloop() method to begin monitoring
##   2. Define an instance of the EmailBot class with the required email credentials
##
##


import requests
import time
from typing import List

import node_monitor.load_config as c
from node_monitor.bot_email import EmailBot

CHECK_INTERVAL_SECONDS = 15 * 60 # 15 minutes


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

    def mainloop(self) -> None:
        print("Watchdog is running...")
        while True:
            if not self.is_node_monitor_online():
                self.send_notification()
            time.sleep(CHECK_INTERVAL_SECONDS)


# init
email_bot = EmailBot(c.EMAIL_USERNAME, c.EMAIL_PASSWORD)
watchdog = Watchdog(email_bot, c.EMAIL_ADMINS_LIST, c.NODE_MONITOR_URL)


# pre-flight check
assert c.EMAIL_USERNAME != '', "Please set email credentials in .env"
assert c.EMAIL_PASSWORD != '', "Please set email credentials in .env"
assert c.EMAIL_ADMINS_LIST != '', "Please set email credentials in .env"
assert c.NODE_MONITOR_URL != '', "Please set email credentials in .env"
assert watchdog.is_node_monitor_online() == True, "Init fail: Node Monitor is offline"


if __name__ == "__main__":
    watchdog.mainloop()
