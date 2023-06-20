import slack
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

client = slack.WebClient(token=os.environ['slackToken'])

client.chat_postMessage(channel='#node-monitor', text="Hello world!")
