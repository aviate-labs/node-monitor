import requests
import logging
from node_monitor.load_config import telegramBotToken, telegramChatId, telegramChannelId


class TelegramBot():
    def send_message_to_channel(self, message_content):
        try:
            request = requests.get(
                f"https://api.telegram.org/bot{telegramBotToken}/sendMessage?chat_id={telegramChannelId}&text={message_content}")
            request.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # logging.error(e)
            logging.error(
                f"Error occurred while sending Telegram message. Check that the name of the Telegram channel id and/or Telegram Bot API token is correct")

    def send_message_to_chat(self, message_content):
        try:
            request = requests.get(
                f"https://api.telegram.org/bot{telegramBotToken}/sendMessage?chat_id={telegramChatId}&text={message_content}")
            request.raise_for_status()
        except Exception as e:
            # logging.error(e)
            logging.error(
                f"Error occurred while sending Telegram message. Check that the name of the Telegram chat id and/or Telegram Bot API token is correct")
