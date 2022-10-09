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


load_dotenv()
gmailUsername          = os.environ.get('gmailUsername')
gmailPassword          = os.environ.get('gmailPassword')
discordBotToken        = os.environ.get('discordBotToken')
emailRecipient         = os.environ.get('emailRecipient')
nodeProviderId         = os.environ.get('nodeProviderIdAllusion')



class NodeMonitor:

    def __init__(self):
        self.snapshots = deque(maxlen=2)

    def update(self):
        """updates snapshots with a new snapshot,
        automatically popleft from queue due to maxsize=2"""
        self.snapshots.append(NodesSnapshot.from_api(nodeProviderId))
        print(f'[{datetime.utcnow()}]: -- Fetched New Data')

    def get_diff(self) -> dict:
        """runs a diff on prev and new snapshot"""
        # possible diff keys (scraped from source):
        # 'set_item_added'
        # 'set_item_removed'
        # 'iterable_item_removed'
        # 'iterable_item_added'
        # 'iterable_item_moved'
        # 'values_changed'
        # 'repetition_change'
        # 'type_changes'
        # 'dictionary_item_added'
        # 'dictionary_item_removed'
        return DeepDiff(self.snapshots[0], self.snapshots[1],
                        view='tree', group_by='node_id')

    def run_once(self):
        """run nodemonitor once"""
        diff = self.get_diff()
        if diff:
            print(f'[{datetime.utcnow()}]: !! Change Detected, Sending Email')
            changed = self.extract_from_diff(diff)
            msg_content = self.pretty_string(changed)
            self.send_email(msg_content)
            print(f'[{datetime.utcnow()}]: -- Email Sent')
        else:
            print(f'[{datetime.utcnow()}]: -- No Change (5 min)')


    def runloop(self):
        """main loop"""
        print(f'[{datetime.utcnow()}]: Starting Node Monitor...')
        self.update()
        try:
            while True:
                self.update()
                self.run_once()
                time.sleep(60*5)
        except KeyboardInterrupt:
            print(f'[{datetime.utcnow()}]: Stopped Node Monitor')


    @staticmethod
    def extract_from_diff(diff):
        """extracts relevant data from a diff into a list of dictionaries,
        one dictionary for each relevant change"""
        utcdate = datetime.utcnow()
        changed = []
        if 'values_changed' in diff.keys():
            for change in diff['values_changed']:
                # relevant info, even if unused, keep for reference
                path = change.path()
                path_list = change.path(output_format='list')
                changed.append({"eventtime": utcdate,
                                "node_id":   path_list[0],
                                "parameter": path_list[1],
                                "t1":        change.t1,
                                "t2":        change.t2,
                                "parent_t2": change.up.t1,
                                "parent_t2": change.up.t2})
        if 'dictionary_item_removed' in diff.keys():
            for change in diff['dictionary_item_removed']:
                path_list = change.path(output_format='list')
                changed.append({"eventtime": utcdate,
                                "node_id": path_list[0],
                                "t1": change.t1,
                                "t2": None,
                                "parameter": 'removed_node'
                                })
        if 'dictionary_item_added' in diff.keys():
            for change in diff['dictionary_item_added']:
                path_list = change.path(output_format='list')
                changed.append({"eventtime": utcdate,
                                "node_id": path_list[0],
                                "t1": None,
                                "t2": change.t2,
                                "parameter": 'added_node'
                                })
        return changed

    @staticmethod
    def filter_by(d, changed):
        """only show changes that reflect d
        for example, d = {'parameter': "status"}
        will only show node changes that contain the key 'paramater'
        and the value 'status'
        """
        return [change for change in changed if d.items() <= change.items()]

    @staticmethod
    def pretty_string(changed):
        """prettify string of dict of change objects"""
        def make_string(d):
            return (
                f'For NODE with ID: {d["node_id"]}:\n'
                f'-- Change Type: {d["parameter"].upper()}\n\n'
                f'Details: old-->new\n'
                f'old: \n{pformat(d["t1"])}\n'
                f'new: \n{pformat(d["t2"])}\n'
                f'-----------------------------------------------\n'
            )
        return "".join(map(make_string, changed))
    
    @staticmethod
    def send_email(msg_content):
        msg = EmailMessage()
        msg['Subject'] = "Node Alert"
        msg['To']      = emailRecipient
        msg['From']    = "Node Monitor by Aviate Labs"
        msg.set_content(msg_content)

        with SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(gmailUsername, gmailPassword)
            server.send_message(msg)
            print("Email Sent")




class NodesSnapshot(list):
    """A list of node dictionaries in the format from the dfinity API"""

    endpoint = "https://ic-api.internetcomputer.org/api/v3/nodes"

    def __init__(self, data):
        list.__init__(self, data)

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

