from typing import Dict, List, Any
from node_monitor.ic_api import NodeProvider

Principal = str

def get_new_node_providers(
    node_providers_api_dict: Dict[Principal, str],
    node_providers_db: Dict[Principal, Dict[str, Any]],
) -> List[NodeProvider]:
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
