import sqlite3
import requests
import json
import hashlib
import time
import logging

DEVELOPMENT = False   # uses in-memory database
SAFEGUARD = True      # disables dangerous methods

class HistoryBuilderDB:
    """Database class for node monitor.
    Queries the API every (30?) seconds.
    Stores data in 2 tables:
    1. refs        { uuid: str, raw_json: str }
    2. timestamps  { epoch_seconds: int, uuid: str }
    
             TABLE refs
    |   uuid (md5)  |      raw_json      |
    | ------------- | -------------------|
    | "1b3f8h34..." | "[{node1...}, ..." ]
    | "ac23b48e..." | "[{node2...}, ..." ]
    | "a3cc912h..." | "[{node3...}, ..." ]

            TABLE timestamps
    | epoch_seconds |     uuid      |  
    | ------------- | --------------| 
    |  1620000000   | "1b3f8h34..." ]
    |  1620000030   | "1b3f8h34..." ]
    |  1620000060   | "a3cc912h..." ]
    # VSCode Extension: SQLite Viewer (Florian Klampfer) is a good option
    """
    endpoint = "https://ic-api.internetcomputer.org/api/v3/nodes"


    def __init__(self):
        if DEVELOPMENT:
            self.conn = sqlite3.connect(":memory:")
        else:
            self.conn = sqlite3.connect('master.db')
        assert self.conn.total_changes == 0
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS refs (uuid TEXT, raw_json TEXT)')
        self.c.execute('CREATE TABLE IF NOT EXISTS timestamps (epoch_seconds INTEGER, uuid TEXT)')
        self.conn.commit()
        logging.info("DB Connection Opened")


    def _refs_uuid_already_exists(self, md5: str) -> bool:
        self.c.execute("SELECT * FROM refs WHERE uuid = ?", (md5,))
        return self.c.fetchone() is not None


    def _refs_add(self, md5: str, raw_json: str) -> None:
        self.c.execute("INSERT INTO refs (uuid, raw_json) VALUES (?, ?)",
                  (md5, raw_json))
        self.conn.commit()
        logging.info(f"Added new entry to refs table: {md5}")


    def timestamps_add(self, epoch_seconds: int, raw_json: str) -> None:
        uuid = HistoryBuilderDB.str_to_uuid(raw_json)
        if not self._refs_uuid_already_exists(uuid):
            self._refs_add(uuid, raw_json)
        self.c.execute("INSERT INTO timestamps (epoch_seconds, uuid) VALUES (?, ?)",
                  (epoch_seconds, uuid))
        self.conn.commit()
        

    def DANGEROUSLY_delete_everything(self) -> None:
        if not SAFEGUARD:
            self.c.execute("DELETE FROM timestamps")
            self.c.execute("DELETE FROM refs")
            self.conn.commit()
            logging.info("Deleted all data from both tables")


    def get_between(self,
                    epoch_seconds_start: int, 
                    epoch_seconds_end: int) -> list:
        self.c.execute(f"SELECT epoch_seconds, refs.uuid, raw_json "
                       f"FROM timestamps "
                       f"JOIN refs ON timestamps.uuid = refs.uuid "
                       f"WHERE epoch_seconds BETWEEN ? AND ? ",
                       (epoch_seconds_start, epoch_seconds_end))
        rows = self.c.fetchall()
        rows = [(row[0], row[1], json.loads(row[2])) for row in rows]
        return rows


    def __del__(self):
        self.conn.close()
        logging.info("DB Connection Closed")
        

    @staticmethod
    def get_seconds_since_epoch() -> int:
        return int(time.time())
    

    @staticmethod
    def str_to_uuid(s: str) -> str:
        md5: str = hashlib.md5(s.encode()).hexdigest()
        return md5
        


# Example:
# python_json: dict = requests.get(db.endpoint).json()
# raw_json = json.dumps(python_json)
# db.timestamps_add(db.get_seconds_since_epoch(), raw_json)

if __name__ == "__main__":
    from devtools import debug
    db = HistoryBuilderDB()
    rows = db.get_between(1701200280, 1701200438)
    # rows = [(row[0], row[1]) for row in rows]
    debug(rows)
