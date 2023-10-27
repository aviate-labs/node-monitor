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


    def validate_table(self, table_name: str) -> None:
        """Validate that the table exists with the expected schema"""
        pass

    def read_rows() -> List[Dict[str, Any]]:
        """Read all rows from database"""
        pass




if __name__ == "__main__":
    import load_config as c
    db = DictDB(c.DB_HOST, c.DB_NAME, c.DB_PORT, c.DB_USERNAME, c.DB_PASSWORD)
    db.connect()
    print("Connected to database")
    db.disconnect()