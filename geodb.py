import argparse
import sqlite3
import sys

NONFUZZY_QUERY = """
SELECT b.*, s.name as s_name, m.name as m_name 
FROM buildings b 
LEFT JOIN municipalities m on b.municipality_code = m.code 
LEFT JOIN streets s on b.street_id = s.id 
WHERE m.name = :city_name 
AND s.name = :street_name
AND b.house_number = :house_number 
COLLATE NOCASE 
LIMIT 1
"""

FUZZY_QUERY = """
SELECT b.*, s.name as s_name, m.name as m_name 
FROM buildings b 
LEFT JOIN municipalities m on b.municipality_code = m.code 
LEFT JOIN streets s on b.street_id = s.id 
WHERE m.name = :city_name 
AND s.name = :street_name
AND b.house_number LIKE :house_number_prefix 
COLLATE NOCASE 
LIMIT 1
"""


class GeoDB:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    @classmethod
    def from_file(cls, db_path: str):
        geodb = sqlite3.connect(db_path)
        geodb.row_factory = sqlite3.Row
        return cls(db=geodb)

    def query(
        self, *, city_name: str, street_name: str, house_number: str, fuzzy=False
    ):
        params = {
            "city_name": city_name,
            "street_name": street_name,
            "house_number": house_number,
            "house_number_prefix": f"{house_number}%",
        }
        res = self.db.execute((FUZZY_QUERY if fuzzy else NONFUZZY_QUERY), params)
        return res.fetchone()


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--database", default="geo4.db")
    sp = ap.add_subparsers(dest="action")
    query_p = sp.add_parser("query")
    query_p.add_argument("-c", "--city", required=True)
    query_p.add_argument("-s", "--street", required=True)
    query_p.add_argument("-n", "--number", required=True)
    query_p.add_argument("-f", "--fuzzy", action="store_true")
    query_p.add_argument(
        "-o", "--output-format", choices=("verbose", "lnglat"), default="verbose"
    )
    args = ap.parse_args()
    db = GeoDB.from_file(args.database)
    if args.action == "query":
        res = db.query(
            city_name=args.city,
            street_name=args.street,
            house_number=args.number,
            fuzzy=args.fuzzy,
        )
        if res:
            if args.output_format == "verbose":
                for key, value in sorted(dict(res).items()):
                    print(f"{key}: {value}")
            elif args.output_format == "lnglat":
                print(res["longitude_wgs84"], res["latitude_wgs84"], sep="\t")
        else:
            print("No results", file=sys.stderr)
    else:
        ap.error("No action")


if __name__ == "__main__":
    cli()
