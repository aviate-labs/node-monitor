# Node Monitor

Node monitoring software for notifications of changes to Internet Computer Nodes.
Queries the API with a specified interval and reports changes to email and other various communication channels.

## Setup

Place a `.env` file in this directory.  
Use `.env.example` as a template.  
You will also need a running Postgres database to store user information.


## Running

### Docker (recommended)
```bash
# To run the app
$ docker compose up --build
# To only run the tests, then exit
$ TEST=true docker compose up --build
```

### Without Docker

```bash
# Install dependencies
$ pip install -r requirements.txt

# Check static typing, basic tests
$ make check
$ make test
# Integration tests (live email, database)
$ make testall

# Run the app, using Gunicorn as the WSGI server
$ make prod
```

For more control over testing, see `tests/conftest.py`, and/or `Makefile`.



## Notes

#### Rsync Example
```bash
# a=preserve links, n=dry run, v=verbose
$ rsync -anv --exclude '.git/' . username@remote_host:/root/directory
# remove the `n` to run for real
```

#### 2FA Gmail
If you are using gmail, you may need to create an ['app password'](https://support.google.com/mail/answer/185833)

#### Setting up the Slack Bot
1. Follow the steps in [this walkthrough](https://app.tango.us/app/workflow/Setting-up-a-Node-Monitor-Bot-in-Slack--Step-by-Step-Instructions-c971a31e13a344dc8cba4c2ebc3f4e4e), and keep track of the bot API token and the channel name.
2. Update the `TOKEN_SLACK` field in `.env` with the bot API token.
3. Update your database with any necessary channel information.

#### Setting up the Telegram Bot
- Not Yet Implemented
1. Follow the steps in this [walkthrough](https://help.nethunt.com/en/articles/6467726-how-to-create-a-telegram-bot-and-use-it-to-post-in-telegram-channels)
2. Update the `TOKEN_TELEGRAM` field in the `.env` file with the bot API token.
3. Update your database with any necessary channel information (for messaging a channel)
4. Update your database with the chat ID (for messaging a chat)
