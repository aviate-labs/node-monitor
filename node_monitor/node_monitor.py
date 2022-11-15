import requests
import json
import time
from dotenv import load_dotenv
import os
from smtplib import SMTP
from email.message import EmailMessage
from collections import deque
from deepdiff import DeepDiff
from datetime import datetime
from pprint import pprint, pformat
from dataclasses import dataclass


### Secrets
load_dotenv()
gmailUsername       = os.environ.get('gmailUsername')
gmailPassword       = os.environ.get('gmailPassword')
discordBotToken     = os.environ.get('discordBotToken')


### Config File
with open("config.json") as f:
    config = json.load(f)
    emailRecipients = config['emailRecipients']
    nodeProviderId  = config['nodeProviderId']

# config['intervalMinutes']
# config['NotifyOnNodeMonitorStartup']
# config['NotifyOnNodeChangeStatus']
# config['NotifyOnAllNodeChanges']
# config['NotifyOnNodeAdded']
# config['NotifyOnNodeRemoved']


def plog(s):
    "prints and logs"
    new_s = f'[{datetime.utcnow()}]: -- ' + s
    print(new_s)


class NodeMonitor:

    def __init__(self):
        self.snapshots = deque(maxlen=2)

    def update(self):
        """fetches a snapshot from API and pushes to fixed size deque"""
        self.snapshots.append(NodesSnapshot.from_api(nodeProviderId))
        plog("Fetched New Data")

    def run_once(self):
        """run nodemonitor once"""
        diff = NodeMonitorDiff(self.snapshots[0], self.snapshots[1])
        if diff:
            plog("!! Change Detected, Sending Email")
            change_events = diff.aggregate_changes()
            for email_recipient in emailRecipients:
                for change_event in change_events:
                    msg_content = str(change_event)
                    NodeMonitorEmail(email_recipient, msg_content).send()
            plog("-- Emails Sent")
        else:
            plog(f"-- No Change ({config['intervalMinutes']} min)")


    def runloop(self):
        """main loop"""
        plog("Starting Node Monitor...")
        self.update()
        try:
            while True:
                self.update()
                self.run_once()
                time.sleep(60 * config['intervalMinutes'])
        except KeyboardInterrupt:
            plog("Stopped Node Monitor")


    def welcome_message(self, recipient):
        return (
            f"""
            Welcome, {recipient}!
            Thank you for subscribing to Node Monitor by Aviate Labs!
            Your Node Monitor Settings:
            -- Dfinity API query update interval: {config['intervalMinutes']} minutes
            -- Send Email on Node Change status (UP, DOWN, UNASSIGNED): {config['NotifyOnNodeChangeStatus']}
            -- Send Email on Any Node update (verbose mode): {config['NotifyOnAllNodeChanges']}
            -- Send Email if new node appears on network: {config['NotifyOnNodeAdded']}
            -- Send Email if node gets removed from network {config['NotifyOnNodeRemoved']}

            There are currently {self.snapshots[-1].get_num_up_nodes()} nodes in 'UP' status.
            There are currently {self.snapshots[-1].get_num_down_nodes()} nodes in 'DOWN' status.
            There are currently {self.snapshots[-1].get_num_unassigned_nodes()} nodes in 'UNASSIGNED' status.
            """
        )




class NodeMonitorEmail(EmailMessage):
    def __init__(self, msg_to, msg_content, msg_subject="Node Alert"):
        EmailMessage.__init__(self)
        self['Subject'] = msg_subject
        self['To']      = msg_to
        self['From']    = "Node Monitor by Aviate Labs"
        self.set_content(msg_content)

    def send(self):
        with SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(gmailUsername, gmailPassword)
            server.send_message(self)
            print(f"Email Sent to {self['To']}")



    # possible diff keys (scraped from source):
    # 'set_item_added', 'set_item_removed', 'iterable_item_removed'
    # 'iterable_item_added', 'iterable_item_moved', 'values_changed'
    # 'repetition_change', 'type_changes', 'dictionary_item_added'
    # 'dictionary_item_removed'


