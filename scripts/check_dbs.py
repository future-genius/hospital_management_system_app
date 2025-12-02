#!/usr/bin/env python3
import os
import sqlite3

paths = ['app.db', 'instance/app.db']

for p in paths:
    print('\nChecking:', p)
    if not os.path.exists(p):
        print('  -> File not found')
        continue
    try:
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        
        tables = ['session', 'provider', 'recipient']
        for table in tables:
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
            if not cur.fetchone():
                print(f'  -> Table "{table}" not found')
                continue
            cur.execute(f'PRAGMA table_info({table});')
            cols = [r[1] for r in cur.fetchall()]
            print(f'  -> {table} columns: {cols}')
        
        conn.close()
    except Exception as e:
        print('  -> Error reading DB:', e)
