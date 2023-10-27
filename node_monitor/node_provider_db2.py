from typing import List, Dict, Any, Optional, Tuple
import psycopg2, psycopg2.extensions

Principal = str

class DictDB:
    """Class used to operate with a postgres database using dictionaries.
    This class is not intended to be called directly, instead it should be
    inherited from and the schema should be defined in the child class."""
    ##
    ## Any child class should define a schema.
    ## The schema should be a dictionary of dictionaries, where the keys
    ## are the table names, and the values are dictionaries of column names
    ## and data types. See the example schema for reference.
    ## 
    ## Any schema that is a superset of this should be considered valid and
    ## interoperable, and should not throw errors.
    schema = {}
    example_schema = {
        "table_name": {
            "column_name": "data_type",
            "column_name": "data_type"
        }
    }
    ##
    ## Function Definitions

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
        # TODO: see connections pooling
        # https://www.psycopg.org/docs/pool.html


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


    def get_table_schema(self) -> List[Tuple[str]]:
        """Query the database for the table schema."""
        assert self.conn is not None
        q = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """
        with self.conn.cursor() as cur:
            cur.execute(q)
            rows = cur.fetchall()
        return rows
    

    def get_column_schema(self, table_name: str) -> List[Tuple[str, str]]:
        """Query the database for the column schema of a table."""
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
    

    def validate_schema(self) -> bool:
        """Validate the schema against the database.
        Used for testing, not in production."""
        actual_tables = self.get_tables()
        expected_tables = DictDB.schema.keys()
        # TODO: this will fail, the data isnt properly formatted
        return set(actual_tables) == set(expected_tables)
    

    def get_table_as_dict(self, table_name: str) -> List[dict]:
        """Get a table as a list of flat (unnested) dictionaries.
        Example:
        |  id  | col1 | col2 |
        |------|------|------|
        | val0 | val1 | val2 |
        | val3 | val4 | val5 |
        | val6 | val7 | val8 |

        Will be returned as:
        [
            {"id": "val0", "col1": "val1", "col2": "val2"},
            {"id": "val3", "col1": "val4", "col2": "val5"},
            {"id": "val6", "col1": "val7", "col2": "val8"}
        ]
        """
        assert self.conn is not None
        q = f"""
            SELECT *
            FROM {table_name}
        """
        with self.conn.cursor() as cur:
            cur.execute(q)
            column_names = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
        return [dict(zip(column_names, row)) for row in rows]





class NodeProviderDB(DictDB):
    """Class used to define and test the proper schema."""

    schema = {
        "subscribers": {
            "node_provider_id": "TEXT PRIMARY KEY",
            "node_provider_name": "TEXT",
            "notify_on_status_change": "BOOLEAN", # do we want this?
            "notify_email": "BOOLEAN",
            "notify_slack": "BOOLEAN",
            "notify_telegram": "BOOLEAN"
        },
        "email_lookup": {
            "id": "SERIAL PRIMARY KEY",
            "node_provider_id": "TEXT",
            "email_address": "TEXT"
        },
        "slack_channel_lookup": {
            "id": "SERIAL PRIMARY KEY",
            "node_provider_id": "TEXT",
            "slack_channel_id": "TEXT"
        },
        "telegram_chat_lookup": {
            "id": "SERIAL PRIMARY KEY",
            "node_provider_id": "TEXT",
            "telegram_chat_id": "TEXT"
        },
        "node_label_lookup": {
            "node_id": "TEXT PRIMARY KEY",
            "node_label": "TEXT"
        }
    }





if __name__ == "__main__":
    import load_config as c
    from pprint import pprint
    db = DictDB(c.DB_HOST, c.DB_NAME, c.DB_PORT, c.DB_USERNAME, c.DB_PASSWORD)
    db.connect()
    pprint("---------------------------------")
    print("Tables:")
    pprint(db.get_table_schema())
    print("")
    print("Schema:")
    pprint(db.get_column_schema('email_lookup'))
    print("Subscribers as dict")
    pprint(db.get_table_as_dict('subscribers'))
    pprint(db.get_table_as_dict('email_lookup'))
    pprint("---------------------------------")
    db.disconnect()
