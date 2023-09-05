import os
from dotenv import load_dotenv

load_dotenv()


##############################################
## Secrets

EMAIL_USERNAME  = os.environ.get('EMAIL_USERNAME',   '')
EMAIL_PASSWORD  = os.environ.get('EMAIL_PASSWORD',   '')
TOKEN_DISCORD   = os.environ.get('TOKEN_DISCORD', '')  # Not implemented
TOKEN_SLACK     = os.environ.get('TOKEN_SLACK',   '')
DB_HOST         = os.environ.get('DB_HOST', '')
DB_USERNAME     = os.environ.get('DB_USERNAME', '')
DB_PASSWORD     = os.environ.get('DB_PASSWORD', '')
DB_NAME         = os.environ.get('DB_NAME', '')
DB_PORT         = os.environ.get('DB_PORT', '')

## Pre-flight check
# We assert that the secrets are not empty so that
# Node Monitor will fail when run incorrectly
# Note: it may be wise to move this into `__main__.py` instead
assert EMAIL_USERNAME != '', "Please set email credentials in .env"
assert EMAIL_PASSWORD != '', "Please set email credentials in .env"
assert DB_HOST        != '', "Please set database credentials in .env"
assert DB_USERNAME    != '', "Please set database credentials in .env"
assert DB_PASSWORD    != '', "Please set database credentials in .env"
assert DB_NAME        != '', "Please set database credentials in .env"
assert DB_HOST        != '', "Please set database credentials in .env"
