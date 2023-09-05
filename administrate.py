#!/usr/bin/env python3
import code
from devtools import debug

import node_monitor.load_config as c
from node_monitor.node_provider_db import NodeProviderDB


db = NodeProviderDB(
    c.DB_HOST, c.DB_NAME, c.DB_USERNAME, c.DB_PASSWORD, c.DB_PORT)


debug(dir(db))
code.interact(local=locals())


# Examples:
# > debug(db.get_subscribers())
# > debug(db.insert_subscriber.__annotations__)
# > db.insert_subscriber("test", "test", "test", "test")
