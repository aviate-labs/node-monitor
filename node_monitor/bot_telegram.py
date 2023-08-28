import requests
import logging


class TelegramBot:
    def __init__(self, telegram_token: str) -> None:
        self.telegram_token = telegram_token

    def send_message_to_channel(self, channel_id: str, message: str) -> None:
        try:
            request = requests.get(
                f"https://api.telegram.org/bot{self.telegram_token}"
                f"/sendMessage?chat_id={channel_id}&text={message}"
            )
            request.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # logging.error(e)
            logging.error(
                f"Error occurred while sending Telegram message. "
                f"Check that the Telegram channel id and/or Telegram bot API token is correct"
            )

    def send_message_to_chat(self, chat_id: str, message: str) -> None:
        try:
            request = requests.get(
                f"https://api.telegram.org/bot{self.telegram_token}"
                f"/sendMessage?chat_id={chat_id}&text={message}"
            )
            request.raise_for_status()
        except Exception as e:
            # logging.error(e)
            logging.error(
                f"Error occurred while sending Telegram message. "
                f"Check that the Telegram chat id and/or Telegram bot API token is correct"
            )

