from typing import List, Dict, Any, Optional, Tuple
import psycopg2, psycopg2.extensions
from toolz import groupby # type: ignore


Principal = str

class NodeProviderDB:
    """
    This class is used to interact with the database that stores node-provider
    configurations.

    This database contains 4 tables:
    1. subscribers:
        Main table for keeping track of which node providers are subscribed to
        notifications, and their notification preferences.
    2. email_lookup:
        Table for keeping track of which email addresses are associated with
        which node providers.
    3. channel_lookup:
        Table for keeping track of which slack channels and telegram chats
        are associated with which node providers.
    4. node_label_lookup:
        Table for keeping track of which custom node labels are associated with 
        which node_id (individual node machine principals).
    """

    # TABLE subscribers
    # Subscribers are identified by their unique node_provider_id, so we use 
    # that as the primary key. 'node_provider_id' is the name of the
    # principal of the node provider, consistent with the ic-api.
    create_table_subscribers = """
        CREATE TABLE IF NOT EXISTS subscribers (
            node_provider_id TEXT PRIMARY KEY ,
            notify_on_status_change BOOLEAN,
            notify_email BOOLEAN,
            notify_slack BOOLEAN,
            notify_telegram_chat BOOLEAN,
            notify_telegram_channel BOOLEAN
        );
    """

    # TABLE email_lookup
    # A node provider can have multiple unique email addresses.
    create_table_email_lookup = """
        CREATE TABLE IF NOT EXISTS email_lookup (
            id SERIAL PRIMARY KEY,
            node_provider_id TEXT,
            email_address TEXT
        );
    """

    # TABLE channel_lookup
    create_table_channel_lookup = """
        CREATE TABLE IF NOT EXISTS channel_lookup (
            id SERIAL PRIMARY KEY,
            node_provider_id TEXT,
            slack_channel_name TEXT,
            telegram_chat_id TEXT,
            telegram_channel_id TEXT
        );
    """

    # TABLE node_label_lookup
    # 'node-id' is the name of the principal of the node, 
    # consistent with the ic-api.
    create_table_node_label_lookup = """
        CREATE TABLE IF NOT EXISTS node_label_lookup (
            node_id TEXT PRIMARY KEY,
            node_label TEXT
        );
    """



    ##############################################
    ## Init and Connect

    def __init__(self, host: str, db: str, username: str, 
            password: str, port: str) -> None:
        """Initializes the database object. Automatically creates the tables
        if they don't already exist."""
        self.host = host
        self.db = db
        self.username = username
        self.password = password
        self.port = port
        self.conn: Optional[psycopg2.extensions.connection] = None
        self._create_tables()


    def connect(self) -> None:
        """Connects to the database."""
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.db,
            user=self.username,
            password=self.password,
            port=self.port)


    def disconnect(self) -> None:
        """Commits and closes the connection to the database."""
        assert self.conn is not None   # needed for mypy --strict
        self.conn.commit()
        self.conn.close()
        self.conn = None
    

    def _create_tables(self) -> None:
        """Automatically creates the tables if they don't already exist."""
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(self.create_table_subscribers)
            cur.execute(self.create_table_email_lookup)
            cur.execute(self.create_table_channel_lookup)
            cur.execute(self.create_table_node_label_lookup)
        self.disconnect()
    

    def _validate_col_names(self, table_name: str, cols: List[str]) -> None:
        """Validates that the actual column names in the table match the 
        expected column names defined in the program. Useful for testing."""
        # TODO: Move this to a separate test file
        query = f"SELECT * FROM {table_name}"
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query)
            assert cur.description is not None
            column_names = [desc[0] for desc in cur.description]
        self.disconnect()
        assert column_names == cols, "Column names do not match expected names."



    def get_public_schema_tables(self) -> List[str]:
        """Returns a list of all tables in the public schema. 
        Useful for testing."""
        select_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(select_query)
            rows = cur.fetchall()
        self.disconnect()
        return [row[0] for row in rows]
    



    ##############################################
    ## CRUD :: TABLE subscribers

    def _insert_subscriber(
            self, node_provider_id: Principal, notify_on_status_change: bool, 
            notify_email: bool, notify_slack: bool, notify_telegram_chat: bool,
            notify_telegram_channel: bool) -> None:
        """Inserts a subscriber into the subscribers table. Overwrites if
        subscriber already exists."""
        query = """
            INSERT INTO subscribers (
                node_provider_id,
                notify_on_status_change,
                notify_email,
                notify_slack,
                notify_telegram_chat,
                notify_telegram_channel
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (node_provider_id) DO UPDATE SET
                notify_on_status_change = EXCLUDED.notify_on_status_change,
                notify_email = EXCLUDED.notify_email,
                notify_slack = EXCLUDED.notify_slack,
                notify_telegram_chat = EXCLUDED.notify_telegram_chat,
                notify_telegram_channel = EXCLUDED.notify_telegram_channel
        """
        values = (
            node_provider_id,
            notify_on_status_change,
            notify_email,
            notify_slack,
            notify_telegram_chat,
            notify_telegram_channel
        )
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query, values)
        self.disconnect()

    
    def _delete_subscriber(self, node_provider_id: Principal) -> None:
        """Deletes a subscriber from the subscribers table."""
        query = """
            DELETE FROM subscribers
            WHERE node_provider_id = %s
        """
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query, (node_provider_id,))
        self.disconnect()


    def get_subscribers(self) -> List[Tuple[Any, ...]]: 
        """Returns the table of all subscribers."""
        query = "SELECT * FROM subscribers"
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        self.disconnect()
        return rows
    

    def get_subscribers_as_dict(self) -> Dict[Principal, Dict[str, bool]]:
        """Returns the table of all subscribers as a dictionary."""
        cols = \
            ['node_provider_id', 'notify_on_status_change', 'notify_email',
            'notify_slack', 'notify_telegram_chat', 'notify_telegram_channel']
        self._validate_col_names("subscribers", cols)
        subs = self.get_subscribers()
        subscribers_dict = {row[0]: dict(zip(cols, row)) for row in subs}
        return subscribers_dict





    ##############################################
    ## CRUD :: TABLE email_lookup

    def _insert_email(
        self, node_provider_id: Principal, email_address: str) -> None:
        """Inserts an email address into the email_lookup table."""
        query = """
            INSERT INTO email_lookup (node_provider_id, email_address)
            VALUES (%s, %s)
        """
        values = (
            node_provider_id,
            email_address)
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query, values)
        self.disconnect()
    

    def _delete_email(self, email_address: str) -> None:
        """Deletes an email address from the email_lookup table."""
        query = """
            DELETE FROM email_lookup
            WHERE email_address = %s
        """
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query, (email_address,))
        self.disconnect()
    

    def get_emails(self) -> List[Tuple[Any, ...]]:
        """Returns the table of all emails."""
        query = "SELECT * FROM email_lookup"
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        self.disconnect()
        return rows
    

    def get_emails_as_dict(self) -> Dict[Principal, List[str]]:
        """Returns the table of all emails as a dictionary"""
        # Group by principal -> convert tuples to lists -> remove duplicates
        grouped = groupby(lambda row: row[1], self.get_emails())
        filtered: Dict[Principal, List[str]] = {k: [row[2] for row in v] 
                                                for k, v in grouped.items()}
        deduped = {k: list(set(v)) for k, v in filtered.items()}
        return deduped



    ##############################################
    ## CRUD :: TABLE channel_lookup
    
    def _insert_channel(
        self, node_provider_id: Principal, slack_channel_name: str,
        telegram_chat_id: str, telegram_channel_id: str) -> None:
        """Inserts or updates a record in the channel_lookup table."""
        query = """
            INSERT INTO channel_lookup (
                node_provider_id,
                slack_channel_name,
                telegram_chat_id,
                telegram_channel_id
            ) VALUES (%s, %s, %s, %s)
        """
        values = (
            node_provider_id,
            slack_channel_name,
            telegram_chat_id,
            telegram_channel_id)
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query, values)
        self.disconnect()

    
    def _delete_channel_lookup(self, node_provider_id: Principal) -> None:
        """Delete record from the channel_lookup table by node_provider_id."""
        query = """
            DELETE FROM channel_lookup
            WHERE node_provider_id = %s
        """
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query, (node_provider_id,))
        self.disconnect()

    
    def get_channels(self) -> List[Tuple[Any, ...]]: 
        """Returns the table of all channels."""
        query = "SELECT * FROM channel_lookup"
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        self.disconnect()
        return rows
    
    
    def get_channels_as_dict(self) -> Dict[Principal, Dict[str, str]]:
        """Returns the table of all channels as a dictionary

        Inserts entries into the dictionary based on the first occurrence of a 
        node provider ID in the channel_lookup table, 
        even if there are duplicates.
        """
        cols = \
            ['id', 'node_provider_id', 'slack_channel_name', 
             'telegram_chat_id', 'telegram_channel_id']
        self._validate_col_names("channel_lookup", cols)
        chans = self.get_channels()
        channels_dict = {}
        for row in chans:
            node_provider_id = row[1]
            if node_provider_id not in channels_dict:
                channels_dict[node_provider_id] = dict(zip(cols[1:], row[1:]))

        return channels_dict


    ##############################################
    ## CRUD :: TABLE node_label_lookup
    
    def _insert_node_label(self, node_id: Principal, node_label: str) -> None:            
        """Inserts or updates a node label into the node_label_lookup table."""
        query = """
            INSERT INTO node_label_lookup (node_id, node_label)
            VALUES (%s, %s)  
            ON CONFLICT (node_id) DO UPDATE SET
                node_label = EXCLUDED.node_label
        """
        values = (node_id, node_label)
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query, values)
        self.disconnect()
    
    
    def _delete_node_label(self, node_id: Principal) -> None:
        """Deletes a node label from the node_label_lookup table."""
        query = """
            DELETE FROM node_label_lookup
            WHERE node_id = %s
        """
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query, (node_id,))
        self.disconnect()
        
    
    def get_node_labels(self) -> List[Tuple[Any, ...]]:
        """Returns the table of all node labels."""
        query = "SELECT * FROM node_label_lookup"
        self.connect()
        assert self.conn is not None
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        self.disconnect()
        return rows
    

    def get_node_labels_as_dict(self) -> Dict[Principal, str]:
        """Returns the table of all node labels as a dictionary."""
        labels = self.get_node_labels()
        node_labels = {row[0]: row[1] for row in labels}
        return node_labels

