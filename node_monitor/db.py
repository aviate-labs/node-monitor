import sqlite3
import requests
import json
import datetime
import hashlib
import time

DEVELOPMENT = False

class NodeMonitorDB:
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

    def _refs_uuid_already_exists(self, md5: str) -> bool:
        self.c.execute("SELECT * FROM refs WHERE uuid = ?", (md5,))
        return self.c.fetchone() is not None

    def _refs_add(self, md5: str, raw_json: str) -> None:
        self.c.execute("INSERT INTO refs (uuid, raw_json) VALUES (?, ?)",
                  (md5, raw_json))
        self.conn.commit()

    def timestamps_add(self, epoch_seconds: int, raw_json: str) -> None:
        uuid = NodeMonitorDB.str_to_uuid(raw_json)
        if not self._refs_uuid_already_exists(uuid):
            self._refs_add(uuid, raw_json)
        self.c.execute("INSERT INTO timestamps (epoch_seconds, uuid) VALUES (?, ?)",
                  (epoch_seconds, uuid))
        self.conn.commit()
        
    def DANGEROUSLY_delete_everything(self) -> None:
        self.c.execute("DELETE FROM refs")
        self.c.execute("DELETE FROM timestamps")
        self.conn.commit()

    def __del__(self):
        self.conn.close()
        
    @staticmethod
    def get_seconds_since_epoch() -> int:
        return int(datetime.datetime.now().timestamp())
    
    @staticmethod
    def str_to_uuid(s: str) -> str:
        md5: str = hashlib.md5(s.encode()).hexdigest()
        return md5
        



def main():
    db = NodeMonitorDB()
    db.DANGEROUSLY_delete_everything()
    while True:
        try: 
            python_json: dict = requests.get(db.endpoint).json()
            raw_json = json.dumps(python_json)
        except Exception as e:
            raise e
        print(f"{db.get_seconds_since_epoch()}:\n"
              f"\t{db.str_to_uuid(raw_json)}\n"
              f"\t{raw_json[:40]}\n\n"
        )
        db.timestamps_add(db.get_seconds_since_epoch(), raw_json)
        time.sleep(30)


if __name__ == "__main__":
    main()



