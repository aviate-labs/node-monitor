from devtools import debug

from node_monitor.node_monitor import NodeMonitor
import node_monitor.ic_api as ic_api
from node_monitor.bot_email import EmailBot


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
