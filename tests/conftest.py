import pytest
import node_monitor.ic_api as ic_api


## Options usage:
##   -s is to print to stdout
##   --send_emails is a custom flag to send live emails
##   --send_slack is a custom flag to send live slack messages
##   --db is a custom flag to test CRUD operations on the database
## example: pytest -s --send_emails tests/test_bot_email.py
## example: pytest -s --send_slack tests/test_bot_slack.py
## example: pytest -s --db tests/test_node_provider_db.py



def pytest_addoption(parser):
    parser.addoption(
        "--send_emails",
        action="store_true",
        default=False,
        help="send actual emails over the network to a test inbox")
    parser.addoption(
        "--send_slack",
        action="store_true",
        default=False,
        help="send actual slack messages via webclient to test slack channel")
    parser.addoption(
        "--db",
        action="store_true",
        default=False,
        help="test CRUD operations on the database")

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "live_email: test sends a live email over the network")
    config.addinivalue_line(
        "markers", "live_slack: test sends a live slack message over the network")
    config.addinivalue_line(
        "markers", "db: test CRUD operations on the database")


def pytest_collection_modifyitems(config, items):
    # if the --db flag is not given in cli: skip db tests
    # if the --send_emails flag is not given in cli: skip live_email tests
    # if the --send_slack flag is not given in cli: skip live_slack tests
    if not config.getoption("--db"):
        skip_db = pytest.mark.skip(reason="need --db option to run")
        for item in items:
            if "db" in item.keywords:
                item.add_marker(skip_db)
    if not config.getoption("--send_emails"):
        skip_live_email = pytest.mark.skip(reason="need --send_emails option to run")
        for item in items:
            if "live_email" in item.keywords:
                item.add_marker(skip_live_email)
    if not config.getoption("--send_slack"):
        skip_live_slack = pytest.mark.skip(reason="need --send_slack option to run")
        for item in items:
            if "live_slack" in item.keywords:
                item.add_marker(skip_live_slack)



## Create mock data for testing
## Data was pulled from the ic-api using cURL and stored in json files.
## This is data only from nodes with aviate labs provider id
## TODO: Update this data set to reflect multiple node providers
cached = {
    "control":                ic_api.get_nodes_from_file("data/t0.json"),
    "one_node_down":          ic_api.get_nodes_from_file("data/t1.json"),
    "two_nodes_down":         ic_api.get_nodes_from_file("data/t2.json"),
    "one_node_change_subnet": ic_api.get_nodes_from_file("data/t3.json"),
    "one_node_removed":       ic_api.get_nodes_from_file("data/t4.json"),
}

# Do we want this implemented?
# https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary


