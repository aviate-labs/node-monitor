#!/usr/bin/env python3
from historybuilder_py.HistoryBuilderDB import HistoryBuilderDB
from devtools import debug

target = "2cov2-kcta2-rsiae-jvmot-jhp4z-kmq7n-75e35-4dvf7-tobjm-ml4lt-bqe"

def get_status(parsed_json: dict):
    try: 
        nodes = parsed_json["nodes"]
        filtered = [node for node in nodes if node['node_id'] == target]
        result = filtered[0]['status']
    except IndexError:
        result = "NONEXISTENT"
    return result


if __name__ == "__main__":
    from devtools import debug
    db = HistoryBuilderDB()
    rows = db.get_between(1701200280, 1701200438)
    # rows = [(row[0], row[1], row[3]) for row in rows]
    for row in rows:
        time, uuid, parsed_json = row
        status = get_status(parsed_json)
        print(f"{time}    {uuid}    {status}")
    # debug(rows)

