import pytest
from collections import deque
from typing import Deque

import node_monitor.ic_api as ic_api
from node_monitor.node_monitor_helpers.get_compromised_nodes import \
    get_compromised_nodes

from tests.conftest import mock


def test_get_compromised_nodes():
    #
    # --->  [ 0 0 0 ]   # no nodes down
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(mock["control"])
    dq.append(mock["control"])
    dq.append(mock["control"])
    assert len(get_compromised_nodes(dq)) == 0
    # 
    # --->  [ 0 X 0 ]  # 1 node down (bounce)
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(mock["control"])
    dq.append(mock["one_node_down"])
    dq.append(mock["control"])
    assert len(get_compromised_nodes(dq)) == 0
    #
    # --->  [ 0 X X ]  # 1 node down for 2 snapshots
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(mock["control"])
    dq.append(mock["one_node_down"])
    dq.append(mock["one_node_down"])
    assert len(get_compromised_nodes(dq)) == 1
    #
    # --->  [ 0 X2 X2 ]  # 2 nodes down for 2 snapshots
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(mock["control"])
    dq.append(mock["two_nodes_down"])
    dq.append(mock["two_nodes_down"])
    assert len(get_compromised_nodes(dq)) == 2
    #
    # --->   [ 0 C C ]   # 1 node change subnet for 2 snapshots
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(mock["control"])
    dq.append(mock["one_node_change_subnet"])
    dq.append(mock["one_node_change_subnet"])
    assert len(get_compromised_nodes(dq)) == 0
    #
    # --->   [ 0 R 0 ]   # 1 node removed for 1 snapshot (bounce)
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(mock["control"])
    dq.append(mock["one_node_removed"])
    dq.append(mock["one_node_removed"])
    assert len(get_compromised_nodes(dq)) == 0
    #
    # --->   [ 0 R R ]   # 1 node removed for 2 snapshots
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(mock["control"])
    dq.append(mock["one_node_removed"])
    dq.append(mock["one_node_removed"])
    assert len(get_compromised_nodes(dq)) == 0
    #
    # --->   [ 0 A A ]   # 1 node added for 2 snapshots
    dq: Deque[ic_api.Nodes] = deque(maxlen=3)
    dq.append(mock["one_node_removed"])
    dq.append(mock["control"])
    dq.append(mock["control"])
    