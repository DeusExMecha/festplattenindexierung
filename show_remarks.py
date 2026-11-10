import sqlite3
import argparse

parser = argparse.ArgumentParser(description="Zeigt alle Remarks.")
parser.add_argument('--db', default='file_database.sqlite', help='Pfad zur SQLite-Datenbank')
args = parser.parse_args()

conn = sqlite3.connect(args.db)
c = conn.cursor()
c.execute('SELECT filename, remarks FROM files ORDER BY id')
for r in c.fetchall():
    print(f"{r[0]}:")
    print(f"  {r[1]}")
    print()
conn.close()