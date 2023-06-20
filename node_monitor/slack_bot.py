import slack
from dotenv import load_dotenv
from node_monitor.load_config import slackBotToken


class SlackBot():
    def __init__(self):
        self.client = slack.WebClient(token=slackBotToken)
    
    def send_message(self, message_content):
        self.client.chat_postMessage(channel='#node-monitor', text=message_content)




# client = slack.WebClient(token=slackBotToken)

# client.chat_postMessage(channel='#node-monitor', text="Hello world!")

