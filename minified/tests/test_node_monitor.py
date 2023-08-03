from node_monitor.node_monitor import NodeMonitor
import node_monitor.ic_api as ic_api
from devtools import debug
from typing import List

## TODO: Make this work from the data stored on disk instead of from the API.

def test__resync():
    nm = NodeMonitor()
    nm._resync()
    assert len(nm.snapshots) == 1

def test__analyze():
    nm = NodeMonitor()
    nm._resync()
    nm._resync()
    nm._resync()
    nm._analyze()
