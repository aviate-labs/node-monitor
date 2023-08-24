from flask import Flask, request, Response
from typing import Dict, Callable
from node_monitor.node_monitor import NodeMonitor
import node_monitor.load_config as c


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

    @app.route('/slack-node-status', methods=['POST'])
    def send_node_status_report_slack():
        """Slack endpoint for sending a node status report"""
        # Get data from POST request
        data = request.form
        channel_id = data.get('channel_id')

        #TODO: call function to generate a node_status_report here
        text = "This is a node status report"

        nm.slack_bot.send_message(channel_id, text)

        return Response(), 200

    return app

