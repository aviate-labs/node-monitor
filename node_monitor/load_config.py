from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import json
import logging


# Secrets
load_dotenv()
gmailUsername = os.environ.get('gmailUsername')
gmailPassword = os.environ.get('gmailPassword')
discordBotToken = os.environ.get('discordBotToken')  # Not implemented
slackBotToken = os.environ.get('slackBotToken')


# Config File
with open("config.json") as f:
    config = json.load(f)
    emailRecipients = config['emailRecipients']
    nodeProviderId = config['nodeProviderId']
    lookupTableFile = config['lookupTableFile']
    slackChannelName = config['slackChannelName']

# config['intervalMinutes']
# config['NotifyOnNodeMonitorStartup']
# config['NotifyOnNodeChangeStatus']
# config['NotifyOnAllNodeChanges']
# config['NotifyOnNodeAdded']
# config['NotifyOnNodeRemoved']
# config['IMAPClientEnabled']

# Lookup Table
lookuptable = {}
if lookupTableFile != "":
    with open(lookupTableFile) as f:
        lookuptable = json.load(f)


# Logging - use systemd to forward stdout/stderr to journald
logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper(),
                    format='%(asctime)s:%(levelname)s:%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
