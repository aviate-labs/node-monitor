import pytest
import node_monitor.ic_api as ic_api


# Pydantic will return a ValidationError if an expected field is missing
# or if a field's value is of the wrong type.

def test_get_nodes():
    nodes = ic_api.get_nodes()
    assert len(nodes.nodes) > 0

def test_get_nodes_from_file():
    nodes = ic_api.get_nodes_from_file("../tests/t0.json")
    assert len(nodes.nodes) > 0
