from typing import Deque, List
import node_monitor.ic_api as ic_api

def get_compromised_nodes(snapshots: Deque[ic_api.Nodes]) -> List[ic_api.Node]:
    """
    Function to check for compromised nodes in a deque of snapshots.
    It debounces these checks to filter out temporary blips

    Parameters
    ----------
    snapshots : Deque[ic_api.Nodes]
        A deque containing exactly three snapshots, where each snapshot is an
        ic_api.Nodes object representing the nodes fetched from the 
        ic-api at that time.

    Returns
    -------
    List[ic_api.Node]
        A list of nodes that are found to be compromised based on the comparison
        of status across the snapshots.

    Raises:
    -------
    AssertionError
        If the length of the snapshots deque is not 3.
    """
    
    # We used to use a diff here to monitor any type of changes, but we 
    # prefer this method of checking manually because it results in less code.
    # Original NodeMonitorDiff: commit d743197e4f5da80611ece61e63580b2a65c41491

    assert len(snapshots) == 3, \
        "snapshots must be of length 3, not {}".format(len(snapshots))
    
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
        # if the node just came online in c, skip it to avoid IndexError
        if node_id not in ai or node_id not in bi: continue
        node_a = ai[node_id]
        node_b = bi[node_id]
        node_c = ci[node_id]
        # debounce: eliminate false positives
        # sometimes the nodes go down for a few minutes and come back up
        node_c_is_compromised: bool = all([
            node_a.status == 'UP' or node_a.status == 'UNASSIGNED',
            node_b.status == 'DOWN' or node_b.status == 'DEGRADED',
            node_c.status == 'DOWN' or node_c.status == 'DEGRADED',
        ])
        if node_c_is_compromised:
            compromised_nodes.append(node_c)

    return compromised_nodes
