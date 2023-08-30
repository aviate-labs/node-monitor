import time
from collections import deque
from typing import Deque, List, Dict
from toolz import groupby # type: ignore

import node_monitor.ic_api as ic_api
from node_monitor.bot_email import EmailBot
from node_monitor.node_provider_db import NodeProviderDB
from node_monitor.node_monitor_helpers.get_compromised_nodes import \
    get_compromised_nodes

Seconds = int
sync_interval: Seconds = 60 * 4
Principal = str

class NodeMonitor:

    def __init__(self, email_bot: EmailBot, node_provider_db: NodeProviderDB) -> None:
        """NodeMonitor is a class that monitors the status of the nodes."""
        self.email_bot = email_bot
        self.node_provider_db = node_provider_db
        self.snapshots: Deque[ic_api.Nodes] = deque(maxlen=3)
        self.last_update: float | None = None
        self.compromised_nodes: List[ic_api.Node] = []
        self.compromised_nodes_by_provider: \
            Dict[Principal, List[ic_api.Node]] = {}
        self.actionables: Dict[Principal, List[ic_api.Node]] = {}


    def _resync(self, override_data: ic_api.Nodes | None = None) -> None:
        """
        Fetches the current nodes from the ic-api and appends them to the
        snapshots.
        
        Args:
            override_data: If provided, this arg will be used instead of 
                live fetching Nodes from the ic-api. Useful for testing.
        """
        data = override_data if override_data else ic_api.get_nodes()
        self.snapshots.append(data)
        self.last_update = time.time()
    

    def _analyze(self) -> None:
        """Run analysis on the snapshots."""
        if len(self.snapshots) != 3:
            return None
        self.compromised_nodes = get_compromised_nodes(self.snapshots)
        self.compromised_nodes_by_provider = \
            groupby(lambda node: node.node_provider_id, self.compromised_nodes)
        subscribers = self.node_provider_db.get_subscribers()
        subscribers_list: List[Principal] = [entry[0] for entry in subscribers]
        self.actionables = {k: v for k, v
                            in self.compromised_nodes_by_provider.items()
                            if k in subscribers_list}
    

    def broadcast(self) -> None:
        """Broadcast relevant information to the appropriate channels."""
        subscribers = self.node_provider_db.get_subscribers_as_dict()
        node_labels = self.node_provider_db.get_node_labels_as_dict()
        email_recipients = self.node_provider_db.get_emails_as_dict()
        for node_provider_id, nodes in self.actionables.items():
            # - - - - - - - - - - - - - - - - -
            def _represent(nodes: List[ic_api.Node]) -> str:
                # TODO: Move this into its own helper function
                return ', '.join([node.node_id for node in nodes])
            preferences = subscribers[node_provider_id]
            subject = f"""Node Down Alert"""
            msg = f"""The following nodes are down: {_represent(nodes)}"""
            # - - - - - - - - - - - - - - - - -
            if preferences['notify_email'] == True:
                recipients = email_recipients[node_provider_id]
                self.email_bot.send_emails(recipients, subject, msg)
            if preferences['notify_slack'] == True:
                # TODO: Not Yet Implemented
                raise NotImplementedError
            if preferences['notify_telegram_chat'] == True:
                # TODO: Not Yet Implemented
                raise NotImplementedError
            if preferences['notify_telegram_channel'] == True:
                # TODO: Not Yet Implemented
                raise NotImplementedError
            # - - - - - - - - - - - - - - - - -


    def step(self) -> None:
        self._resync()
        self._analyze()
        self.broadcast()


    def mainloop(self) -> None:
        while True:
            self.step()
            time.sleep(sync_interval)
