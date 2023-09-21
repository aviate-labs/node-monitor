import time
from collections import deque
from typing import Deque, List, Dict
from toolz import groupby # type: ignore

import node_monitor.ic_api as ic_api
from node_monitor.bot_email import EmailBot
from node_monitor.bot_slack import SlackBot
from node_monitor.node_provider_db import NodeProviderDB
from node_monitor.node_monitor_helpers.get_compromised_nodes import \
    get_compromised_nodes
import node_monitor.node_monitor_helpers.messages as messages

Seconds = int
Principal = str
sync_interval: Seconds = 60 * 4 # 4 minutes -> Seconds
status_report_interval: Seconds = 60 * 60 * 24 # 24 hours -> Seconds

class NodeMonitor:

    def __init__(
            self, email_bot: EmailBot,slack_bot: SlackBot, 
            node_provider_db: NodeProviderDB) -> None:
        """NodeMonitor is a class that monitors the status of the nodes.
        It is responsible for syncing the nodes from the ic-api, analyzing
        the nodes, and broadcasting alerts to the appropriate channels.

        Args:
            email_bot: An instance of EmailBot
            node_provider_db: An instance of NodeProviderDB

        Attributes:
            email_bot: An instance of EmailBot
            node_provider_db: An instance of NodeProviderDB
            snapshots: A deque of the last 3 snapshots of the nodes
            last_update: The timestamp of the last time the nodes were synced
            compromised_nodes: A list of compromised nodes
            compromised_nodes_by_provider: A dict of compromised nodes, grouped
                by node_provider_id
            actionables: A dict of compromised nodes, grouped by 
                node_provider_id, but only including node_providers that are 
                subscribed to alerts.
        """
        self.email_bot = email_bot
        self.node_provider_db = node_provider_db
        self.slack_bot = slack_bot
        self.snapshots: Deque[ic_api.Nodes] = deque(maxlen=3)
        self.last_update: float | None = None
        self.last_status_report: float = 0
        self.compromised_nodes: List[ic_api.Node] = []
        self.compromised_nodes_by_provider: \
            Dict[Principal, List[ic_api.Node]] = {}
        self.actionables: Dict[Principal, List[ic_api.Node]] = {}


    def _resync(self, override_data: ic_api.Nodes | None = None) -> None:
        """Fetches the current nodes from the ic-api and appends them to the
        snapshots. Updates the last_update attribute.
        
        Args:
            override_data: If provided, this arg will be used instead of 
                live fetching Nodes from the ic-api. Useful for testing.
        """
        data = override_data if override_data else ic_api.get_nodes()
        self.snapshots.append(data)
        self.last_update = time.time()
    

    def _analyze(self) -> None:
        """Run analysis on the snapshots.
        Does not query any external services, rather just analyzes the data.
        Updates the following attributes from most recently synced data:
            compromised_nodes
            compromised_nodes_by_provider
            actionables
        """
        if len(self.snapshots) != 3:
            return None
        self.compromised_nodes = get_compromised_nodes(self.snapshots)
        self.compromised_nodes_by_provider = \
            groupby(lambda node: node.node_provider_id, self.compromised_nodes)
        subscriber_ids = self.node_provider_db.get_subscribers_as_dict().keys()
        self.actionables = {k: v for k, v
                            in self.compromised_nodes_by_provider.items()
                            if k in subscriber_ids}
    

    def broadcast_alerts(self) -> None:
        """Broadcast relevant alerts to the appropriate channels. Retrieves
        subscribers, node_labels, and email_recipients from the database."""
        subscribers = self.node_provider_db.get_subscribers_as_dict()
        node_labels = self.node_provider_db.get_node_labels_as_dict()
        email_recipients = self.node_provider_db.get_emails_as_dict()
        channels = self.node_provider_db.get_channels_as_dict()
        for node_provider_id, nodes in self.actionables.items():
            preferences = subscribers[node_provider_id]
            subject = f"Node Down Alert"
            msg = messages.nodes_down_message(nodes, node_labels)
            # - - - - - - - - - - - - - - - - -
            if preferences['notify_email'] == True:
                recipients = email_recipients[node_provider_id]
                self.email_bot.send_emails(recipients, subject, msg)
            if preferences['notify_slack'] == True:
                self.slack_bot.send_message(
                    channels[node_provider_id]['slack_channel_name'], msg)
            if preferences['notify_telegram_chat'] == True:
                # TODO: Not Yet Implemented
                raise NotImplementedError
            if preferences['notify_telegram_channel'] == True:
                # TODO: Not Yet Implemented
                raise NotImplementedError
            # - - - - - - - - - - - - - - - - -


    def broadcast_status_report(self) -> None:
        """Broadcasts a Node Status Report to all Node Providers.
        Retrieves subscribers, node_labels, and email_recipients from the
        database. Filters out Node Providers that are not subscribed to
        status reports.
        """
        subscribers = self.node_provider_db.get_subscribers_as_dict()
        node_labels = self.node_provider_db.get_node_labels_as_dict()
        email_recipients = self.node_provider_db.get_emails_as_dict()
        latest_snapshot_nodes = self.snapshots[-1].nodes
        all_nodes_by_provider: Dict[Principal, List[ic_api.Node]] = \
            groupby(lambda node: node.node_provider_id, latest_snapshot_nodes)
        reportable_nodes = {k: v for k, v
                            in all_nodes_by_provider.items()
                            if k in subscribers.keys()}
        # - - - - - - - - - - - - - - - - -
        for node_provider_id, nodes in reportable_nodes.items():
            preferences = subscribers[node_provider_id]
            subject = f"Node Status Report"
            msg = messages.nodes_status_message(nodes, node_labels)
            # - - - - - - - - - - - - - - - - -
            if preferences['notify_email'] == True:
                recipients = email_recipients[node_provider_id]
                self.email_bot.send_emails(recipients, subject, msg)
            # - - - - - - - - - - - - - - - - -


    def step(self) -> None:
        """Iterate NodeMonitor one step."""
        seconds_since_epoch = time.time()
        do_broadcast_status_report: bool = seconds_since_epoch >= \
            (self.last_status_report + status_report_interval)
        # - - - - - - - - - - - - - - - - -
        self._resync()
        self._analyze()
        self.broadcast_alerts()
        if do_broadcast_status_report:
            self.broadcast_status_report()
            self.last_status_report = time.time()


    def mainloop(self) -> None:
        """Iterate NodeMonitor in a loop. This is the main entrypoint."""
        while True:
            self.step()
            time.sleep(sync_interval)