class NodeMonitorDiff(DeepDiff):
    """Extends DeepDiff to easily support the node check API"""

    def __init__(self, t1, t2):
        DeepDiff.__init__(self, t1, t2, view='tree', group_by='node_id')

    def aggregate_changes(self):
        """extract diff into a list of ChangeEvent objects"""
        utcdate = datetime.utcnow()
        change_events = []
        if 'values_changed' in self.keys():
            for change in self['values_changed']:
                # relevant info, even if unused, keep for reference
                path        = change.path()
                path_list   = change.path(output_format='list')
                change_events.append(
                    ChangeEvent(
                        event_time=utcdate,
                        change_type="value_change",
                        node_id= path_list[0],
                        changed_parameter=path_list[1],
                        t1=change.t1,
                        t2=change.t2,
                        parent_t1=change.up.t1,
                        parent_t2=change.up.t2
                    )
                )
        if 'dictionary_item_removed' in self.keys():
            for change in self['dictionary_item_removed']:
                path_list = change.path(output_format='list')
                change_events.append(
                    ChangeEvent(
                        event_time=utcdate,
                        change_type="node_removed",
                        node_id=path_list[0],
                        t1=change.t1
                    )
                )
        if 'dictionary_item_added' in self.keys():
            for change in self['dictionary_item_added']:
                path_list = change.path(output_format='list')
                change_events.append(
                    ChangeEvent(
                        event_time=utcdate,
                        change_type="node_added",
                        node_id=path_list[0],
                        t2=change.t2
                    )
                )
        return change_events





class ChangeEvent:
    def __init__(self, event_time=None, change_type=None, node_id=None,
                 changed_parameter=None, t1=None, t2=None, parent_t1=None,
                 parent_t2=None):
        self.event_time = event_time
        self.change_type = change_type
        self.node_id = node_id
        self.changed_parameter = changed_parameter
        self.t1 = t1
        self.t2 = t2
        self.parent_t1 = parent_t1
        self.parent_t2 = parent_t2

    def __ge__(self, other):
        """checks to see if other's values are contained within self"""
        a = [(k,v) for (k,v) in self.__dict__.items() if v is not None]
        b = [(k,v) for (k,v) in other.__dict__.items() if v is not None]
        for (k, v) in b:
            if (k, v) not in a: return False
        return True


    def __node_added(self):
        return (
            f'Alert: Node added!'
        )
    
    def __node_removed(self):
        return (
            f'Alert: Node removed!'
        )

    def __status_change(self):
        return (
            f'Alert: status change!'
        )

    def __generic(self):
        return (
            f'For NODE with ID: {self.node_id}:\n'
            f'-- Change Type: {self.change_type}\n\n'
            f'Details: old-->new\n'
            f'old: \n{pformat(self.t1)}\n'
            f'new: \n{pformat(self.t2)}\n'
            f'-----------------------------------------------\n'
        )

    def __str__(self):
        return self.__generic()
        ### 
        match self.change_type:
            case "node_added": self.__node_added()
            case "node_removed": self.__node_removed()
            case "value_change": 
                match self.changed_parameter:
                    case "status": self.__status_change()
                    case _: self.generic()
            case _: self.__generic()





class NodesSnapshot(list):
    """A list of node dictionaries in the format from the dfinity API"""

    endpoint = "https://ic-api.internetcomputer.org/api/v3/nodes"

    def __init__(self, data):
        list.__init__(self, data)

    def get_num_up_nodes(self):
        pass

    def get_num_down_nodes(self):
        pass

    def get_num_unassigned_nodes(self):
        pass

    @staticmethod
    def from_file(file_path):
        """slurps nodes from a json file retrieved with curl"""
        with open(file_path) as f:
            return NodesSnapshot(json.load(f)["nodes"])

    @staticmethod
    def from_api(provider_id=None):
        """slurps nodes from the dfinity api, optional node_provider_id"""
        payload = {"node_provider_id": provider_id} if provider_id else None
        response = requests.get(NodesSnapshot.endpoint, params=payload)
        return NodesSnapshot(response.json()["nodes"])

