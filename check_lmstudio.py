"""Prueft, ob LM Studio unter http://localhost:1234 erreichbar ist und ein Modell geladen hat."""

import sys

try:
    import requests
except ImportError:
    print("FEHLER: 'requests' ist nicht installiert.")
    sys.exit(1)


def main() -> None:
    try:
        resp = requests.get("http://localhost:1234/v1/models", timeout=5)
    except Exception as exc:
        print(f"FEHLER: LM Studio nicht erreichbar unter http://localhost:1234")
        print(f"  Ursache: {exc}")
        sys.exit(1)

    if resp.status_code != 200:
        print(f"FEHLER: Unerwarteter Statuscode {resp.status_code} von LM Studio.")
        sys.exit(1)

    models = resp.json().get("data", [])
    if not models:
        print("WARNUNG: LM Studio ist erreichbar, aber es ist KEIN Modell geladen!")
        sys.exit(2)

    print("OK: LM Studio ist erreichbar. Geladene Modelle:")
    for m in models:
        print(f"  - {m.get('id')}")


if __name__ == "__main__":
    main()