
# Running Watchdog

## Running from terminal
```bash
$ python3 -m watchdog
```

## Setting up Watchdog
Create a .env file in the root of the directory and ensure the following are set
```
NODE_MONITOR_URL = "http://your.url.here/"
EMAIL_ADMINS_LIST = "email1@mail.com,email2@mail.com"
```
`NODE_MONITOR_URL` - URL of the server your instance of Node Monitor is running on
`EMAIL_ADMINS_LIST` - List of emails to be notified if Node Monitor goes offline
