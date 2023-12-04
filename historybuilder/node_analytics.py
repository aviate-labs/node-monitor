#!/usr/bin/env python3
import pandas as pd
import plotly.express as px
from historybuilder_py.HistoryBuilderDB import HistoryBuilderDB
import more_itertools

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
    # Gather the data
    db = HistoryBuilderDB(filename="historybuilder_2023-09-29_2023-11-10.db")
    start, end = db.get_start_end()
    print(
        f"Start: {start}, {HistoryBuilderDB.epoch_seconds_to_datetime(start)}\n"
        f"End: {end}, {HistoryBuilderDB.epoch_seconds_to_datetime(end)}"
    )

    t1 = HistoryBuilderDB.datetime_to_epoch_seconds("2023-09-29")
    t2 = HistoryBuilderDB.datetime_to_epoch_seconds("2023-11-04")
    print(t1, t2)
    # rows = db.get_between(1696006820, 1696009820)
    intervals = range(t1, t2, 3600) # 3600 seconds / 60 = 60 minutes
    windows = more_itertools.windowed(intervals, 2)

    def list_2_dataframe(t1, t2) -> pd.DataFrame:
        """Returns a dataframe with the following columns:
        time, status, datetime, status_value"""
        l = db.get_between(t1, t2)
        df = pd.DataFrame(l, columns=['time', 'uuid', 'parsed_json'])
        df['status'] = df['parsed_json'].apply(get_status)
        df['datetime'] = df['time'].apply(HistoryBuilderDB.epoch_seconds_to_datetime)
        df = df.drop('uuid', axis=1)         # drop column uuid
        df = df.drop('parsed_json', axis=1)
        df['status_value'] = df['status'].apply(lambda x: 1 if x == 'UP' else 0)
        return df

    for window in windows:
        print(window, flush=True)
        t0, t1 = window
        df = list_2_dataframe(t0, t1)
    
    print("Done!")

    # Create dataframe
    # df = pd.DataFrame(rows, columns=['time', 'uuid', 'parsed_json'])
    # df['status'] = df['parsed_json'].apply(get_status)
    # df['datetime'] = df['time'].apply(HistoryBuilderDB.epoch_seconds_to_datetime)

    # df = df.drop('uuid', axis=1)         # drop column uuid
    # df = df.drop('parsed_json', axis=1)  # drop column parsed_json
    # df['status_value'] = df['status'].apply(lambda x: 1 if x == 'UP' else 0)

    # Calculate uptime percentage
    total_data_points = df.shape[0]
    up_data_points = df[df['status'] == 'UP'].shape[0]
    uptime_percentage = (up_data_points / total_data_points) * 100
    print("Uptime Percentage: {:.2f}%".format(uptime_percentage))

    # Plot
    fig = px.line(df, x='datetime', y='status_value', title='Node Uptime')
    fig.update_layout(yaxis_range=[-0.1, 1.1])
    fig.show()
    # print(df[['time', 'status']])
