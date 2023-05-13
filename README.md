# Node Monitor by Aviate Labs

Node monitoring software for notifications of changes to Internet Computer Nodes.

Queries the API with a specified interval (configurable) and reports changes to email.
Can be configured to filter different kinds of events.

Includes an optional feature to send a status update to any incoming emails that contain the word 'status' in the body or subject.


## Setup
Create a .env file in this directory like so
```text
gmailUsername   = "email.sender@gmail.com"
gmailPassword   = "mypassword"
```

If you have 2FA enabled on your gmail account. You will need to use an application specific password in the `gmailPassword` field. Follow the steps [here](https://myaccount.google.com/security?rapt=AEjHL4Om5qy2rzbyiFcFfbM_6SJOqxVDf6I4Bw9j9We5m7aLrn5TdXhlPSrZ4wChfQQaUyHZrt4zAHb6CYZVDbWAVgoHOb0t0w).


Create a config.json file in this directory. Below is a good default config.
```js
{
    "emailRecipients": ["email.receiver1@gmail.com", "email.receiver2@gmail.com"],
    "nodeProviderId": "abc2d-48fgj-32ab3-2a...",
    "intervalMinutes": 5,
    "lookupTableFile": "lookuptable.json",
    "NotifyOnNodeMonitorStartup": true,
    "NotifyOnNodeChangeStatus": true,
    "NotifyOnAllNodeChanges": false,
    "NotifyOnNodeAdded": true,
    "NotifyOnNodeRemoved": true,
    "IMAPClientEnabled": false
}
```

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

