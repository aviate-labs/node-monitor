import slack
import logging
from node_monitor.load_config import slackBotToken, slackChannelName


class SlackBot():
    def __init__(self):
        self.client = slack.WebClient(token=slackBotToken)

    def send_message(self, message_content):
        try:
            self.client.chat_postMessage(
                channel=slackChannelName, text=message_content)
        except Exception as e:
            # logging.exception(e)
            logging.info(
                f"Error occurred while sending Slack message. " 
                f"Check the name of the Slack channel and/or bot API token is correct"
            )


# TODO: allow slack bot to monitor chat for "status message"
