#!/usr/bin/env python3

## A custom script that imports some classes from node_monitor
## and sends out a custom email message


## Import the deired email as text (this name is in the .gitignore)
with open('email_to_send.txt', 'r') as f:
    email = f.read()


## Import nodemonitor
from node_monitor.node_monitor import NodeMonitor



## Send the emails

def main():
    print("I don't do anything, yet...")


if __name__ == "__main__":
    main()