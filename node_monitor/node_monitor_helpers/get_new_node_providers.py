from typing import Dict, List, Any
from node_monitor.ic_api import NodeProvider

Principal = str

def get_new_node_providers(
    node_providers_api_dict: Dict[Principal, str],
    node_providers_db: Dict[Principal, Dict[str, Any]],
) -> List[NodeProvider]:
    """
    Identify new node providers by comparing a dictionary of node providers from
    the API with those already present in the database.

    Parameters
    ----------
    node_providers_api_dict : Dict[Principal, str]
    A dictionary where keys are the principal IDs of node providers from the
    API, and values are their display names.

    node_providers_db : Dict[Principal, Dict[str, Any]]
    A dictionary representing node providers already present in the database.
    Keys are principal IDs, and values are dictionaries containing information
    about the node provider.

    Returns
    -------
    List[NodeProvider]
    A list of new NodeProvider objects found in the API but not in the database.
    Each NodeProvider object includes a display name and principal ID.

    Raises
    ------
    None
    """
    principals_api = set(node_providers_api_dict.keys())
    principals_db = set(node_providers_db.keys())
    principals_new = principals_api - principals_db

    node_providers_new = [
        NodeProvider(
            display_name=node_providers_api_dict[principal_id],
            principal_id=principal_id
        ) for principal_id in principals_new
    ]

    return node_providers_new
