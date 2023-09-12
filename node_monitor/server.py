from flask import Flask
from typing import Dict, Callable
from node_monitor.node_monitor import NodeMonitor


def create_server(
        nm: NodeMonitor, 
        thread_is_alive: Callable[[], bool]) -> Flask:

    app = Flask(__name__)

    ## - - - - - - 
    @app.route('/')
    def root() -> Dict[str, str]:
        deque_length = str(len(nm.snapshots))
        last_update = str(nm.last_update)
        status = "online" if thread_is_alive() else "offline"
        d = {
            "status": status,
            "deque_length": deque_length,
            "last_update": last_update
        }
        return d
    # - - - - - -

    return app
