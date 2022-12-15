from datetime import datetime, timezone
from dotenv import load_dotenv
import os, json


### Secrets
load_dotenv()
gmailUsername       = os.environ.get('gmailUsername')
gmailPassword       = os.environ.get('gmailPassword')
discordBotToken     = os.environ.get('discordBotToken')


### Config File
with open("config.json") as f:
    config = json.load(f)
    emailRecipients = config['emailRecipients']
    nodeProviderId  = config['nodeProviderId']
    lookupTableFile = config['lookupTableFile']

# config['intervalMinutes']
# config['NotifyOnNodeMonitorStartup']
# config['NotifyOnNodeChangeStatus']
# config['NotifyOnAllNodeChanges']
# config['NotifyOnNodeAdded']
# config['NotifyOnNodeRemoved']
# config['loggingEnabled']


### Lookup Table
lookuptable = {}
if lookupTableFile != "":
    with open(lookupTableFile) as f:
        lookuptable = json.load(f)



def plog(s):
    """prints and logs"""
    ## TODO: delete and replace with logging library
    new_s = f'[{datetime.utcnow()}]: -- ' + s
    if config['loggingEnabled']:
        utcdatestr = datetime.now(timezone.utc).date().isoformat()
        with open('logs/' + utcdatestr + '.log', 'a') as f:
            f.write(new_s + "\n")
    print(new_s)

