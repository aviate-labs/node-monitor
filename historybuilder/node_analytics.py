#!/usr/bin/env python3
import pandas as pd
from historybuilder_py.HistoryBuilderDB import HistoryBuilderDB

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
    db = HistoryBuilderDB()
    rows = db.get_between(1701200280, 1701200938)
    df = pd.DataFrame(rows, columns=['time', 'uuid', 'parsed_json'])
    df['status'] = df['parsed_json'].apply(get_status)
    print(df[['time', 'uuid', 'status']])
