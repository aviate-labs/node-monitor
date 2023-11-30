import pytest
from unittest.mock import patch

import node_monitor.load_config as c
import node_monitor.node_monitor_helpers.messages as messages
from node_monitor.bot_telegram import TelegramBot
import node_monitor.ic_api as ic_api


@patch("requests.post")
def test_send_message(mock_post):
    telegram_bot = TelegramBot(c.TOKEN_TELEGRAM)
    chat_id = "1234567890"
    subject = "Test subject"
    message = "Test message"
    payload = {
        "chat_id": chat_id,
        "text": f"{subject}  {message}"
    }
    mock_response = mock_post.return_value
    mock_response.raise_for_status.return_value = None

    telegram_bot.send_message(chat_id, subject, message)

    mock_post.assert_called_once_with(
        f"https://api.telegram.org/bot{telegram_bot.telegram_token}/sendMessage",
        data=payload
    )
    mock_response.raise_for_status.assert_called_once()



@pytest.mark.live_telegram
def test_send_live_message():
    telegram_bot = TelegramBot(c.TOKEN_TELEGRAM)
    chat_id = "-1001925583150"  

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

    subject, message = messages.nodes_compromised_message([fakenode], fakelabel)

    err = telegram_bot.send_message(chat_id, subject, message)
    if err is not None:
        raise err
