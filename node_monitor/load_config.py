import os
from dotenv import load_dotenv

load_dotenv()


##############################################
## Secrets

EMAIL_USERNAME          = os.environ.get('EMAIL_USERNAME',          '')
EMAIL_PASSWORD          = os.environ.get('EMAIL_PASSWORD',          '')
TOKEN_DISCORD           = os.environ.get('TOKEN_DISCORD',           '')  # Not implemented
TOKEN_SLACK             = os.environ.get('TOKEN_SLACK',             '')
SLACK_SIGNING_SECRET    = os.environ.get('SLACK_SIGNING_SECRET',    '')
TOKEN_TELEGRAM  = os.environ.get('TOKEN_TELEGRAM',   '')

## Pre-flight check
# We assert that the secrets are not empty so that
# Node Monitor will fail when run incorrectly
# Note: it may be wise to move this into `__main__.py` instead
assert EMAIL_USERNAME != '', "Please set credentials in .env"
assert EMAIL_PASSWORD != '', "Please set credentials in .env"
