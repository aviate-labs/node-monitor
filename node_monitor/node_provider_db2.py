from typing import List, Dict, Any, Optional, Tuple
import psycopg2, psycopg2.extensions, psycopg2.pool
from psycopg2.extras import DictCursor, RealDictCursor
from toolz import groupby # type: ignore

Principal = str

## This class is a rewrite of our previous NodeProviderDB class.
## The previous class represented a slightly different database schema.
## It was verbose, and was hard to build upon or change.
## It is available for reference in this commit:
## daf8ee36b5b1309692d3d8583701023ca68b6c54
##
## References:
## This API was inspired by:
## https://cljdoc.org/d/seancorfield/next.jdbc/
##
## Information about psycopg2 connection pooling and cursors:
## https://www.psycopg.org/docs/pool.html
## https://www.psycopg.org/docs/cursor.html
##
## Please note that we did include a NodeProviderDB.close() class here, 
## but we will probably never need to call it:
## https://stackoverflow.com/questions/47018695/psycopg2-close-connection-pool
##


class NodeProviderDB():
    """A class to interact with the node_provider database."""

    # Postgres has no efficiency gain for using a VARCHAR instead of TEXT:
    # We've chosen to use VARCHAR so that any user or admin can't store
    # an arbitrarily large amount of data in the database.

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
        self.pool = psycopg2.pool.SimpleConnectionPool(
            1, 3, host=host, database=db, port=port,
            user=username, password=password)
    
    
    def _execute(self, sql: str,
                 params: Tuple[Any, ...]) -> List[Dict[str, Any]]:
        """Execute a SQL statement with a connection from the pool.
        An empty tuple should be passed if no parameters are needed.
        All transactions are committed.
        Returns a list of dicts instead of the default list of tuples.
        Ex. [{'column_name': value, ...}, ...]
        """
        # Note: this method can also be used for read-only queries, because
        # conn.commit() adds insignificant overhead for read-only queries.
        # Note: we convert 'result' from type List[RealDictCursor] to List[dict]
        conn = self.pool.getconn()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            result = cur.fetchall()
        conn.commit()
        self.pool.putconn(conn)
        return [dict(r) for r in result]
    

    def _execute1(self, sql: str, params: Tuple[Any, ...]) -> List[Tuple[Any, ...]]:
        """Execute a SQL statement with a connection from the pool.
        An empty tuple should be passed if no parameters are needed.
        All transactions are committed.
        Returns a list of tuples, as is standard.
        Prefer _execute() instead.
        """
        conn = self.pool.getconn()
        with conn.cursor() as cur:
            cur.execute(sql, params)
            result: List[Tuple[Any, ...]] = cur.fetchall()
        conn.commit()
        self.pool.putconn(conn)
        return result


    def _validate_schema(self) -> bool:
        """Validate the database schema."""
        # TODO: This function is still incomplete
        # TODO: could we use pg_dump or generate_ddl to test this instead?
        # Get the column names, data types
        table_name = "subscribers"
        query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
        """
        result = self._execute(query, ())
        raise NotImplementedError
        return None


    def get_subscribers_as_dict(self) -> Dict[Principal, Dict[str, Any]]:
        """Returns the table of all subscribers as a dictionary."""
        result = self._execute("SELECT * FROM subscribers", ())
        as_dict = {row['node_provider_id']: row for row in result}
        return as_dict
    

    def get_emails_as_dict(self) -> Dict[Principal, List[str]]:
        """Returns the table of all emails as a dictionary"""
        result = self._execute("SELECT * FROM email_lookup", ())
        grouped = groupby(lambda d: d['node_provider_id'], result)
        lookupd = {k: [row['email_address'] for row in v] 
                   for k, v in grouped.items()}
        return lookupd
    

    def get_slack_channels_as_dict(self) -> Dict[Principal, List[str]]:
        """Returns the table of all slack channels as a dictionary."""
        result = self._execute("SELECT * FROM slack_channel_lookup", ())
        grouped = groupby(lambda d: d['node_provider_id'], result)
        lookupd = {k: [row['slack_channel_id'] for row in v] 
                   for k, v in grouped.items()}
        return lookupd
    

    def get_telegram_chats_as_dict(self) -> Dict[Principal, List[str]]:
        """Returns the table of all telegram chats as a dictionary."""
        result = self._execute("SELECT * FROM telegram_chat_lookup", ())
        grouped = groupby(lambda d: d['node_provider_id'], result)
        lookupd = {k: [row['telegram_chat_id'] for row in v] 
                   for k, v in grouped.items()}
        return lookupd
    

    def get_node_labels_as_dict(self) -> Dict[Principal, str]:
        rows = self._execute("SELECT * FROM node_label_lookup", ())
        lookupd = {row['node_id']: row['node_label'] for row in rows}
        return lookupd


    def close(self) -> None:
        self.pool.closeall()



# if __name__ == "__main__":
#     import load_config as c
#     from pprint import pprint
#     db = NodeProviderDB(c.DB_HOST, c.DB_NAME, c.DB_PORT, c.DB_USERNAME, c.DB_PASSWORD)
#     pprint("---------------------------------")
#     # db._validate_schema()
#     result = db._execute("SELECT * FROM subscribers", ())
#     pprint(result)
#     pprint("---------------------------------")
#     result = db.get_emails_as_dict()
#     result = db.get_slack_channels_as_dict()
#     result = db.get_node_labels_as_dict()
#     pprint(result)
