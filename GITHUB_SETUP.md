# GITHUB_SETUP — Repo-Einrichtung & Push (Kurzanleitung)

## Repository
- **Repo:** `DeusExMecha/festplattenindexierung` (öffentlich), Branch `main`
- **Remote `origin`:** `https://github.com/DeusExMecha/festplattenindexierung.git` — immer ohne Token in der Konfiguration!
- **Commit-Identität** (lokal nicht gesetzt, pro Commit übergeben):
  `git -c user.name="DeusExMachina" -c user.email="deusexmachina@users.noreply.github.com" commit ...`

## Credentials (lokal, gitignoriert)
| Datei | Inhalt |
|---|---|
| `Github_GH_Token.key` | GitHub-Token — **nie ausgeben, nie committen** |
| `Github_GH_Token.username` | Username (`DeusExMecha`) |

Regeln: Token nur in Skripten lesen (`.read_text().strip()`), nie hartkodieren,
in Ausgaben/Logs maskieren (`replace(token, "***")`). Token-URLs nur für den
einzelnen Push-Aufruf verwenden — niemals als Remote speichern.

## Push-Ablauf
1. `python push_token.py` → pusht `main` via `https://x-access-token:<token>@github.com/...`
   mit `-c credential.helper=` (wird nicht gespeichert).
2. Danach: `git fetch origin` → Tracking-Verweis `[origin/main]` aktualisieren.
3. Neues Repo anlegen (nur falls nötig): `python push_new_repo.py`
   (erstellt via API, setzt Remote sauber, pusht mit Token-URL).

## Gelernte API-/Shell-Fakten
- **Repo erstellen:** `POST /user/repos` nutzen — `POST /users/{username}/repos`
  liefert 404, auch bei korrektem Username. `/auth` ebenfalls 404 (Token-Typ);
  `GET /user`, `GET /user/repos`, `DELETE /repos/{owner}/{repo}` funktionieren.
- **Auth beim Push:** GitHub akzeptiert bei Git-over-HTTPS nur Basic-Auth →
  Prefix `x-access-token:` in der URL, kein Bearer-Token.
- **Upstream-Falle:** `git push -u <token-url>` hinterlegt die tokenisierte URL als
  Tracking-Zweig. Stattdessen: Push ohne `-u`, danach `fetch` + sauberes `origin/main`.
- **PowerShell-Pitfalls:** kein `&&` als Befehlstrenner; `$`-Variablen und
  Anführungszeichen in One-Linern (`python -c "..."`) werden geschluckt →
  lieber kleine Python-Skripte schreiben und ausführen.
