import slack_sdk
from slack_sdk.errors import SlackApiError

class SlackBot:

    def __init__(self, slack_token: str) -> None:
        self.client = slack_sdk.WebClient(token=slack_token)

    def send_message(
            self, slack_channel_name: str,
            message: str) -> None | SlackApiError:
        try:
            self.client.chat_postMessage(
                channel=slack_channel_name,
                text=message)
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            # If ok is False, e.response["error"] contains a
            # str like 'invalid_auth', 'channel_not_found'
            assert e.response["ok"] is False
            assert e.response["error"]
            print(f"Got an error: {e.response['error']}")
            return e
        return None
