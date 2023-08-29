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
def test_insert_and_get_and_delete_subscriber():
    # Create new subscribers / overwrite subscriber 1
    node_provider_db._insert_subscriber(
        'test-dummy-principal-1', 
        True, True, False, False, False)
    node_provider_db._insert_subscriber(
        'test-dummy-principal-2', 
        True, True, False, False, False)
    node_provider_db._insert_subscriber(
        'test-dummy-principal-1',
        True, True, True, True, True)

    # Get and check subscribers
    subs = node_provider_db.get_subscribers()

    assert ('test-dummy-principal-1', True, True, True, True, True) in subs
    assert ('test-dummy-principal-2', True, True, False, False, False) in subs


    # Delete subscribers
    node_provider_db._delete_subscriber('test-dummy-principal-1')
    node_provider_db._delete_subscriber('test-dummy-principal-2')

    # Get and check subscribers
    subs = node_provider_db.get_subscribers()
    assert ('test-dummy-principal-1', True, True, True, True, True) not in subs
    assert ('test-dummy-principal-2', True, True, False, False, False) not in subs




##############################################
## TEST CRUD :: TABLE email_lookup

@pytest.mark.db
def test_insert_and_get_and_delete_email():
    # Insert new emails, including multiple for the same principal
    node_provider_db._insert_email('test-dummy-principal-1', 'foo@mail.com')
    node_provider_db._insert_email('test-dummy-principal-1', 'bar@mail.com')
    node_provider_db._insert_email('test-dummy-principal-2', 'baz@mail.com')

    # Get the emails, remove surrogate id column
    emails = node_provider_db.get_emails()
    emails = [(row[1], row[2]) for row in emails]

    # Check that the emails were inserted correctly
    assert ('test-dummy-principal-1', 'foo@mail.com') in emails
    assert ('test-dummy-principal-1', 'bar@mail.com') in emails
    assert ('test-dummy-principal-2', 'baz@mail.com') in emails

    # Delete emails
    node_provider_db._delete_email('foo@mail.com')
    node_provider_db._delete_email('bar@mail.com')
    node_provider_db._delete_email('baz@mail.com')

    # Get the emails again, remove surrogate id column
    emails = node_provider_db.get_emails()
    emails = [(row[1], row[2]) for row in emails]

    # Check that the emails were deleted correctly
    assert ('test-dummy-principal-1', 'foo@mail.com') not in emails
    assert ('test-dummy-principal-1', 'bar@mail.com') not in emails
    assert ('test-dummy-principal-2', 'baz@mail.com') not in emails




##############################################
## TEST CRUD :: TABLE channel_lookup

@pytest.mark.db
def test_insert_and_get_and_delete_channel():
    # Insert new channels
    node_provider_db._insert_channel(
        'test-dummy-principal-1',
        'slack_channel_1',
        'telegram_chat_1',
        'telegram_channel_1'
    )
    node_provider_db._insert_channel(
        'test-dummy-principal-2',
        'slack_channel_2',
        'telegram_chat_2',
        'telegram_channel_2'
    )
    node_provider_db._insert_channel(
        'test-dummy-principal-1',
        'slack_channel_3',
        'telegram_chat_3',
        'telegram_channel_3'
    )

    # Get the channels, remove surrogate
    channels = node_provider_db.get_channels()
    channels = [(row[1], row[2], row[3], row[4]) for row in channels]


    # Check for specific content in the channels
    assert (
        'test-dummy-principal-1', 
        'slack_channel_1', 
        'telegram_chat_1', 
        'telegram_channel_1'
    ) in channels
    assert (
        'test-dummy-principal-2', 
        'slack_channel_2', 
        'telegram_chat_2', 
        'telegram_channel_2'
    ) in channels
    assert (
        'test-dummy-principal-1', 
        'slack_channel_3', 
        'telegram_chat_3', 
        'telegram_channel_3'
    ) in channels

    # Delete channels
    node_provider_db._delete_channel_lookup('test-dummy-principal-1')
    node_provider_db._delete_channel_lookup('test-dummy-principal-2')

    # Get the channels, remove surrogate
    channels = node_provider_db.get_channels()
    channels = [(row[1], row[2], row[3], row[4]) for row in channels]

    # Check that the specific content is no longer present
    assert (
        'test-dummy-principal-1', 
        'slack_channel_3', 
        'telegram_chat_3', 
        'telegram_channel_3'
    ) not in channels
    assert ( 
        'test-dummy-principal-2', 
        'slack_channel_2', 
        'telegram_chat_2', 
        'telegram_channel_2'
    ) not in channels





##############################################
## TEST CRUD :: TABLE node_label_lookup

@pytest.mark.db
def test_insert_and_get_and_delete_node_label():
    # Insert new node labels
    node_provider_db._insert_node_label('test-dummy-node-id-1', 'test-dummy-node-label-1')
    node_provider_db._insert_node_label('test-dummy-node-id-2', 'test-dummy-node-label-2')
    
    # Get the node labels
    node_labels = node_provider_db.get_node_labels()

    # Check for specific content in the node labels
    assert ('test-dummy-node-id-1', 'test-dummy-node-label-1') in node_labels
    assert ('test-dummy-node-id-2', 'test-dummy-node-label-2') in node_labels

    # Overwrite a record
    node_provider_db._insert_node_label('test-dummy-node-id-2', 'test-dummy-node-label-b')

    # Get the new node labels
    node_labels = node_provider_db.get_node_labels()

    assert ('test-dummy-node-id-2', 'test-dummy-node-label-b') in node_labels

    # Delete node labels
    node_provider_db._delete_node_label('test-dummy-node-id-1')
    node_provider_db._delete_node_label('test-dummy-node-id-2')

    # Get the node labels again
    node_labels = node_provider_db.get_node_labels()

    # Check that the specific content is no longer present
    assert ('test-dummy-node-id-1', 'test-dummy-node-label-1') not in node_labels
    assert ('test-dummy-node-id-2', 'test-dummy-node-label-b') not in node_labels


