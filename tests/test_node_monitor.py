import pytest
from devtools import debug
from unittest.mock import patch, Mock

from node_monitor.node_monitor import NodeMonitor
import node_monitor.ic_api as ic_api
import node_monitor.load_config as c
from node_monitor.bot_email import EmailBot
from node_monitor.bot_slack import SlackBot
from node_monitor.bot_telegram import TelegramBot
from node_monitor.node_provider_db import NodeProviderDB

from tests.conftest import cached

# This uses data stored on disk that has been fetched with cURL from the ic-api.


class TestNodeMonitor:

    # init
    mock_email_bot = Mock(spec=EmailBot)
    mock_slack_bot = Mock(spec=SlackBot)
    nm = NodeMonitor(mock_email_bot, mock_slack_bot)
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



# Set up a mock database so that we can test the broadcast() function
# without needing to access a database. This (temporarily) uses Allusion's 
# node-provider-id (principal) on our test data stored in 'data/'
# TODO: expand these tests to work on all nodes, not just Allusion's nodes 
# (currently all data in the 'data/' directory is filtered to only contain
# Allusion's nodes)

mock_node_provider_db = Mock(spec=NodeProviderDB)
mock_node_provider_db.get_email_recipients.return_value = \
    ['test_recipient@gmail.com']
mock_node_provider_db.get_subscribers.return_value = \
    ['rbn2y-6vfsb-gv35j-4cyvy-pzbdu-e5aum-jzjg6-5b4n5-vuguf-ycubq-zae']
mock_node_provider_db.get_preferences.return_value = \
    {'rbn2y-6vfsb-gv35j-4cyvy-pzbdu-e5aum-jzjg6-5b4n5-vuguf-ycubq-zae':
     {'notify_email': True,
      'notify_slack': True,
      'notify_telegram_chat': True,
      'notify_telegram_channel': True}}
mock_node_provider_db.get_channel_details.return_value = \
    {'rbn2y-6vfsb-gv35j-4cyvy-pzbdu-e5aum-jzjg6-5b4n5-vuguf-ycubq-zae': 
     {'channel_detail_id': 1, 
      'node_provider_principal': \
        'rbn2y-6vfsb-gv35j-4cyvy-pzbdu-e5aum-jzjg6-5b4n5-vuguf-ycubq-zae', 
      'slack_channel_name': '#node-monitor', 
      'telegram_chat_id': '5734534558', 
      'telegram_channel_id': '-1001925583150'}}



def test_control():
    """Test the control case. No nodes down."""
    # init
    mock_email_bot = Mock(spec=EmailBot)
    mock_slack_bot = Mock(spec=SlackBot)
    nm = NodeMonitor(mock_email_bot, mock_slack_bot)
    nm.node_provider_db = mock_node_provider_db
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
    mock_node_provider_db.reset_mock()



def test_one_node_bounce():
    """Test the case where one node bounces.
    Should not result in a false positive."""
    # init
    mock_email_bot = Mock(spec=EmailBot)
    mock_slack_bot = Mock(spec=SlackBot)
    nm = NodeMonitor(mock_email_bot, mock_slack_bot)
    nm.node_provider_db = mock_node_provider_db
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
    mock_node_provider_db.reset_mock()


def test_two_nodes_down():
    """Test the case where two nodes truly go down."""
    # init
    mock_email_bot = Mock(spec=EmailBot)
    mock_slack_bot = Mock(spec=SlackBot)
    mock_telgram_bot = Mock(spec=TelegramBot)
    nm = NodeMonitor(mock_email_bot, mock_slack_bot, mock_telgram_bot)
    nm.node_provider_db = mock_node_provider_db
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
    assert mock_slack_bot.send_message.call_count == 1
    assert mock_telgram_bot.send_message_to_chat.call_count == 1
    assert mock_telgram_bot.send_message_to_channel.call_count == 1
    mock_node_provider_db.reset_mock()

