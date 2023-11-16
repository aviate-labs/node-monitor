import pytest
from unittest.mock import patch, Mock
from node_monitor_tracker.node_monitor_tracker import NodeMonitorTracker
from node_monitor.bot_email import EmailBot

@patch("requests.get")
def test_check_server_status(mock_get):
    mock_node_monitor_tracker = Mock(spec=NodeMonitorTracker)

    mock_response = Mock()
    mock_response.json.return_value = {"status": "offline"}
    mock_get.return_value = mock_response

    mock_node_monitor_tracker.check_server_status()

    assert mock_get.assert_called_once_with("insert dummy URL here")
    assert mock_node_monitor_tracker.send_notification.call_count == 1