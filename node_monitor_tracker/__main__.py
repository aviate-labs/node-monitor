import schedule
import time
import node_monitor.load_config as c
from node_monitor.bot_email import EmailBot
from node_monitor_tracker.node_monitor_tracker import NodeMonitorTracker


if __name__ == "__main__":
    email_bot = EmailBot(c.EMAIL_USERNAME, c.EMAIL_PASSWORD)
    node_monitor_tracker = NodeMonitorTracker(email_bot, c.EMAIL_ADMINS_LIST, c.NODE_MONITOR_URL)
    schedule.every(15).minutes.do(node_monitor_tracker.check_node_monitor_status)
    while True:
        schedule.run_pending()
        time.sleep(15)
        