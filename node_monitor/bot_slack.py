from typing import List
import slack_sdk
from slack_sdk.errors import SlackApiError

class SlackBot:

    def __init__(self, slack_token: str) -> None:
        self.client = slack_sdk.WebClient(token=slack_token)

    def send_message(
            self, slack_channel_name: str,
            message: str) -> None | SlackApiError:
        """Send a message to a single Slack channel."""
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
            # print(f"Got an error: {e.response['error']}")
            return e
        return None
    

    def send_messages(
            self, slack_channel_names: List[str],
            message: str) -> None | SlackApiError:
        """Send a message to multiple Slack channels."""
        # Propagate the last error that occurs
        err = None
        for slack_channel_name in slack_channel_names:
            this_err = self.send_message(slack_channel_name, message)
            if this_err is not None:
                err = this_err
        return err
