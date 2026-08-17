"""app_paths — katalogi i ścieżki aplikacji.

Ownership: jedyne źródło prawdy dla lokalizacji Cache/, LINKS/, Reports/,
config.json oraz legacy configu z katalogu domowego.

Behavior preserved from legacy single-file module.

UWAGA (kluczowe dla zgodności zachowania):
Legacy liczył SCRIPT_DIR jako katalog PLIKU głównego skryptu
(Path(__file__).resolve().parent). Ten moduł leży o jeden poziom niżej
(pakiet pylinks/), więc dla wersji nie-frozen bierzemy .parent.parent —
czyli katalog nadrzędny pakietu, który jest katalogiem aplikacji (obok
którego powstają Cache/ i LINKS/). Dzięki temu ścieżki są IDENTYCZNE jak
przed refaktorem. Wersja frozen (PyInstaller) bez zmian: katalog exe.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Katalogi tworzone automatycznie obok aplikacji
# (frozen = uruchomiony jako .exe przez PyInstaller)
SCRIPT_DIR = (
    Path(sys.executable).parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent.parent
)
CACHE_DIR   = SCRIPT_DIR / "Cache"    # baza SQLite + pobrane grafiki
LINKS_DIR   = SCRIPT_DIR / "LINKS"    # skróty (.lnk/.url) pogrupowane per platforma
REPORTS_DIR = SCRIPT_DIR / "Reports"  # raporty HTML / TXT z tworzenia skrótów

# FIX v7.4: config w katalogu programu (obok Cache/ i LINKS/), nie w $HOME
CONFIG_PATH = SCRIPT_DIR / "config.json"
_LEGACY_CONFIG_PATH = Path.home() / ".create-links-config.json"
