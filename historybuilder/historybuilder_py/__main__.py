import logging, requests, json, os, time
from historybuilder_py.NodeMonitorDB import NodeMonitorDB

## Logging - use systemd to forward stdout/stderr to journald
logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper(),
                    format='%(asctime)s:%(levelname)s:%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
    logging.info("Starting HistoryBuilder")
    db = NodeMonitorDB()
    while True:
        try: 
            python_json: dict = requests.get(db.endpoint).json()
            raw_json = json.dumps(python_json)
            logging.info("Retrieved JSON")
        except Exception as e:
            logging.error(f"Exception occured: {e}")
        else:
            db.timestamps_add(db.get_seconds_since_epoch(), raw_json)
        time.sleep(30)








