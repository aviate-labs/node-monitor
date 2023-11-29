#!/usr/bin/env python3
from historybuilder_py.HistoryBuilderDB import HistoryBuilderDB
from devtools import debug

if __name__ == "__main__":
    from devtools import debug
    db = HistoryBuilderDB()
    rows = db.get_between(1701200280, 1701200438)
    rows = [(row[0], row[1]) for row in rows]
    debug(rows)

