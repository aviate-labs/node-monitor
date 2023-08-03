import time
from collections import deque
from typing import Deque, List, Dict
from toolz import groupby # type: ignore

import node_monitor.ic_api as ic_api
from node_monitor.load_config import defaultConfig

Seconds = int
sync_interval: Seconds = 60 * 4


class NodeMonitor():
    def __init__(self) -> None:
        """NodeMonitor is a class that monitors the status of the nodes."""
        self.snapshots: Deque[ic_api.Nodes] = deque(maxlen=3)
        self.compromised_nodes: List[ic_api.Node] = []

    def _resync(self) -> None:
        """Fetch the current nodes and append to the snapshots."""
        self.snapshots.append(ic_api.get_nodes())
    
    def _analyze(self) -> None:
        """Run analysis on the snapshots."""
        self.compromised_nodes = get_compromised_nodes(self.snapshots)
    
    def broadcast(self) -> None:
        """Broadcast relevant information to the appropriate channels."""
        actionables: Dict[str, List[ic_api.Node]] = \
            groupby('node_provider_id', self.compromised_nodes)
        for node_provider_id, nodes in actionables.items():
            config = defaultConfig
            if config['NotifyByEmail'] == True:
                pass
            if config['NotifyBySlack'] == True:
                #TODO: Implement This
                pass
            if config['NotifyByTelegramChannel'] == True:
                #TODO: Implement This
                pass
            if config['NotifyByTelegramChat'] == True:
                #TODO: Implement This
                pass

    def step(self) -> None:
        self._resync()
        self._analyze()
        self.broadcast()

    def mainloop(self) -> None:
        while True:
            self.step()
            time.sleep(sync_interval)



def get_compromised_nodes(snapshots: Deque[ic_api.Nodes]) -> List[ic_api.Node]:
    """Check for compromised nodes, making sure to debounce."""
    # We used to use a diff here to monitor any type of changes, but we 
    # prefer this method of checking manually because it results in less code.
    # Original NodeMonitorDiff: commit d743197e4f5da80611ece61e63580b2a65c41491

    if len(snapshots) < 3:
        return []
    
    # destructure the nodes from the snapshots
    a = snapshots[0].nodes
    b = snapshots[1].nodes
    c = snapshots[2].nodes 

    # index the nodes by node_id
    ai = {node.node_id: node for node in a}
    bi = {node.node_id: node for node in b}
    ci = {node.node_id: node for node in c}

    # collect downed nodes
    compromised_nodes = []
    for node_id in ci.keys():
        node_a = ai[node_id]
        node_b = bi[node_id]
        node_c = ci[node_id]
        # debounce: eliminate false positives
        # sometimes the nodes go down for a few minutes and come back up
        node_c_is_compromised: bool = all([
            node_a.status == 'UP',
            node_b.status != 'UP',
            node_c.status != 'UP',
        ])
        if node_c_is_compromised:
            compromised_nodes.append(node_c)

    return compromised_nodes
