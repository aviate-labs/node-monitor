import requests
import logging
from node_monitor.load_config import telegramBotToken, telegramChatId, telegramChannelId


class TelegramBot():
    @staticmethod
    def send_message_to_channel(message_content):
        try:
            request = requests.get(
                f"https://api.telegram.org/bot{telegramBotToken}"
                f"/sendMessage?chat_id={telegramChannelId}&text={message_content}"
            )
            request.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # logging.error(e)
            logging.error(
                f"Error occurred while sending Telegram message. "
                f"Check that the Telegram channel id and/or Telegram bot API token is correct"
            )

    @staticmethod
    def send_message_to_chat(message_content):
        try:
            request = requests.get(
                f"https://api.telegram.org/bot{telegramBotToken}"
                f"/sendMessage?chat_id={telegramChatId}&text={message_content}"
            )
            request.raise_for_status()
        except Exception as e:
            # logging.error(e)
            logging.error(
                f"Error occurred while sending Telegram message. "
                f"Check that the Telegram chat id and/or Telegram bot API token is correct"
            )
