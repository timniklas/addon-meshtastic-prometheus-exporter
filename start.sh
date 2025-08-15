#!/bin/bash

#get ha config
CONFIG_PATH=/data/options.json
HOST=$(jq --raw-output '.host' $CONFIG_PATH)

/app/bin/python3 -u /app/mesh_exporter.py $HOST
