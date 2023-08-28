import threading
import queue  # Import the queue module for inter-thread communication

from node_monitor.bot_email import EmailBot
from node_monitor.bot_slack import SlackBot
from node_monitor.bot_telegram import TelegramBot
from node_monitor.node_monitor import NodeMonitor
from node_monitor.server import create_server
import node_monitor.load_config as c


## Initialize
## Objects are passed by reference, so we can pass around the NodeMonitor
## instance and work on the same data in different functions/threads
email_bot = EmailBot(c.EMAIL_USERNAME, c.EMAIL_PASSWORD)
slack_bot = SlackBot(c.TOKEN_SLACK)
telegram_bot = TelegramBot(c.TOKEN_TELEGRAM)
telegram_bot.start()
nm = NodeMonitor(email_bot, slack_bot, telegram_bot) # Pass None as the Telegram bot for now

## Run NodeMonitor in a separate thread
## daemon threads stop when the main thread stops
## can we call nm.mainloop as the target without creating a new fn?
def start_node_monitor() -> None:
    nm.mainloop()
print("Starting NodeMonitor...", end=" ")
nm_thread = threading.Thread(target=start_node_monitor, daemon=True)
nm_thread.start()
print("Running.")

## Run Flask server in main thread
app = create_server(nm, nm_thread.is_alive)




## Run only during development
if __name__ == "__main__":
    # debug=True will run two instances of the thread
    app.run(debug=False, port=3000)
    # There is an issue where the latest mac os as it uses the default 
    # port for flask. To resolve it, change your default flask port to 
    # something other than 5000.

