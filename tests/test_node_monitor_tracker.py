import pytest
from unittest.mock import patch, Mock
from node_monitor_tracker.node_monitor_tracker import NodeMonitorTracker
from node_monitor.bot_email import EmailBot
import node_monitor.load_config as c

@patch("requests.get")
def test_check_server_status(mock_get):
    mock_email_bot = Mock(spec=EmailBot)
    node_monitor_tracker = NodeMonitorTracker(
        mock_email_bot, c.EMAIL_ADMINS_LIST, c.NODE_MONITOR_URL )

    mock_response = Mock()
    mock_response.json.return_value = {"status": "offline"}
    mock_get.return_value = mock_response

    node_monitor_tracker.check_node_monitor_status()

    mock_get.assert_called_once_with(c.NODE_MONITOR_URL)
    assert mock_email_bot.send_emails.call_count == 1