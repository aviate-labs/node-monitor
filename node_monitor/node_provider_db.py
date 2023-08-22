from typing import List, Dict, Any, Optional, Tuple
import psycopg2


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

    Prefer directly inserting into the tables over using the
    'insert' and 'delete' methods in this class. These methods are primarily
    used for programmatic testing.
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
            email_address TEXT UNIQUE
        );
    """

    # TABLE channel_lookup
    create_table_channel_lookup = """
        CREATE TABLE IF NOT EXISTS channel_lookup (
            id SERIAL PRIMARY KEY,
            node_provider_id TEXT UNIQUE,
            slack_channel_name TEXT UNIQUE,
            telegram_chat_id TEXT UNIQUE,
            telegram_channel_id TEXT UNIQUE
        );
    """

    # TABLE node_label_lookup
    # 'node-id' is the name of the principal of the node, 
    # consistent with the ic-api.
    create_table_node_label_lookup = """
        CREATE TABLE IF NOT EXISTS node_label_lookup (
            node_id TEXT PRIMARY KEY,
            node_label TEXT UNIQUE
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
        self.conn: Optional[psycopg2.connection] = None
        self._create_tables()


    def connect(self) -> None:
        """Connects to the database."""
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.db,
            user=self.username,
            password=self.password,
            port=self.port
        )


    def disconnect(self) -> None:
        """Commits and closes the connection to the database."""
        assert self.conn is not None   # needed for mypy --strict
        self.conn.commit()
        self.conn.close()
        self.conn = None
    

    def _create_tables(self) -> None:
        """Automatically creates the tables if they don't already exist."""
        self.connect()
        assert self.conn is not None   # needed for mypy --strict
        with self.conn.cursor() as cur:
            cur.execute(self.create_table_subscribers)
            cur.execute(self.create_table_email_lookup)
            cur.execute(self.create_table_channel_lookup)
            cur.execute(self.create_table_node_label_lookup)
        self.disconnect()


    def get_public_schema_tables(self) -> List[str]:
        """Returns a list of all tables in the public schema. 
        Useful for testing."""
        select_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """
        self.connect()
        assert self.conn is not None   # needed for mypy --strict
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
        assert self.conn is not None   # needed for mypy --strict
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
        assert self.conn is not None   # needed for mypy --strict
        with self.conn.cursor() as cur:
            cur.execute(query, (node_provider_id,))
        self.disconnect()


    def get_subscribers(self) -> List[Tuple[Any, ...]]: 
        """Returns the table of all subscribers."""
        query = "SELECT * FROM subscribers"
        self.connect()
        assert self.conn is not None   # needed for mypy --strict
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        self.disconnect()
        return rows
    


    ##############################################
    ## CRUD :: TABLE email_lookup

    def _insert_email(self) -> None:
        """Inserts an email address into the email_lookup table."""
        raise NotImplementedError
    
    def _delete_email(self) -> None:
        """Deletes an email address from the email_lookup table."""
        raise NotImplementedError
    
    def get_emails(self) -> Any:
        """Returns the table of all emails."""
        raise NotImplementedError 
    


    ##############################################
    ## CRUD :: TABLE channel_lookup
    
    def _insert_channel(
        self,
        node_provider_id: Principal,
        slack_channel_name: str,
        telegram_chat_id: str,
        telegram_channel_id: str
    ) -> None:
        """Inserts or updates a record in the channel_lookup table."""
        query = """
            INSERT INTO channel_lookup (
                node_provider_id,
                slack_channel_name,
                telegram_chat_id,
                telegram_channel_id
            ) VALUES (%s, %s, %s, %s)
            ON CONFLICT (node_provider_id) DO UPDATE SET
                slack_channel_name = EXCLUDED.slack_channel_name,
                telegram_chat_id = EXCLUDED.telegram_chat_id,
                telegram_channel_id = EXCLUDED.telegram_channel_id
        """
        values = (
            node_provider_id,
            slack_channel_name,
            telegram_chat_id,
            telegram_channel_id,
        )
        self.connect()
        assert self.conn is not None   # needed for mypy --strict
        with self.conn.cursor() as cur:
            cur.execute(query, values)
        self.disconnect()

    
    def _delete_channel_lookup(self, node_provider_id: str) -> None:
        """Delete record from the channel_lookup table by node_provider_id."""
        query = """
            DELETE FROM channel_lookup
            WHERE node_provider_id = %s
        """
        self.connect()
        assert self.conn is not None   # needed for mypy --strict
        with self.conn.cursor() as cur:
            cur.execute(query, (node_provider_id,))
        self.disconnect()

    
    def get_channels(self) -> List[Tuple[Any, ...]]: 
        """Returns the table of all channels."""
        query = "SELECT * FROM channel_lookup"
        self.connect()
        assert self.conn is not None   # needed for mypy --strict
        with self.conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
        self.disconnect()
        return rows
    


    ##############################################
    ## CRUD :: TABLE node_label_lookup
    
    def _insert_node_label(self) -> None:
        """Inserts a node label into the node_label_lookup table."""
        raise NotImplementedError
    
    def _delete_node_label(self) -> None:
        """Deletes a node label from the node_label_lookup table."""
        raise NotImplementedError
    
    def get_node_labels(self) -> Dict[Principal, str]:
        """Returns the table of all node labels."""
        raise NotImplementedError
    


    ##############################################
    ## Deprecated Interface - Do Not Use (will be removed)

    def get_email_recipients(self, node_provider: Principal) -> List[str]:
        """Deprecated. Returns the table of all email recipients.
        Use get_emails() instead."""
        raise NotImplementedError

    def get_preferences(self) -> Dict[Principal, Dict[str, bool]]:
        """Deprecated. Returns the table of all preferences.
        Use get_subscribers() instead."""
        raise NotImplementedError
    
    def get_subscribers_list(self) -> List[Principal]:
        """Deprecated. Returns the table of all subscribers.
        Use get_subscribers() instead."""
        return [row[0] for row in self.get_subscribers()]
