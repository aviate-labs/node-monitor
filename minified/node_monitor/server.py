from flask import Flask
from typing import Dict
from node_monitor.node_monitor import NodeMonitor


def create_server(nm: NodeMonitor) -> Flask:

    app = Flask(__name__)

    ## - - - - - - 
    @app.route('/')
    def root() -> Dict[str, str]:
        deque_length = str(len(nm.snapshots))
        d = {
            "status": "online",
            "deque_length": deque_length,
        }
        return d
    # - - - - - -

    return app

