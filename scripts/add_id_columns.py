#!/usr/bin/env python3
"""
Add unique ID columns to provider and recipient tables.
This script safely adds missing columns if they don't exist.
"""
import sqlite3
import sys

DB_PATH = 'instance/app.db'

def column_exists(conn, table, column):
    """Check if a column exists in a table."""
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    cols = [r[1] for r in cur.fetchall()]
    return column in cols


def add_columns():
    """Add missing columns to provider and recipient tables."""
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"ERROR: Could not open database '{DB_PATH}': {e}")
        return False

    changes = []
    
    try:
        cur = conn.cursor()
        
        # Add doctor_unique_id to provider table (nullable first, unique constraint in model)
        if not column_exists(conn, 'provider', 'doctor_unique_id'):
            sql = "ALTER TABLE provider ADD COLUMN doctor_unique_id VARCHAR(32);"
            cur.execute(sql)
            changes.append("Added doctor_unique_id to provider")
        else:
            print("SKIP: doctor_unique_id already exists in provider")
        
        # Add patient_unique_id to recipient table (nullable first, unique constraint in model)
        if not column_exists(conn, 'recipient', 'patient_unique_id'):
            sql = "ALTER TABLE recipient ADD COLUMN patient_unique_id VARCHAR(32);"
            cur.execute(sql)
            changes.append("Added patient_unique_id to recipient")
        else:
            print("SKIP: patient_unique_id already exists in recipient")
        
        # Add appointment_date to recipient table
        if not column_exists(conn, 'recipient', 'appointment_date'):
            sql = "ALTER TABLE recipient ADD COLUMN appointment_date DATE;"
            cur.execute(sql)
            changes.append("Added appointment_date to recipient")
        else:
            print("SKIP: appointment_date already exists in recipient")
        
        if changes:
            conn.commit()
            for change in changes:
                print(f"OK: {change}")
        
        return True
    except sqlite3.OperationalError as oe:
        print(f"SQL ERROR: {oe}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    success = add_columns()
    sys.exit(0 if success else 1)
