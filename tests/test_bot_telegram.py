import pytest
from unittest.mock import patch

import node_monitor.load_config as c
import node_monitor.node_monitor_helpers.messages as messages
import node_monitor.ic_api as ic_api
from node_monitor.bot_telegram import TelegramBot

@patch("requests.get")
def test_send_message(mock_get):
    telegram_bot = TelegramBot(c.TOKEN_TELEGRAM)
    chat_id = "1234567890" 
    message = "Test message"
    mock_response = mock_get.return_value
    mock_response.raise_for_status.return_value = None

    telegram_bot.send_message(chat_id, message)

    mock_get.assert_called_once_with(
        f"https://api.telegram.org/bot{telegram_bot.telegram_token}/sendMessage?chat_id={chat_id}&text={message}"
    )
    mock_response.raise_for_status.assert_called_once()



@pytest.mark.live_telegram
def test_send_live_message():
    telegram_bot = TelegramBot(c.TOKEN_TELEGRAM)
    chat_id = "-1001925583150"  
    message = "🔬 This is a test message from Node Monitor"

    err = telegram_bot.send_message(chat_id, message)
    if err is not None:
        raise err

