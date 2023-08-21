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
    raise NotImplementedError




##############################################
## TEST CRUD :: TABLE channel_lookup

def test_insert_and_get_and_delete_channel():
    raise NotImplementedError




##############################################
## TEST CRUD :: TABLE node_label_lookup

def test_insert_and_get_and_delete_node_label():
    raise NotImplementedError

