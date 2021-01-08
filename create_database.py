import sqlite3
import csv
import sys


def write_mun_table(db):
    db.execute("CREATE TABLE municipalities (code INTEGER PRIMARY KEY, name TEXT)")
    with open("data/municipalities.csv") as f:
        db.executemany(
            "INSERT INTO municipalities (code, name) VALUES (?, ?)",
            [(r["code"], r["name"]) for r in csv.DictReader(f)],
        )


def insertdicts(db, table, keys, items):
    cols = ", ".join(keys)
    phs = ", ".join(f":{key}" for key in keys)
    query = f"INSERT INTO {table} ({cols}) VALUES ({phs})"
    return db.executemany(query, items)


def read_addresses(db):
    db.executescript(
        """
CREATE TABLE streets(
    id INTEGER PRIMARY KEY,
    name TEXT
);
CREATE TABLE buildings (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "building_id" TEXT,
  "region" TEXT,
  "municipality_code" INTEGER,
  "street_id" INTEGER,
  "house_number" TEXT,
  "postal_code" TEXT,
  "latitude_wgs84" REAL,
  "longitude_wgs84" REAL,
  "building_use" INTEGER,
  FOREIGN KEY(street_id) REFERENCES streets(id)
  FOREIGN KEY(municipality_code) REFERENCES municipalities(code)
);
"""
    )
    # interned_strings = {}
    # intern = lambda x: interned_strings.setdefault(x, x)
    streets = {}
    save_street = lambda street: streets.setdefault(street, len(streets) + 1)
    rows = []

    with open("data/Finland_addresses_2020-11-13.csv") as f:
        for i, r in enumerate(csv.DictReader(f), 1):
            if i % 10_000 == 0:
                print(
                    i,
                    "buildings parsed,",
                    len(streets),
                    "unique streetnames...",
                    end="\r",
                )
            street = r.pop("street")
            mun = r.pop("municipality")
            if not (street and mun):
                continue
            r["street_id"] = save_street(street)
            r["municipality_code"] = int(mun)
            rows.append(r)
    print("Data read, inserting...")
    print(f"Inserting {len(streets)} streets...")

    db.executemany("INSERT INTO streets (name, id) VALUES (?, ?)", streets.items())

    print(f"Inserting {len(rows)} buildings...")
    insertdicts(db, "buildings", rows[0].keys(), rows)
    print(f"Creating indexes...")
    db.execute("create index ix_street_name_nocase on streets ('name' COLLATE NOCASE)")
    db.execute("create index ix_addr_municipality_code on buildings ('municipality_code')")
    db.execute("create index ix_addr_street_id on buildings ('street_id')")


def main():
    db = sqlite3.connect(sys.argv[1])
    write_mun_table(db)
    read_addresses(db)
    db.commit()


if __name__ == "__main__":
    main()
