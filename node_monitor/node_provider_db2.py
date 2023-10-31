from typing import List, Dict, Any, Optional, Tuple
import psycopg2, psycopg2.extensions, psycopg2.pool
from psycopg2.extras import DictCursor

Principal = str


class NodeProviderDB():

    create_table_subscribers = """
        CREATE TABLE IF NOT EXISTS subscribers (
            node_provider_id VARCHAR(255) PRIMARY KEY,
            node_provider_name VARCHAR(255),
            notify_on_status_change BOOLEAN,
            notify_email BOOLEAN,
            notify_slack BOOLEAN,
            notify_telegram BOOLEAN
        )
        """

    create_table_email_lookup = """
        CREATE TABLE IF NOT EXISTS email_lookup (
            id SERIAL PRIMARY KEY,
            node_provider_id VARCHAR(255),
            email_address VARCHAR(255)
        )
    """

    create_table_slack_channel_lookup = """
        CREATE TABLE IF NOT EXISTS slack_channel_lookup (
            id SERIAL PRIMARY KEY,
            node_provider_id VARCHAR(255),
            slack_channel_id VARCHAR(255)
        )
    """

    create_table_telegram_chat_lookup = """
        CREATE TABLE IF NOT EXISTS telegram_chat_lookup (
            id SERIAL PRIMARY KEY,
            node_provider_id VARCHAR(255),
            telegram_chat_id VARCHAR(255)
        )
    """

    create_table_node_label_lookup = """
        CREATE TABLE IF NOT EXISTS node_label_lookup (
            node_id VARCHAR(255) PRIMARY KEY,
            node_label VARCHAR(255)
        )
    """

    def __init__(self, host: str, db: str, port: str,
                 username: str,password: str) -> None:
        # https://www.psycopg.org/docs/pool.html
        self.pool = psycopg2.pool.SimpleConnectionPool(
            1, 3, host=host, database=db, port=port,
            user=username, password=password)
        
            
    def _validate(self) -> None:
        raise NotImplementedError


    def get_subscribers(self) -> List[Tuple[Any, ...]]:
        conn = self.pool.getconn()
        # https://www.psycopg.org/docs/cursor.html
        cur = conn.cursor()
        cur.execute("SELECT * FROM subscribers")
        rows = cur.fetchall()
        cur.close()
        self.pool.putconn(conn)
        return rows


    def close(self):
        # We will probably never call this
        # https://stackoverflow.com/questions/47018695/psycopg2-close-connection-pool
        self.pool.closeall()




if __name__ == "__main__":
    import load_config as c
    from pprint import pprint
    db = NodeProviderDB(c.DB_HOST, c.DB_NAME, c.DB_PORT, c.DB_USERNAME, c.DB_PASSWORD)
    pprint("---------------------------------")
    result = db.get_subscribers()
    pprint(result)
