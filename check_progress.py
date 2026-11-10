import sqlite3
import argparse

parser = argparse.ArgumentParser(description="Zeigt den Indexierungs-Fortschritt.")
parser.add_argument('--db', default='file_database.sqlite', help='Pfad zur SQLite-Datenbank')
args = parser.parse_args()

conn = sqlite3.connect(args.db)
c = conn.cursor()

c.execute('SELECT COUNT(1) FROM files')
total = c.fetchone()[0]
print(f'Indexierte Dateien: {total}\n')

c.execute("SELECT COUNT(1) FROM files WHERE remarks IS NULL OR remarks = ''")
empty = c.fetchone()[0]
if empty > 0:
    print(f'Davon ohne Bemerkung: {empty}\n')

c.execute('SELECT filename, remarks FROM files ORDER BY id DESC LIMIT 5')
for fname, remark in c.fetchall():
    print(f'{fname}:')
    print(f'  {remark}')
    print()

conn.close()
