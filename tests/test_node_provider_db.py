import pytest
from devtools import debug

from node_monitor.node_provider_db import NodeProviderDB
import node_monitor.load_config as c



##############################################
## SETUP & TEST SETUP

# We're breaking the PEP8 line length limit here on purpose, it makes the
# database operations and assert statements more readable.



node_provider_db = NodeProviderDB(
        c.DB_HOST, c.DB_NAME, c.DB_PORT,
        c.DB_USERNAME, c.DB_PASSWORD)


@pytest.mark.db 
def test_validate_subscribers_schema():
    expected_schema = NodeProviderDB.schema_table_subscribers
    actual_schema = node_provider_db._get_schema('subscribers')
    assert expected_schema == actual_schema


@pytest.mark.db
def test_validate_schema_email_lookup():
    expected_schema = NodeProviderDB.schema_table_email_lookup
    actual_schema = node_provider_db._get_schema('email_lookup')
    assert expected_schema == actual_schema


@pytest.mark.db
def test_validate_schema_slack_channel_lookup():
    expected_schema = NodeProviderDB.schema_table_slack_channel_lookup
    actual_schema = node_provider_db._get_schema('slack_channel_lookup')
    assert expected_schema == actual_schema


@pytest.mark.db
def test_validate_schema_telegram_chat_lookup():
    expected_schema = NodeProviderDB.schema_table_telegram_chat_lookup
    actual_schema = node_provider_db._get_schema('telegram_chat_lookup')
    assert expected_schema == actual_schema


@pytest.mark.db
def test_validate_schema_node_label_lookup():
    expected_schema = NodeProviderDB.schema_table_node_label_lookup
    actual_schema = node_provider_db._get_schema('node_label_lookup')
    assert expected_schema == actual_schema
