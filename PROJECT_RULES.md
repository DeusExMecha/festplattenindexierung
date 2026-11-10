---
name: File Indexer Project Rules
description: Kernregeln, Technische Vorgaben und Steno-Stil für den File-Indexer
alwaysApply: true
globs: "**/*.py"
---

# Projekt: File-Indexer (Windows/PowerShell)

## Architektur & Komponenten
- **Datenbank:** `file_database.sqlite` mit Tabelle `files(id, filename, remarks)`.
- **Kernskript (`file_indexer.py`):** 
  - Scannt ein übergebenes Verzeichnis (unterstützt optionale Tiefe).
  - Indexiert alle relevanten Dateien (`.txt`, `.md`, `.py`, `.js`, `.json`, `.html`, `.css`, `.csv`, `.log`, `.yml`).
  - Funktioniert strikt mit **relativen Pfaden**.
- **Hilfsskripte:** `check_progress.py`, `analyze_remarks.py`, `show_remarks.py`, `test_api.py`.

## Kernregeln & Einschränkungen
- **Read-Only:** Der Indexer liest und indexiert nur. Es wird **nichts gelöscht** und keine Cleanup-Logik implementiert.
- **Isoliert:** Keine harten Referenzen auf konkrete lokale Projektordner im Code oder in Prompts.

## Fehlerbehebung (Priorität)
- **Problem:** Die `remarks`-Spalte bleibt aktuell leer.
- **Maßnahme:** LM Studio-Aufruf (`http://localhost:1234/v1/chat/completions`), Modell-ID-Abfrage und Parsing der API-Antwort prüfen und korrigieren.

## Vorgaben für Remarks (Steno-Stil)
- **Format:** Ausschließlich Fakten, kommagetrennt, keinerlei Füllwörter oder ganze Sätze.
- **Beispiel:** `Python,sqlite3,indexierung` (Falsch: *"Dieses Skript indexiert Dateien..."*).