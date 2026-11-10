"""File-Indexer: scannt ein Verzeichnis und indexiert Textdateien mit KI-Bemerkungen."""

import argparse
import re
import sqlite3
from pathlib import Path

import requests

# ── Konfiguration ────────────────────────────────────────────────
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_MODELS_URL = "http://localhost:1234/v1/models"
DEFAULT_DB = "file_database.sqlite"

TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".js", ".json",
    ".html", ".css", ".csv", ".log", ".yml",
}


# ── Modell-Auflösung (einmalig beim Import) ───────────────────────
def _resolve_model_id() -> str:
    """Holt die ID des ersten geladenen Modells von LM Studio."""
    try:
        resp = requests.get(LM_STUDIO_MODELS_URL, timeout=5)
        if resp.status_code == 200 and (data := resp.json().get("data")):
            return data[0]["id"]
    except Exception as exc:
        print(f"[!] Konnte Modell-ID nicht ermitteln: {exc}")
    return "local-model"


MODEL_ID = _resolve_model_id()
print(f"> Verwende Modell: {MODEL_ID}\n")


# ── Datenbank-Helfer ──────────────────────────────────────────────
def init_db(db_name: str) -> None:
    """Erstellt die SQLite-Datenbank, falls sie noch nicht existiert."""
    with sqlite3.connect(db_name) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                path            TEXT UNIQUE,
                filename        TEXT,
                file_type       TEXT,
                content_snippet TEXT,
                remarks         TEXT
            )
        """)


def _already_indexed(cursor: sqlite3.Cursor, relative_path: str) -> bool:
    cursor.execute("SELECT 1 FROM files WHERE path = ?", (relative_path,))
    return cursor.fetchone() is not None


# ── Text-Normalisierung ───────────────────────────────────────────
def normalize_remark(raw: str) -> str:
    """Trimmt, entfernt Punkte und normalisiert auf Komma-Trennung."""
    text = raw.strip().strip(".").strip()
    text = " ".join(text.split())          # Leerzeichen zusammenfassen
    text = re.sub(r"[;:]", ",", text)       # ; und : → ,
    text = re.sub(r",{2,}", ",", text)      # aufeinanderfolgende Kommas → eins
    return text.strip(",")


# ── KI-Abfrage ────────────────────────────────────────────────────
def get_ai_remark(filename: str, content: str) -> str:
    """Fragt LM Studio nach einer Steno-Bemerkung (max. 5 kommagetrennte Fakten)."""
    prompt = (
        f"Extrahiere max 5 kommagetrennte Fakten aus Datei {filename}. "
        f"Nur Stichwörter, keine Sätze.\n\n{content[:1500]}"
    )

    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    try:
        resp = requests.post(
            LM_STUDIO_URL, json=payload, timeout=30,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code == 200:
            raw = resp.json()["choices"][0]["message"]["content"]
            return normalize_remark(raw)
    except Exception as exc:
        print(f"  [!] KI-Fehler bei {filename}: {exc}")

    return "keine-bemerkung"


# ── Datei-Verarbeitung (eine Datei) ───────────────────────────────
def _index_single_file(
    cursor: sqlite3.Cursor,
    file_path: Path,
    relative_path: str,
) -> None:
    """Liest eine einzelne Datei ein und speichert sie in der DB."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        print(f"  [!] Konnte Datei nicht lesen: {exc}")
        return

    snippet = content[:1000]
    remark = get_ai_remark(file_path.name, snippet)
    print(f"   -> Bemerkung: {remark}")

    cursor.execute(
        """INSERT OR REPLACE INTO files
           (path, filename, file_type, content_snippet, remarks)
           VALUES (?, ?, ?, ?, ?)""",
        (relative_path, file_path.name, file_path.suffix.lower(), snippet, remark),
    )


# ── Haupt-Scan ────────────────────────────────────────────────────
def _iter_candidate_files(
    target: Path, max_depth: int | None
):
    """Yieldet alle Textdateien innerhalb der erlaubten Tiefe."""
    for file_path in target.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if max_depth is not None:
            depth = len(file_path.relative_to(target).parts) - 1
            if depth > max_depth:
                continue
        yield file_path


def scan_and_index(
    directory: str,
    db_name: str = DEFAULT_DB,
    max_depth: int | None = None,
) -> None:
    """Scannt das Verzeichnis und indexiert alle relevanten Dateien."""
    target = Path(directory)
    if not target.exists():
        print(f"Fehler: Der Ordner {directory} existiert nicht.")
        return

    init_db(db_name)

    print(f"> Starte Scan von: {target.absolute()}")
    if max_depth is not None:
        print(f"> Max. Tiefe: {max_depth}")

    conn = sqlite3.connect(db_name)
    try:
        cursor = conn.cursor()
        for file_path in _iter_candidate_files(target, max_depth):
            relative_path = str(file_path.relative_to(target))

            if _already_indexed(cursor, relative_path):
                print(f" Überspringe (bereits indexiert): {relative_path}")
                continue

            print(f" Verarbeite: {relative_path}...")
            _index_single_file(cursor, file_path, relative_path)
            conn.commit()
    finally:
        conn.close()

    print(" FERTIG! Alle Dateien wurden indexiert.")


# ── CLI-Einstiegspunkt ────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="File-Indexer: scannt ein Verzeichnis und indexiert "
                    "Textdateien mit KI-Bemerkungen."
    )
    parser.add_argument("directory", help="Zielverzeichnis zum Scannen")
    parser.add_argument("--db", default=DEFAULT_DB,
                        help=f"Pfad zur SQLite-Datenbank (Standard: {DEFAULT_DB})")
    parser.add_argument("--depth", type=int, default=None,
                        help="Optionale maximale Scan-Tiefe (0 = nur oberstes Level)")
    args = parser.parse_args()

    scan_and_index(args.directory, db_name=args.db, max_depth=args.depth)


if __name__ == "__main__":
    main()