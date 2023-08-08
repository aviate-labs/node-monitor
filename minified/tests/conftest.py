import pytest
import node_monitor.ic_api as ic_api

def pytest_addoption(parser):
    parser.addoption(
        "--send_emails", 
        action="store_true", 
        default=False, 
        help="Send actual emails over the network to a test inbox"
    )

## Create mock data for testing
## Data was pulled from the ic-api using cURL and stored in json files.
## This is data only from nodes with aviate labs provider id
## TODO: Update this data set to reflect multiple node providers
mock = {
    "control":                ic_api.get_nodes_from_file("../tests/t0.json"),
    "one_node_down":          ic_api.get_nodes_from_file("../tests/t1.json"),
    "two_nodes_down":         ic_api.get_nodes_from_file("../tests/t2.json"),
    "one_node_change_subnet": ic_api.get_nodes_from_file("../tests/t3.json"),
    "one_node_removed":       ic_api.get_nodes_from_file("../tests/t4.json"),
}

# Do we want this implemented?
# https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary


