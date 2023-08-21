import pytest
import node_monitor.load_config as c
from node_monitor.bot_slack import SlackBot  
from unittest.mock import Mock

@pytest.fixture
def mock_slack_client(mocker):
    mock_client = Mock()
    mocker.patch("slack_sdk.WebClient", return_value=mock_client)
    return mock_client

def test_send_message(mock_slack_client):
    slack_bot = SlackBot(slack_token=c.TOKEN_SLACK)

    expected_message = "Hello, Slack!"
    expected_chanel = "#node-monitor"
    slack_bot.send_message(expected_chanel, expected_message)

    mock_slack_client.chat_postMessage.assert_called_once_with(
        channel=expected_chanel,  
        text=expected_message,
    )

@pytest.mark.live_email
def test_send_message_slack():
    """Send real messages to a test Slack workspace"""
    slack_bot = SlackBot(slack_token=c.TOKEN_SLACK)
    
    slack_channel_name = "#node-monitor"
    message = "Hello from test_send_message_slack()"

    slack_bot.send_message(slack_channel_name, message)
