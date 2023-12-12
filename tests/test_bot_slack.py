import pytest
from unittest.mock import patch

from node_monitor.bot_slack import SlackBot
import node_monitor.node_monitor_helpers.messages as messages
import node_monitor.load_config as c
from tests.conftest import fake_data


@patch("slack_sdk.WebClient")
def test_send_message(mock_web_client):
    mock_client = mock_web_client.return_value

    expected_channel = "#node-monitor"
    expected_subject = "Subject message"
    expected_message = "Hello, Slack!"
    dispatch = f"{expected_subject}\n\n{expected_message}"

    slack_bot = SlackBot(c.TOKEN_SLACK)
    slack_bot.send_message(expected_channel, dispatch)

    mock_client.chat_postMessage.assert_called_once_with(
        channel=expected_channel,
        text=f"{expected_subject}\n\n{expected_message}")


@pytest.mark.live_slack
def test_send_message_slack(fake_data):
    """Send a real test message to a Slack workspace"""
    fakenode, fakelabel = fake_data
    slack_bot = SlackBot(c.TOKEN_SLACK)
    slack_channel_name = "node-monitor"

    subject, message = messages.nodes_compromised_message([fakenode], fakelabel)
    dispatch = f"{subject}\n\n{message}"

    ## SlackBot.send_message() normally returns an error without raising 
    ## an exception to prevent NodeMonitor from crashing if the message 
    ## fails to send. We make sure to raise it here to purposely fail the test.
    err = slack_bot.send_message(slack_channel_name, dispatch)
    if err is not None:
        raise err
