# Node Monitor

Node monitoring software for notifications of changes to Internet Computer Nodes.
Queries the API with a specified interval and reports changes to email and other various communication channels.

## Setup

Place a `.env` file in this directory.  
Use `.env.example` as a template.

You will also need a file `tmp_prod_db.json` in this directory.  
This is our temporary database until we implement SQLite.


Install dependencies
```sh
$ pip install -r requirements.txt
```


## Testing

We use mypy and pytest to do testing and type checking.

```bash
$ make check
$ make test
# To run the test with a live email
# -s flag is to show print statements
$ pytest -s --send_emails tests/
```



## Running

We use Gunicorn as our WSGI server.

```bash
$ make prod
```


## Notes

#### Usage with rsync
```bash
# a=preserve links, n=dry run, v=verbose
$ rsync -anv --exclude '.git/' . username@remote_host:/root/directory
# remove the `n` to run for real
```

#### 2FA Gmail
If you have 2FA enabled on your gmail account. You will need to use an application specific password in the `gmailPassword` field. Follow the steps [here](https://support.google.com/mail/answer/185833?hl=en-GB).

#### Fetching data from the API
For testing, fetch api data with curl. The repo should already include tests and accompanying json documents, so this shouldn't really be necessary
```sh
$ curl "https://ic-api.internetcomputer.org/api/v3/nodes" -o t0.json
```


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

