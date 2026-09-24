import json
import os
from contextlib import closing
import psycopg2

try:
    with closing(psycopg2.connect(host=os.getenv('DB_HOST', 'practice-db'),
            port=int(os.getenv('DB_PORT', '5432')), dbname='practice',
            user='practice', password=os.environ['DB_PASSWORD'], connect_timeout=3)) as conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)')
                cur.executemany('INSERT INTO users VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name',
                                [(1, 'Anna'), (2, 'Boris'), (3, 'Vera')])
                cur.execute('SELECT id, name FROM users ORDER BY id')
                print(json.dumps(cur.fetchall()))
except psycopg2.Error:
    print('Database connection or query failed')
    raise SystemExit(1)
