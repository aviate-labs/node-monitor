from typing import List, Dict, Any
import csv
import psycopg2
import logging


# with open('./tmp_prod_db.json') as f:
#     tmp_db: Dict[Any, Any] = json.load(f)
# # channel_detail
# # email_recipient
# # preferences
# # node_labels

Principal = str

class NodeProviderDB:
    def __init__(
            self, 
            host: str, 
            db: str, 
            username: str, 
            password: str, 
            port: str
        ) -> None:
        
        self.host = host
        self.db = db
        self.username = username
        self.password = password
        self.port = port

        self._create_tables()

    def setup_conn(self) -> None:
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.db,
            user=self.username,
            password=self.password,
            port=self.port
        )

    def teardown_conn(self) -> None:
        self.conn.commit()
        self.conn.close()
    
    def _create_tables(self) -> None:
        self.setup_conn()

        create_channel_detail = '''
            CREATE TABLE IF NOT EXISTS channel_detail (
                channel_detail_id SERIAL PRIMARY KEY,
                node_provider_principal TEXT UNIQUE,
                slack_channel_name TEXT,
                telegram_chat_id TEXT,
                telegram_channel_id TEXT
            );
        '''

        create_email_recipient_table='''
            CREATE TABLE IF NOT EXISTS email_recipient (
                email_recipient_id SERIAL PRIMARY KEY,
                node_provider_principal TEXT,
                email_address TEXT UNIQUE
            );
        '''

        create_preference_table = '''
            CREATE TABLE IF NOT EXISTS preference (
                preference_id SERIAL PRIMARY KEY,
                node_provider_principal TEXT UNIQUE,
                notify_on_status_change BOOLEAN,
                notify_email BOOLEAN,
                notify_slack BOOLEAN,
                notify_telegram_chat BOOLEAN,
                notify_telegram_channel BOOLEAN
            );
        '''
        create_node_table = '''
            CREATE TABLE IF NOT EXISTS node (
                node_id SERIAL PRIMARY KEY,
                node_provider_principal TEXT,
                node_machine_id TEXT UNIQUE,
                node_machine_label TEXT UNIQUE
            );
        '''

        with self.conn.cursor() as cur:
            cur.execute(create_channel_detail)
            cur.execute(create_email_recipient_table)
            cur.execute(create_preference_table)
            cur.execute(create_node_table)

        self.teardown_conn()





    # def get_email_recipients(self, node_provider: Principal) -> List[str]:
    #     emails: List[str] = [
    #         entry['email_address'] 
    #         for entry in tmp_db['email_recipient']
    #         if entry['node_provider_principal'] == node_provider]
    #     return emails


    # def get_subscribers(self) -> List[Principal]:
    #     subs = [entry["node_provider_principal"] 
    #             for entry in tmp_db['preference']]
    #     return subs
    
    # def get_preferences(self) -> Dict[Principal, Dict[str, bool]]:
    #     prefs: Dict[Principal, Dict[str, bool]] = {
    #         entry['node_provider_principal']: entry
    #         for entry in tmp_db['preference']}
    #     return prefs
    
    # def get_node_labels(self) -> Dict[Principal, str]:
    #     labels: Dict[Principal, str] = tmp_db['node_labels']
    #     return labels


if __name__ == '__main__':
    pass
