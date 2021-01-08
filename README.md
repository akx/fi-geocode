# fi-geocode

A simple, non-fuzzy data pipeline to geocode Finnish addresses using Maanmittauslaitos's address database.

Actual usage will probably require some additional code, but it's a start.

## Usage

You'll need cURL, 7-zip and Sqlite available.

Run `make`. After some crunching, you should end up with `geo3.db`, a SQLite database with two tables.