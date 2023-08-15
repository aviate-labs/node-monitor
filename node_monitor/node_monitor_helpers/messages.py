from typing import List, Dict

import node_monitor.ic_api as ic_api

Principal = str

def node_details(node: ic_api.Node, label: str) -> str:
    status_url = "https://dashboard.internetcomputer.org/node/{node.node_id}"
    return (
        f"Node ID:          {node.node_id}\n"
        f"Node Label:       {label}\n"
        f"Node Status:      {node.status}\n"
        f"Live Node Status: {status_url}\n"
    )

def multiple_node_details(nodes: List[ic_api.Node], 
                          labels: Dict[Principal, str]) -> str:
    s = ""
    for node in nodes:
        s += node_details(node, labels[node.node_provider_id]) + '\n'
    return s


def node_down_message(nodes: List[ic_api.Node]) -> str:
    s = ', '.join([node.node_id for node in nodes])
    return (
        f"The following Nodes are compromised:\n"
        f"{s}"
    )


def _represent(nodes: List[ic_api.Node]) -> str:
    """Deprecated. Do not use."""
    # TODO: Move this into its own helper function
    return ', '.join([node.node_id for node in nodes])