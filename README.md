# SQL Alter Tool

A small desktop utility (customtkinter GUI) for generating `ALTER TABLE`
scripts across **Oracle**, **MSSQL**, and **DB2** from a single form, tied
to an issue/ticket number for change-tracking.

Fill in the table name, issue number, choose **ADD** or **DROP**, list
your columns (with data type + length when adding), hit **RUN** — and the
tool builds a ready-to-use payload that `service.py` turns into three
dialect-correct `.sql` scripts.

## Features

- Single form drives all three SQL dialects — no manual syntax lookup.
- ADD mode: per-column data type (`TEXT`, `DATE`, `NUMBER`, `TIMESTAMP`)
  and length, with fixed lengths auto-filled for `DATE` (8) / `TIMESTAMP` (20).
- DROP mode: just column names, no type needed.
- Dialect-specific quoting and keyword handling (e.g. DB2's quoted
  identifiers, MSSQL's `DATETIME2` vs. its reserved `TIMESTAMP` keyword).
- Outputs spooled, transaction-wrapped scripts per database, named by
  issue number (`ORA_<issue>.sql`, `MsSQL_<issue>.sql`, `DB2_<issue>.sql`).
- Checks GitHub for a newer version on startup (silently skips if offline
  or rate-limited — never blocks the app from launching).

## Project structure

    sql-alter-tool/
    ├── VERSION                  # current version, e.g. "1.0.0"
    ├── src/
    │   ├── main.py               # entry point - runs update check, then launches GUI
    │   ├── gui.py                # customtkinter GUI
    │   ├── service.py            # writes the .sql files for all 3 dialects
    │   ├── updater.py            # checks GitHub releases for a newer version
    │   └── databases/
    │       ├── __init__.py
    │       ├── database_syntax.py   # shared base class: type/length conversion
    │       ├── oracle.py
    │       ├── mssql.py
    │       └── db2.py
    ├── requirements.txt
    ├── requirements-build.txt
    ├── build.spec
    ├── version_info.txt
    └── BUILD.md

## Requirements

- Python 3.10+
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter)

## Setup

```bash
git clone https://github.com/<your-username>/sql-alter-tool.git
cd sql-alter-tool
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

On launch, `main.py` runs a quick update check against GitHub Releases
(see [Updating](#updating) below) and then opens the GUI regardless of
the outcome — a failed or rate-limited check never prevents the app from
starting.

1. Enter the **table name** and **issue number**.
2. Choose **ADD** or **DROP**.
3. Add one or more columns (`+ Add Column`). For ADD, pick a data type;
   the length field auto-fills and locks for `DATE`/`TIMESTAMP`, and stays
   editable for `TEXT`/`NUMBER` (accepts `precision.scale`, e.g. `15.5` →
   rendered as `NUMERIC(15,5)`).
4. Click **RUN**. The generated payload is logged in the output box.
5. Hand the payload to `service.calculate_n_write(...)` to write the three
   `.sql` files to disk.

## Data type mapping

| Generic  | Oracle    | MSSQL      | DB2       |
|----------|-----------|------------|-----------|
| TEXT     | CHAR(n)   | CHAR(n)    | CHAR(n)   |
| NUMBER   | NUMERIC(p[,s]) | NUMERIC(p[,s]) | NUMERIC(p[,s]) |
| DATE     | DATE      | DATE       | DATE      |
| TIMESTAMP| TIMESTAMP | DATETIME2  | TIMESTAMP |

> MSSQL's own `TIMESTAMP` keyword is a row-versioning binary type, not a
> date/time type — the tool substitutes `DATETIME2` automatically.

## Updating

The app is version-tracked via the plain-text `VERSION` file at the repo
root, compared against the latest GitHub release tag. `src/updater.py`
handles this check; `main.py` calls it once at startup, in a way that
never interrupts the app if it fails (offline, GitHub rate limit, etc.).

GitHub's unauthenticated API allows 60 requests/hour per IP — plenty for
normal use, but easy to burn through while actively developing/testing.
If you hit `HTTP 403: rate limit exceeded`, it's this quota, not a bug;
check `https://api.github.com/rate_limit` (doesn't count against the
quota) to see when it resets.

## Building a Windows executable

See [`BUILD.md`](BUILD.md) for PyInstaller packaging and code-signing
instructions.

## License

[MIT](LICENSE)