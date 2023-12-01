import pytest
import time
from unittest.mock import patch
import requests
import re

from node_monitor.bot_email import EmailBot
import node_monitor.load_config as c
import node_monitor.node_monitor_helpers.messages as messages
from tests.conftest import fake_data


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
    message = 'Test Body'

    bot = EmailBot('username', 'password')
    bot.send_emails(recipients, subject, message)

    assert mock_instance.ehlo.call_count == 2
    assert mock_instance.starttls.call_count == 1
    assert mock_instance.login.call_count == 1
    assert mock_instance.send_message.call_count == 2
    mock_instance.login.assert_called_once_with('username', 'password')



@pytest.mark.live_email
def test_send_emails_network(fake_data):
    """Send real emails over a network to a test inbox and check that 
    they were received."""

    ## Generate fake node and label
    fakenode, fakelabel = fake_data

    ## Init the authenticated email bot instance
    email_bot = EmailBot(c.EMAIL_USERNAME, c.EMAIL_PASSWORD)

    ## Set recipient (we use an anonymous email inbox for testing)
    recipients = ['nodemonitortest@mailnesia.com']

    ## Create the messages. We use unittest.mock.patch to remove the private URL.
    with patch.object(c, 'FEEDBACK_FORM_URL', 'https://url-has-been-redacted.ninja'):
        subject1, message1 = messages.nodes_compromised_message([fakenode], fakelabel)
        subject2, message2 = messages.nodes_status_message([fakenode], fakelabel)

    ## Append the time to the subject to act as an identifier for the test,
    ## making it easy to do a regex search to validate the email.
    subject1 = str(f'{time.time()} - {subject1}')
    subject2 = str(f'{time.time()} - {subject2}')

    ## Send both nodes_compromised_message and nodes_status_message as emails.
    email_bot.send_emails(recipients, subject1, message1)
    email_bot.send_emails(recipients, subject2, message2)

    ## Automatically check the email inbox
    print(f'\nhttps://mailnesia.com/mailbox/nodemonitortest')
    print(f'Email 1 Subject should match: {subject1}')
    print(f'Email 2 Subject should match: {subject2}')
    print('Checking now... Waiting 10 seconds...')
    time.sleep(10)

    ## Validate Response
    url = 'https://mailnesia.com/mailbox/nodemonitortest'
    response = requests.get(url)
    assert response.status_code == 200, "Mailnesia website did not respond."
    assert re.search(subject1, response.text), "The nodes_compromised_message email was not received."
    assert re.search(subject2, response.text), "The nodes_status_message email was not received."
    print('Email received!')
