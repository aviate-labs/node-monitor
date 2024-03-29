import pytest
from devtools import debug
from unittest.mock import patch, Mock

from node_monitor.node_monitor import NodeMonitor
from node_monitor.bot_email import EmailBot
from node_monitor.bot_slack import SlackBot
from node_monitor.bot_telegram import TelegramBot
from node_monitor.node_provider_db import NodeProviderDB

from tests.conftest import cached

# This uses data stored on disk that has been fetched with cURL from the ic-api.

# Set up a mock database so that we can test the broadcast() function
# without needing to access a database. This (temporarily) uses Allusion's 
# node-provider-id (principal) on our test data stored in 'data/'
# TODO: expand these tests to work on all nodes, not just Allusion's nodes 
# (currently all data in the 'data/' directory is filtered to only contain
# Allusion's nodes)

mock_node_provider_db = Mock(spec=NodeProviderDB)
mock_node_provider_db.get_subscribers_as_dict.return_value = \
{'rbn2y-6vfsb-gv35j-4cyvy-pzbdu-e5aum-jzjg6-5b4n5-vuguf-ycubq-zae': {
        'node_provider_id': 'rbn2y-6vfsb-gv35j-4cyvy-pzbdu-e5aum-jzjg6-5b4n5-vuguf-ycubq-zae',
        'notify_on_status_change': True,
        'notify_email': True,
        'notify_slack': True,
        'node_provider_name': 'Allusion',
        'notify_telegram': True,
    },
    'eipr5-izbom-neyqh-s3ec2-52eww-cyfpg-qfomg-3dpwj-4pffh-34xcu-7qe': {
        'node_provider_id': 'eipr5-izbom-neyqh-s3ec2-52eww-cyfpg-qfomg-3dpwj-4pffh-34xcu-7qe', 
        'notify_on_status_change': True, 
        'notify_email': True, 
        'notify_slack': True, 
        'node_provider_name': '87m Neuron, LLC', 
        'notify_telegram': True}}
mock_node_provider_db.get_node_labels_as_dict.return_value = \
    {'77fe5-a4oq4-o5pk6-glxt7-ejfpv-tdkrr-24mgs-yuvvz-2tqx6-mowdr-eae': 'dummy-node-label-1',
     'clb2i-sz6tk-tlcpr-hgnfv-iybzf-ytorn-dmzkz-m2iw2-lpkqb-l455g-pae': 'dummy-node-label-2'}
mock_node_provider_db.get_emails_as_dict.return_value = \
    {'rbn2y-6vfsb-gv35j-4cyvy-pzbdu-e5aum-jzjg6-5b4n5-vuguf-ycubq-zae':
     ['test_recipient@gmail.com']}
    #  'eipr5-izbom-neyqh-s3ec2-52eww-cyfpg-qfomg-3dpwj-4pffh-34xcu-7qe':
    #  ['test_recipient1@gmail.com']}
mock_node_provider_db.get_slack_channels_as_dict.return_value = \
    {'rbn2y-6vfsb-gv35j-4cyvy-pzbdu-e5aum-jzjg6-5b4n5-vuguf-ycubq-zae':
        ['#node-monitor']}
mock_node_provider_db.get_telegram_chats_as_dict.return_value = \
    {'rbn2y-6vfsb-gv35j-4cyvy-pzbdu-e5aum-jzjg6-5b4n5-vuguf-ycubq-zae':
        ['5734534558']}
mock_node_provider_db.get_node_providers_as_dict.return_value = \
    {'7k7b7-4pzhf-aivy6-y654t-uqyup-2auiz-ew2cm-4qkl4-nsl4v-bul5k-5qe': '1G',
    'sqhxa-h6ili-qkwup-ohzwn-yofnm-vvnp5-kxdhg-saabw-rvua3-xp325-zqe': '43rd Big Idea Films'}

# Note that reset_mock() doesn’t clear the return value, side_effect or any 
# child attributes you have set using normal assignment by default


class TestNodeMonitor:

    # init
    mock_email_bot = Mock(spec=EmailBot)
    mock_slack_bot = Mock(spec=SlackBot)
    mock_telegram_bot = Mock(spec=TelegramBot)
    nm = NodeMonitor(mock_node_provider_db, mock_email_bot, 
                     mock_slack_bot, mock_telegram_bot)
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



def test_control():
    """Test the control case. No nodes down."""
    # init
    mock_email_bot = Mock(spec=EmailBot)
    mock_slack_bot = Mock(spec=SlackBot)
    mock_telegram_bot = Mock(spec=TelegramBot)
    nm = NodeMonitor(mock_node_provider_db, mock_email_bot, 
                     mock_slack_bot, mock_telegram_bot)
    nm._resync(cached['control'])
    nm._resync(cached['control'])
    nm._resync(cached['control'])

    # test _analyze()
    nm._analyze()
    assert len(nm.compromised_nodes) == 0
    assert len(nm.compromised_nodes_by_provider) == 0
    assert len(nm.actionables) == 0

    # test broadcast_alerts()
    nm.broadcast_alerts()
    assert mock_email_bot.send_emails.call_count == 0
    assert mock_slack_bot.send_messages.call_count == 0
    assert mock_telegram_bot.send_messages.call_count == 0
    mock_node_provider_db.reset_mock()
    mock_email_bot.reset_mock()
    mock_slack_bot.reset_mock()
    mock_telegram_bot.reset_mock()

    # test broadcast_status_report()
    nm.broadcast_status_report()
    assert mock_email_bot.send_emails.call_count == 1
    assert mock_slack_bot.send_messages.call_count == 1
    assert mock_telegram_bot.send_messages.call_count == 1
    mock_node_provider_db.reset_mock()
    mock_email_bot.reset_mock()
    mock_slack_bot.reset_mock()
    mock_telegram_bot.reset_mock()



