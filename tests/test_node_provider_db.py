from devtools import debug

from node_monitor.node_provider_db import NodeProviderDB
import node_monitor.load_config as c



##############################################
## SETUP & TEST SETUP

node_provider_db = NodeProviderDB(
    c.DB_HOST, c.DB_NAME, c.DB_USERNAME, c.DB_PASSWORD, c.DB_PORT)

def test_get_public_schema_tables():
    all_public_tables = set(node_provider_db.get_public_schema_tables())
    necessary_tables = {'subscribers', 'email_lookup', 
                        'channel_lookup', 'node_label_lookup'}
    assert necessary_tables.issubset(all_public_tables)




##############################################
## TEST CRUD :: TABLE subscribers

def test_insert_and_get_and_delete_subscriber():
    ## Create new subscribers
    node_provider_db._insert_subscriber(
        'test-dummy-principal-1', 
        True, True, False, False, False)
    node_provider_db._insert_subscriber(
        'test-dummy-principal-2', 
        True, True, False, False, False)
    ## Overwrite existing subscriber
    node_provider_db._insert_subscriber(
        'test-dummy-principal-1',
        True, True, True, True, True)

    ## Get and check subscribers
    subs = node_provider_db.get_subscribers()
    # debug(subs)
    # TODO: This will break. Please update to not check by length.
    assert len(subs) == 2

    ## Delete subscribers
    node_provider_db._delete_subscriber('test-dummy-principal-1')
    node_provider_db._delete_subscriber('test-dummy-principal-2')

    ## Get and check subscribers
    subs = node_provider_db.get_subscribers()
    # TODO: This will break. Please update to not check by length.
    assert len(subs) == 0




##############################################
## TEST CRUD :: TABLE email_lookup

def test_insert_and_get_and_delete_email():
    # Insert new emails
    node_provider_db._insert_email('test-dummy-principal-1', 'email1@example.com')
    node_provider_db._insert_email('test-dummy-principal-2', 'email2@example.com')

    # Get and check emails
    emails = node_provider_db.get_emails()

    expected_values = [
        ('test-dummy-principal-1', 'email1@example.com'),
        ('test-dummy-principal-2', 'email2@example.com')
    ]

    # Check that the values match, ignoring the primary key
    for expected in expected_values:
        assert any(expected == item[1:] for item in emails)
    print(expected[1:])

    # Delete emails
    node_provider_db._delete_email('email1@example.com')
    node_provider_db._delete_email('email2@example.com')

    # Get and check emails again
    emails = node_provider_db.get_emails()

    # Check that the specific content is no longer present
    for expected in expected_values:
        assert not any(expected == item[1:] for item in emails)




##############################################
## TEST CRUD :: TABLE channel_lookup

def test_insert_and_get_and_delete_channel():
    dummy_channel_1 = (
        'test-dummy-principal-1', 
        'slack_channel_1', 
        'telegram_chat_1', 
        'telegram_channel_1'
    )

    dummy_channel_2 = (
        'test-dummy-principal-2', 
        'slack_channel_2', 
        'telegram_chat_2', 
        'telegram_channel_2'
    )

    dummy_channel_3 = (
        'test-dummy-principal-1', 
        'slack_channel_3', 
        'telegram_chat_3', 
        'telegram_channel_3'
    )


    # Insert new channels
    node_provider_db._insert_channel(*dummy_channel_1)
    node_provider_db._insert_channel(*dummy_channel_2)

    # Get and check channels
    channels = node_provider_db.get_channels()

    # Define the expected content for each channel
    expected_channels = [dummy_channel_1, dummy_channel_2]

    # Check that the expected content is in the channels
    for expected_channel in expected_channels:
        assert any(expected_channel == channel[1:] for channel in channels)

    # Overwrite existing channel
    node_provider_db._insert_channel(*dummy_channel_3)

    # Get the new set of channels
    channels = node_provider_db.get_channels()

    # Define the new expected content for each channel
    new_expected_channels = [dummy_channel_3, dummy_channel_2]

    # Check that the old value is not there
    assert not any ( dummy_channel_1 == channel[1:] for channel in channels)

    # Check that the overwritten value and old values are present
    for expected_channel in new_expected_channels:
        assert any(expected_channel == channel[1:] for channel in channels)

    # Delete channels
    node_provider_db._delete_channel_lookup('test-dummy-principal-1')
    node_provider_db._delete_channel_lookup('test-dummy-principal-2')

    # Get and check channels again
    channels = node_provider_db.get_channels()

    # Check that the specific content is no longer present
    for expected_channel in new_expected_channels:
        assert not any(expected_channel == channel[1:] for channel in channels)




##############################################
## TEST CRUD :: TABLE node_label_lookup

def test_insert_and_get_and_delete_node_label():
    raise NotImplementedError

