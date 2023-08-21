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

    
    def insert_channel_detail(
        self,
        node_provider_principal: str,
        slack_channel_name: str,
        telegram_chat_id: str,
        telegram_channel_id: str
    ) -> None:

        insert_sql = '''
            INSERT INTO channel_detail (
                node_provider_principal,
                slack_channel_name,
                telegram_chat_id,
                telegram_channel_id
            ) VALUES (%s, %s, %s, %s)
        '''
        values = (
            node_provider_principal,
            slack_channel_name,
            telegram_chat_id,
            telegram_channel_id
        )

        with self.conn.cursor() as cur:
            try:
                cur.execute(insert_sql, values)
                self.conn.commit() 
            except psycopg2.Error as e:
                logging.error(f'Error occurred while inserting channel detail - {e}')
                self.conn.rollback()


    def insert_node(
        self,
        node_provider_principal: str,
        node_machine_id: str,
        node_machine_label: str
    ) -> None:

        insert_sql = '''
            INSERT INTO node (
                node_provider_principal, 
                node_machine_id, 
                node_machine_label
            ) VALUES (%s, %s, %s)
        '''
        values = (
            node_provider_principal,
            node_machine_id,
            node_machine_label
        )

        with self.conn.cursor() as cur:
            try:
                cur.execute(insert_sql, values)
                self.conn.commit()
            except psycopg2.Error as e:
                logging.error(f'Error occurred while inserting node - {e}')
                self.conn.rollback()

    
    def insert_email_recipient(
            self, 
            node_provider_principal: str, 
            email_address: str
        ) -> None:

        insert_sql = '''
            INSERT INTO email_recipient (node_provider_principal, email_address)
            VALUES (%s, %s)
        '''
        
        with self.conn.cursor() as cur:
            try:
                cur.execute(insert_sql, (node_provider_principal, email_address))
                self.conn.commit()
            except psycopg2.Error as e:
                logging.error(f'Error occurred while inserting email recipient - {e}')
                self.conn.rollback()


    def insert_preference(
        self,
        node_provider_principal: str,
        notify_on_status_change: bool,
        notify_email: bool,
        notify_slack: bool,
        notify_telegram_chat: bool,
        notify_telegram_channel: bool
    ) -> None:

        insert_sql = '''
            INSERT INTO preference (
                node_provider_principal, 
                notify_on_status_change, 
                notify_email, 
                notify_slack, 
                notify_telegram_chat, 
                notify_telegram_channel
            ) VALUES (%s, %s, %s, %s, %s, %s)
        '''
        values = (
            node_provider_principal,
            notify_on_status_change,
            notify_email,
            notify_slack,
            notify_telegram_chat,
            notify_telegram_channel
        )

        with self.conn.cursor() as cur:
            try:
                cur.execute(insert_sql, values)
                self.conn.commit()
            except psycopg2.Error as e:
                logging.error(f'Error occurred while inserting preference - {e}')
            self.conn.rollback()


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
