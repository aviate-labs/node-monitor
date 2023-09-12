import pytest
import node_monitor.load_config as c
from node_monitor.bot_slack import SlackBot  
from unittest.mock import patch

@patch("slack_sdk.WebClient")
def test_send_message(mock_web_client):
    mock_client = mock_web_client.return_value

    expected_channel = "#node-monitor"
    expected_message = "Hello, Slack!"

    slack_bot = SlackBot(c.TOKEN_SLACK)
    slack_bot.send_message(expected_channel, expected_message)

    mock_client.chat_postMessage.assert_called_once_with(
        channel=expected_channel,
        text=expected_message,
    )


@pytest.mark.live_slack
def test_send_message_slack():
    """Send real messages to a test Slack workspace"""
    slack_bot = SlackBot(c.TOKEN_SLACK)
    
    slack_channel_name = "#node-monitor"
    message = "Hello from test_send_message_slack()"

    # Checks if a print statement is called within send_message().
    # If it is called the test fails.
    with patch('builtins.print') as mock_print:
        try:
            slack_bot.send_message(slack_channel_name, message)
        except Exception as e:
            raise AssertionError(f"An exception occurred: {e}")

        mock_print.assert_not_called()
