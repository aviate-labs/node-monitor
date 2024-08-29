from datetime import datetime
from typing import List, Dict, Tuple

import node_monitor.ic_api as ic_api
import node_monitor.load_config as c

# Forgive me Lord Guido, for I have broken PEP8.
Principal = str

def datetime_iso8601() -> str:
    """Returns the current time in ISO 8601 format, excluding milliseconds.
    Example: 2021-05-01T00:00:00.
    """
    return datetime.utcnow().isoformat(timespec='seconds')


def detailnode(node: ic_api.Node, label: str) -> str:
    """Returns:
        Data Center:      <dc_id>
        Node Label:       <label>
        Node Status:      <status>
        Node ID:          <node_id>
        Live Node Status: <status_url>
    """
    status_url = f"https://dashboard.internetcomputer.org/node/{node.node_id}"
    return (
        f"Data Center: {node.dc_id.upper()}\n"
        f"Node Label: {label}\n"
        f"Node Status: {node.status}\n"
        f"Node ID: {node.node_id}\n"
        f"Live Node Status: {status_url}\n")



def detailnodes(nodes: List[ic_api.Node],
                labels: Dict[Principal, str]) -> str:
    """Runs detailnode on each node in nodes and returns a string of the
    results, separated by newlines. For empty lists, returns an empty string.
    Returns:
        Data Center:      <dc_id>
        Node Label:       <label>
        Node Status:      <status>
        Node ID:          <node_id>
        Live Node Status: <status_url>

        Data Center:      <dc_id>
        Node Label:       <label>
        Node Status:      <status>
        Node ID:          <node_id>
        Live Node Status: <status_url>
        
        ...
        ...
        ...
    """
    msgs = [detailnode(node, labels.get(node.node_id, 'N/A'))
            for node in nodes]
    return '\n'.join(msgs)



def nodes_compromised_message(nodes: List[ic_api.Node], 
                       labels: Dict[Principal, str]) -> Tuple[str, str]:
    """Returns a message that describes the nodes that are compromised, in the
    format of an email or message for a comprable communication channel.
    """
    nodes_compromised = [node for node in nodes 
                         if node.status == 'DOWN' or node.status == 'DEGRADED']
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _make_subject() -> str:
        datacenters = {node.dc_id.upper() for node in nodes_compromised}
        match len(nodes_compromised):
            case 0: return "🟢 All Systems Healthy"
            case _: return "🟡 Action Required @ " + ', '.join(sorted(datacenters))
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    formatted_nodes_compromised = detailnodes(nodes, labels)
    subject = _make_subject()
    message = (
        f"Node(s) Compromised:\n"
        f"\n"
        f"{formatted_nodes_compromised}\n"
        f"\n"
        f"Report Generated: {datetime_iso8601()} UTC\n")
    return (subject, message)



def nodes_status_message(nodes: List[ic_api.Node],
                         labels: Dict[Principal, str]) -> Tuple[str, str]:
    """Returns a message that describes the status of all nodes, in the
    format of an email or message for a comprable communication channel.
    """
    nodes_up           = [node for node in nodes if node.status == 'UP']
    nodes_down         = [node for node in nodes if node.status == 'DOWN']
    nodes_unassigned   = [node for node in nodes if node.status == 'UNASSIGNED']
    nodes_disabled     = [node for node in nodes if node.status == 'DISABLED']
    nodes_degraded     = [node for node in nodes if node.status == 'DEGRADED']
    total_nodes        = len(nodes)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _make_diagnostic_message() -> str:
        match len(nodes_down):
            case 0: return ""
            case _: return (f"Node(s) Compromised:\n"
                            f"\n"
                            f"{detailnodes(nodes_down, labels)}\n\n")
    def _make_subject() -> str:
        datacenters = {node.dc_id.upper() for node in nodes_down}
        match len(nodes_down):
            case 0: return "🟢 All Systems Healthy"
            case _: return "🟡 Action Required @ " + ', '.join(sorted(datacenters))
    def _render_frac(numerator: int, denominator: int) -> str:
        match numerator:
            case 0: return "None"
            case _: return f"{numerator}/{denominator}"
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    subject = _make_subject()
    message = (
        f"\nNode Provider: {nodes[0].node_provider_name}\n"
        f"Nodes Total: {total_nodes}\n"
        f"Node Health: {len(nodes_degraded) + len(nodes_down)} Unhealthy, {len(nodes_unassigned) + len(nodes_up)} Healthy\n"
        f"Node Assignment:  {len(nodes_unassigned)} Unassigned, {len(nodes_up)} Assigned\n"
        f"\n\n"
        f"{_make_diagnostic_message()}"
        f"Report generated: {datetime_iso8601()} UTC\n"
    )
    return (subject, message)
