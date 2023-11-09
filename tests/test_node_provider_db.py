import pytest
from devtools import debug

from node_monitor.node_provider_db import NodeProviderDB
import node_monitor.ic_api as ic_api
from tests.conftest import cached
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
                        'channel_lookup', 'node_label_lookup', 
                        'node_provider_lookup'}
    assert necessary_tables.issubset(all_public_tables)

@pytest.mark.db
def test_validate_column_names():
    node_provider_db._validate_col_names('subscribers', NodeProviderDB.table_subscribers_cols)
    node_provider_db._validate_col_names('email_lookup', NodeProviderDB.table_email_lookup_cols)
    node_provider_db._validate_col_names('channel_lookup', NodeProviderDB.table_channel_lookup_cols)
    node_provider_db._validate_col_names('node_label_lookup', NodeProviderDB.table_node_label_lookup_cols)
    node_provider_db._validate_col_names('node_provider_lookup', NodeProviderDB.table_node_provider_lookup_cols)


##############################################
## TEST CRUD :: TABLE subscribers

@pytest.mark.db
def test_subscribers_crud():
    # Create new subscribers from test file
    node_provider_db.insert_multiple_subscribers(cached["node_provider_crud"].node_providers)
    
    # Note: 6th argument of _insert_subscriber is deprecated
    subs = node_provider_db.get_subscribers()
    assert ('test-dummy-principal-1', False, False, False, False, False, 'Node Provider A') in subs
    assert ('test-dummy-principal-2', False, False, False, False, False, 'Node Provider B') in subs

    # Overwrite the newly added subscribers
    node_provider_db._insert_subscriber('test-dummy-principal-1', True, True, False, False, False, 'test-dummy-node-provider-name-1')
    node_provider_db._insert_subscriber('test-dummy-principal-2', True, True, False, False, False, 'test-dummy-node-provider-name-2')

    # Get and check subscribers
    # Note: 6th argument of asssert statement is deprecated
    subs = node_provider_db.get_subscribers()
    assert ('test-dummy-principal-1', True, True, False, False, False, 'test-dummy-node-provider-name-1') in subs
    assert ('test-dummy-principal-2', True, True, False, False, False, 'test-dummy-node-provider-name-2') in subs

    # Get and check subscribers as dict
    # Note: notify_telegram_channel field in assert statement is deprecated
    subs = node_provider_db.get_subscribers_as_dict()
    assert subs['test-dummy-principal-1'] == \
        {'node_provider_id': 'test-dummy-principal-1', 'notify_on_status_change': True, 'notify_email': True,
         'notify_slack': False, 'notify_telegram_chat': False, 'notify_telegram_channel': False, 'node_provider_name': 'test-dummy-node-provider-name-1'}
    assert subs['test-dummy-principal-2'] == \
        {'node_provider_id': 'test-dummy-principal-2', 'notify_on_status_change': True, 'notify_email': True,
         'notify_slack': False, 'notify_telegram_chat': False, 'notify_telegram_channel': False, 'node_provider_name': 'test-dummy-node-provider-name-2'}

    # Delete subscribers
    node_provider_db._delete_subscriber('test-dummy-principal-1')
    node_provider_db._delete_subscriber('test-dummy-principal-2')

    # Get and check subscribers
    # Note: 6th argument of asssert statement is deprecated
    subs = node_provider_db.get_subscribers()
    assert ('test-dummy-principal-1', True, True, False, False, False, 'test-dummy-node-provider-name-1') not in subs
    assert ('test-dummy-principal-2', True, True, False, False, False, 'test-dummy-node-provider-name-2') not in subs

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
    # Note: last argument of _insert_channel() is deprecated
    node_provider_db._insert_channel(
        'test-dummy-principal-1', 'dummy-slack-channel-1', 'dummy-telegram-chat-1', 'dummy-telegram-channel-1')
    node_provider_db._insert_channel(
        'test-dummy-principal-2', 'dummy-slack-channel-2', 'dummy-telegram-chat-2', 'dummy-telegram-channel-2')
    node_provider_db._insert_channel(
        'test-dummy-principal-1', 'dummy-slack-channel-3', 'dummy-telegram-chat-3', 'dummy-telegram-channel-3')

    # Get the channels, remove surrogate id column
    # Note: row[4] is deprecated - telegram channel not used
    channels = node_provider_db.get_channels()
    channels = [(row[1], row[2], row[3], row[4]) for row in channels]

    # Check that the proper channels were inserted correctly
    # Note: last argument of assert statement is deprecated
    assert ('test-dummy-principal-1', 'dummy-slack-channel-1', 'dummy-telegram-chat-1', 'dummy-telegram-channel-1') in channels
    assert ('test-dummy-principal-2', 'dummy-slack-channel-2', 'dummy-telegram-chat-2', 'dummy-telegram-channel-2') in channels
    assert ('test-dummy-principal-1', 'dummy-slack-channel-3', 'dummy-telegram-chat-3', 'dummy-telegram-channel-3') in channels

    # Note: telegram_channel_id is deprecated
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
    # Note: row[4] is deprecated - telegram channel not used
    channels = node_provider_db.get_channels()
    channels = [(row[1], row[2], row[3], row[4]) for row in channels]

    # Check that the channel lookups were deleted correctly
    # Note: last argument of assert statement is deprecated
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


##############################################
# ## TEST CRUD :: TABLE node_provider_lookup

@pytest.mark.db
def test_node_provider_lookup_crud():
    # Insert new records
    node_provider_db.insert_multiple_node_providers(cached["node_provider_crud"].node_providers)

    # Get and check node provider lookup records
    node_providers = node_provider_db.get_node_providers()
    assert ('test-dummy-principal-1', 'Node Provider A') in node_providers
    assert ('test-dummy-principal-2', 'Node Provider B') in node_providers

    # Overwrite an existing node provider principal
    node_provider_db._insert_node_provider('test-dummy-principal-1', 'Node Provider C')

    # Get the new node provider records, make sure the value was overwritten
    node_providers = node_provider_db.get_node_providers()
    assert ('test-dummy-principal-1', 'Node Provider C') in node_providers

    # Get the node providers as dict, make sure they were inserted correctly
    node_providers = node_provider_db.get_node_providers_as_dict()
    assert node_providers['test-dummy-principal-1'] == 'Node Provider C'
    assert node_providers['test-dummy-principal-2'] == 'Node Provider B'

    # Delete node providers
    node_provider_db._delete_node_provider('test-dummy-principal-1')
    node_provider_db._delete_node_provider('test-dummy-principal-2')

    # Get and check node provider lookup records
    node_providers = node_provider_db.get_node_providers()
    assert ('test-dummy-principal-1', 'Node Provider C') not in node_providers
    assert ('test-dummy-principal-2', 'Node Provider B') not in node_providers

