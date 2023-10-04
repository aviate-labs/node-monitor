from datetime import datetime
from typing import List, Dict, Tuple

import node_monitor.ic_api as ic_api

# Forgive me Lord Guido, for I have broken PEP8.
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
        f"Live Node Status: {status_url}\n")


def detailnodes(nodes: List[ic_api.Node],
                labels: Dict[Principal, str]) -> str:
    """Runs detailnode on each node in nodes and returns a string of the
    results, separated by newlines. For empty lists, returns an empty string.
    """
    msgs = [detailnode(node, labels.get(node.node_id, 'N/A'))
            for node in nodes]
    return '\n'.join(msgs)


def nodes_down_message(nodes: List[ic_api.Node], 
                       labels: Dict[Principal, str]) -> Tuple[str, str]:
    """Returns a message that describes the nodes that are down, in the
    format of an email or message for a comprable communication channel.
    """
    formatted_nodes_down = detailnodes(nodes, labels)
    subject = "Node Down Alert"
    message = (
        f"🛑 Node/s Down:\n"
        f"The following nodes are compromised:\n\n"
        f"{formatted_nodes_down}")
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
    diagnostic_message = "" if len(nodes_down) == 0 else (
        f"Details of Nodes that are currently DOWN:\n"
        f"{detailnodes(nodes_down, labels)}")
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _make_diagnostic_message() -> str:
        match len(nodes_down):
            case 0: return ""
            case _: return (f"Details of Nodes that are currently DOWN:\n"
                            f"{detailnodes(nodes_down, labels)}")
    def _make_subject() -> str:
        datacenters = {node.dc_id.upper() for node in nodes_down}
        match len(nodes_down):
            case 0: return "All Systems Healthy"
            case _: return "Action Required @ " + ', '.join(sorted(datacenters))
    def _render_frac(numerator: int, denominator: int) -> str:
        match numerator:
            case 0: return "None"
            case _: return f"{numerator}/{denominator}"
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    diagnostic_message = _make_diagnostic_message()
    subject = _make_subject()
    message = (
        f"{diagnostic_message}\n\n"
        f"🔎 Node/s Status Breakdown:\n"
        f"Total Nodes:      {  total_nodes                                       }\n"
        f"Nodes Up:         {  _render_frac(len(nodes_up  ), total_nodes)        }\n"
        f"Nodes Down:       {  _render_frac(len(nodes_down), total_nodes)        }\n"
        f"Nodes Unassigned: {  _render_frac(len(nodes_unassigned), total_nodes)  }\n"
        f"Nodes Disabled:   {  _render_frac(len(nodes_disabled), total_nodes)    }\n"
        f"Nodes Degraded:   {  _render_frac(len(nodes_degraded), total_nodes)    }\n\n"
        f"Thanks for reviewing today's report. We'll be back tomorrow!\n"
        f"Node Monitor by Aviate Labs.\n"
        f"Report generated: {datetime.utcnow().isoformat()} UTC\n"
        f"Help us serve you better! Provide your feedback!\n")
    return (subject, message)
