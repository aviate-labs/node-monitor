import slack_sdk
import logging

class SlackBot:
    def __init__(self, slack_token: str) -> None:
        self.client = slack_sdk.WebClient(token=slack_token)

    def send_message(self, slack_channel_name: str, message: str) -> None:
        try:
            self.client.chat_postMessage(
                channel=slack_channel_name, text=message)
        except Exception as e:
            # logging.exception(e)
            logging.info(
                f"Error occurred while sending Slack message. "
                f"Check the name of the Slack channel and/or bot API token is correct"
            )




