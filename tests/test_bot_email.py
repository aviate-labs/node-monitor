import pytest
import time
from unittest.mock import patch
import requests
import re

from node_monitor.bot_email import EmailBot
import node_monitor.load_config as c
import node_monitor.node_monitor_helpers.messages as messages
import node_monitor.ic_api as ic_api

# This test sends emails by default
# Usage to disable live email sending:
# pytest -m "not live_email" tests/test_bot_email.py

# Usage to enable printing of stdout:
# pytest -s tests/test_bot_email.py

@patch('smtplib.SMTP')
def test_send_emails_mock(mock_smtp):
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



@pytest.mark.live_email
def test_send_emails_network():
    """Send real emails over a network to a test inbox and check that 
    they were received."""

    ## Create a fake node model
    fakenode = ic_api.Node(
        dc_id = 'fake_dc_id',
        dc_name = 'fake_dc_name',
        node_id = 'fake_node_id',
        node_operator_id = 'fake_node_operator_id',
        node_provider_id = 'fake_node_provider_id',
        node_provider_name = 'fake_node_provider_name',
        owner = 'fake_owner',
        region = 'fake_region',
        status = 'fake_status',
        subnet_id = 'fake_subnet_id',
    )
    fakelabel = {'fake_node_provider_id': 'fake_label'}

    ## Init the authenticated email bot instance
    email_bot = EmailBot(c.EMAIL_USERNAME, c.EMAIL_PASSWORD)

    ## Set paramaters (uses an anonymous email inbox for testing)
    recipients = ['nodemonitortest@mailnesia.com']
    subject = str(time.time())
    body = messages.nodes_down_message([fakenode], fakelabel)
    email_bot.send_emails(recipients, subject, body)

    ## Automatically check the email inbox
    print(f'\nhttps://mailnesia.com/mailbox/nodemonitortest')
    print(f'Email Subject should match: {subject}')
    print('Checking now... Waiting 10 seconds...')
    time.sleep(10)

    ## Validate Response
    url = 'https://mailnesia.com/mailbox/nodemonitortest'
    response = requests.get(url)
    assert response.status_code == 200, "Mailnesia website did not respond."
    assert re.search(subject, response.text), "The sent email was not received."
    print('Email received!')
