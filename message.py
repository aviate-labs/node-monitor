#!/usr/bin/env python3
from devtools import debug
import toolz

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


# Initialize broadcaster (this is for email, slack, telegram)
# We don't need to use it (we can just send emails with email_bot)
subscribers = nm.node_provider_db.get_subscribers_as_dict()
email_lookup = nm.node_provider_db.get_emails_as_dict()
subscriber_principals = list(subscribers.keys())
broadcaster = nm._make_broadcaster()
unique_emails = list(toolz.unique(toolz.concat(list(email_lookup.values()))))
# debug(unique_emails)


## Set up the email parameters
recipients = ['george@aviatelabs.co']
subject = "Custom Email Subject"
message = email


def main():
    print("Sending emails...")
    # Uncomment this following line to actually send the emails
    # email_bot.send_emails(recipients, subject, message)
    print("Done!")


if __name__ == "__main__":
    main()