import requests


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
            print(f"Got an error: {e}")

    def send_message_to_chat(self, chat_id: str, message: str) -> None:
        try:
            request = requests.get(
                f"https://api.telegram.org/bot{self.telegram_token}"
                f"/sendMessage?chat_id={chat_id}&text={message}"
            )
            request.raise_for_status()
        except Exception as e:
            print(f"Got an error: {e}")

