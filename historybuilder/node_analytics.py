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
    db = HistoryBuilderDB(filename="historybuilder_2023-09-29_2023-11-10.db")
    start, end = db.get_start_end()
    print(
        f"Start: {start}, {HistoryBuilderDB.epoch_seconds_to_datetime(start)}\n"
        f"End: {end}, {HistoryBuilderDB.epoch_seconds_to_datetime(end)}"
    )
    
    t1 = HistoryBuilderDB.datetime_to_epoch_seconds("2023-09-29")
    t2 = HistoryBuilderDB.datetime_to_epoch_seconds("2023-10-05")
    print(t1, t2)
    rows = db.get_between(t1, t2)

    df = pd.DataFrame(rows, columns=['time', 'uuid', 'parsed_json'])
    df['status'] = df['parsed_json'].apply(get_status)
    df = df.drop('uuid', axis=1)
    # Calculate uptime percentage
    total_data_points = df.shape[0]
    up_data_points = df[df['status'] == 'UP'].shape[0]
    uptime_percentage = (up_data_points / total_data_points) * 100
    print("Uptime Percentage: {:.2f}%".format(uptime_percentage))
    print(df[['time', 'status']])
