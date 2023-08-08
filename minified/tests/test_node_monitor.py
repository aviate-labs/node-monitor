from devtools import debug
from typing import Deque
from collections import deque

from node_monitor.node_monitor import NodeMonitor, get_compromised_nodes
import node_monitor.ic_api as ic_api
from node_monitor.bot_email import EmailBot

# This is data only from nodes with aviate labs provider id
# TODO: Update this data set for all node providers
d = {
    "control":                ic_api.get_nodes_from_file("../tests/t0.json"),
    "one_node_down":          ic_api.get_nodes_from_file("../tests/t1.json"),
    "two_nodes_down":         ic_api.get_nodes_from_file("../tests/t2.json"),
    "one_node_change_subnet": ic_api.get_nodes_from_file("../tests/t3.json"),
    "one_node_removed":       ic_api.get_nodes_from_file("../tests/t4.json"),
}

# Do we want this implemented?
# https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary


# TODO: Make this work either with data stored on disk or from the API
# depending upon flags passed in the command line (see test_bot_email.py)

class TestNodeMonitor:

    def test_resync(self):
        # make sure resync works
        # make sure that the deque never goes over 3
        email_bot = EmailBot
        nm = NodeMonitor(email_bot)
        nm._resync()
        nm._resync()
        nm._resync()
        nm._resync()
        assert len(nm.snapshots) == 3

    def test_analyze(self):
        pass

    def test_broadcast(self):
        pass



def test_get_compromised_nodes():
    #
    # --->  [ 0 0 0 ]   # no nodes down
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(d["control"])
    dq.append(d["control"])
    dq.append(d["control"])
    assert len(get_compromised_nodes(dq)) == 0
    # 
    # --->  [ 0 X 0 ]  # 1 node down (bounce)
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(d["control"])
    dq.append(d["one_node_down"])
    dq.append(d["control"])
    assert len(get_compromised_nodes(dq)) == 0
    #
    # --->  [ 0 X X ]  # 1 node down for 2 snapshots
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(d["control"])
    dq.append(d["one_node_down"])
    dq.append(d["one_node_down"])
    assert len(get_compromised_nodes(dq)) == 1
    #
    # --->  [ 0 X2 X2 ]  # 2 nodes down for 2 snapshots
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(d["control"])
    dq.append(d["two_nodes_down"])
    dq.append(d["two_nodes_down"])
    assert len(get_compromised_nodes(dq)) == 2
    #
    # --->   [ 0 C C ]   # 1 node change subnet for 2 snapshots
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(d["control"])
    dq.append(d["one_node_change_subnet"])
    dq.append(d["one_node_change_subnet"])
    assert len(get_compromised_nodes(dq)) == 0
    #
    # --->   [ 0 R 0 ]   # 1 node removed for 1 snapshot (bounce)
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(d["control"])
    dq.append(d["one_node_removed"])
    dq.append(d["one_node_removed"])
    assert len(get_compromised_nodes(dq)) == 0
    #
    # --->   [ 0 R R ]   # 1 node removed for 2 snapshots
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(d["control"])
    dq.append(d["one_node_removed"])
    dq.append(d["one_node_removed"])
    assert len(get_compromised_nodes(dq)) == 0
    #
    # --->   [ 0 A A ]   # 1 node added for 2 snapshots
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(d["one_node_removed"])
    dq.append(d["control"])
    dq.append(d["control"])
    
