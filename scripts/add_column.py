#!/usr/bin/env python3
"""
Add missing `unique_appointment_code` column to `session` table in SQLite DB.
This script is non-destructive: it checks the schema first and only adds the column
if it does not already exist.
"""
import sqlite3
import sys

DB_PATH = 'instance/app.db'
COLUMN_NAME = 'unique_appointment_code'
COLUMN_DEF = "VARCHAR(32)"

def column_exists(conn, table, column):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    cols = [r[1] for r in cur.fetchall()]
    return column in cols


def main():
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"ERROR: Could not open database '{DB_PATH}': {e}")
        sys.exit(2)

    try:
        if column_exists(conn, 'session', COLUMN_NAME):
            print(f"SKIP: Column '{COLUMN_NAME}' already exists on 'session'.")
            return

        sql = f"ALTER TABLE session ADD COLUMN {COLUMN_NAME} {COLUMN_DEF};"
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        print(f"OK: Column '{COLUMN_NAME}' added to 'session'.")
    except sqlite3.OperationalError as oe:
        print(f"SQL ERROR: {oe}")
        sys.exit(3)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(4)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
