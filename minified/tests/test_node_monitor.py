import pytest
from devtools import debug
from unittest.mock import patch, Mock

from node_monitor.node_monitor import NodeMonitor
import node_monitor.ic_api as ic_api
from node_monitor.bot_email import EmailBot

from tests.conftest import cached

# This uses data stored on disk that has been cURL'd from the ic-api.


class TestNodeMonitor:

    # init
    mock_email_bot = Mock(spec=EmailBot)
    nm = NodeMonitor(mock_email_bot)
    nm._resync(cached['control'])
    nm._resync(cached['control'])
    nm._resync(cached['control'])

    def test_resync(self):
        # make sure resync works
        # make sure that the deque never goes over 3
        self.nm._resync(cached['one_node_down'])
        assert len(self.nm.snapshots) == 3
    
    @pytest.mark.skip(reason="Not implemented")
    def _test_analyze(self):
        # Not implemented: No easy way to test. 
        # Test functions below should be enough
        pass

    @pytest.mark.skip(reason="Not implemented")
    def _test_analyze(self):
        # Not implemented: No easy way to test. 
        # Test functions below should be enough
        pass




def test_control():
    """Test the control case. No nodes down."""
    # init
    mock_email_bot = Mock(spec=EmailBot)
    nm = NodeMonitor(mock_email_bot)
    nm._resync(cached['control'])
    nm._resync(cached['control'])
    nm._resync(cached['control'])

    # test _analyze()
    nm._analyze()
    assert len(nm.compromised_nodes) == 0
    assert len(nm.compromised_nodes_by_provider) == 0
    assert len(nm.actionables) == 0

    # test broadcast()
    nm.broadcast()
    assert mock_email_bot.send_emails.call_count == 0



def test_one_node_bounce():
    """Test the case where one node bounces.
    Should not result in a false positive."""
    # init
    mock_email_bot = Mock(spec=EmailBot)
    nm = NodeMonitor(mock_email_bot)
    nm._resync(cached['control'])
    nm._resync(cached['one_node_down'])
    nm._resync(cached['control'])

    # test _analyze()
    nm._analyze()
    assert len(nm.compromised_nodes) == 0
    assert len(nm.compromised_nodes_by_provider) == 0
    assert len(nm.actionables) == 0

    # test broadcast()
    nm.broadcast()
    assert mock_email_bot.send_emails.call_count == 0



def test_two_nodes_down():
    """Test the case where two nodes truly go down."""
    # init
    mock_email_bot = Mock(spec=EmailBot)
    nm = NodeMonitor(mock_email_bot)
    nm._resync(cached['control'])
    nm._resync(cached['two_nodes_down'])
    nm._resync(cached['two_nodes_down'])

    # test _analyze()
    nm._analyze()
    assert len(nm.compromised_nodes) == 2
    assert len(nm.compromised_nodes_by_provider) == 1
    assert len(nm.actionables) == 1

    # test broadcast()
    nm.broadcast()
    assert mock_email_bot.send_emails.call_count == 1

