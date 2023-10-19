import pytest

import node_monitor.ic_api as ic_api
import node_monitor.node_monitor_helpers.messages as messages

## Create a fake node model
fakenode = ic_api.Node(
    dc_id = 'fake_dc_id',
    dc_name = 'fake_dc_name',
    node_id = 'fake_node_id',
    node_operator_id = 'fake_node_operator_id',
    node_provider_id = 'fake_node_provider_id',
    node_provider_name = 'fake_node_provider_name',
    owner = 'fake_owner',
    region = 'fake_region',
    status = 'fake_status',
    subnet_id = 'fake_subnet_id')
fakelabel = {'fake_node_id': 'fake_label'}


def test_detailnodes():

    # Test empty list returns an empty string
    assert messages.detailnodes([], {}) == ""

    # Test fake node returns correct string
    result = messages.detailnodes([fakenode], fakelabel)
    assert len(result) > 20 # greater than 20 characters
    assert result.startswith("Data Center: FAKE_DC_ID")
