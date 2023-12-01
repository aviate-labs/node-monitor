import pytest
from unittest.mock import patch

import node_monitor.load_config as c
import node_monitor.node_monitor_helpers.messages as messages
from node_monitor.bot_telegram import TelegramBot
from tests.conftest import fake_data


@patch("requests.post")
def test_send_message(mock_post):
    telegram_bot = TelegramBot(c.TOKEN_TELEGRAM)
    chat_id = "1234567890"
    subject = "Test subject"
    message = "Test message"
    payload = {
        "chat_id": chat_id,
        "text": f"{subject}\n\n{message}"
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
def test_send_live_message(fake_data):
    """Send a real test message to a Telegram channel"""
    fakenode, fakelabel = fake_data
    telegram_bot = TelegramBot(c.TOKEN_TELEGRAM)
    chat_id = "-1001925583150"  

    subject, message = messages.nodes_compromised_message([fakenode], fakelabel)

    err = telegram_bot.send_message(chat_id, subject, message)
    if err is not None:
        raise err
