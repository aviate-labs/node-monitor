import requests
import json
import time
from collections import deque
from deepdiff import DeepDiff
from datetime import datetime
from pprint import pprint, pformat
import signal
import sys
import logging
import threading


from node_monitor.node_monitor_email import NodeMonitorEmail, email_watcher
from node_monitor.load_config import (
    nodeProviderId, emailRecipients, config, lookuptable
)





class NodeMonitor:

    def __init__(self):
        self.snapshots = deque(maxlen=3)
        if config['IMAPClientEnabled']:
            self.email_watcher_thread = threading.Thread(
                target=email_watcher, args=(self,),
            )
            self.email_watcher_thread.start()
            self.email_watcher_exit_event = threading.Event()

    def update_state(self):
        """fetches a snapshot from API and pushes to fixed size deque"""
        self.snapshots.append(NodesSnapshot.from_api(nodeProviderId))
        logging.info("Fetched New Data")

    def run_once(self):
        diff_boundary = NodeMonitorDiff(self.snapshots[0], self.snapshots[2])
        diff_01 = NodeMonitorDiff(self.snapshots[0], self.snapshots[1])
        diff_12 = NodeMonitorDiff(self.snapshots[1], self.snapshots[2])
        diffs = [DeepDiff(diff_boundary, diff_01), 
                 DeepDiff(diff_boundary, diff_12), 
                 DeepDiff(diff_01, diff_12)]
        all_true = all(diffs)
        if not all_true:
            logging.info("!! Change Detected")
            events = diff_boundary.aggregate_changes()
            events_actionable = [event for event in events
                                if event.is_actionable()]
            email = NodeMonitorEmail(
                "\n\n".join(str(event) for event in events_actionable)
                + "\n\n" + self.stats_message()
            )
            email.send_recipients(emailRecipients)
            logging.info("Emails Sent")
        else:
            logging.info(f"No Change ({config['intervalMinutes']} min)")


    def runloop(self):
        """main loop"""
        logging.info("Starting Node Monitor...")
        self.update_state()
        if config['NotifyOnNodeMonitorStartup']:
            welcome_email = NodeMonitorEmail(self.welcome_message() + self.stats_message())
            welcome_email.send_recipients(emailRecipients)
        signal.signal( signal.SIGINT, lambda s, f : self.exit())
        while True:
            try: 
                self.update_state()
                self.run_once()
            except Exception as e:
                logging.exception(e)
                logging.info("Error occurred. Retrying...")
            time.sleep(60 * config['intervalMinutes'])


    def exit(self):
        logging.info(f"Node Monitor shutting down...")
        if config['IMAPClientEnabled']:
            self.email_watcher_exit_event.set()
            self.email_watcher_thread.join()
        logging.info("Shut Down")
        sys.exit(0)



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
            f"There are currently {self.snapshots[-1].get_num_up_nodes()} nodes in 'UP' status.\n"
            f"There are currently {self.snapshots[-1].get_num_down_nodes()} nodes in 'DOWN' status.\n"
            f"There are currently {self.snapshots[-1].get_num_unassigned_nodes()} nodes in 'UNASSIGNED' status.\n\n"
        )





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


    def is_actionable(self):
        match self.change_type:
            case "node_added":
                return config['NotifyOnNodeAdded']
            case "node_removed":
                return config['NotifyOnNodeRemoved']
            case "value_change":
                if config['NotifyOnAllNodeChanges']:
                    return True
                elif config['NotifyOnNodeChangeStatus']:
                    return self.changed_parameter == 'status'
            case _: return False


    def __ge__(self, other):
        """checks to see if other's values are contained within self"""
        a = [(k,v) for (k,v) in self.__dict__.items() if v is not None]
        b = [(k,v) for (k,v) in other.__dict__.items() if v is not None]
        for (k, v) in b:
            if (k, v) not in a: return False
        return True


    def _node_added(self):
        return (
            f'Alert: Node added!\n'
            f'It looks as if a new node has been added to the IC network, and has become visible on the dashboard.\n'
            f'If you planned on this, all should be working accordingly.\n'
            f'Node ID: {self.node_id}\n'
            f'Node DC ID: {self.t2["dc_id"]}\n'
            f'Node Label: {lookuptable.get(self.node_id, "Not Found")}\n'
        )
    
    def _node_removed(self):
        return (
            f'Alert: Node removed!\n'
            f'It looks as if one node has been removed from the IC network, as it is no longer visible on the dashboard.\n'
            f'If you planned on this, all should be working accordingly.\n'
            f'Node ID: {self.node_id}\n'
            f'Node DC ID: {self.t1["dc_id"]}\n'
            f'Node Label: {lookuptable.get(self.node_id, "Not Found")}\n'
        )

    def _status_change(self):
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
            case _: return self._generic()


    def _generic(self):
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
            case "node_added": return self._node_added()
            case "node_removed": return self._node_removed()
            case "value_change": 
                match self.changed_parameter:
                    case "status": return self._status_change()
                    case _: return self.generic()
            case _: return self._generic()





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

