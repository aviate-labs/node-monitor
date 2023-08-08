from typing import List, Dict, Any
import json


# TODO: Replace this with a proper SQLite database

with open('tmp_prod_db.json') as f:
    tmp_db: Dict[Any, Any] = json.load(f)
# channel_detail
# email_recipient
# preferences
# node_labels

Principal = str

class NodeProviderDB:

    def __init__(self) -> None:
        pass

    def get_email_recipients(self, node_provider: Principal) -> List[str]:
        emails: List[str] = [
            entry['email_address'] 
            for entry in tmp_db['email_recipient']
            if entry['node_provider_id'] == node_provider]
        return emails


    def get_subscribers(self) -> List[Principal]:
        subs = [entry["node_provider_id"] for entry in tmp_db['preferences']]
        return subs
    
    def get_preferences(self) -> Dict[Principal, Dict[str, bool]]:
        prefs: Dict[Principal, Dict[str, bool]] = {
            entry['node_provider_id']: entry
            for entry in tmp_db['preferences']}
        return prefs
    
    def get_node_lables(self) -> Dict[Principal, str]:
        labels: Dict[Principal, str] = tmp_db['node_labels']
        return labels


if __name__ == '__main__':
    pass
