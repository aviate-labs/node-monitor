import json
import requests
from typing import List, Optional
import pydantic
from pydantic import BaseModel


##############################################
## Prelim
assert pydantic.__version__.startswith("2.")
nodes_endpoint = "https://ic-api.internetcomputer.org/api/v3/nodes"



##############################################
## Pydancic Models

# If the API starts returning extra fields that aren't in the model,
# those fields will be ignored and won't cause an error. However, if an
# expected field is missing or if a field's value is of the wrong type,
# then Pydantic raises a ValidationError.

Principal = str

class Node(BaseModel):
    dc_id: str
    dc_name: str
    node_id: Principal
    node_operator_id: Principal
    node_provider_id: Principal
    node_provider_name: str
    owner: str
    region: str
    status: str
    subnet_id: Optional[Principal]

class Nodes(BaseModel):
    nodes: List[Node]



##############################################
## API Fetch Functions

def get_nodes(provider_id: Optional[Principal] = None) -> Nodes:
    """slurps nodes from the dfinity api, optional node_provider_id"""
    payload = {"node_provider_id": provider_id} if provider_id else None
    response = requests.get(nodes_endpoint, params=payload)
    return Nodes(**response.json())

def get_nodes_from_file(file_path: str) -> Nodes:
    """slurps nodes from a json file previously retrieved with curl"""
    with open(file_path) as f:
        j = json.load(f)
    return Nodes(**j)




##############################################
## Development

if __name__ == "__main__":
    from devtools import debug
    debug(get_nodes())
    debug(get_nodes_from_file("tests/t0.json"))
