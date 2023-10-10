import threading

from node_monitor.bot_email import EmailBot
from node_monitor.bot_slack import SlackBot
from node_monitor.bot_telegram import TelegramBot
from node_monitor.node_monitor import NodeMonitor
from node_monitor.node_provider_db import NodeProviderDB
from node_monitor.server import create_server
import node_monitor.load_config as c


## Initialize
## Objects are passed by reference, so we can pass around the NodeMonitor
## instance and work on the same data in different functions/threads
email_bot = EmailBot(c.EMAIL_USERNAME, c.EMAIL_PASSWORD)
slack_bot = SlackBot(c.TOKEN_SLACK)
node_provider_db = NodeProviderDB(
    c.DB_HOST, c.DB_NAME, c.DB_USERNAME, c.DB_PASSWORD, c.DB_PORT)
nm = NodeMonitor(email_bot, slack_bot, node_provider_db)


## Run NodeMonitor in a separate thread
## daemon threads stop when the main thread stops
## can we call nm.mainloop as the target without creating a new fn?
def start_node_monitor() -> None:
    nm.mainloop()
print("Starting NodeMonitor...", end=" ")
thread = threading.Thread(target=start_node_monitor, daemon=True)
thread.start()
print("Running.")

## Run Flask server in main thread
app = create_server(nm, thread.is_alive)



## Run only during development
if __name__ == "__main__":
    # debug=True will run two instances of the thread
    app.run(debug=False)
