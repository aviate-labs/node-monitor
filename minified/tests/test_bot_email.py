import pytest
from node_monitor.bot_email import EmailBot


## Initialize EmailBot
import node_monitor.load_config as c
email_bot = EmailBot(c.gmailUsername, c.gmailPassword)


## Run PyTests
def test_send_email():
    pass
