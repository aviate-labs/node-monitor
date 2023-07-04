# Node Monitor by Aviate Labs

Node monitoring software for notifications of changes to Internet Computer Nodes.

Queries the API with a specified interval (configurable) and reports changes to email.
Can be configured to filter different kinds of events.

Includes an optional feature to send a status update to any incoming emails that contain the word 'status' in the body or subject.


## Setup
Create a .env file in this directory like so
```text
gmailUsername       = "email.sender@gmail.com"
gmailPassword       = "mypassword"
slackBotToken       = "your-slack-bot-api-token"
telegramBotToken    = "your-telegram-bot-api-token"
```
The email address listed in the `gmailUsername` field serves as the primary sender for notifications and the point of contact for getting the status of your nodes. 

If you have 2FA enabled on your gmail account. You will need to use an application specific password in the `gmailPassword` field. Follow the steps [here](https://support.google.com/mail/answer/185833?hl=en-GB).


Create a config.json file in this directory. Below is a good default config.
```js
{
    "emailRecipients": ["email.receiver1@gmail.com", "email.receiver2@gmail.com"],
    "slackChannelName": "your-node-monitor-channel",
    "telegramChatId": "0123456789",
    "telegramChannelId": "-1234567890987",
    "nodeProviderId": "abc2d-48fgj-32ab3-2a...",
    "intervalMinutes": 5,
    "intervalStatusReport": 1440, 
    "lookupTableFile": "lookuptable.json",
    "NotifyOnNodeMonitorStartup": true,
    "NotifyOnNodeChangeStatus": true,
    "NotifyOnAllNodeChanges": false,
    "NotifyOnNodeAdded": true,
    "NotifyOnNodeRemoved": true,
    "IMAPClientEnabled": false,
    "NotifyBySlack": true,
    "NotifyByEmail": true
}
```
The `intervalStatusReport` value, set in minutes, determines how often you'll receive these reports. It should always be larger than the `intervalMinutes` value. If it this is not set in your config.json file, or the `intervalStatusReport` < `intervalMinutes`, you will not recieve a status report.

The lookuptable.json file is mapping of node-ids to custom labels. Its use is optional.
Example lookuptable.json:
```js
{
    "5jo56-bx...": "an1-dll01",
    "vseni-vz...": "an1-dll02",
    "rbr7v-bi...": "an1-dll03",
    "kby7l-tp...": "an1-dll04",
}
```


Install dependencies
```sh
$ pip install -r requirements.txt
```


## Running
Run with python, and stop with keyboardinterrupt (crtl-c)
```sh
$ python3 -m node_monitor
[2022-10-08 07:52:37.210304]: Starting Node Monitor...
[2022-10-08 07:52:37.982442]: -- Fetched New Data
[2022-10-08 07:52:38.650524]: -- Fetched New Data
[2022-10-08 07:52:38.671211]: -- No Change (5 min)
^C[2022-10-08 07:52:41.509254]: Stopped Node Monitor
```


## TODO
- Better error handling

## Using with rsync
```bash
# a=preserve links, n=dry run, v=verbose
$ rsync -anv --exclude 'config.json' --exclude '.git/' . username@remote_host:/root/directory
# remove the `n` to run for real
```

## Testing
```sh
$ python3 -m unittest tests/test_node_monitor.py
```
### Notes
For testing, fetch api data with curl. The repo should already include tests and accompanying json documents, so this shouldn't really be necessary
```sh
$ curl "https://ic-api.internetcomputer.org/api/v3/nodes" -o t0.json
```



## Settings Explained

- intervalMinutes: The interval in which to wait to query the dashboard API

- NotifyOnNodeMonitorStartup: Send a notification email each time Node Monitor is started

- NotifyOnNodeChangeStatus: Sends an email if node changes to 'UP', 'DOWN', or 'UNASSIGNED'

- NotifyOnAllNodeChanges: Sends an email for any kind of node change (subnet, owner, etc), basically verbose mode

- NotifyOnNodeAdded: Send an email when a new node is discovered on the dashboard API

- NotifyOnNodeRemoved: Send an email when a node is removed from the dashboard API

- IMAPClientEnabled: Watch inbox and send any responses to emails querying a status update

## Set up Node Monitor Slack Bot

- Follow the steps in this [walkthrough](https://app.tango.us/app/workflow/Setting-up-a-Node-Monitor-Bot-in-Slack--Step-by-Step-Instructions-c971a31e13a344dc8cba4c2ebc3f4e4e).

- After following the steps in this tutorial you should have the bot API token and the channel name (step 24 and 29).

- Put the bot API token in the `.env` file in the `slackBotToken` field and the channel name in the `config.json` file in the `slackChannelName` field.

## Set up Node Monitor Telegram bot

### Messaging a channel 
- Follow the steps in this [walkthrough](https://help.nethunt.com/en/articles/6467726-how-to-create-a-telegram-bot-and-use-it-to-post-in-telegram-channels)

- After following the steps in the tutorial, you should have a bot API token and the channel ID. Put the bot API token in the `.env` file in the `telegramBotToken` field and the channel ID in the `config.json` file in the `telegramChanelId` field.

### Messaging a chat 
- Follow the same steps as in the tutorial for messaging a channel.

- In step 3, look for your chat ID. It should look something like:
    ```json
    'chat': {'id': this-is-your-chat-id, ...}
    ```

- Now you have the bot API token and the chat ID, put the bot API token in the `.env` file in the `telegramBotToken` field and the chat ID in the `config.json` file in the `telegramChatId` field.