from flask import Flask
from typing import Dict
from node_monitor.node_monitor import NodeMonitor


def create_server(nm: NodeMonitor) -> Flask:

    app = Flask(__name__)

    ## - - - - - - 
    @app.route('/')
    def root() -> Dict[str, str]:
        deque_length = str(len(nm.snapshots))
        last_update = str(nm.last_update)
        d = {
            "status": "online",
            "deque_length": deque_length,
            "last_update": last_update
        }
        return d
    # - - - - - -

    return app

