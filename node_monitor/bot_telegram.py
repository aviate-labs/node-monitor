import requests
from typing import List


class TelegramBot:
    def __init__(self, telegram_token: str) -> None:
        self.telegram_token = telegram_token

    def send_message(
            self, chat_id: str, message: str
        ) -> None | requests.exceptions.HTTPError:
        """Send a message to a single Telegram chat."""
        try:
            request = requests.get(
                f"https://api.telegram.org/bot{self.telegram_token}"
                f"/sendMessage?chat_id={chat_id}&text={message}"
            )
            request.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # print(f"Got an error: {e}")
            return e
        return None
    

    def send_messages(
            self, chat_ids: List[str], message: str
            ) -> None | requests.exceptions.HTTPError:
        """Send a message to multiple Telegram chats."""
        # Propagate the last error that occurs
        err = None
        for chat_id in chat_ids:
            this_err = self.send_message(chat_id, message)
            if this_err is not None:
                err = this_err
        return err
