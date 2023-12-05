#!/usr/bin/env bash

# This file pulls example data from the ic-api and examines different ways
# of compressing the data and the resulting file sizes.


curl "https://ic-api.internetcomputer.org/api/v3/nodes" -o nodes.json

# Python script that converts nodes.json to nodes.cbor
cbor_py="
import json
import cbor2
with open('nodes.json', 'r') as json_file:
    json_data = json.load(json_file)
with open('nodes.cbor', 'wb') as cbor_file:
    cbor2.dump(json_data, cbor_file)
"

gzip -c nodes.json > nodes.json.gz
python3 -c "$cbor_py" # > nodes.cbor
gzip -c nodes.cbor > nodes.cbor.gz
bzip2 -c nodes.json > nodes.json.bz2
xz -c nodes.json > nodes.json.xz


# Store byte counts in variables
nodes_json_size=$(wc -c "nodes.json" | awk '{print $1}')
nodes_cbor_size=$(wc -c "nodes.cbor" | awk '{print $1}')
nodes_json_gz_size=$(wc -c "nodes.json.gz" | awk '{print $1}')
nodes_cbor_gz_size=$(wc -c "nodes.cbor.gz" | awk '{print $1}')
nodes_json_bz2_size=$(wc -c "nodes.json.bz2" | awk '{print $1}')
nodes_json_xz_size=$(wc -c "nodes.json.xz" | awk '{print $1}')


echo "FILENAME            SIZE (BYTES)               COMPRESSION RATIO"
echo "nodes.json          $nodes_json_size           (1.00 - original)"
echo "nodes.cbor          $nodes_cbor_size           ($(echo "scale=2; $nodes_cbor_size/$nodes_json_size" | bc))"
echo "nodes.json.gz       $nodes_json_gz_size        ($(echo "scale=2; $nodes_json_gz_size/$nodes_json_size" | bc))"
echo "nodes.cbor.gz       $nodes_cbor_gz_size        ($(echo "scale=2; $nodes_cbor_gz_size/$nodes_json_size" | bc))"
echo "nodes.json.bz2      $nodes_json_bz2_size       ($(echo "scale=2; $nodes_json_bz2_size/$nodes_json_size" | bc))"
echo "nodes.json.xz       $nodes_json_xz_size        ($(echo "scale=2; $nodes_json_xz_size/$nodes_json_size" | bc))"

rm nodes.json nodes.cbor nodes.json.gz nodes.cbor.gz nodes.json.bz2 nodes.json.xz

# If the script above isn't working, the results as of 2023-09-16T05:00:31+00:00:
#  FILENAME            SIZE (BYTES)     COMPRESSION RATIO
#  nodes.json          604496           (1.00 - original)
#  nodes.cbor          550721           (.91)
#  nodes.json.gz       127090           (.21)
#  nodes.cbor.gz       122175           (.20)
#  nodes.json.bz2      85300            (.14)
#  nodes.json.xz       72352            (.11)

# If ic-api queries every 30 seconds, the api generates about 8gb/5months of raw json data
# At 0.20 compression ratio, a 4GB file is compressed to 800MB
# At 0.10 compression ratio, a 4GB file is compressed to 400MB

# It's worth noting that this does not at all scale linearly with repeditive data.
# If historybuilder is ran and generates an 8GB file of raw uncompressed JSON data,
# the entire file can be compressed to ~16 MB with xz, which is a compression ratio of 0.0008889

