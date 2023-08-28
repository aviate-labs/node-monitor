import requests
import asyncio
import logging
import logging
import queue
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


class TelegramBot:
    def __init__(self, telegram_token: str) -> None:
        self.telegram_token = telegram_token
        self.application = None
    
    def start(self):
        # Enable logging
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
        )
        # Set higher logging level for httpx to avoid all GET and POST requests being logged
        logging.getLogger("httpx").setLevel(logging.WARNING)

        # Create the Application and pass it your bot's token.
        self.application = Application.builder().token(self.telegram_token).build()

        # Register command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))

        # Register message handler
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo_message)
        )

        # Run the bot until the user presses Ctrl-C
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}!",
            reply_markup=ForceReply(selective=True),
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        await update.message.reply_text("Help!")

    async def echo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        await update.message.reply_text(update.message.text)



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


