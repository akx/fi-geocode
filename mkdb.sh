#!/bin/bash
set -xeuo pipefail
DBF=$1
echo -ne ".mode csv mun\n.import data/municipalities.csv mun" | sqlite3 "$DBF"
echo -ne ".mode csv addr\n.import data/Finland_addresses_2020-11-13.csv addr" | sqlite3 "$DBF"
sqlite3 "$DBF" "create unique index ix_mun_code on mun ('code')"
sqlite3 "$DBF" "create index ix_addr_code on addr ('municipality')"
