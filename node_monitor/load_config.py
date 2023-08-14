import os
from dotenv import load_dotenv

load_dotenv()


##############################################
## Secrets

gmailUsername    = os.environ.get('gmailUsername',   '')
gmailPassword    = os.environ.get('gmailPassword',   '')
discordBotToken  = os.environ.get('discordBotToken', '')  # Not implemented
slackBotToken    = os.environ.get('slackBotToken',   '')


# We assert that the secrets are not empty so that
# Node Monitor will fail when run incorrectly
assert gmailUsername != '', "Please set credentials in .env"
assert gmailPassword != '', "Please set credentials in .env"
