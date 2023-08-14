import os
from dotenv import load_dotenv

load_dotenv()


##############################################
## Secrets

EMAIL_USERNAME    = os.environ.get('EMAIL_USERNAME',   '')
EMAIL_PASSWORD    = os.environ.get('EMAIL_PASSWORD',   '')
TOKEN_DISCORD  = os.environ.get('TOKEN_DISCORD', '')  # Not implemented
TOKEN_SLACK    = os.environ.get('TOKEN_SLACK',   '')

assert EMAIL_USERNAME != ''
assert EMAIL_PASSWORD != ''
