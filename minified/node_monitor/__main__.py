import threading

from node_monitor.node_monitor import NodeMonitor
from node_monitor.server import create_server


## Initialize
nm = NodeMonitor()
app = create_server(nm)


## Run NodeMonitor in a separate thread
#  daemon threads stop when the main thread stops
#  can we call nm.mainloop as the target without creating a new fn?
def start_node_monitor() -> None:
    print("Starting NodeMonitor...")
    nm.mainloop()
thread = threading.Thread(target=start_node_monitor, daemon=True)
thread.start()



## Run only during development
if __name__ == "__main__":
    # debug=True will run two instances of the thread
    app.run(debug=False)

