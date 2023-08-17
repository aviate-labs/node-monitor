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
sync_interval: Seconds = 60 * 4 # 4 minutes -> Seconds
status_report_interval: Seconds = 60 * 60 * 24 # 24 hours -> Seconds
Principal = str

class NodeMonitor:

    def __init__(self, email_bot: EmailBot) -> None:
        """NodeMonitor is a class that monitors the status of the nodes."""
        self.email_bot = email_bot
        self.node_provider_db = NodeProviderDB()
        self.snapshots: Deque[ic_api.Nodes] = deque(maxlen=3)
        self.last_update: float | None = None
        self.last_status_report: float = 0
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
        self.actionables = {k: v for k, v
                            in self.compromised_nodes_by_provider.items()
                            if k in subscribers}
    

    def broadcast(self) -> None:
        """Broadcast relevant information to the appropriate channels."""
        preferences = self.node_provider_db.get_preferences()
        labels = self.node_provider_db.get_node_labels()
        for node_provider_id, nodes in self.actionables.items():
            # - - - - - - - - - - - - - - - - -
            def _represent(nodes: List[ic_api.Node]) -> str:
                # TODO: Move this into its own helper function
                return ', '.join([node.node_id for node in nodes])
            pref = preferences[node_provider_id]
            subject = f"""Node Down Alert"""
            msg = f"""The following nodes are down: {_represent(nodes)}"""
            # - - - - - - - - - - - - - - - - -
            if pref['notify_email'] == True:
                recipients = \
                    self.node_provider_db.get_email_recipients(node_provider_id)
                self.email_bot.send_emails(recipients, subject, msg)
            if pref['notify_slack'] == True:
                # TODO: Not Yet Implemented
                raise NotImplementedError
            if pref['notify_telegram_chat'] == True:
                # TODO: Not Yet Implemented
                raise NotImplementedError
            if pref['notify_telegram_channel'] == True:
                # TODO: Not Yet Implemented
                raise NotImplementedError
            # - - - - - - - - - - - - - - - - -


    def broadcast_status_report(self) -> None:
        """Sends a daily Node Status Report to all Node Providers through
        email."""
        subscribers = self.node_provider_db.get_subscribers()
        for node_provider_id in subscribers:
            recipients = \
                self.node_provider_db.get_email_recipients(node_provider_id)
            subject = f"""Node Status Report"""
            msg = f"""Not Yet Implemented"""
            self.email_bot.send_emails(recipients, subject, msg)



    def step(self) -> None:
        self._resync()
        self._analyze()
        self.broadcast()
        if (self.last_status_report + status_report_interval) <= time.time():
            self.broadcast_status_report()
            self.last_status_report = time.time()


    def mainloop(self) -> None:
        while True:
            self.step()
            time.sleep(sync_interval)
