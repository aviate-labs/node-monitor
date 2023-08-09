import pytest
import time
from unittest.mock import patch
import requests
import re
from node_monitor.bot_email import EmailBot
import node_monitor.load_config as c

# Usage to actually send emails:
#   -s is to print to stdout
#   --send_emails is a custom flag
# pytest -s --send_emails tests/test_bot_email.py

@patch('smtplib.SMTP')
def _send_emails_mock(mock_smtp):
    """Mock sending emails and check that the correct calls were made."""
    mock_instance = mock_smtp.return_value.__enter__.return_value

    recipients = ['test1@example.com', 'test2@example.com']
    subject = 'Test Subject'
    body = 'Test Body'

    bot = EmailBot('username', 'password')
    bot.send_emails(recipients, subject, body)

    assert mock_instance.ehlo.call_count == 2
    assert mock_instance.starttls.call_count == 1
    assert mock_instance.login.call_count == 1
    assert mock_instance.send_message.call_count == 2
    mock_instance.login.assert_called_once_with('username', 'password')


def _send_emails_network():
    """Send real emails over a network to a test inbox and check that 
    they were received."""
    email_bot = EmailBot(c.gmailUsername, c.gmailPassword)
    # Uses an anonymous email inbox for testing
    recipients = ['nodemonitortest@mailnesia.com']
    subject = str(time.time())
    body = 'Test Body'
    email_bot.send_emails(recipients, subject, body)
    # Automatically check the email inbox
    print("https://mailnesia.com/mailbox/nodemonitortest")
    print(f'Email Subject should match: {subject}')
    print('Checking now... Waiting 10 seconds...')
    time.sleep(10)
    url = 'https://mailnesia.com/mailbox/nodemonitortest'
    response = requests.get(url)
    assert response.status_code == 200, "Mailnesia website did not respond."
    assert re.search(subject, response.text), "The sent email was not received."
    print('Email received!')


def test_send_emails(pytestconfig):
    if pytestconfig.getoption('send_emails'):
        print('Sending Live Emails...')
        _send_emails_network()
    else:
        print('Mocking Emails...')
        _send_emails_mock()
