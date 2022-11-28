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
import signal
import sys


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
    lookupTableFile = config['lookupTableFile']

# config['intervalMinutes']
# config['NotifyOnNodeMonitorStartup']
# config['NotifyOnNodeChangeStatus']
# config['NotifyOnAllNodeChanges']
# config['NotifyOnNodeAdded']
# config['NotifyOnNodeRemoved']


### Lookup Table
lookuptable = {}
if lookupTableFile != "":
    with open(lookupTableFile) as f:
        lookuptable = json.load(f)



def plog(s):
    """prints and logs"""
    new_s = f'[{datetime.utcnow()}]: -- ' + s
    print(new_s)


class NodeMonitor:

    def __init__(self):
        self.snapshots = deque(maxlen=2)

    def update_state(self):
        """fetches a snapshot from API and pushes to fixed size deque"""
        self.snapshots.append(NodesSnapshot.from_api(nodeProviderId))
        plog("Fetched New Data")

    def run_once(self):
        diff = NodeMonitorDiff(self.snapshots[0], self.snapshots[1])
        if diff:
            plog("!! Change Detected")
            actionables = []
            events = diff.aggregate_changes()
            if config['NotifyOnNodeAdded']:
                actionables.extend([event for event in events if event.change_type == "node_added"])
            if config['NotifyOnNodeRemoved']:
                actionables.extend([event for event in events if event.change_type == "node_removed"])
            if config['NotifyOnAllNodeChanges']:
                actionables.extend([event for event in events if event.change_type == "value_change"])
            elif config['NotifyOnNodeChangeStatus']:
                actionables.extend([event for event in events if (event.change_type == "value_change" and event.changed_parameter == "status")])

            for event in actionables:
                email = NodeMonitorEmail(str(event) + self.stats_message())
                email.send_recipients(emailRecipients)
            plog("Emails Sent")
        else:
            plog(f"No Change ({config['intervalMinutes']} min)")


    def runloop(self):
        """main loop"""
        plog("Starting Node Monitor...")
        self.update_state()
        if config['NotifyOnNodeMonitorStartup']:
            welcome_email = NodeMonitorEmail(self.welcome_message() + self.stats_message())
            welcome_email.send_recipients(emailRecipients)
        signal.signal( signal.SIGINT, lambda s, f : sys.exit(0))
        while True:
            self.update_state()
            self.run_once()
            time.sleep(60 * config['intervalMinutes'])


    def welcome_message(self):
        return (
            f"Thank you for subscribing to Node Monitor by Aviate Labs!\n"
            f"Your Node Monitor Settings:\n"
            f"\t ► Dfinity API query update interval: {config['intervalMinutes']} minutes\n"
            f"\t ► Send Email on Node Change status (UP, DOWN, UNASSIGNED): {config['NotifyOnNodeChangeStatus']}\n"
            f"\t ► Send Email on Any Node update (verbose mode): {config['NotifyOnAllNodeChanges']}\n"
            f"\t ► Send Email if new node appears on network: {config['NotifyOnNodeAdded']}\n"
            f"\t ► Send Email if node gets removed from network: {config['NotifyOnNodeRemoved']}\n"
        )

    def stats_message(self):
        return (
            f"\n\n"
            f"There are currently {self.snapshots[-1].get_num_up_nodes()} nodes in 'UP' status.\n"
            f"There are currently {self.snapshots[-1].get_num_down_nodes()} nodes in 'DOWN' status.\n"
            f"There are currently {self.snapshots[-1].get_num_unassigned_nodes()} nodes in 'UNASSIGNED' status.\n\n"
        )




class NodeMonitorEmail(EmailMessage):
    def __init__(self, msg_content, msg_subject="Node Alert"):
        EmailMessage.__init__(self)
        self['Subject'] = msg_subject
        # self['To']      = "NA"
        self['From']    = "Node Monitor by Aviate Labs"
        self.set_content(msg_content)

    def send_to(self, recipient):
        self['To'] = recipient
        with SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(gmailUsername, gmailPassword)
            server.send_message(self)
            plog(f"Email Sent to {self['To']}")
        del self['To']

    def send_recipients(self, recipients):
        for recipient in recipients:
            self.send_to(recipient)



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
            f'Alert: Node added!\n'
            f'It looks as if a new node has been added to the IC network, and has become visible on the dashboard.\n'
            f'If you planned on this, all should be working accordingly.\n'
            f'Node ID: {self.node_id}\n'
        )
    
    def __node_removed(self):
        return (
            f'Alert: Node removed!\n'
            f'It looks as if one node has been removed from the IC network, as it is no longer visible on the dashboard.\n'
            f'If you planned on this, all should be working accordingly.\n'
            f'Node ID: {self.node_id}\n'
        )

    def __status_change(self):
        match self.t2:
            case "UP":
                return (
                    f'🟢🟢🟢 Node UP! 🟢🟢🟢\n'
                    f'Node Back Online\n'
                    f'Node ID: {self.node_id}\n'
                    f'Node DC ID: {self.parent_t2["dc_id"]}\n'
                    f'Node Label: {lookuptable.get(self.node_id, "Not Found")}\n'
                    f'Check live node status here: \nhttps://dashboard.internetcomputer.org/node/{self.node_id}'
                )
            case "DOWN":
                return (
                    f'🛑🛑🛑 MAYDAY! NODE DOWN! 🛑🛑🛑\n'
                    f'Node ID: {self.node_id}\n'
                    f'Node DC ID: {self.parent_t2["dc_id"]}\n'
                    f'Node Label: {lookuptable.get(self.node_id, "Not Found")}\n'
                    f'Check live node status here: \nhttps://dashboard.internetcomputer.org/node/{self.node_id}'
                )
            case "UNASSIGNED":
                return (
                    f'🟡🟡🟡 Alert: status change: UNASSIGNED 🟡🟡🟡\n'
                    f"Node's status is now UNASSIGNED\n"
                    f'Node ID: {self.node_id}\n'
                    f'Node DC ID: {self.parent_t2["dc_id"]}\n'
                    f'Node Label: {lookuptable.get(self.node_id, "Not Found")}\n'
                    f'Check live node status here: \nhttps://dashboard.internetcomputer.org/node/{self.node_id}'
                )
            case _: return self.__generic()


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
        match self.change_type:
            case "node_added": return self.__node_added()
            case "node_removed": return self.__node_removed()
            case "value_change": 
                match self.changed_parameter:
                    case "status": return self.__status_change()
                    case _: return self.generic()
            case _: return self.__generic()





class NodesSnapshot(list):
    """A list of node dictionaries in the format from the dfinity API"""

    endpoint = "https://ic-api.internetcomputer.org/api/v3/nodes"

    def __init__(self, data):
        list.__init__(self, data)

    def get_num_up_nodes(self):
        return len([d for d in self if d['status'] == "UP"])

    def get_num_down_nodes(self):
        return len([d for d in self if d['status'] == "DOWN"])

    def get_num_unassigned_nodes(self):
        return len([d for d in self if d['status'] == "UNASSIGNED"])

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

