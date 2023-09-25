import pytest
from devtools import debug

from node_monitor.node_provider_db import NodeProviderDB
import node_monitor.load_config as c



##############################################
## SETUP & TEST SETUP

# We're breaking the PEP8 line length limit here on purpose, it makes the
# database operations and assert statements more readable.

node_provider_db = None

@pytest.mark.db
def test_init():
    global node_provider_db
    node_provider_db = NodeProviderDB(
        c.DB_HOST, c.DB_NAME, c.DB_USERNAME, c.DB_PASSWORD, c.DB_PORT)
    assert node_provider_db is not None

@pytest.mark.db
def test_get_public_schema_tables():
    all_public_tables = set(node_provider_db.get_public_schema_tables())
    necessary_tables = {'subscribers', 'email_lookup', 
                        'channel_lookup', 'node_label_lookup'}
    assert necessary_tables.issubset(all_public_tables)




##############################################
## TEST CRUD :: TABLE subscribers

@pytest.mark.db
def test_subscribers_crud():
    # Create new subscribers / overwrite subscriber 1
    node_provider_db._insert_subscriber('test-dummy-principal-1', True, True, False, False, False)
    node_provider_db._insert_subscriber('test-dummy-principal-2', True, True, False, False, False)
    node_provider_db._insert_subscriber('test-dummy-principal-1', True, True, True, True, True)

    # Get and check subscribers
    subs = node_provider_db.get_subscribers()
    assert ('test-dummy-principal-1', True, True, True, True, True) in subs
    assert ('test-dummy-principal-2', True, True, False, False, False) in subs

    # Get and check subscribers as dict
    subs = node_provider_db.get_subscribers_as_dict()
    assert subs['test-dummy-principal-1'] == \
        {'node_provider_id': 'test-dummy-principal-1', 'notify_on_status_change': True, 'notify_email': True,
         'notify_slack': True, 'notify_telegram_chat': True, 'notify_telegram_channel': True}
    assert subs['test-dummy-principal-2'] == \
        {'node_provider_id': 'test-dummy-principal-2', 'notify_on_status_change': True, 'notify_email': True,
         'notify_slack': False, 'notify_telegram_chat': False, 'notify_telegram_channel': False}

    # Delete subscribers
    node_provider_db._delete_subscriber('test-dummy-principal-1')
    node_provider_db._delete_subscriber('test-dummy-principal-2')

    # Get and check subscribers
    subs = node_provider_db.get_subscribers()
    assert ('test-dummy-principal-1', True, True, True, True, True) not in subs
    assert ('test-dummy-principal-2', True, True, False, False, False) not in subs

    # Get and check subscribers as dict
    subs = node_provider_db.get_subscribers_as_dict()
    assert 'test-dummy-principal-1' not in subs
    assert 'test-dummy-principal-2' not in subs




##############################################
## TEST CRUD :: TABLE email_lookup

@pytest.mark.db
def test_email_lookup_crud():
    # Insert new emails, including multiple for the same principal
    node_provider_db._insert_email('test-dummy-principal-1', 'a@mail.com')
    node_provider_db._insert_email('test-dummy-principal-1', 'b@mail.com')
    node_provider_db._insert_email('test-dummy-principal-2', 'c@mail.com')

    # Get the emails, remove surrogate id column
    # Check that the emails were inserted correctly
    emails = node_provider_db.get_emails()
    emails = [(row[1], row[2]) for row in emails]
    assert ('test-dummy-principal-1', 'a@mail.com') in emails
    assert ('test-dummy-principal-1', 'b@mail.com') in emails
    assert ('test-dummy-principal-2', 'c@mail.com') in emails

    # Get and check emails as dict, any order is fine
    emails = node_provider_db.get_emails_as_dict()
    assert emails['test-dummy-principal-1'] == ['b@mail.com', 'a@mail.com'] \
        or emails['test-dummy-principal-1'] == ['a@mail.com', 'b@mail.com']
    assert emails['test-dummy-principal-2'] == ['c@mail.com']

    # Delete emails
    node_provider_db._delete_email('a@mail.com')
    node_provider_db._delete_email('b@mail.com')
    node_provider_db._delete_email('c@mail.com')

    # Get the emails again, remove surrogate id column
    # Check that the emails were deleted correctly
    emails = node_provider_db.get_emails()
    emails = [(row[1], row[2]) for row in emails]
    assert ('test-dummy-principal-1', 'a@mail.com') not in emails
    assert ('test-dummy-principal-1', 'b@mail.com') not in emails
    assert ('test-dummy-principal-2', 'c@mail.com') not in emails

    # Get and check emails as dict
    emails = node_provider_db.get_emails_as_dict()
    assert 'test-dummy-principal-1' not in emails
    assert 'test-dummy-principal-2' not in emails




##############################################
## TEST CRUD :: TABLE channel_lookup

