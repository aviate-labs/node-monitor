
# Running HistoryBuilder

## Running from terminal
```bash
$ python3 -m historybuilder
```

## Setting up a service
Create the file `/etc/systemd/system/historybuilder.service`
```ini
[Unit]
Description=Queries DFINITY API and writes to master.db
After=network.target

[Service]
WorkingDirectory=<path_to_this_repo>
ExecStart=python3 -m historybuilder
Restart=always
RestartSec=5
Type=simple
```

## Running the service
Start Service
```bash
# reload the service if changes have been made
$ sudo systemctl daemon-reload
# start the service
$ sudo systemctl start historybuilder
# get the status of the service
$ sudo systemctl status historybuilder
# stop the service
$ sudo systemctl stop historybuilder
```

Viewing The logs
```bash
# you can view the raw output, which gets written here:
$ tail /var/log/syslog
# or you can use journalctl (-f for real time)
$ journalctl -u historybuilder -f
```

## Resources
<https://mysystemd.talos.sh/>
