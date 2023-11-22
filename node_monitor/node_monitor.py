import time
from collections import deque
from typing import Deque, List, Dict, Optional, Callable
from toolz import groupby # type: ignore
import schedule
import logging

from node_monitor.bot_email import EmailBot
from node_monitor.bot_slack import SlackBot
from node_monitor.bot_telegram import TelegramBot
from node_monitor.node_provider_db import NodeProviderDB
from node_monitor.node_monitor_helpers.get_compromised_nodes import \
    get_compromised_nodes
import node_monitor.node_monitor_helpers.messages as messages
import node_monitor.ic_api as ic_api

Seconds = int
Principal = str
sync_interval: Seconds = 60 * 4 # 4 minutes -> Seconds

class NodeMonitor:

    def __init__(
            self, 
            node_provider_db: NodeProviderDB, 
            email_bot: EmailBot, 
            slack_bot: Optional[SlackBot] = None, 
            telegram_bot: Optional[TelegramBot] = None) -> None:
        """NodeMonitor is a class that monitors the status of the nodes.
        It is responsible for syncing the nodes from the ic-api, analyzing
        the nodes, and broadcasting alerts to the appropriate channels.

        Args:
            email_bot: An instance of EmailBot
            slack_bot: An instance of SlackBot
            telegram_bot: An instance of TelegramBot
            node_provider_db: An instance of NodeProviderDB

        Attributes:
            email_bot: An instance of EmailBot
            slack_bot: An instance of SlackBot
            telegram_bot: An instance of TelegramBot
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
        self.node_provider_db = node_provider_db
        self.email_bot = email_bot
        self.slack_bot = slack_bot
        self.telegram_bot = telegram_bot
        self.snapshots: Deque[ic_api.Nodes] = deque(maxlen=3)
        self.last_update: float | None = None
        self.last_status_report: float = 0
        self.compromised_nodes: List[ic_api.Node] = []
        self.compromised_nodes_by_provider: \
            Dict[Principal, List[ic_api.Node]] = {}
        self.actionables: Dict[Principal, List[ic_api.Node]] = {}
        self.jobs = [
            schedule.every().day.at("15:00", "UTC").do(
                self.broadcast_status_report),
            schedule.every().day.at("15:00", "UTC").do(
                self.update_node_provider_lookup_if_new)
        ]


    def _resync(self, override_data: ic_api.Nodes | None = None) -> None:
        """Fetches the current nodes from the ic-api and appends them to the
        snapshots. Updates the last_update attribute.
        
        Args:
            override_data: If provided, this arg will be used instead of 
                live fetching Nodes from the ic-api. Useful for testing.
        """
        logging.info("Resyncing node states from ic-api...")
        nodes_api = override_data if override_data else ic_api.get_nodes()
        self.snapshots.append(nodes_api)
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


    def _make_broadcaster(self) -> Callable[[str, str, str], None]:
        """A closure that returns a broadcast function with a local cache.
        Allows the returned function to be run in a loop without
        querying the database.
        """
        subscribers = self.node_provider_db.get_subscribers_as_dict()
        email_recipients = self.node_provider_db.get_emails_as_dict()
        slack_channels = self.node_provider_db.get_slack_channels_as_dict()
        telegram_chats = self.node_provider_db.get_telegram_chats_as_dict()

        def broadcaster(node_provider_id: str,
                      subject: str, message: str) -> None:
            """Broadcasts a generic message to a subscriber through their
            selected communication channel(s)."""
            preferences = subscribers[node_provider_id]
            if preferences['notify_email'] == True:
                recipients = email_recipients.get(node_provider_id, None)
                if recipients is not None:
                    self.email_bot.send_emails(recipients, subject, message)
            if preferences['notify_slack'] == True:
                if self.slack_bot is not None:
                    channels = slack_channels.get(node_provider_id, None)
                    if recipients is not None:
                        err1 = self.slack_bot.send_messages(channels, message)
            if preferences['notify_telegram'] == True:
                if self.telegram_bot is not None:
                    chats = telegram_chats.get(node_provider_id, None)
                    if recipients is not None:
                        err2 = self.telegram_bot.send_messages(chats, message)
            return None
        
        return broadcaster
    

    def broadcast_alerts(self) -> None:
        """Broadcast relevant alerts to the appropriate channels."""
        broadcaster = self._make_broadcaster()
        node_labels = self.node_provider_db.get_node_labels_as_dict()
        for node_provider_id, nodes in self.actionables.items():
            logging.info(f"Broadcasting alert message to {node_provider_id}...")
            subject, message = messages.nodes_compromised_message(nodes, node_labels)
            broadcaster(node_provider_id, subject, message)


    def broadcast_status_report(self) -> None:
        """Broadcasts a Node Status Report to all Node Providers."""
        broadcaster = self._make_broadcaster()
        subscribers = self.node_provider_db.get_subscribers_as_dict()
        node_labels = self.node_provider_db.get_node_labels_as_dict()
        latest_snapshot_nodes = self.snapshots[-1].nodes
        all_nodes_by_provider: Dict[Principal, List[ic_api.Node]] = \
            groupby(lambda node: node.node_provider_id, latest_snapshot_nodes)
        reportable_nodes = {k: v for k, v
                            in all_nodes_by_provider.items()
                            if k in subscribers.keys()}
        for node_provider_id, nodes in reportable_nodes.items():
            logging.info(f"Broadcasting status report {node_provider_id}...")
            subject, message = messages.nodes_status_message(nodes, node_labels)
            broadcaster(node_provider_id, subject, message)
    

    def update_node_provider_lookup_if_new(
            self, 
            override_data: ic_api.NodeProviders | None = None) -> None:
        """Fetches the current node providers from the ic-api and compares
        them to what is currently in the node_provider_lookup table in the 
        database. If there is a new node provider in the API, they will be
        added to our database.

        Args:
            override_data: If provided, this arg will be used instead of 
                live fetching Node Providers from the ic-api. Useful for testing.
        """
        data = override_data if override_data else ic_api.get_node_providers()

        node_providers_api = {d.principal_id: d.display_name for d in data.node_providers}
        node_providers_db = self.node_provider_db.get_node_providers_as_dict()
        
        principals_api = set(node_providers_api.keys())
        principals_db = set(node_providers_db.keys())
        principals_diff = principals_api - principals_db

        node_providers_new = {
            principal: node_providers_api[principal] for principal in principals_diff}
        
        if node_providers_new:
            self.node_provider_db.insert_node_providers(node_providers_new)



    def step(self) -> None:
        """Iterate NodeMonitor one step."""
        try:
            # These all need to be in the same try/catch block, because if
            # _resync fails, we don't want to analyze or broadcast_alerts.
            self._resync()
            self._analyze()
            self.broadcast_alerts()
        except Exception as e:
            logging.error(f"NodeMonitor.step() failed with error: {e}")


    def mainloop(self) -> None:
        """Iterate NodeMonitor in a loop. This is the main entrypoint."""
        while True:
            self.step()
            schedule.run_pending()
            time.sleep(sync_interval)
