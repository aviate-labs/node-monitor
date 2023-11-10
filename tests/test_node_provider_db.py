import pytest
from devtools import debug

from node_monitor.node_provider_db import NodeProviderDB
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
    new_node_providers = cached["new_node_providers"]  
    query = """
        INSERT INTO subscribers (
            node_provider_id,
            notify_on_status_change,
            notify_email,
            notify_slack,
            node_provider_name,
            notify_telegram
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (node_provider_id) DO UPDATE SET
            notify_on_status_change = EXCLUDED.notify_on_status_change,
            notify_email = EXCLUDED.notify_email,
            notify_slack = EXCLUDED.notify_slack,
            node_provider_name = EXCLUDED.node_provider_name,
            notify_telegram = EXCLUDED.notify_telegram
    """
    for node_provider in new_node_providers.node_providers:
        params = (node_provider.principal_id, False, False, 
                    False, node_provider.display_name, False)
        node_provider_db.execute_insert(query, params)

    subs = node_provider_db.get_subscribers_as_dict()
    assert subs['test-dummy-principal-1'] == \
        {'node_provider_id': 'test-dummy-principal-1', 'notify_on_status_change': False, 'notify_email': False,
         'notify_slack': False, 'node_provider_name': 'Node Provider A', 'notify_telegram': False,}
    assert subs['test-dummy-principal-2'] == \
        {'node_provider_id': 'test-dummy-principal-2', 'notify_on_status_change': False, 'notify_email': False,
         'notify_slack': False, 'node_provider_name': 'Node Provider B', 'notify_telegram': False,}
    
    params = ('test-dummy-principal-1', False, False, 
              False, 'Node Provider C', False)
    node_provider_db.execute_insert(query, params)
    subs = node_provider_db.get_subscribers_as_dict()
    assert subs['test-dummy-principal-1'] == \
        {'node_provider_id': 'test-dummy-principal-1', 'notify_on_status_change': False, 'notify_email': False,
         'notify_slack': False, 'node_provider_name': 'Node Provider C', 'notify_telegram': False,}
    
    delete_query = """
        DELETE FROM subscribers
        WHERE node_provider_id = %s
    """
    # Delete subscribers
    node_provider_db.execute_insert(delete_query, ('test-dummy-principal-1',))
    node_provider_db.execute_insert(delete_query, ('test-dummy-principal-2',))
    subs = node_provider_db.get_subscribers_as_dict()
    assert 'test-dummy-principal-1' not in subs
    assert 'test-dummy-principal-2' not in subs

    
