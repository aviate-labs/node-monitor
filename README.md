# Node Monitor

Node monitoring is an open-source notification service for [Internet Computer Nodes](https://internetcomputer.org/node-providers).
It queries the Internet Computer API with a specified interval and reports status changes to email and communication channels like [Slack and Telegram](https://github.com/aviate-labs/node-monitor#free-hosted-version).

You can run Node Monitor yourself or use the free __[hosted version](https://www.aviatelabs.co/node-monitor).__
## Setup

Place a `.env` file in this directory.  
Use `.env.example` as a template.  
You will also need a running Postgres database to store user information.

### 🚀 Hosted version 

Don't want the hassle of hosting the service yourself? We've got you covered! 
Introducing our free hosted version - instant monitoring, zero setup. Sign up here: [aviatelabs.co/node-monitor](https://www.aviatelabs.co/node-monitor)

The service uses the same functionality as the open-source service, with Slack and Telegram already integrated. Features will be added to provide management and incident-handling support to Node Providers.  

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


## Logging

Node Monitor writes all logs to the `logs/` directory.  
- `logs/gunicorn_access.log` contains all HTTP requests.
- `logs/gunicorn_error.log` contains all gunicorn errors and information.
- `logs/node_monitor.log` contains all `Node Monitor` specific logs.



## Notes

#### Rsync Example
```bash
# a=preserve links, n=dry run, v=verbose
$ rsync -anv --exclude '.git/' . username@remote_host:/root/directory
# remove the `n` to run for real
```

#### 2FA Gmail
If you are using gmail, you may need to create an ['app password'](https://support.google.com/mail/answer/185833)
