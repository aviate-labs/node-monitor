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
    fakeurl = 'https://forms.gle/thisisfake'
    
    subject1, message1 = messages.nodes_down_message(
        [fakenode], fakelabel, fakeurl)
    subject2, message2 = messages.nodes_status_message(
        [fakenode], fakelabel, fakeurl)

    err1 = telegram_bot.send_message(chat_id, message1)
    err2 = telegram_bot.send_message(chat_id, message2)
    if err1 is not None:
        raise err1
    if err2 is not None:
        raise err2

