import pytest
from devtools import debug

from node_monitor.node_provider_db import NodeProviderDB
from node_monitor.node_monitor_helpers.sql_constants import \
    DELETE_SUBSCRIBER, INSERT_SUBSCRIBER
from tests.conftest import cached
import node_monitor.load_config as c



##############################################
## SETUP & TEST SETUP


# We have to create this global var this as None, then assign its value in a
# marked test, because the NodeProviderDB.__init__() instantiates a 
# connection pool and will fail if we try and instantiate it with fake
# credentials.
node_provider_db = None

@pytest.mark.db
def test_init_node_provider_db():
    global node_provider_db
    node_provider_db = NodeProviderDB(
        c.DB_HOST, c.DB_NAME, c.DB_PORT,
        c.DB_USERNAME, c.DB_PASSWORD)


# In these fns we're testing a minimum schema. This means that these
# tests will pass as long as the schema contains the minimum required typed
# columns, but it may also contain additional columns.

@pytest.mark.db 
def test_validate_subscribers_schema():
    expected_schema = NodeProviderDB.schema_table_subscribers
    actual_schema = node_provider_db._get_schema('subscribers')
    assert set(expected_schema.items()) <= set(actual_schema.items())


@pytest.mark.db
def test_validate_schema_email_lookup():
    expected_schema = NodeProviderDB.schema_table_email_lookup
    actual_schema = node_provider_db._get_schema('email_lookup')
    assert set(expected_schema.items()) <= set(actual_schema.items())


@pytest.mark.db
def test_validate_schema_slack_channel_lookup():
    expected_schema = NodeProviderDB.schema_table_slack_channel_lookup
    actual_schema = node_provider_db._get_schema('slack_channel_lookup')
    assert set(expected_schema.items()) <= set(actual_schema.items())


@pytest.mark.db
def test_validate_schema_telegram_chat_lookup():
    expected_schema = NodeProviderDB.schema_table_telegram_chat_lookup
    actual_schema = node_provider_db._get_schema('telegram_chat_lookup')
    assert set(expected_schema.items()) <= set(actual_schema.items())


@pytest.mark.db
def test_validate_schema_node_label_lookup():
    expected_schema = NodeProviderDB.schema_table_node_label_lookup
    actual_schema = node_provider_db._get_schema('node_label_lookup')
    assert set(expected_schema.items()) <= set(actual_schema.items())
    

@pytest.mark.db
def test_insert_subscriber_crud():

    # Insert new node providers
    new_node_providers = cached["new_node_providers"]  
    for node_provider in new_node_providers.node_providers:
        params = (node_provider.principal_id, False, False, 
                    False, node_provider.display_name, False)
        node_provider_db.execute_write(INSERT_SUBSCRIBER, params)

    # Check new node providers were added properly
    subs = node_provider_db.get_subscribers_as_dict()
    assert subs['test-dummy-principal-1'] == \
        {'node_provider_id': 'test-dummy-principal-1', 'notify_on_status_change': False, 'notify_email': False,
         'notify_slack': False, 'node_provider_name': 'Node Provider A', 'notify_telegram': False,}
    assert subs['test-dummy-principal-2'] == \
        {'node_provider_id': 'test-dummy-principal-2', 'notify_on_status_change': False, 'notify_email': False,
         'notify_slack': False, 'node_provider_name': 'Node Provider B', 'notify_telegram': False,}
    
    # Check overwriting existing records occurs properly 
    params = ('test-dummy-principal-1', False, False, 
              False, 'Node Provider C', False)
    node_provider_db.execute_write(INSERT_SUBSCRIBER, params)
    subs = node_provider_db.get_subscribers_as_dict()
    assert subs['test-dummy-principal-1'] == \
        {'node_provider_id': 'test-dummy-principal-1', 'notify_on_status_change': False, 'notify_email': False,
         'notify_slack': False, 'node_provider_name': 'Node Provider C', 'notify_telegram': False,}
    
    # Delete subscribers
    node_provider_db.execute_write(DELETE_SUBSCRIBER, ('test-dummy-principal-1',))
    node_provider_db.execute_write(DELETE_SUBSCRIBER, ('test-dummy-principal-2',))
    subs = node_provider_db.get_subscribers_as_dict()
    assert 'test-dummy-principal-1' not in subs
    assert 'test-dummy-principal-2' not in subs

    
