from typing import List, Dict, Any, Optional, Tuple
import psycopg2, psycopg2.extensions

Principal = str

class DictDB:
    """Class used to operate with a postgres database using dictionaries"""

    def __init__(self, host: str, db: str, port: str,
                 username: str,password: str) -> None:
        """Initialize database connection"""
        self.host = host
        self.db = db
        self.port = port
        self.username = username
        self.password = password
        # TODO: perhaps this isnt the right way to do this?
        self.conn: Optional[psycopg2.extensions.connection] = None


    def connect(self) -> None:
        """Connect to database"""
        self.conn = psycopg2.connect(
            host=self.host, database=self.db, port=self.port, 
            user=self.username, password=self.password)
        
    
    def disconnect(self) -> None:
        """Disconnect from database"""
        assert self.conn is not None # needed for mypy --strict
        self.conn.commit() # TODO: is this needed?
        self.conn = None


    def get_tables(self) -> List[str]:
        """List all the table names in the database"""
        assert self.conn is not None
        q = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """
        with self.conn.cursor() as cur:
            cur.execute(q)
            rows = cur.fetchall()
        return [row[0] for row in rows]
    

    def get_table_schema(self, table_name: str) -> List[Tuple[str, str]]:
        """Get the schema of a table by its name"""
        assert self.conn is not None
        q = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
        """
        with self.conn.cursor() as cur:
            cur.execute(q)
            rows = cur.fetchall()
        return rows




## Our schema
## This is a minimum schema. 
## Any schema that is a superset of this is valid.

tables = [
    'subscribers',
    'email_lookup',
    'slack_channel_lookup',
    'telegram_chat_lookup',
    'node_label_lookup'
]

table_subscribers = {
    'node_provider_id': 'TEXT PRIMARY KEY',
    'node_provider_name': 'TEXT',
    'notify_on_status_change': 'BOOLEAN', # do we want this?
    'notify_email': 'BOOLEAN',
    'notify_slack': 'BOOLEAN',
    'notify_telegram': 'BOOLEAN',
}

table_email_lookup = {
    'id': 'SERIAL PRIMARY KEY',
    'node_provider_id': 'TEXT',
    'email_address': 'TEXT'
}

table_slack_channel_lookup = {
    'id': 'SERIAL PRIMARY KEY',
    'node_provider_id': 'TEXT',
    'slack_channel_id': 'TEXT'
}

table_telegram_chat_lookup = {
    'id': 'SERIAL PRIMARY KEY',
    'node_provider_id': 'TEXT',
    'telegram_chat_id': 'TEXT'
}

table_node_label_lookup = {
    'node_id': 'TEXT PRIMARY KEY',
    'node_label': 'TEXT'
}



if __name__ == "__main__":
    import load_config as c
    from pprint import pprint
    db = DictDB(c.DB_HOST, c.DB_NAME, c.DB_PORT, c.DB_USERNAME, c.DB_PASSWORD)
    db.connect()
    pprint("---------------------------------")
    print("Tables:")
    pprint(db.get_tables())
    print("")
    print("Schema:")
    pprint(db.get_table_schema('email_lookup'))
    pprint("---------------------------------")
    db.disconnect()
