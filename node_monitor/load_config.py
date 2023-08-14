import os
from dotenv import load_dotenv

load_dotenv()


##############################################
## Secrets

gmailUsername    = os.environ.get('gmailUsername',   '')
gmailPassword    = os.environ.get('gmailPassword',   '')
discordBotToken  = os.environ.get('discordBotToken', '')  # Not implemented
slackBotToken    = os.environ.get('slackBotToken',   '')

## Pre-flight check
# We assert that the secrets are not empty so that
# Node Monitor will fail when run incorrectly
# Note: it may be wise to move this into `__main__.py` instead
assert gmailUsername != '', "Please set credentials in .env"
assert gmailPassword != '', "Please set credentials in .env"
