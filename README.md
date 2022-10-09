# Node Monitor by Aviate Labs

Node monitoring software for (near) immediate notifications of changes to Internet Computer Nodes.

Queries the API every 5 minutes and reports changes to email.
Can be configured to filter different kinds of events.


### Setup
Create a .env file in this directory like so
```text
gmailUsername   = "email.sender@gmail.com"
gmailPassword   = "mypassword"
discordBotToken = "xxxxxxxxxxxxxx"
emailRecipient  = "email.receiver@gmail.com"
nodeProviderId  = "abc2d-48fgj-32ab3-2a..."
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
- discord bot
- slack bot
- easy config options (filters, intervals)
- better & more tests

### Notes
fetch api data with curl
```sh
> curl "https://ic-api.internetcomputer.org/api/v3/nodes" -o t0.json
```