def test_one_node_bounce():
    """Test the case where one node bounces.
    Should not result in a false positive.
    """
    # init
    mock_email_bot = Mock(spec=EmailBot)
    mock_slack_bot = Mock(spec=SlackBot)       
    mock_telegram_bot = Mock(spec=TelegramBot)
    nm = NodeMonitor(mock_node_provider_db, mock_email_bot, 
                     mock_slack_bot, mock_telegram_bot)
    nm._resync(cached['control'])
    nm._resync(cached['one_node_down'])
    nm._resync(cached['control'])

    # test _analyze()
    nm._analyze()
    assert len(nm.compromised_nodes) == 0
    assert len(nm.compromised_nodes_by_provider) == 0
    assert len(nm.actionables) == 0

    # test broadcast_alerts()
    nm.broadcast_alerts()
    assert mock_email_bot.send_emails.call_count == 0
    assert mock_slack_bot.send_messages.call_count == 0
    assert mock_telegram_bot.send_messages.call_count == 0
    mock_node_provider_db.reset_mock()
    mock_email_bot.reset_mock()
    mock_slack_bot.reset_mock()
    mock_telegram_bot.reset_mock()


def test_two_nodes_down():
    """Test the case where two nodes truly go down."""
    # init
    mock_email_bot = Mock(spec=EmailBot)
    mock_slack_bot = Mock(spec=SlackBot)
    mock_telegram_bot = Mock(spec=TelegramBot)
    nm = NodeMonitor(mock_node_provider_db, mock_email_bot, 
                     mock_slack_bot, mock_telegram_bot)
    nm._resync(cached['control'])
    nm._resync(cached['two_nodes_down'])
    nm._resync(cached['two_nodes_down'])

    # test _analyze()
    nm._analyze()
    assert len(nm.compromised_nodes) == 2
    assert len(nm.compromised_nodes_by_provider) == 1
    assert len(nm.actionables) == 1

    # test broadcast_alerts()
    nm.broadcast_alerts()
    assert mock_email_bot.send_emails.call_count == 1
    assert mock_slack_bot.send_messages.call_count == 1
    assert mock_telegram_bot.send_messages.call_count == 1
    mock_node_provider_db.reset_mock()
    mock_email_bot.reset_mock()
    mock_slack_bot.reset_mock()
    mock_telegram_bot.reset_mock()


def test_one_new_node_online():
    """Test the case where one new node comes online."""
    # init
    mock_email_bot = Mock(spec=EmailBot)
    mock_slack_bot = Mock(spec=SlackBot)
    mock_telegram_bot = Mock(spec=TelegramBot)
    nm = NodeMonitor(mock_node_provider_db, mock_email_bot, 
                     mock_slack_bot, mock_telegram_bot)
    nm._resync(cached['one_node_removed'])
    nm._resync(cached['one_node_removed'])
    nm._resync(cached['control'])

    # test _analyze()
    nm._analyze()
    assert len(nm.compromised_nodes) == 0
    assert len(nm.compromised_nodes_by_provider) == 0
    assert len(nm.actionables) == 0

    # test broadcast_alerts()
    nm.broadcast_alerts()
    assert mock_email_bot.send_emails.call_count == 0
    assert mock_slack_bot.send_message.call_count == 0
    assert mock_telegram_bot.send_message.call_count == 0
    mock_node_provider_db.reset_mock()
    mock_email_bot.reset_mock()
    mock_slack_bot.reset_mock()
    mock_telegram_bot.reset_mock()



def test_no_new_node_provider():
    mock_email_bot = Mock(spec=EmailBot)
    mock_slack_bot = Mock(spec=SlackBot)
    mock_telegram_bot = Mock(spec=TelegramBot)
    nm = NodeMonitor(mock_node_provider_db, mock_email_bot, 
                     mock_slack_bot, mock_telegram_bot)
    
    nm.update_node_provider_lookup_if_new(cached['node_provider_control'])
    assert mock_node_provider_db.insert_node_providers.call_count == 0



def test_one_new_node_provider():
    mock_email_bot = Mock(spec=EmailBot)
    mock_slack_bot = Mock(spec=SlackBot)
    mock_telegram_bot = Mock(spec=TelegramBot)
    nm = NodeMonitor(mock_node_provider_db, mock_email_bot, 
                     mock_slack_bot, mock_telegram_bot)
    
    nm.update_node_provider_lookup_if_new(cached['new_node_providers'])
    assert mock_node_provider_db.insert_node_providers.call_count == 1
    