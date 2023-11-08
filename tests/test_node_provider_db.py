import pytest
from devtools import debug

from node_monitor.node_provider_db import NodeProviderDB
import node_monitor.load_config as c



##############################################
## SETUP & TEST SETUP

# We're breaking the PEP8 line length limit here on purpose, it makes the
# database operations and assert statements more readable.


@pytest.mark.db 
def test_validate_schema():
    node_provider_db = NodeProviderDB(
        c.DB_HOST, c.DB_NAME, c.DB_PORT,
        c.DB_USERNAME, c.DB_PASSWORD)
    result = node_provider_db._validate_schema()
    assert result is True
