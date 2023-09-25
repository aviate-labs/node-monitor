import pytest
from unittest.mock import patch

import node_monitor.load_config as c
from node_monitor.bot_slack import SlackBot


@patch("slack_sdk.WebClient")
def test_send_message(mock_web_client):
    mock_client = mock_web_client.return_value

    expected_channel = "#node-monitor"
    expected_message = "Hello, Slack!"

    slack_bot = SlackBot(c.TOKEN_SLACK)
    slack_bot.send_message(expected_channel, expected_message)

    mock_client.chat_postMessage.assert_called_once_with(
        channel=expected_channel,
        text=expected_message)


@pytest.mark.live_slack
def test_send_message_slack():
    """Send a real test message to a Slack workspace"""
    slack_bot = SlackBot(c.TOKEN_SLACK)
    
    slack_channel_name = "node-monitor"
    message = "🔬 Hello from test_send_message_slack()"

    # SlackBot.send_message() returns an error without raising an exception
    # to prevent NodeMonitor from crashing if the message fails to send.
    # Instead, we raise it here.
    err = slack_bot.send_message(slack_channel_name, message)
    if err is not None:
        raise err
