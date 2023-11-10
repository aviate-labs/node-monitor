import pytest
from unittest.mock import patch

import node_monitor.load_config as c
from node_monitor.bot_telegram import TelegramBot

@pytest.mark.asyncio
@patch("node_monitor.bot_telegram.TelegramBot.send_message")
async def test_send_message(mock_send_message):
    telegram_bot = TelegramBot(c.TOKEN_TELEGRAM)
    chat_id = "1234567890" 
    message = "Test message"

    await telegram_bot.send_message(chat_id, message)

    mock_send_message.assert_called_once_with(chat_id, message)



@pytest.mark.live_telegram
@pytest.mark.asyncio
async def test_send_live_message():
    telegram_bot = TelegramBot(c.TOKEN_TELEGRAM)
    chat_id = "-1001925583150"  
    message = "🔬 This is a test message from Node Monitor"

    err = await telegram_bot.send_message(chat_id, message)
    if err is not None:
        raise err

