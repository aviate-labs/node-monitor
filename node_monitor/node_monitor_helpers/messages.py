from typing import List, Dict

import node_monitor.ic_api as ic_api

Principal = str

def detailnode(node: ic_api.Node, label: str) -> str:
    """Returns:
        Node ID:          <node_id>
        Node Label:       <label>
        Node Status:      <status>
        Live Node Status: <status_url>
    """
    status_url = f"https://dashboard.internetcomputer.org/node/{node.node_id}"
    return (
        f"Node ID: {node.node_id}\n"
        f"Node Label: {label}\n"
        f"Node Status: {node.status}\n"
        f"Live Node Status: {status_url}\n"
    )

def detailnodes(nodes: List[ic_api.Node], 
                          labels: Dict[Principal, str]) -> str:
    """Runs detailnode on each node in nodes and returns a string of the
    results, separated by newlines.
    """
    msgs = [detailnode(node, labels[node.node_provider_id]) for node in nodes]
    return '\n'.join(msgs)


def nodes_down_message(nodes: List[ic_api.Node], 
                      labels: Dict[Principal, str]) -> str:
    """Returns a message that describes the nodes that are down, in the
    format of an email or message for a comprable communication channel.
    """
    formatted_nodes_down = detailnodes(nodes, labels)
    return (
        f"🛑 Node/s Down:\n"
        f"The following nodes are compromised:\n\n"
        f"{formatted_nodes_down}"
    )
