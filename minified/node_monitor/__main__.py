from flask import Flask
from typing import Dict
import threading
import time

from node_monitor.node_monitor import NodeMonitor


## Initialize
app = Flask(__name__)
nm = NodeMonitor()


## Create Routes
@app.route('/')
def root() -> Dict[str, str]:
    deque_length = str(len(nm.snapshots))
    d = {
        "status": "online",
        "deque_length": deque_length,
    }
    return d


## Run NodeMonitor
def start_node_monitor() -> None:
    # run as a daemon thread so that it stops when the main thread stops
    nm.mainloop()
thread = threading.Thread(target=start_node_monitor, daemon=True)
thread.start()



## Run only during development
if __name__ == "__main__":
    # debug=True will run two instances of the thread
    app.run(debug=False)

