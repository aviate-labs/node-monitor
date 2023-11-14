#!/usr/bin/env python3

## A custom script that imports some classes from node_monitor
## and sends out a custom email message


## Import the deired email as text (this name is in the .gitignore)
with open('email_to_send.txt', 'r') as f:
    email = f.read()


## Import nodemonitor
from node_monitor.node_monitor import NodeMonitor
from node_monitor.bot_email import EmailBot
from node_monitor.node_provider_db import NodeProviderDB
import node_monitor.load_config as c

# Initialize nodemonitor
email_bot = EmailBot(c.EMAIL_USERNAME, c.EMAIL_PASSWORD)
node_provider_db = NodeProviderDB(
    c.DB_HOST, c.DB_NAME, c.DB_PORT,
    c.DB_USERNAME, c.DB_PASSWORD)
nm = NodeMonitor(node_provider_db, email_bot, None, None)


# Initialize broadcaster



## Send the emails

def main():
    print("I don't do anything, yet...")


if __name__ == "__main__":
    main()