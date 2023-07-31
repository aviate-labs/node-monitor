from collections import deque
from typing import Deque, List

import ic_api

class NodeMonitor():
    def __init__(self):
        """NodeMonitor is a class that monitors the status of the nodes."""
        self.snapshots: Deque[ic_api.Nodes] = deque(maxlen=3)

    def update(self):
        """Fetch the current nodes and append to the snapshots."""
        self.snapshots.append(ic_api.get_nodes())

    def check(self) -> List[ic_api.Node]:
        """Check for compromised nodes, making sure to debounce."""
        if len(self.snapshots) < 3:
            return []
        
        # destructure the nodes from the snapshots
        a = self.snapshots[0].nodes
        b = self.snapshots[1].nodes
        c = self.snapshots[2].nodes 

        # index the nodes by node_id
        ai = {node['node_id']: node for node in a}
        bi = {node['node_id']: node for node in b}
        ci = {node['node_id']: node for node in c}

        # collect downed nodes
        compromised_nodes = []
        for _, node_c in ci.items():
            node_a = ai[ai['node_id']]
            node_b = bi[bi['node_id']]
            # debounce: eliminate false positives
            # sometimes the nodes go down for a few minutes and come back up
            node_c_is_compromised: bool = all([
                node_a['status'] == 'UP',
                node_b['status'] != 'UP',
                node_c['status'] != 'UP',
            ])
            if node_c_is_compromised:
                compromised_nodes.append(node_c)

        return compromised_nodes
        

    def step(self):
        self.update()
        pass

    def mainloop(self):
        pass
