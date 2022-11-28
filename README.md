# Node Monitor by Aviate Labs

Node monitoring software for (near) immediate notifications of changes to Internet Computer Nodes.

Queries the API with a specified interval (configurable) and reports changes to email.
Can be configured to filter different kinds of events.


### Setup
Create a .env file in this directory like so
```text
gmailUsername   = "email.sender@gmail.com"
gmailPassword   = "mypassword"
discordBotToken = "xxxxxxxxxxxxxx"
```

Create a config.json file in this directory like so
```js
{
    "emailRecipients": ["email.receiver1@gmail.com", "email.receiver2@gmail.com"],
    "nodeProviderId": "abc2d-48fgj-32ab3-2a...",
    "intervalMinutes": 15,
    "lookupTableFile": "lookuptable.json",
    "loggingEnabled": true,
    "NotifyOnNodeMonitorStartup": true,
    "NotifyOnNodeChangeStatus": true,
    "NotifyOnAllNodeChanges": false,
    "NotifyOnNodeAdded": true,
    "NotifyOnNodeRemoved": true
}
```


Install dependencies
```sh
$ pip install -r requirements.txt
```


### Running
Run with python, and stop with keyboardinterrupt (crtl-c)
```sh
$ python3 -m node_monitor
[2022-10-08 07:52:37.210304]: Starting Node Monitor...
[2022-10-08 07:52:37.982442]: -- Fetched New Data
[2022-10-08 07:52:38.650524]: -- Fetched New Data
[2022-10-08 07:52:38.671211]: -- No Change (5 min)
^C[2022-10-08 07:52:41.509254]: Stopped Node Monitor
```


### TODO
- asyncio
- logging
- discord bot (probably not)
- slack bot (probably not)
- ability to send an email and get back a status update

### Notes
fetch api data with curl
```sh
> curl "https://ic-api.internetcomputer.org/api/v3/nodes" -o t0.json
```

### Settings Explained
- intervalMinutes: The interval in which to wait to query the dashboard API

- NotifyOnNodeMonitorStartup: Send a notification email each time Node Monitor is started

- NotifyOnNodeChangeStatus: Sends an email if node changes to 'UP', 'DOWN', or 'UNASSIGNED'

- NotifyOnAllNodeChanges: Sends an email for any kind of node change (subnet, owner, etc), basically verbose mode

- NotifyOnNodeAdded: Send an email when a new node is discovered on the dashboard API

- NotifyOnNodeRemoved: Send an email when a node is removed from the dashboard API


