import csv
import json

def csv_to_json():
    """helps to parse a csv lookup file into a json file that
    node monitor can read directly"""

    ### Read the csv file (mind the encoding)
    with open('lookuptable.csv', newline='', encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        lookuptable = {row['Node ID']: row['Node Label'] for row in reader}

    ### Dump it to json
    with open("lookuptable.json", "w") as outfile:
        json.dump(lookuptable, outfile, indent=4)


if __name__ == "__main__":
    csv_to_json()