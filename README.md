# fi-geocode

A simple, non-fuzzy data pipeline to geocode Finnish addresses using Maanmittauslaitos's address database.

Actual usage will probably require some additional code, but it's a start.

## Usage

You'll need cURL, 7-zip and Python 3.6 with Sqlite available.

Run `make`. After some crunching, you should end up with `geo4.db`, a SQLite database with three tables.
