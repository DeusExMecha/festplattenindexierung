import sqlite3
import argparse
from collections import Counter

parser = argparse.ArgumentParser(description="Analysiert die Steno-Qualität der Remarks.")
parser.add_argument('--db', default='file_database.sqlite', help='Pfad zur SQLite-Datenbank')
args = parser.parse_args()

conn = sqlite3.connect(args.db)
c = conn.cursor()
c.execute('SELECT filename, remarks FROM files ORDER BY id')
rows = c.fetchall()
conn.close()

if not rows:
    print("Keine Einträge in der Datenbank.")
else:
    # Termanzahl pro remark (kommagetrennt)
    term_counts = []
    for fname, remark in rows:
        terms = [t.strip() for t in remark.split(',') if t.strip()]
        term_counts.append(len(terms))

    print("=== TERMANZAHL PRO REMARK ===\n")
    counts = Counter(term_counts)
    for n in sorted(counts):
        pct = counts[n] / len(rows) * 100
        bar = '#' * int(pct / 5)
        print(f"  {n:2d} Terme: {counts[n]:3d}x ({pct:3.0f}%) {bar}")

    # Wortanzahl pro remark (Satz-Erkennung)
    word_counts = []
    for fname, remark in rows:
        words = [w for w in remark.replace(',', ' ').split() if w]
        word_counts.append(len(words))

    print("\n=== WORTRANZAHL PRO REMARK ===\n")
    counts_w = Counter(word_counts)
    for n in sorted(counts_w):
        pct = counts_w[n] / len(rows) * 100
        bar = '#' * int(pct / 5)
        print(f"  {n:2d} Wörter: {counts_w[n]:3d}x ({pct:3.0f}%) {bar}")

    # Verdächtige remarks (>5 Terme oder enthält Punkt → Satz statt Steno)
    print("\n=== VERDÄCHTIGE REMARKS (>5 Terme oder Punkt) ===\n")
    suspicious = []
    for fname, remark in rows:
        terms = [t.strip() for t in remark.split(',') if t.strip()]
        if len(terms) > 5 or '.' in remark:
            suspicious.append((fname, remark))
    if suspicious:
        for fname, remark in suspicious:
            print(f"  {fname}: \"{remark}\"")
    else:
        print("  keine gefunden")

    # Fallback- und Leerwerte zählen
    fallback = sum(1 for _, r in rows if r == 'keine-bemerkung')
    empty = sum(1 for _, r in rows if not r)

    print(f"\nGesamt: {len(rows)} Dateien")
    print(f"Leere remarks: {empty}")
    print(f"Fallback 'keine-bemerkung': {fallback} ({fallback/len(rows)*100:.0f}%)")
