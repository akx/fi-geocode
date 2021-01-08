import sqlite3
import csv
import re
import sys

fi_addr_re = re.compile(r"([-:a-zåäö ]+)\s(\d+)$", flags=re.IGNORECASE | re.UNICODE)

geodb = sqlite3.connect("geo3.db")
geodb.row_factory = sqlite3.Row

def get_candidate_addresses(line):
    city = line["Kaupunki"]
    addr = line["Osoite"]
    fi_addr_m = fi_addr_re.search(addr)
    if fi_addr_m:
        street, bldg = tuple(fi_addr_m.groups())
        yield (city, street, bldg)
    try:
        street, bldg = addr.rsplit(None, 1)
    except ValueError:
        street = addr
        bldg = ''
    yield (city, street, bldg)



with open("a.tsv", "r") as f:
    df = csv.DictReader(f, dialect=csv.excel_tab)
    lines = list(df)

for line in lines:
    matches = []
    for fuzzy_house in (False, True):
        if matches:
            break
        for city, street, bldg in get_candidate_addresses(line):
            street = street.strip()
            bldg = bldg.strip()
            cur = geodb.cursor()
            if fuzzy_house:
                cur.execute(
                    "SELECT * FROM addr "
                    "LEFT JOIN mun on (addr.municipality = mun.code) "
                    "WHERE mun.name = ? AND addr.street = ? AND addr.house_number LIKE ? COLLATE NOCASE "
                    "LIMIT 1",
                    (city, street, f'{bldg}%'),
                )
            else:
                cur.execute(
                    "SELECT * FROM addr "
                    "LEFT JOIN mun on (addr.municipality = mun.code) "
                    "WHERE mun.name = ? AND addr.street = ? AND addr.house_number = ? COLLATE NOCASE "
                    "LIMIT 1",
                    (city, street, bldg),
                )
            row = cur.fetchone()
            if row:
                matches.append({**dict(row), "fuzzy": fuzzy_house})
    if not matches:
        print((line["Nimi"], line["Osoite"], line["Kaupunki"]), file=sys.stderr)
        print("-", "-", sep="\t")
    else:
        m = matches[0]
        print(m["longitude_wgs84"], m["latitude_wgs84"], sep="\t")