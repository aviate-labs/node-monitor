import slack_sdk

class SlackBot:
    def __init__(self, slack_token: str):
        self.client = slack_sdk.WebClient(token="")

    def send_message(self, message: str):
        pass
