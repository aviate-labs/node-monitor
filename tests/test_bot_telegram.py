import pytest
import requests
from unittest.mock import patch, Mock

import node_monitor.load_config as c
from node_monitor.bot_telegram import TelegramBot  # Replace 'your_module' with the actual module name


@patch.object(requests, "get")
def test_send_message(mock_get):
    telegram_bot = TelegramBot(c.TOKEN_TELEGRAM)
    channel_id = "1234567890"  # Replace with a valid channel ID
    message = "Test message"
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    telegram_bot.send_message(channel_id, message)

    mock_get.assert_called_once_with(
        f"https://api.telegram.org/bot{telegram_bot.telegram_token}/sendMessage?chat_id={channel_id}&text={message}"
    )
    mock_response.raise_for_status.assert_called_once()



@pytest.mark.live_telegram
def test_send_message():
    telegram_bot = TelegramBot(c.TOKEN_TELEGRAM)
    channel_id = "-1001925583150"  
    message = "Test message"

    telegram_bot.send_message(channel_id, message)

