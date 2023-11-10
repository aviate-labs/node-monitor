import telegram
from typing import List


class TelegramBot:
    def __init__(self, telegram_token: str) -> None:
        self.telegram_bot = telegram.Bot(token=telegram_token)
    
    async def send_message(
            self,
            chat_id: str, 
            message: str) -> None | telegram.error.TelegramError:
        try:
            await self.telegram_bot.send_message(chat_id=chat_id, text=message)
        except telegram.error.TelegramError as e:
            print(f"Got an error: {e}")
            return e
        return None
    
    async def send_messages(
            self, chat_ids: List[str], message: str
            ) -> None | telegram.error.TelegramError:
        """Send a message to multiple Telegram chats."""
        # Propagate the last error that occurs
        err = None
        for chat_id in chat_ids:
            this_err = await self.send_message(chat_id, message)
            if this_err is not None:
                err = this_err
        return err



        
