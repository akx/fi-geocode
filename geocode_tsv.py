import csv
import re
import sys

from geodb import GeoDB

fi_addr_re = re.compile(r"([-:a-zåäö ]+)\s(\d+)$", flags=re.IGNORECASE | re.UNICODE)


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


def get_matches(geodb, line):
    matches = []
    for fuzzy_house in (False, True):
        if matches:
            break
        for city, street, bldg in get_candidate_addresses(line):
            street = street.strip()
            bldg = bldg.strip()
            row = geodb.query(
                city_name=city,
                street_name=street,
                house_number=bldg,
                fuzzy=fuzzy_house,
            )
            if row:
                matches.append({**dict(row), "fuzzy": fuzzy_house})
    return matches


def main():
    geodb = GeoDB.from_file("geo4.db")

    with open("a.tsv", "r") as f:
        df = csv.DictReader(f, dialect=csv.excel_tab)
        lines = list(df)

    for line in lines:
        matches = get_matches(geodb, line)
        if not matches:
            print((line["Nimi"], line["Osoite"], line["Kaupunki"]), file=sys.stderr)
            print("-", "-", sep="\t")
        else:
            m = matches[0]
            print(m["longitude_wgs84"], m["latitude_wgs84"], sep="\t")


if __name__ == '__main__':
    main()
