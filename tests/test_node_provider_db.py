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
    from devtools import debug
    debug(expected_schema)
    debug(actual_schema)
    assert expected_schema == actual_schema