@pytest.mark.db
def test_channel_lookup_crud():
    # Insert new channels, including duplicate principals
    node_provider_db._insert_channel(
        'test-dummy-principal-1', 'dummy-slack-channel-1', 'dummy-telegram-chat-1', 'dummy-telegram-channel-1')
    node_provider_db._insert_channel(
        'test-dummy-principal-2', 'dummy-slack-channel-2', 'dummy-telegram-chat-2', 'dummy-telegram-channel-2')
    node_provider_db._insert_channel(
        'test-dummy-principal-1', 'dummy-slack-channel-3', 'dummy-telegram-chat-3', 'dummy-telegram-channel-3')

    # Get the channels, remove surrogate id column
    channels = node_provider_db.get_channels()
    channels = [(row[1], row[2], row[3], row[4]) for row in channels]

    # Check that the proper channels were inserted correctly
    assert ('test-dummy-principal-1', 'dummy-slack-channel-1', 'dummy-telegram-chat-1', 'dummy-telegram-channel-1') in channels
    assert ('test-dummy-principal-2', 'dummy-slack-channel-2', 'dummy-telegram-chat-2', 'dummy-telegram-channel-2') in channels
    assert ('test-dummy-principal-1', 'dummy-slack-channel-3', 'dummy-telegram-chat-3', 'dummy-telegram-channel-3') in channels

    channels = node_provider_db.get_channels_as_dict()
    assert channels['test-dummy-principal-1'] == \
        {'node_provider_id': 'test-dummy-principal-1', 'slack_channel_name': 'dummy-slack-channel-3', 
         'telegram_chat_id': 'dummy-telegram-chat-3', 'telegram_channel_id': 'dummy-telegram-channel-3'}
    assert channels['test-dummy-principal-2'] == \
        {'node_provider_id': 'test-dummy-principal-2', 'slack_channel_name': 'dummy-slack-channel-2', 
         'telegram_chat_id': 'dummy-telegram-chat-2', 'telegram_channel_id': 'dummy-telegram-channel-2'}

    # Delete channels. This deletes all channels for a given principal
    node_provider_db._delete_channel_lookup('test-dummy-principal-1')
    node_provider_db._delete_channel_lookup('test-dummy-principal-2')

    # Get the channels, remove surrogate id column
    channels = node_provider_db.get_channels()
    channels = [(row[1], row[2], row[3], row[4]) for row in channels]

    # Check that the channel lookups were deleted correctly
    assert ('test-dummy-principal-1', 'dummy-slack-channel-1', 'dummy-telegram-chat-1', 'dummy-telegram-channel-1') not in channels
    assert ('test-dummy-principal-2', 'dummy-slack-channel-2', 'dummy-telegram-chat-2', 'dummy-telegram-channel-2') not in channels
    assert ('test-dummy-principal-1', 'dummy-slack-channel-3', 'dummy-telegram-chat-3', 'dummy-telegram-channel-3') not in channels




##############################################
## TEST CRUD :: TABLE node_label_lookup

@pytest.mark.db
def test_node_label_lookup_crud():
    # Insert new node labels
    node_provider_db._insert_node_label('test-dummy-node-id-1', 'test-dummy-node-label-1')
    node_provider_db._insert_node_label('test-dummy-node-id-2', 'test-dummy-node-label-2')
    
    # Get the node labels, make sure they were inserted correctly
    node_labels = node_provider_db.get_node_labels()
    assert ('test-dummy-node-id-1', 'test-dummy-node-label-1') in node_labels
    assert ('test-dummy-node-id-2', 'test-dummy-node-label-2') in node_labels

    # Overwrite a node label
    node_provider_db._insert_node_label('test-dummy-node-id-2', 'test-dummy-node-label-b')

    # Get the new node labels, make sure the value was overwritten
    node_labels = node_provider_db.get_node_labels()
    assert ('test-dummy-node-id-2', 'test-dummy-node-label-b') in node_labels

    # Get the node labels as dict, make sure they were inserted correctly
    node_labels = node_provider_db.get_node_labels_as_dict()
    assert node_labels['test-dummy-node-id-1'] == 'test-dummy-node-label-1'
    assert node_labels['test-dummy-node-id-2'] == 'test-dummy-node-label-b'

    # Delete node labels
    node_provider_db._delete_node_label('test-dummy-node-id-1')
    node_provider_db._delete_node_label('test-dummy-node-id-2')

    # Get the node labels, make sure they were deleted correctly
    node_labels = node_provider_db.get_node_labels()
    assert ('test-dummy-node-id-1', 'test-dummy-node-label-1') not in node_labels
    assert ('test-dummy-node-id-2', 'test-dummy-node-label-b') not in node_labels

    # Get the node labels as dict, make sure they were deleted correctly
    node_labels = node_provider_db.get_node_labels_as_dict()
    assert 'test-dummy-node-id-1' not in node_labels
    assert 'test-dummy-node-id-2' not in node_labels
