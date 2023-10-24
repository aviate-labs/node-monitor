import pytest
from unittest.mock import patch

from node_monitor.bot_slack import SlackBot
import node_monitor.load_config as c
import node_monitor.node_monitor_helpers.messages as messages
import node_monitor.ic_api as ic_api


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
        status = 'DOWN',
        subnet_id = 'fake_subnet_id',
    )
    fakelabel = {'fake_node_id': 'fake_label'}
    
    slack_channel_name = "node-monitor"
    with patch.object(c, 'FEEDBACK_FORM_URL', 'https://url-has-been-redacted.ninja'):
        subject1, message1 = messages.nodes_down_message([fakenode], fakelabel)
        subject2, message2 = messages.nodes_status_message([fakenode], fakelabel)

    ## SlackBot.send_message() normally returns an error without raising 
    ## an exception to prevent NodeMonitor from crashing if the message 
    ## fails to send. We make sure to raise it here to purposely fail the test.
    err1 = slack_bot.send_message(slack_channel_name, message1)
    err2 = slack_bot.send_message(slack_channel_name, message2)
    if err1 is not None:
        raise err1
    if err2 is not None:
        raise err2
