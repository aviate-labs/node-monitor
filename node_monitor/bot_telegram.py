import requests
import textwrap
from typing import List


class TelegramBot:
    def __init__(self, telegram_token: str) -> None:
        self.telegram_token = telegram_token


    def send_message(
            self, chat_id: str, subject: str, message: str
        ) -> None | requests.exceptions.HTTPError:
        """Send a message to a single Telegram chat."""
        dispatch = f"{subject}\n\n{message}"
        max_message_length = 4096
        message_parts = textwrap.wrap(dispatch, width=max_message_length)

        try:
            for part in message_parts:
                payload = {"chat_id": chat_id, "text": part}
                response = requests.post(
                    f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                    data=payload
                )
                response.raise_for_status()
        except requests.exceptions.HTTPError as e:
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
        
