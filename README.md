# Node Monitor

Node monitoring software for notifications of changes to Internet Computer Nodes.
Queries the API with a specified interval and reports changes to email and other various communication channels.

## Setup

Place a `.env` file in this directory.  
Use `.env.example` as a template.  
You will also need a running Postgres database to store user information.

### Free hosted version

🚀 Don't want the hassle of hosting the code yourself? We've got you covered! Introducing our free hosted version - instant monitoring, zero setup. [Sign up here](https://www.aviatelabs.co/node-monitor)!


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
