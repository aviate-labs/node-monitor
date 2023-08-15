from typing import List

import node_monitor.ic_api as ic_api

def node_details(node: ic_api.Node, label: str) -> str:
    return (
        f"Node ID:    {node.node_id}\n"
        f"Node Label: {label}\n"
    )


def node_down_message(nodes: List[ic_api.Node]) -> str:
    s = ', '.join([node.node_id for node in nodes])
    return (
        f"The following Nodes are down:\n"
        f"{s}"
    )


def _represent(nodes: List[ic_api.Node]) -> str:
    """Deprecated. Do not use."""
    # TODO: Move this into its own helper function
    return ', '.join([node.node_id for node in nodes])