import schedule
import time
import node_monitor.load_config as c
from node_monitor.bot_email import EmailBot
from watchdog.watchdog import Watchdog

CHECK_INTERVAL = 15 * 60

if __name__ == "__main__":
    email_bot = EmailBot(c.EMAIL_USERNAME, c.EMAIL_PASSWORD)
    watchdog = Watchdog(email_bot, c.EMAIL_ADMINS_LIST, c.NODE_MONITOR_URL)
    schedule.every(15).minutes.do(watchdog.check_node_monitor_status)
    while True:
        schedule.run_pending()
        time.sleep(CHECK_INTERVAL)
        