"""
PyLinks_v7.py
=============
Ulepszona wersja skryptu do tworzenia skrótów z gier Steam/Extra/Epic/GOG.

PyLinks v8.4 — PS3/Steam eksport, multi-disc PS2, wydajność trybu Steam
======================================================================
Zmiany v8.4 (na bazie v8.3; pełny dziennik: CHANGELOG.md):
- Steam eksport: ROM-y uruchamiane przez .lnk (PS3/RPCS3) trafiają do biblioteki
  (read_lnk_target → exe+args+workdir). Raport HTML eksportu (dodane/zaktualizowane/
  pominięte/błąd/usunięty duplikat). Zbijanie duplikatów po appid (Disc 1/Disc 2).
- Multi-disc: .m3u zostaje w skanie/liście (frontendy filtrują dyski), ale skróty
  .lnk/Steam dla emulatorów bez obsługi .m3u (PS2/PCSX2) celują w istniejący Disc 1
  (weryfikacja istnienia; fallback na dostępny dysk). PS1/DuckStation dalej .m3u.
- Tryb Steam: FIX zwiechy przy ładowaniu miniatur (sieć zeszła z wątku UI na pulę);
  FIX przewijania kółkiem (NotifyInferior); grafiki Steam ZAPAMIĘTYWANE trwale
  (steam_art_by_key, symetrycznie do ikon .lnk).
- Wybór ikony/grafiki zapisywany NATYCHMIAST po kliknięciu (_persist_now) — przeżywa
  nagłe zamknięcie, można dokończyć wybór po ponownym uruchomieniu.

PyLinks v8.3 — grzbiety platform, cache, GOG workdir, strzałki skrótów
=====================================================================
Zmiany v8.3 (na bazie v8.2; pełny dziennik: CHANGELOG.md):
- Grzbiet platformy na ikonie (białe logo konsoli z pakietu console-logos),
  świadomy proporcji (portret vs kwadrat), ujednolicenie do 256, alias
  wariantów (SNESMSU1→SNES; priorytet: własny plik platformy).
- Okno „Grzbiety platform": kolorystyka + wybór wariantu logo online + wybór
  WŁASNEGO pliku z dysku (PNG/WEBP/…); lista zawiera też systemy ROM.
- FIX cache: wyłączony domyślny limit eksmisji (kasował grafiki), ochrona
  wybranych ikon z configu, reconcile z dysku, stabilny game_id (ROM po nazwie).
- GOG/extra: „Rozpocznij w" i argumenty z goggame-*.info; diagnostyka błędów
  tworzenia skrótów.
- SGDB/IGDB/TGDB: fix endpointu games/id, próg podobieństwa + świadomość
  platformy, przycisk „Wyczyść grafiki".
- Steam: poprawny shortcuts.vdf + tagi + kolekcje (cloudstorage), pobieranie
  grafik do grid/ z paskiem postępu; tryb Desktop/Steam w głównym oknie.
- Windows: opcja „Usuń/Przywróć strzałki na skrótach" (imageres.dll,197; UAC).

PyLinks v8.2 — Steam shortcuts.vdf binary VDF fix + tags
========================================================
Zmiany v8.2 (FIX: eksport non-Steam shortcuts + tagi/kolekcje Steam):
- FIX (przyczyna): dawny writer binarnego shortcuts.vdf NIE zapisywał
  bajtów-typów pól (0x00 obiekt / 0x01 string / 0x02 uint32) ani nie
  domykał obiektów bajtem 0x08 (zamiast tego wstawiał 0x00, a root w ogóle
  nie był domykany). Powstawał strukturalnie niepoprawny plik, który Steam
  odrzucał / kasował przy starcie. Writer i parser zostały przepisane na
  poprawny binarny KeyValues (KV1): root "shortcuts" → numerowane wpisy →
  pola z prawidłowymi znacznikami typów, obiekt "tags" oraz podwójne 0x08
  zamykające mapę "shortcuts" i cały dokument.
- NOWE: każdemu eksportowanemu skrótowi nadawany jest tag "Non-Steam"
  plus tag platformy/źródła (np. PS2, PS1, GameCube, MAME, PS3 dla ROM-ów,
  "Windows" dla gier extra). Tagi zapisywane są jako binarny obiekt VDF
  wewnątrz wpisu (grupy/kolekcje Steam), bez osobnego pliku tekstowego.
- NOWE: bezpieczny zapis — kopia zapasowa z datą, wykrywanie uszkodzonego
  pliku (kopia .corrupt-*), atomowy zapis przez plik tymczasowy + os.replace,
  ostrzeżenie gdy Steam jest uruchomiony, lepsza deduplikacja (AppName +
  Exe+LaunchOptions), diagnostyka i wewnętrzny self-test round-trip.
- NOWE: kolekcje per system zapisywane do magazynu cloudstorage
  (config/cloudstorage/cloud-storage-namespace-1.json) — nowy klient Steam nie
  używa już leveldb; zachowuje istniejące kolekcje, backup + atomowy zapis.
- NOWE: pobieranie grafik ze SteamGridDB do folderu grid/ (okładka 600×900,
  pozioma 460×215, hero, logo, ikona) z paskiem postępu i możliwością anulowania.
- NOWE: PRZEŁĄCZNIK TRYBU w głównym oknie — Desktop (.lnk) / Steam. Wspólna
  lista gier i korekta tytułu (Ręczne wyszukiwanie → sgdb_id). W trybie Steam
  panel grafik pokazuje zakładki typów i pozwala wybrać po jednej grafice na typ
  (zapis do game["steam_art"]), używane przy eksporcie.
- FIX: sgdb_get_by_id używał /api/v2/games/{id} (405 Method Not Allowed) —
  poprawiono na /api/v2/games/id/{id}; wklejenie URL-a SGDB znów działa.

Zmiany v8.1 (PERF: wirtualizacja listy biblioteki — duże kolekcje):
- PERF (główne): lewa lista NIE tworzy już 4 widgetów × N gier. Przy pełnych
  setach (No-Intro/MAME/GOG) to były dziesiątki tysięcy obiektów Tcl —
  tworzenie i niszczenie ich przy każdym rebuildzie/filtrze zawieszało GUI.
  Teraz utrzymywana jest stała PULA wierszy wielkości widocznego okna
  (~20 sztuk), przypinana do widocznych gier przy przewijaniu (place() na
  wysokim, pustym _list_inner; scrollregion = N*_row_h). Liczba widgetów
  jest stała niezależnie od rozmiaru kolekcji. Model bez zmian (stan trzyma
  g["enabled"]); istniejące helpery malujące (_color_from_state,
  _paint_list_row, _color_list_item) działają bez zmian — dla gier poza
  oknem są no-opem, a przy wejściu w okno wiersz jest malowany ze stanu.
- PERF (sortowanie): klucz sortowania listy robił po jednym exists()/stat()
  na KAŻDĄ widoczną grę przy każdym rebuildzie (na NTFS bardzo drogie).
  Teraz jedno CACHE_DIR.glob("*.ico") → zbiór w pamięci (_output_ico_stems).
- Nowe metody: _make_row/_bind_row/_relayout_rows/_reset_list_view/
  _ensure_gi_visible; _select_game(scroll=...) — klik przewija do gry,
  restore stanu po filtrze już nie. _row_h (domyślnie 22 px) to jedyny
  parametr do ewentualnego dostrojenia wysokości wiersza pod Windows.

Zmiany v8.0 (przeprojektowanie GUI: tryb prosty + porządki):
- NOWE (wariant 1): TRYB PROSTY — uproszczony widok w 3 krokach dla osób
  nietechnicznych. Trzy duże ponumerowane przyciski (Znajdź gry →
  Sprawdź obrazki → Utwórz skróty) z podświetleniem aktualnego kroku,
  banner statusu prostym językiem ("197 gotowych, 16 do sprawdzenia"),
  lista gier ze światłami (zielone = nic nie rób, żółte/czerwone =
  kliknij 2× aby poprawić przez wyszukiwanie obrazka), filtr "pokaż
  tylko do sprawdzenia", wiersz skanowania konsol (ROM) i tworzenie
  skrótów z prostym podsumowaniem zamiast tabeli DRY RUN. Przełączanie:
  przycisk "🙂 TRYB PROSTY" / "Tryb zaawansowany ▸"; wybrany tryb jest
  zapamiętywany (config ui_mode) i przywracany przy starcie. Nakładka
  NIE zmienia istniejącego UI — chowa je (pack_forget ze snapshotem
  pack_info) i przywraca 1:1 przy wyjściu; kroki wywołują istniejące
  funkcje (_scan_click, _manual_search_for_current, _create_thread).
- NOWE (wariant 2): toolbar pogrupowany w nazwane sekcje (BIBLIOTEKA |
  TWORZENIE | NARZĘDZIA) z separatorami; "DRY RUN" przemianowany na
  "PODGLĄD ZMIAN"; wszystkie przyciski toolbara i trybu prostego mają
  dymki podpowiedzi prostym językiem (nowa klasa Tooltip — pojawia się
  po 500 ms pod kursorem).

Zmiany v7.9.2:
- FIX (PS3/RPCS3): kopiowanie skrótów .lnk — naprawa duplikatów plików
  i losowo niepodmienionych ikon. Poprzednio plik był kopiowany prosto
  pod docelową nazwę i od razu modyfikowany przez WScript.Shell: (1)
  świeża kopia bywała chwilowo blokowana przez Defender/indexer, Save()
  padał po cichu → w LINKS zostawał skrót ze starą ikoną; (2) przy
  nazwach z nietypowymi znakami COM zapisywał wynik pod ścieżką
  znormalizowaną przez Win32 inaczej niż Python → w katalogu lądowały
  DWA pliki .lnk tej samej gry. Teraz cała modyfikacja odbywa się na
  pliku tymczasowym o ASCII-owej nazwie w katalogu docelowym, Save() ma
  retry (3×) na blokady AV, ikona jest WERYFIKOWANA ponownym odczytem
  IconLocation, a gotowy plik jest atomowo podmieniany (os.replace) pod
  docelową nazwą — w LINKS nigdy nie ma pliku w stanie pośrednim.
- NOWE: przed utworzeniem skrótu .lnk sprzątane są duplikaty z
  poprzednich uruchomień — pliki o nazwie identycznej po normalizacji
  (NFC/wielkość liter/kropki i spacje na końcu), ale innej ścieżce.

Zmiany v7.9.1:
- FIX UI: dodanie/usunięcie systemu w ⚙ ROMy natychmiast aktualizuje
  dropdown filtra widoku biblioteki ("ROM: ...") — wcześniej pasek
  platform budował się tylko przy starcie, więc nowy system pojawiał się
  w filtrze dopiero po restarcie programu. Gdy aktywny filtr wskazywał
  właśnie usunięty system, widok wraca do "wszystkie".

Zmiany v7.9 (cache-diet: warianty A + B + D):
- A (tiery): kandydaci ikon/grafik zapisywani są jako miniatury 256 px
  WEBP (tier='thumb') z zapamiętanym URL-em źródła; pełna wersja (tier=
  'full') pobierana jest lazy — dopiero gdy kandydat zostaje użyty do
  skrótu (ensure_full_asset przy CREATE; fallback: .ico z miniatury gdy
  brak sieci). Nowe kolumny assets.url i assets.tier (migracja ALTER
  TABLE w locie, stare wiersze = 'full').
- B (rekompresja): każdy zapisywany asset przechodzi przez WEBP —
  ikony bezstratnie (~30-40% mniej niż PNG), gridy/plakaty q88
  (wizualnie nieodróżnialne, ~60-75% mniej). Gdy WEBP wychodzi większy,
  zostaje oryginał.
- D (limit LRU): ustawienie "Limit cache assetów (MB)" (domyślnie 2048,
  0 = bez limitu). Po skanie eksmisja w tle: nie-wybrane assety gier od
  najdawniej używanych (games.last_sync) aż rozmiar zejdzie pod limit;
  wybrane ikony (wskazywane przez .lnk) nigdy nie są ruszane.
- NOWE: przycisk "🧹 KOMPAKTUJ" — jednorazowa migracja istniejącego
  cache: nie-wybrane assety → miniatury 256 px, wybrane → pełny WEBP;
  typowy zysk 85-95% rozmiaru bez utraty funkcjonalności (podgląd rysuje
  z miniatur, a pełne wersje wracają z internetu przy wyborze).
- Dla miniatur (tier='thumb') nie są już generowane duplikaty: miniatura
  256 px i plik .ico powstają dopiero przy promocji do 'full'.

Zmiany v7.8:
- FIX (zawieszanie GUI): ręczne wyszukiwanie tytułu (🔍) wykonuje całą
  pracę sieciową (SGDB search/get_by_id, pobieranie kandydatów, IGDB/TGDB)
  w wątku roboczym. Okno nie "zamiera" na czas żądań HTTP; dialogi wyboru
  i finalne odświeżenie wracają do wątku UI przez after(). Przycisk jest
  blokowany na czas wyszukiwania (brak podwójnych zapytań).
- PERF (odczyt cache): start z cache czyta assety WSZYSTKICH gier jednym
  zapytaniem SQL (assets_bulk) zamiast 2 zapytań per gra; istnienie plików
  sprawdzane jednym os.listdir() na katalog (współdzielony dir_cache)
  zamiast 2× stat() na wiersz; ścieżki liczone bez mkdir() (wcześniej
  mkdir(parents=True) przy KAŻDYM wywołaniu thumb_path). Upsert biblioteki
  w jednej transakcji (1 fsync zamiast 1 na grę). To samo w resolve ROM-ów
  (bulk prefetch przed workerami). Pomiar: ~4.4× szybciej już na tmpfs,
  na NTFS (Windows) zysk znacznie większy.
- NOWE (PS3/RPCS3): skróty .lnk utworzone w RPCS3 i wrzucone do roms/PS3
  są skanowane jako gry (każdy .lnk = jedna gra, tytuł = nazwa pliku).
  Nazwa służy do wyszukania ikon (SGDB/IGDB/TGDB), a przy CREATE skrót
  jest KOPIOWANY 1:1 do LINKS/PS3/ i w kopii podmieniana jest ikona
  (IconLocation) — komenda uruchamiania z RPCS3 zostaje nienaruszona.
  Preset PS3: primary_ext = lnk,iso,pkg; istniejące configi migrowane
  automatycznie (dopisywane "lnk"). Emulator nie jest wymagany, gdy w
  katalogu są .lnk. Diff-skan przy starcie widzi .lnk tak samo jak SKANUJ.

Zmiany v7.7:
- FIX: deduplikacja gubiła gry z serii — normalizacja tytułu sklejała
  tokeny po usunięciu interpunkcji ("I & II" → "III"), przez co np.
  DRAGON QUEST III HD-2D Remake znikał jako "duplikat" DRAGON QUEST
  I & II HD-2D Remake. Teraz interpunkcja → spacja, "&" ≡ "and".
- FIX: deduplikacja działa wyłącznie między różnymi źródłami; gry z tym
  samym źródłem lub różnymi appid nigdy nie są łączone.

Zmiany v7.6:
- ZMIANA: wszystkie gry PC (Steam/GOG/Epic/Extra) trafiają do jednego
  katalogu LINKS/PC. Stare skróty z LINKS/Steam|GOG|Epic|Extra są
  automatycznie przenoszone przy starcie; "Zaznacz brakujące" rozumie
  też starą strukturę.
- FIX: deduplikacja gier PC między źródłami — ta sama gra wykryta przez
  skaner GOG/Epic/Steam i jednocześnie jako folder Extra (np. Wiedźmin 3
  z GOG w katalogu Extra) pojawia się raz; wygrywa źródło
  steam > gog > epic > extra (porównanie po tytule i po katalogu gry).

Zmiany v7.5:
- FIX UI: przyciski "☑ Wszystkie / ☐ Żadna / ☑ Brakujące" (zaznaczanie
  checkboxów gier do utworzenia skrótów) przeniesione NAD listę gier —
  wcześniej były na końcu dolnego paska i wypadały poza krawędź okna.
  Obok licznik "Zaznaczone: X/Y". Działają w obrębie aktualnego filtra.

Zmiany v7.4:
- FIX: gry CD z parą plików .bin + .cue (oraz .gdi z trackami) są teraz
  uruchamiane plikiem .cue/.gdi, nigdy .bin — wcześniej wybór alfabetyczny
  brał .bin, przez co np. Dreamcast startował w trybie NAOMI i gra nie
  działała. Pliki danych referencowane przez .cue/.gdi są traktowane jak
  dyski pokryte przez M3U (nie tworzą osobnych wpisów na liście gier).
- Preset Dreamcast: primary_ext = gdi,cdi,chd,cue,iso.

Zmiany v7.3:
- FIX: "Zaznacz wszystkie / Odznacz / Zaznacz brakujące" — wspólna,
  niezawodna implementacja: stan ustawiany w modelu + twarda przebudowa
  listy (checkboxy odtwarzane z g["enabled"]), więc zaznaczanie działa
  niezależnie od ewentualnie nieaktualnych referencji widgetów.
- NOWE: auto-pobieranie grafik obejmuje też ROM-y — po SKANUJ ROM każda
  gra dostaje w tle plakaty SGDB + IGDB/TGDB. Zawodne Libretro/
  ScreenScraper są w tym pipeline pomijane (zostają dostępne ręcznie).

Zmiany v7.2:
- NOWE: filtr systemów ROM nad listą gier jest dynamicznym dropdownem —
  pozycje zawsze zgodne ze skonfigurowanymi systemami (+ "ROM: wszystkie").
- NOWE: po SKANUJ plakaty SGDB (pierwsza strona) i grafiki IGDB/TGDB/CDN
  pobierają się automatycznie w tle (3 wątki) — tak jak ikony — i są
  zapisywane do cache. Wyłączenie: "auto_fetch_art": false w configu.
- NOWE: przycisk "Zaznacz brakujące" — zaznacza tylko gry, które nie mają
  jeszcze skrótu .lnk/.url w katalogu LINKS (działa w obrębie filtra).

Zmiany v7.1:
- FIX: make_lnk — CoInitialize() per wątek (naprawia com_error -2147221008
  "Funkcja CoInitialize nie została wywołana" przy tworzeniu skrótów .lnk).
- FIX: przycisk 🎮 (wybór emulatora) — skan katalogu emulatorów przeniesiony
  do wątku w tle (okno pokazuje status zamiast wieszać GUI) + limit 2000
  plików EXE jako zabezpieczenie przed wskazaniem ogromnego katalogu.

Zmiany v7 (bugfixy + wydajność + usunięcie weryfikacji ROM):
- USUNIĘTE: cała weryfikacja ROM (CHD/RVZ/DAT/RAM-dysk, dialogi Verify
  i DAT Manager, zakładka "Weryfikacja" w Statystykach) — przeniesiona
  do osobnego programu. Plik schudł o ~2 800 linii.
- FIX: plakaty z "Pobierz plakaty" oraz grafiki z IGDB/TGDB/Steam CDN
  są teraz zapisywane do cache SQLite — przeżywają restart programu.
- FIX: przy starcie z cache scalane są OBA typy assetów (icons + grids);
  wcześniej "albo-albo" gubiło zapisane plakaty.
- FIX: zapamiętywanie wybranej ikony — stabilny klucz to remote_asset_id
  (spójny między sesjami); skan najpierw przywraca zapisany wybór,
  best_idx() tylko jako fallback (wcześniej nadpisywał wybór użytkownika).
- PERF: kliknięcie gry — przemalowywane są tylko 2 wiersze listy zamiast
  wszystkich; zapis configu z debounce; miniatury z LRU cache (także dla
  bajtów w RAM i ikon EXE); siatka kandydatów budowana porcjami po 12;
  preferowane są małe miniatury WEBP 128 px z AssetStore.
- FIX: AssetStore z RLock — bezpieczne zapisy SQLite z wielu wątków.
- FIX: fetch() nie odrzuca już odpowiedzi < 200 B (gubił małe ikony/JSON).
- BEZPIECZEŃSTWO: usunięte zaszyte w kodzie klucze API i SteamID64 —
  wpisz własne w Ustawieniach (stare klucze warto zregenerować!).

Zmiany v4-2 (optymalizacje i bugfixy):
- FIX KRYTYCZNY: _manual_search_for_current – sgdb_id ustawiany PRZED pobraniem
  kandydatów; po wyszukaniu wywołuje _rebuild_list() i _color_from_state()
- PERF: _rebuild_list z debounce 150 ms – nie niszczy widgetów przy każdym keypress
- PERF: _icons_to_cands z ThreadPoolExecutor (maks 8 równoczesnych fetch)
- PERF: jeden Image.open() + detect_icon_shape_img() zamiast dwóch decode
- PERF: _save_settings z debounce 500 ms – brak zapisu JSON przy każdym znaku
- PERF: AssetStore SQLite z PRAGMA journal_mode=WAL i synchronous=NORMAL

Zmiany względem v2 (wg propozycji użytkownika):
  1. Osobne okno "Ustawienia" (Steam API Key, SGDB API Key, SteamID64,
     włączanie Steam Web API, regex EXE, minimalna rozdzielczość ikony,
     preferowany typ ikony).
  2. Wyszukiwarka i szybkie filtry nad listą gier.
  3. Profile (Desktop PC / Laptop / TV) - osobny output_dir i zestaw
     zaznaczonych gier per profil.
  4. Auto-detekcja Steam.exe z rejestru + parser libraryfolders.vdf.
  5. Tryb "dry run" (podgląd) + raport HTML/TXT po utworzeniu skrótów.
  6. Integracja z Epic (LauncherInstalled.dat) i GOG (rejestr) +
     eksport do LaunchBox (XML) i Pegasus (metadata.txt).
  Refaktor: logika podzielona na klasy SteamScanner / IconManager /
  ShortcutCreator, a App trzyma tylko GUI.
"""
from __future__ import annotations

import os
import re
import sys
import json
import html
import queue
import time
import unicodedata   # v7.9.2: normalizacja nazw przy sprzątaniu duplikatów .lnk
import uuid          # v7.9.2: unikalne nazwy plików tymczasowych .lnk
import ctypes
import shutil
import binascii
import hashlib
import subprocess
import threading
import urllib.request
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image, ImageTk  # type: ignore
    PIL_OK = True
except Exception:  # pragma: no cover - Pillow required on Windows runtime
    Image = None  # type: ignore
    ImageTk = None  # type: ignore
    PIL_OK = False

IS_WIN = sys.platform.startswith("win")

try:
    import win32com.client  # type: ignore
    WIN32COM = True
except Exception:
    WIN32COM = False

try:
    import winreg  # type: ignore
    WINREG_OK = True
except Exception:
    winreg = None  # type: ignore
    WINREG_OK = False

# ---------------------------------------------------------------------------
# Ścieżki i stałe — WYDZIELONE do pakietu pylinks/ (faza 1 refaktoru).
# Compatibility bridge: import zwrotny zachowuje działanie reszty pliku —
# wszystkie nazwy pozostają dostępne w tym module dokładnie jak wcześniej.
# ---------------------------------------------------------------------------
from pylinks.app_paths import (
    SCRIPT_DIR, CACHE_DIR, LINKS_DIR, REPORTS_DIR,
    CONFIG_PATH, _LEGACY_CONFIG_PATH,
)
from pylinks.constants import (
    DEFAULT_STEAM_EXE, DEFAULT_EXTRA_DIR,
    DEFAULT_STEAM_API_KEY, DEFAULT_STEAM_ID64, DEFAULT_SGDB_KEY,
    DEFAULT_MIN_SIZE, DEFAULT_EXE_SKIP_REGEX, MATCH_THRESHOLD, IGDB_TGDB_MATCH_MIN,
    ICON_TYPES, ICON_SHAPES, MAX_ICONS_CHOICES,
    DEFAULT_MAX_ICONS, UNLIMITED_ICONS_CAP, C, _LEGACY_PC_DIRS,
)
from pylinks.config.defaults import _default_config
from pylinks.core.naming import safe_name
from pylinks.core.matching import name_similarity, needs_disambiguation
from pylinks.core.rom_args import _rom_build_args
from pylinks.core.compression import (
    _init_zstd, compress_stub, decompress_stub,
)
from pylinks.roms.presets import ROM_SYSTEM_PRESETS
from pylinks.config.migrate import migrate_config, _migrate_rom_v3

# _default_config()/migrate_config()/_migrate_rom_v3() → pakiet
# pylinks/config/ (import zwrotny na górze pliku).


def load_config() -> dict:
    # FIX v7.4: jednorazowa migracja starego configu z katalogu domowego
    # (~/.create-links-config.json) do katalogu programu (config.json)
    try:
        if not CONFIG_PATH.exists() and _LEGACY_CONFIG_PATH.exists():
            shutil.copy2(_LEGACY_CONFIG_PATH, CONFIG_PATH)
            print(f"[Config] Zmigrowano ustawienia: "
                  f"{_LEGACY_CONFIG_PATH} -> {CONFIG_PATH}")
    except Exception as e:
        print(f"[Config] Migracja nieudana: {e}")
    try:
        if CONFIG_PATH.exists():
            return migrate_config(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    except Exception:
        pass
    return _default_config()


def save_config(data: dict) -> None:
    try:
        CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Helpery
# ---------------------------------------------------------------------------
# safe_name() → pylinks/core/naming.py (import zwrotny).


# _ZSTD_OK / _init_zstd / compress_stub / decompress_stub →
# pylinks/core/compression.py (import zwrotny).


def _rom_pseudo_hash(rom_path: Path) -> str:
    """Szybki pseudo-hash pliku ROM dla re-identyfikacji.

    Format: <nazwa_pliku>:<CRC32(pierwsze 512KB+ostatnie 512KB) hex>:<rozmiar>
    Obliczanie: < 10 ms nawet dla 4 GB ISO.
    """
    import zlib
    CHUNK = 512 * 1024
    try:
        size = rom_path.stat().st_size
        with open(rom_path, "rb") as f:
            head = f.read(CHUNK)
            tail = b""
            if size > CHUNK * 2:
                f.seek(-CHUNK, 2)
                tail = f.read(CHUNK)
        crc = zlib.crc32(head + tail) & 0xFFFF_FFFF
        return f"{rom_path.name}:{crc:08X}:{size}"
    except Exception:
        return f"{rom_path.name}:ERR:0"


def _game_exists(g: dict) -> bool:
    """Sprawdź czy gra nadal istnieje na dysku.

    Steam / GOG / Epic / extra  → sprawdza game_dir lub launch_exe
    ROM                         → sprawdza czy plik ROM (rom_path) istnieje
    """
    src = g.get("source", "extra")
    if src == "rom":
        rp = g.get("rom_path", "")
        return bool(rp) and Path(rp).exists()
    # Dla Steam: sprawdź game_dir (folder gry)
    exe = g.get("launch_exe", "")
    gd  = g.get("game_dir", "")
    if exe:
        return Path(exe).is_file()
    if gd:
        return Path(gd).is_dir()
    return True   # nie możemy sprawdzić → zakładamy że istnieje


# _LEGACY_PC_DIRS → pylinks/constants.py (import zwrotny).


def _links_dir_for(g: dict) -> Path:
    """Katalog docelowy dla skrótów danej gry, względem LINKS_DIR.

    FIX v7.6: wszystkie gry PC (Steam/GOG/Epic/Extra) → LINKS/PC/
    rom → LINKS/<nazwa_systemu>/   (np. LINKS/PS2/)
    """
    src = g.get("source", "extra")
    if src == "rom":
        plat = (g.get("rom_platform") or "").strip()
        return LINKS_DIR / (safe_name(plat) if plat else "ROM")
    return LINKS_DIR / "PC"


def fetch(url: str, hdrs: dict | None = None, timeout: int = 12) -> bytes | None:
    try:
        h = {"User-Agent": "Mozilla/5.0"}
        if hdrs:
            h.update(hdrs)
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
            if getattr(r, "status", 200) >= 400:
                return None
            d = r.read()
        # FIX v7: nie odrzucamy małych odpowiedzi (drobne ikony/JSON < 200 B były gubione)
        return d if d else None
    except Exception:
        return None


def fetch_post(url: str, body: bytes | str, hdrs: dict | None = None,
               timeout: int = 12) -> bytes | None:
    """POST variant of fetch() — potrzebny dla IGDB API."""
    try:
        h = {"User-Agent": "Mozilla/5.0"}
        if hdrs:
            h.update(hdrs)
        data = body.encode() if isinstance(body, str) else body
        req = urllib.request.Request(url, data=data, headers=h, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = r.read()
        return d if len(d) > 0 else None
    except Exception:
        return None


# _rom_build_args() → pylinks/core/rom_args.py (import zwrotny).


# Emulatory, które POTRAFIĄ uruchomić grę z pliku .m3u (playlisty multi-disc).
# WAŻNE: PCSX2 (PS2) i Dolphin NIE obsługują .m3u — podanie playlisty kończy
# się „Unable to identify the ISO image type". Dla nich uruchamiamy pojedynczy
# dysk (zmiana dysku odbywa się w samym emulatorze).
_M3U_CAPABLE_EMUS = (
    "duckstation", "swanstation", "retroarch", "mednafen", "beetle",
    "mgba", "ppsspp",
)
_M3U_INCAPABLE_EMUS = ("pcsx2", "dolphin", "rpcs3", "xemu", "cemu", "vita3k")


def emulator_supports_m3u(exe: str) -> bool:
    """Czy dany emulator (po nazwie pliku exe) obsługuje playlisty .m3u.

    Whitelist known-good; jawny blacklist na PCSX2/Dolphin itd.; gdy nieznany —
    False (bezpiecznie: uruchom pojedynczy dysk, który zawsze się załaduje)."""
    try:
        b = Path(str(exe)).name.lower()
    except Exception:
        return False
    if any(x in b for x in _M3U_INCAPABLE_EMUS):
        return False
    return any(x in b for x in _M3U_CAPABLE_EMUS)


def resolve_multidisc_m3u(rom_path: str) -> str:
    """Jeśli ROM to jeden dysk zestawu objętego siostrzanym .m3u — zwróć .m3u.

    Chroni przed uruchamianiem gry wielopłytowej pojedynczym dyskiem (np.
    "...(Disc 1).chd") i stabilizuje wpis Steam (zawsze .m3u → jeden appid,
    te same argumenty → brak duplikatów per dysk). Czyta ZAWARTOŚĆ .m3u,
    nie zgaduje po nazwie. Gdy nic nie pasuje — zwraca oryginalną ścieżkę.

    UWAGA: wywołuj tylko dla emulatorów obsługujących .m3u (patrz
    emulator_supports_m3u) — PCSX2/Dolphin nie potrafią otworzyć playlisty.
    """
    try:
        p = Path(rom_path)
    except Exception:
        return rom_path
    if p.suffix.lower() == ".m3u" or not p.name:
        return rom_path
    try:
        parent = p.parent
        if not parent.is_dir():
            return rom_path
        target = p.resolve()
    except Exception:
        return rom_path
    for m3u in parent.glob("*.m3u"):
        try:
            for line in m3u.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                ref = Path(line)
                if not ref.is_absolute():
                    ref = m3u.parent / ref
                try:
                    if ref.resolve() == target:
                        return str(m3u)
                except Exception:
                    if str(ref).lower() == str(p).lower():
                        return str(m3u)
        except Exception:
            continue
    return rom_path


def _disc_number(name: str) -> int:
    """Numer dysku z nazwy: '...(Disc 2).chd' → 2. Brak → 1 (traktuj jak Disc 1)."""
    m = re.search(r'\(dis[ck]\s*(\d+)\)', str(name), re.I)
    return int(m.group(1)) if m else 1


def _m3u_disc_list(m3u_path: str) -> list:
    """Lista dysków z playlisty .m3u (Path, w kolejności z pliku)."""
    out: list = []
    try:
        p = Path(m3u_path)
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            ref = Path(line)
            if not ref.is_absolute():
                ref = p.parent / ref
            out.append(ref)
    except Exception:
        pass
    return out


def first_existing_disc(rom_path: str) -> str:
    """Pierwszy ISTNIEJĄCY dysk zestawu (Disc 1 preferowany).

    Dla emulatorów bez obsługi .m3u (PS2/PCSX2): skróty mają celować w prawdziwy
    dysk, nie w playlistę. WERYFIKUJE istnienie — jeśli Disc 1 brakuje (jak było
    ze Star Ocean, gdzie chwilowo był tylko Disc 2), bierze najniższy dysk który
    JEST na dysku. Zestaw ustalany z: samej .m3u, albo siostrzanej .m3u
    obejmującej podany dysk. Plik samodzielny (bez zestawu) — zwracany bez zmian.
    """
    rp = str(rom_path)
    if rp.lower().endswith(".m3u"):
        discs = _m3u_disc_list(rp)
    else:
        m3u = resolve_multidisc_m3u(rp)
        discs = _m3u_disc_list(m3u) if str(m3u).lower().endswith(".m3u") else []
    if not discs:
        return rp                      # samodzielny plik — nie ruszaj
    discs.sort(key=lambda c: (_disc_number(c.name), c.name.lower()))
    for c in discs:                    # najniższy numer, ale ISTNIEJĄCY
        try:
            if c.exists():
                return str(c)
        except Exception:
            pass
    return str(discs[0])               # nic nie istnieje — najniższy numer


def disc_path_for_emulator(rom_path: str, exe: str) -> str:
    """Dobiera ścieżkę ROM do możliwości emulatora:

    - emulator OBSŁUGUJE .m3u (DuckStation/RetroArch/PPSSPP…): playlista (dysk
      → .m3u jeśli istnieje) — pełny multi-disc;
    - emulator NIE obsługuje .m3u (PS2/PCSX2, Dolphin): pierwszy ISTNIEJĄCY dysk
      (Disc 1, fallback na istniejący). Zmiana dysku w samym emulatorze.

    .m3u zostaje w skanie/liście (frontendy filtrują duplikaty płyt) — tu tylko
    dobór ścieżki do SKRÓTU (.lnk / Steam).
    """
    if emulator_supports_m3u(exe):
        is_m3u = str(rom_path).lower().endswith(".m3u")
        return rom_path if is_m3u else resolve_multidisc_m3u(rom_path)
    return first_existing_disc(rom_path)


def fetch_api(url: str, hdrs: dict | None = None,
              timeout: int = 12) -> bytes | None:
    """Jak fetch(), ale BEZ filtru 200 bajtów.

    Używane dla endpointów API które mogą zwracać krótkie odpowiedzi JSON
    (błędy, potwierdzenia). fetch() odrzuca odpowiedzi < 200 B, co powoduje
    że błędy ScreenScrapera (np. 'Pas de devpassword !') są traktowane
    jako 'brak odpowiedzi' zamiast być parsowane i wyświetlane użytkownikowi.
    """
    try:
        h = {"User-Agent": "Mozilla/5.0"}
        if hdrs:
            h.update(hdrs)
        with urllib.request.urlopen(
                urllib.request.Request(url, headers=h), timeout=timeout) as r:
            d = r.read()
        return d if d else None
    except Exception:
        return None


# name_similarity()/needs_disambiguation() → pylinks/core/matching.py.


# ---------------------------------------------------------------------------
# v8.2: „grzbiet" platformy na ikonie — pionowy pasek jak grzbiet pudełka płyty
# (PS1/PS2/GameCube…). Pomaga odróżnić gry o identycznym tytule na różnych
# platformach po samej ikonie skrótu.
# ---------------------------------------------------------------------------
# platforma -> (kolor tła, kolor tekstu, etykieta na grzbiecie)
PLATFORM_SPINE: dict = {
    "PS1": ("#26272b", "#dfe3ea", "PS1"),   "PS2": ("#0b3aa0", "#ffffff", "PS2"),
    "PS3": ("#0a0a0a", "#ffffff", "PS3"),   "PS4": ("#00347a", "#ffffff", "PS4"),
    "PSP": ("#161616", "#f4c518", "PSP"),   "PSVITA": ("#161616", "#00a3e0", "VITA"),
    "GCN": ("#4a2f8f", "#ffffff", "GAMECUBE"), "WII": ("#dfe7ec", "#141414", "Wii"),
    "WIIU": ("#0a74c4", "#ffffff", "Wii U"), "NSW": ("#e60012", "#ffffff", "SWITCH"),
    "N64": ("#1f7a34", "#ffffff", "N64"),   "SNES": ("#4b3b96", "#ffffff", "SNES"),
    "NES": ("#8a2b2b", "#ffffff", "NES"),   "GB": ("#2f4f2f", "#c7e000", "GB"),
    "GBC": ("#5a2d82", "#ffffff", "GBC"),   "GBA": ("#37308f", "#ffffff", "GBA"),
    "NDS": ("#141414", "#ffffff", "NDS"),   "3DS": ("#c00000", "#ffffff", "3DS"),
    "SATURN": ("#101010", "#ffffff", "SATURN"), "DC": ("#efefef", "#e05a00", "DREAMCAST"),
    "MD": ("#101010", "#e0b000", "GENESIS"), "SMS": ("#161616", "#d42525", "SMS"),
    "GG": ("#161616", "#2a6bd6", "GAME GEAR"), "ARCADE": ("#0f0f0f", "#ffcc00", "ARCADE"),
    "MAME": ("#0f0f0f", "#ffcc00", "ARCADE"), "NEOGEO": ("#111111", "#e0c000", "NEO GEO"),
    "PCENGINE": ("#d97400", "#ffffff", "PC ENGINE"), "3DO": ("#161616", "#c8c8c8", "3DO"),
    "ATARI2600": ("#6f3617", "#ffffff", "ATARI"), "ATARI7800": ("#6f3617", "#ffffff", "ATARI"),
    "XBOX": ("#107c10", "#ffffff", "XBOX"), "X360": ("#107c10", "#ffffff", "X360"),
    "XONE": ("#107c10", "#ffffff", "XBOX ONE"), "PC": ("#2f3237", "#ffffff", "PC"),
}
_SPINE_FONT_CACHE: dict = {}


def _hex_rgba(h: str, a: int = 255) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def _auto_spine_color(key: str) -> str:
    d = hashlib.md5(key.encode("utf-8")).digest()
    r, g, b = d[0] % 130 + 25, d[1] % 130 + 25, d[2] % 130 + 25
    return f"#{r:02x}{g:02x}{b:02x}"


def _spine_font(size: int):
    f = _SPINE_FONT_CACHE.get(size)
    if f is not None or size in _SPINE_FONT_CACHE:
        return f
    font = None
    try:
        from PIL import ImageFont
        for name in ("arialbd.ttf", "segoeuib.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
            try:
                font = ImageFont.truetype(name, size)
                break
            except Exception:
                continue
        if font is None:
            font = ImageFont.load_default()
    except Exception:
        font = None
    _SPINE_FONT_CACHE[size] = font
    return font


# --- Auto-pobieranie logotypów platform (pakiet PRO100BYTE/console-logos) ---
# Prawdziwe logotypy konsol (oryginalne liternictwo). Znaki towarowe — użycie
# na własne ikony to prywatny użytek. Pobierane raz i cache'owane na dysku.
_CLOGOS_API = "https://api.github.com/repos/PRO100BYTE/console-logos/contents/"
_CLOGOS_RECOMMENDED = "Recommended Versions (Normal) (1 Per Platform) v2.1"
_CLOGOS_FULLSET = "Normal (1920x1080 max) (Full Set) v2.1"
_CLOGOS_SUBDIRS = ("Consoles", "Handhelds", "Arcade", "Computers")
# kolorystyki logotypów (nazwa dla użytkownika -> folder stylu w pakiecie)
SPINE_LOGO_STYLES: dict = {
    "Białe (na ciemny grzbiet)": "Light - Just White",
    "Kolorowe":                  "Light - Color",
    "Czarne (na jasny grzbiet)": "Dark - Just Black",
}
_SPINE_STYLE_DEFAULT = "Light - Just White"
# klucz platformy -> docelowa nazwa (dopasowanie rozmyte do nazw plików w repo)
PLATFORM_LOGO_TARGET: dict = {
    "PS1": "Sony PlayStation", "PS2": "Sony PlayStation 2",
    "PS3": "Sony PlayStation 3", "PS4": "Sony PlayStation 4",
    "PSP": "Sony PSP", "PSVITA": "Sony PlayStation Vita",
    "N64": "Nintendo 64", "SNES": "Super Nintendo Entertainment System",
    "NES": "Nintendo Entertainment System", "GCN": "Nintendo GameCube",
    "WII": "Nintendo Wii", "WIIU": "Nintendo Wii U", "NSW": "Nintendo Switch",
    "GB": "Nintendo Game Boy", "GBC": "Nintendo Game Boy Color",
    "GBA": "Nintendo Game Boy Advance", "NDS": "Nintendo DS", "3DS": "Nintendo 3DS",
    "MD": "Sega Genesis", "SMS": "Sega Master System", "GG": "Sega Game Gear",
    "SATURN": "Sega Saturn", "DC": "Sega Dreamcast",
    "3DO": "3DO Interactive Multiplayer", "PCENGINE": "NEC TurboGrafx-16",
    "NEOGEO": "SNK Neo Geo", "ATARI2600": "Atari 2600", "ATARI7800": "Atari 7800",
    "XBOX": "Microsoft Xbox", "X360": "Microsoft Xbox 360", "XONE": "Microsoft Xbox One",
    "MAME": "MAME", "ARCADE": "Arcade",
}

# Aliasy platform → kanoniczny klucz logo/grzbietu. Warianty/rozszerzenia
# konsol (np. SNES MSU-1, Famicom Disk System) używają logo konsoli bazowej.
PLATFORM_SPINE_ALIAS: dict = {
    "SNESMSU1": "SNES", "SNES-MSU1": "SNES", "MSU1": "SNES", "MSU-1": "SNES",
    "SFC": "SNES", "SUPERFAMICOM": "SNES",
    "FAMICOM": "NES", "FDS": "NES",
    "N64DD": "N64",
    "SEGACD": "MD", "MEGACD": "MD", "32X": "MD", "GENESIS": "MD", "MEGADRIVE": "MD",
    "TG16": "PCENGINE", "TURBOGRAFX16": "PCENGINE", "PCE": "PCENGINE",
    "PSX": "PS1", "PLAYSTATION": "PS1",
    "GAMECUBE": "GCN", "NGC": "GCN",
    "SWITCH": "NSW",
    "XBOX360": "X360",
    "XBOXONE": "XONE", "XBONE": "XONE",
    "VITA": "PSVITA",
    "DS": "NDS",
}


def _spine_canon_key(key: str) -> str:
    """Zwraca kanoniczny klucz platformy do logo/grzbietu (rozwija aliasy).

    Normalizuje najpierw klucz — usuwa spacje/separatory i uppercase — więc
    „X 360", „x-360", „X_360" → „X360" (pasuje do X360.png). Dzięki temu nazwa
    systemu ROM nie musi 1:1 odpowiadać nazwie pliku logo."""
    k = re.sub(r"[\s._\-]+", "", str(key or "")).upper()
    return PLATFORM_SPINE_ALIAS.get(k, k)


def _platform_logo_img(key: str, logo_dir):
    if not logo_dir:
        return None
    try:
        for ext in (".png", ".webp"):
            p = Path(logo_dir) / f"{key.upper()}{ext}"
            if p.is_file():
                return Image.open(p).convert("RGBA")
    except Exception:
        pass
    return None


def _ensure_logo_contrast(logo):
    """Czytelność na ciemnym grzbiecie: jeśli logo jest CIEMNE i jednobarwne
    (czarny/szary wordmark), zamień litery na jasne (biała sylwetka wg alfy).
    Logo kolorowe albo już jasne zostaje bez zmian (zachowuje markowe kolory)."""
    try:
        small = logo.convert("RGBA")
        small.thumbnail((64, 64))
        lum_sum = sat_sum = cnt = 0
        for r, g, b, a in small.getdata():
            if a < 40:
                continue
            mx = max(r, g, b)
            mn = min(r, g, b)
            lum_sum += 0.299 * r + 0.587 * g + 0.114 * b
            sat_sum += 0 if mx == 0 else (mx - mn) / mx
            cnt += 1
        if cnt == 0:
            return logo
        mean_lum = lum_sum / cnt
        mean_sat = sat_sum / cnt
        # ciemne + niska nasycenie = czarny wordmark → rozjaśnij do jasnego
        if mean_lum < 125 and mean_sat < 0.30:
            alpha = logo.convert("RGBA").split()[3]
            light = Image.new("RGBA", logo.size, (238, 238, 238, 0))
            light.putalpha(alpha)
            return light
        return logo
    except Exception:
        return logo


def download_platform_logos(logo_dir, only=None, progress=None,
                            style: str = _SPINE_STYLE_DEFAULT,
                            overwrite: bool = False) -> int:
    """Pobiera logotypy platform do logo_dir (folder „1 per platform" danego
    stylu). Dopasowanie rozmyte do PLATFORM_LOGO_TARGET. Zwraca ile pobrano.

    style: folder kolorystyki (SPINE_LOGO_STYLES.values()).
    overwrite: True nadpisuje istniejące (zmiana kolorystyki)."""
    logo_dir = Path(logo_dir)
    try:
        logo_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        return 0
    # 1. indeks plików PNG w repo (Consoles/Handhelds/Arcade/Computers)
    index = []  # (stem, download_url)
    for sub in _CLOGOS_SUBDIRS:
        path = urllib.request.quote(f"{_CLOGOS_RECOMMENDED}/{style}/{sub}", safe="/")
        d = fetch_api(_CLOGOS_API + path, timeout=20)
        if not d:
            continue
        try:
            arr = json.loads(d)
        except Exception:
            continue
        for e in arr:
            nm = e.get("name", "") if isinstance(e, dict) else ""
            url = e.get("download_url") if isinstance(e, dict) else None
            if nm.lower().endswith(".png") and url:
                index.append((nm[:-4], url))
    if not index:
        return 0
    got = 0
    for key, target in PLATFORM_LOGO_TARGET.items():
        if only and key not in only:
            continue
        out = logo_dir / f"{key}.png"
        if out.exists() and not overwrite:
            continue
        best = max(index, key=lambda it: name_similarity(target, it[0]), default=None)
        if not best or name_similarity(target, best[0]) < 0.55:
            continue
        b = fetch_api(best[1], timeout=25)
        if not b:
            continue
        try:
            tmp = out.with_name(out.name + ".tmp")
            tmp.write_bytes(b)
            os.replace(tmp, out)
            got += 1
            if progress:
                progress(key, best[0])
        except Exception:
            pass
    return got


def list_platform_logo_variants(platform_key, style: str = _SPINE_STYLE_DEFAULT,
                                limit: int = 40) -> list:
    """Warianty logo danej platformy z PEŁNEGO zestawu pakietu.

    Zwraca [(nazwa_pliku, download_url)]. Dopasowanie: znormalizowana nazwa
    pliku bez sufiksu „-NN" == docelowa nazwa platformy (PLATFORM_LOGO_TARGET)."""
    target = (PLATFORM_LOGO_TARGET.get(str(platform_key).upper())
              or PLATFORM_LOGO_TARGET.get(_spine_canon_key(platform_key)))
    if not target:
        return []

    def _norm(s: str) -> str:
        # znormalizuj: małe litery + zdejmij WIODĄCY prefiks producenta, bo
        # pełny zestaw bywa nazwany „Nintendo Super Nintendo…" a target bez
        # prefiksu. Rozróżnienie PS1/PS2 zostaje (różnią się końcówką).
        s = s.strip().lower()
        for _m in ("nintendo ", "sony ", "sega ", "microsoft ", "nec ",
                   "snk ", "atari "):
            if s.startswith(_m):
                return s[len(_m):]
        return s

    tnorm = _norm(target)
    out = []
    for sub in _CLOGOS_SUBDIRS:
        path = urllib.request.quote(f"{_CLOGOS_FULLSET}/{style}/{sub}", safe="/")
        d = fetch_api(_CLOGOS_API + path, timeout=20)
        if not d:
            continue
        try:
            arr = json.loads(d)
        except Exception:
            continue
        for e in arr:
            nm = e.get("name", "") if isinstance(e, dict) else ""
            url = e.get("download_url") if isinstance(e, dict) else None
            if not (nm.lower().endswith(".png") and url):
                continue
            # utnij sufiks wariantu „-NN" / „-N-NN" (grupy z MYŚLNIKIEM); liczby
            # będące częścią nazwy (Nintendo 64, PlayStation 2) są po spacji.
            base = _norm(re.sub(r'(-\s*\d+)+$', '', nm[:-4]))
            if base == tnorm:
                out.append((nm, url))
        if out:
            break
    return out[:limit]


def install_logo_from_url(url: str, logo_dir, key: str) -> bool:
    """Pobiera logo z URL i zapisuje jako <KEY>.png w logo_dir (PNG RGBA)."""
    b = fetch_api(url, timeout=30)
    if not b:
        return False
    try:
        ld = Path(logo_dir)
        ld.mkdir(parents=True, exist_ok=True)
        out = ld / f"{str(key).upper()}.png"
        if out.exists():
            try:
                shutil.copy2(out, out.with_suffix(".png.bak"))
            except Exception:
                pass
        if PIL_OK:
            Image.open(BytesIO(b)).convert("RGBA").save(out, "PNG")
        else:
            out.write_bytes(b)
        return True
    except Exception:
        return False


def add_platform_spine(img, platform: str, side: str = "left", frac: float = 0.22,
                       logo_dir: str = ""):
    """Nakłada pionowy „grzbiet" platformy na ikonę (PIL RGBA in/out).

    Jeśli w logo_dir jest logo platformy (<KEY>.png) — składa PRAWDZIWE logo
    obrócone wzdłuż grzbietu na ciemnym tle. W przeciwnym razie rysuje kolorowy
    pasek marki z tekstową etykietą (fallback). Zwraca oryginał, gdy PIL
    niedostępny / brak platformy / ikona za mała."""
    if not PIL_OK or not platform:
        return img
    try:
        from PIL import ImageDraw
        base = img.convert("RGBA")
        W0, H0 = base.size
        if min(W0, H0) < 24:
            return base
        # Supersampling z ZACHOWANIEM proporcji (dluzszy bok ~512) — dzieki temu
        # wiemy czy grafika jest kwadratowa czy portretowa. make_ico_bytes
        # zejdzie potem do 256 (maks .ico).
        _LONG = 512
        if max(W0, H0) != _LONG:
            _r = _LONG / max(W0, H0)
            base = base.resize((max(1, round(W0 * _r)), max(1, round(H0 * _r))),
                               Image.LANCZOS)
        W, H = base.size
        S = max(W, H)                     # bok kwadratowej ikony
        # Logo: NAJPIERW konkretna platforma (np. własny SNESMSU1.png), a gdy
        # go brak — alias do konsoli bazowej (SNESMSU1 -> SNES). Dzięki temu
        # własne logo wariantu ma priorytet, a bez niego jest grzbiet bazowy.
        orig_key = str(platform).upper()
        canon_key = _spine_canon_key(orig_key)
        key = orig_key
        logo = _platform_logo_img(orig_key, logo_dir)
        if logo is None and canon_key != orig_key:
            logo = _platform_logo_img(canon_key, logo_dir)
            key = canon_key
        if logo is not None:
            logo = _ensure_logo_contrast(logo)
        # kolor/etykieta: konkretny wpis, potem alias
        _info = PLATFORM_SPINE.get(orig_key) or PLATFORM_SPINE.get(canon_key)

        # Szerokosc grzbietu + czy zmniejszac grafike:
        #  - PORTRET (H>W): grzbiet wchodzi w NATURALNY margines (S-W) potrzebny
        #    do zrobienia kwadratu -> grafiki NIE zmniejszamy (W == S-sw),
        #  - KWADRAT/poziom: zwezamy grafike, zeby zrobic miejsce na grzbiet.
        target_sw = max(14, int(round(S * frac)))
        pad = S - W                       # >0 tylko dla portretu
        if int(S * 0.15) <= pad <= int(S * 0.42):
            sw = pad
            shrink = False
        else:
            sw = target_sw
            shrink = True

        # --- zbuduj grzbiet (sw x S) ---
        if logo is not None:
            bg = "#141414"
        else:
            bg = _info[0] if _info else _auto_spine_color(key)
        spine = Image.new("RGBA", (sw, S), _hex_rgba(bg))
        d = ImageDraw.Draw(spine)
        if side == "left":
            d.rectangle([sw - 2, 0, sw - 1, S - 1], fill=_hex_rgba("#000000", 120))
            d.line([(1, 0), (1, S)], fill=_hex_rgba("#ffffff", 55))
        else:
            d.rectangle([0, 0, 1, S - 1], fill=_hex_rgba("#000000", 120))
            d.line([(sw - 2, 0), (sw - 2, S)], fill=_hex_rgba("#ffffff", 55))

        if logo is not None:
            lg = logo.rotate(90 if side == "left" else -90, expand=True)
            scale = max(1, int(sw * 0.84)) / max(1, lg.width)
            if lg.height * scale > S * 0.94:
                scale = (S * 0.94) / max(1, lg.height)
            lg = lg.resize((max(1, int(lg.width * scale)),
                            max(1, int(lg.height * scale))), Image.LANCZOS)
            spine.alpha_composite(lg, ((sw - lg.width) // 2, (S - lg.height) // 2))
        else:
            label = _info[2] if _info else key[:10]
            fg = _info[1] if _info else "#ffffff"
            fsize = max(8, int(sw * 0.6))
            font = _spine_font(fsize)

            def _tw(fnt):
                try:
                    l, t, r, b = fnt.getbbox(label)
                    return r - l, b - t
                except Exception:
                    try:
                        return fnt.getsize(label)
                    except Exception:
                        return (len(label) * fsize // 2, fsize)

            if font is not None:
                tw, th = _tw(font)
                guard = 0
                while tw > S * 0.92 and fsize > 7 and guard < 60:
                    fsize -= 1
                    font = _spine_font(fsize)
                    tw, th = _tw(font)
                    guard += 1
                txt = Image.new("RGBA", (max(1, tw + 4), max(1, th + 4)), (0, 0, 0, 0))
                ImageDraw.Draw(txt).text((2, 2), label, font=font, fill=_hex_rgba(fg))
                txt = txt.rotate(90 if side == "left" else -90, expand=True)
                spine.alpha_composite(txt, ((sw - txt.width) // 2, (S - txt.height) // 2))

        # --- zloz kwadratowa ikone S x S ---
        out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        if shrink:
            art = base.resize((max(1, S - sw), S), Image.LANCZOS)
            if side == "left":
                out.alpha_composite(art, (sw, 0))
                out.alpha_composite(spine, (0, 0))
            else:
                out.alpha_composite(art, (0, 0))
                out.alpha_composite(spine, (S - sw, 0))
        else:
            # portret: grafika w NATYWNYM rozmiarze (bez zmniejszania), grzbiet
            # w marginesie. W == S - sw, wiec wypelnia obszar dokladnie.
            ay = (S - H) // 2
            if side == "left":
                out.alpha_composite(base, (sw, ay))
                out.alpha_composite(spine, (0, 0))
            else:
                out.alpha_composite(base, (0, ay))
                out.alpha_composite(spine, (S - sw, 0))
        return out
    except Exception:
        return img


def make_ico_bytes(img) -> bytes:
    img = img.convert("RGBA")
    # NIE ROZCIĄGAJ: grafiki niekwadratowe (np. okładka 600x900) wpasowujemy w
    # kwadrat z PRZEZROCZYSTYMI marginesami po bokach — proporcje zachowane, a
    # ikona jest kwadratem. Kwadratowe (w tym z grzbietem) zostają bez zmian.
    w, h = img.size
    if w != h:
        side = max(w, h)
        canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        canvas.paste(img, ((side - w) // 2, (side - h) // 2), img)
        img = canvas
    # UJEDNOLICENIE ikon: zawsze pełny, kwadratowy wpis 256x256 + mniejsze.
    # 256 to MAKSIMUM formatu .ico (nagłówek katalogu koduje bok na 1 bajcie,
    # 0=256; wpisy >256 są pomijane przez Windows/PIL — sprawdzone). Renderujemy
    # z wysokiej rozdzielczości (LANCZOS), więc 256 jest ostre na każdej ikonie.
    if img.size != (256, 256):
        img = img.resize((256, 256), Image.LANCZOS)
    sizes = [256, 128, 64, 48, 32, 16]
    frames = [img.resize((s, s), Image.LANCZOS) for s in sizes]
    buf = BytesIO()
    frames[0].save(buf, format="ICO", sizes=[(s, s) for s in sizes], append_images=frames[1:])
    return buf.getvalue()


def detect_icon_shape(img_bytes: bytes) -> str:
    """Heurystyczne wykrywanie kształtu ikony: 'square' / 'circular' / 'unknown'.

    - square: ikona proporcjonalna (w == h) bez przezroczystych narożników
    - circular: narożniki są przezroczyste (alpha w 4 rogach < 32), a środek nieprzezroczysty
    """
    if not PIL_OK or not img_bytes:
        return "unknown"
    try:
        img = Image.open(BytesIO(img_bytes))
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        w, h = img.size
        if w < 8 or h < 8:
            return "unknown"
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        corner_alpha = [img.getpixel((x, y))[3] for x, y in corners]
        center_alpha = img.getpixel((w // 2, h // 2))[3]
        # circular: wszystkie narożniki przezroczyste + środek widoczny
        if max(corner_alpha) < 48 and center_alpha > 128:
            return "circular"
        # square: narożniki nieprzezroczyste i proporcje 1:1
        if min(corner_alpha) > 128 and abs(w - h) <= max(2, min(w, h) // 32):
            return "square"
        # jeżeli jest kwadratowa po proporcjach, ale ma mieszane narożniki - traktuj jako square
        if abs(w - h) <= max(2, min(w, h) // 32):
            return "square"
        return "unknown"
    except Exception:
        return "unknown"



def detect_icon_shape_img(img) -> str:
    """Wersja detect_icon_shape przyjmująca gotowy obiekt PIL.Image (RGBA).
    Unikamy podwójnego Image.open() gdy bajty są już zdekodowane.
    """
    if not PIL_OK or img is None:
        return "unknown"
    try:
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        w, h = img.size
        if w < 8 or h < 8:
            return "unknown"
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        corner_alpha = [img.getpixel((x, y))[3] for x, y in corners]
        center_alpha = img.getpixel((w // 2, h // 2))[3]
        if max(corner_alpha) < 48 and center_alpha > 128:
            return "circular"
        if min(corner_alpha) > 128 and abs(w - h) <= max(2, min(w, h) // 32):
            return "square"
        if abs(w - h) <= max(2, min(w, h) // 32):
            return "square"
        return "unknown"
    except Exception:
        return "unknown"

def ico_max_size(path) -> int:
    try:
        d = Path(path).read_bytes()
        n = int.from_bytes(d[4:6], "little")
        ms = 0
        for i in range(n):
            off = 6 + i * 16
            bw = d[off]
            bh = d[off + 1]
            ms = max(ms, 256 if bw == 0 else bw, 256 if bh == 0 else bh)
        return ms
    except Exception:
        return 0


def thumb_from_bytes(b, size: int = 96):
    if not PIL_OK:
        return None
    try:
        img = Image.open(BytesIO(b)).convert("RGBA")
        img.thumbnail((size, size), Image.LANCZOS)
        bg = Image.new("RGBA", (size, size), (30, 30, 46, 255))
        bg.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
        return ImageTk.PhotoImage(bg)
    except Exception:
        return None


def thumb_from_path(path: str, size: int = 96):
    """Miniaturka bezpośrednio z pliku — unika czytania bytes do RAM."""
    if not PIL_OK or not path:
        return None
    try:
        img = Image.open(path).convert("RGBA")
        img.thumbnail((size, size), Image.LANCZOS)
        bg = Image.new("RGBA", (size, size), (30, 30, 46, 255))
        bg.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
        return ImageTk.PhotoImage(bg)
    except Exception:
        return None


# LRU cache miniatur – unika wielokrotnego dekodowania PIL przy przełączaniu gier
_THUMB_CACHE: dict[tuple, object] = {}
_THUMB_CACHE_MAX = 512  # max wpisów (każdy to ~80–200 KB RAM dla PhotoImage)


def _thumb_cache_get(key):
    """FIX v7: prawdziwe LRU — trafienie przesuwa wpis na koniec (dict
    zachowuje kolejność wstawiania), więc eviction usuwa najdawniej użyte."""
    if key in _THUMB_CACHE:
        val = _THUMB_CACHE.pop(key)
        _THUMB_CACHE[key] = val
        return val
    return None


def _thumb_cache_put(key, result):
    if result is None:
        return
    if len(_THUMB_CACHE) >= _THUMB_CACHE_MAX:
        try:
            _THUMB_CACHE.pop(next(iter(_THUMB_CACHE)))  # LRU evict
        except StopIteration:
            pass
    _THUMB_CACHE[key] = result


def thumb_cached(path: str, size: int = 96):
    """Miniaturka z LRU cache (klucz = ścieżka + rozmiar).
    Dzięki temu kliknięcie tej samej gry po raz drugi nie dekoduje PIL ponownie.
    """
    if not path:
        return None
    key = (path, size)
    hit = _thumb_cache_get(key)
    if hit is not None:
        return hit
    result = thumb_from_path(path, size)
    _thumb_cache_put(key, result)
    return result


def thumb_from_bytes_cached(b: bytes, cache_key: str, size: int = 96):
    """FIX v7: PERF — miniaturka z bajtów Z CACHE.

    Wcześniej kandydaci trzymani w RAM (świeżo pobrane plakaty) przechodzili
    przez thumb_from_bytes przy KAŻDYM przerysowaniu siatki — pełne
    Image.open + LANCZOS dla kilkudziesięciu grafik na każde kliknięcie gry.
    """
    if not b:
        return None
    if not cache_key:
        cache_key = hashlib.md5(b[:4096] + str(len(b)).encode()).hexdigest()
    key = ("bytes:" + cache_key, size)
    hit = _thumb_cache_get(key)
    if hit is not None:
        return hit
    result = thumb_from_bytes(b, size)
    _thumb_cache_put(key, result)
    return result


def thumb_from_exe_cached(exe_path, size: int = 96):
    """FIX v7: PERF — ikona EXE z cache (SHGetFileInfo + GDI tylko raz)."""
    if not exe_path:
        return None
    key = ("exe:" + str(exe_path), size)
    hit = _thumb_cache_get(key)
    if hit is not None:
        return hit
    result = thumb_from_exe(exe_path, size)
    _thumb_cache_put(key, result)
    return result


def thumb_from_exe(exe_path, size: int = 96):  # pragma: no cover - Windows-only
    if not IS_WIN:
        return None
    try:
        import ctypes.wintypes
        import win32ui  # type: ignore

        class SHFI(ctypes.Structure):
            _fields_ = [
                ("hIcon", ctypes.wintypes.HICON),
                ("iIcon", ctypes.c_int),
                ("dwAttrib", ctypes.wintypes.DWORD),
                ("szPath", ctypes.c_wchar * 260),
                ("szName", ctypes.c_wchar * 80),
            ]

        info = SHFI()
        res = ctypes.windll.shell32.SHGetFileInfoW(str(exe_path), 0, ctypes.byref(info), ctypes.sizeof(info), 0x100)
        if not res or not info.hIcon:
            return None
        hdc_s = ctypes.windll.user32.GetDC(None)
        hdc = win32ui.CreateDCFromHandle(hdc_s)
        mem = hdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(hdc, size, size)
        mem.SelectObject(bmp)
        mem.FillSolidRect((0, 0, size, size), 0)
        ctypes.windll.user32.DrawIconEx(mem.GetSafeHdc(), 0, 0, info.hIcon, size, size, 0, None, 3)
        ctypes.windll.user32.DestroyIcon(info.hIcon)
        bi = bmp.GetInfo()
        bits = bmp.GetBitmapBits(True)
        img = Image.frombuffer("RGBA", (bi["bmWidth"], bi["bmHeight"]), bits, "raw", "BGRA", 0, 1)
        mem.DeleteDC()
        hdc.DeleteDC()
        ctypes.windll.user32.ReleaseDC(None, hdc_s)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Auto-detekcja Steam z rejestru + parser libraryfolders.vdf
# ---------------------------------------------------------------------------
def detect_steam_exe() -> str | None:
    """Próbuje znaleźć Steam.exe w rejestrze (HKCU/HKLM)."""
    if not WINREG_OK:
        return None
    paths = [
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamExe"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"),
    ]
    for root, key, val in paths:
        try:
            with winreg.OpenKey(root, key) as h:
                data, _ = winreg.QueryValueEx(h, val)
                if val == "SteamExe":
                    p = Path(data)
                else:
                    p = Path(data) / "Steam.exe"
                if p.exists():
                    return str(p)
        except Exception:
            continue
    return None


def parse_libraryfolders_vdf(steam_exe: str) -> list[str]:
    """Parsuje libraryfolders.vdf i zwraca listę katalogów steamapps."""
    try:
        root = Path(steam_exe).parent
        vdf = root / "steamapps" / "libraryfolders.vdf"
        if not vdf.exists():
            vdf = root / "config" / "libraryfolders.vdf"
        if not vdf.exists():
            return []
        txt = vdf.read_text(encoding="utf-8", errors="replace")
        libs: list[str] = []
        for m in re.finditer(r'"path"\s+"((?:[^"\\]|\\.)*)"', txt):
            raw = m.group(1).replace("\\\\", "\\")
            lib = Path(raw) / "steamapps"
            if lib.is_dir():
                libs.append(str(lib))
        # usuń duplikaty z zachowaniem kolejności
        seen: set[str] = set()
        out: list[str] = []
        for p in libs:
            if p.lower() not in seen:
                seen.add(p.lower())
                out.append(p)
        return out
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Epic Games / GOG - skanery zainstalowanych gier
# ---------------------------------------------------------------------------
def _epic_manifests_dir() -> Path | None:
    pd = os.environ.get("PROGRAMDATA") or r"C:\ProgramData"
    d = Path(pd) / "Epic" / "EpicGamesLauncher" / "Data" / "Manifests"
    return d if d.is_dir() else None


def scan_epic_games() -> list[dict]:
    """Zwraca listę gier Epic zainstalowanych w systemie."""
    games: list[dict] = []
    d = _epic_manifests_dir()
    if not d:
        return games
    try:
        for f in sorted(d.glob("*.item")):
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
                name = data.get("DisplayName") or data.get("MainGameAppName") or ""
                app_name = data.get("AppName") or data.get("MainGameAppName") or ""
                install = data.get("InstallLocation") or ""
                launch = data.get("LaunchExecutable") or ""
                if not name or not app_name:
                    continue
                exe_path = str(Path(install) / launch) if install and launch else ""
                games.append({
                    "appid": None, "name": name, "content": "",
                    "game_dir": install or None, "source": "epic",
                    "epic_app_name": app_name, "launch_exe": exe_path or None,
                    "sgdb_results": [], "sgdb_id": None, "ambiguous": False,
                    "candidates": [], "selected_idx": None, "icons_loaded": False,
                    "enabled": True,
                })
            except Exception:
                continue
    except Exception:
        pass
    return games


def scan_gog_games() -> list[dict]:
    """Zwraca listę gier GOG z rejestru (HKLM\\...\\GOG.com\\Games)."""
    if not WINREG_OK:
        return []
    games: list[dict] = []
    roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\GOG.com\Games"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GOG.com\Games"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\GOG.com\Games"),
    ]
    seen_ids: set[str] = set()
    for root, key in roots:
        try:
            with winreg.OpenKey(root, key) as h:
                i = 0
                while True:
                    try:
                        sub = winreg.EnumKey(h, i)
                    except OSError:
                        break
                    i += 1
                    try:
                        with winreg.OpenKey(h, sub) as gh:
                            gid = _reg_val(gh, "gameID") or sub
                            if gid in seen_ids:
                                continue
                            seen_ids.add(gid)
                            name = _reg_val(gh, "gameName") or sub
                            path = _reg_val(gh, "path") or _reg_val(gh, "workingDir") or ""
                            exe = _reg_val(gh, "exe") or _reg_val(gh, "launchCommand") or ""
                            exe_full = str(Path(path) / exe) if path and exe and not os.path.isabs(exe) else exe
                            games.append({
                                "appid": None, "name": name, "content": "",
                                "game_dir": path or None, "source": "gog",
                                "gog_id": gid, "launch_exe": exe_full or None,
                                "sgdb_results": [], "sgdb_id": None, "ambiguous": False,
                                "candidates": [], "selected_idx": None, "icons_loaded": False,
                                "enabled": True,
                            })
                    except Exception:
                        continue
        except Exception:
            continue
    return games


def _reg_val(handle, name: str):
    if not WINREG_OK:
        return None
    try:
        v, _ = winreg.QueryValueEx(handle, name)
        return v
    except Exception:
        return None


def scan_extra_dir(extra_path: str) -> list[dict]:
    games: list[dict] = []
    p = Path(extra_path)
    if not p.is_dir():
        return games
    for subdir in sorted(p.iterdir()):
        if subdir.is_dir():
            games.append({
                "appid": None, "name": subdir.name, "content": "",
                "game_dir": str(subdir), "source": "extra",
                "sgdb_results": [], "sgdb_id": None, "ambiguous": False,
                "candidates": [], "selected_idx": None, "icons_loaded": False,
                "launch_exe": None, "enabled": True,
            })
    return games


def gog_playtask(game_dir) -> "tuple[str, str, str] | None":
    """Czyta goggame-*.info (GOG) i zwraca launcher z primary playTask jako
    (exe_abs, arguments, workingDir_abs) albo None.

    Dzięki temu gry GOG DOSBox/ScummVM/Windows dostają POPRAWNY sposób
    uruchomienia (ścieżka + argumenty + katalog roboczy), a nie zgadywany
    „największy .exe" (który dla DOSBoxa byłby gołym dosbox.exe bez -conf)."""
    try:
        gd = Path(game_dir)
        if not gd.is_dir():
            return None
        infos = sorted(gd.glob("goggame-*.info"))
        if not infos:
            return None
        data = json.loads(infos[0].read_text(encoding="utf-8-sig", errors="replace"))
        tasks = data.get("playTasks") or []

        def _is_file(t):
            return isinstance(t, dict) and t.get("type") == "FileTask" and t.get("path")

        prim = (next((t for t in tasks if _is_file(t) and t.get("isPrimary")), None)
                or next((t for t in tasks if _is_file(t) and t.get("category") == "game"), None)
                or next((t for t in tasks if _is_file(t)), None))
        if prim is None:
            return None
        rel = str(prim["path"]).replace("\\", "/")
        exe = gd / rel
        if not exe.exists():
            return None
        args = prim.get("arguments", "") or ""
        wd = str(prim.get("workingDir", "") or "").replace("\\", "/")
        workdir = str(gd / wd) if wd else str(exe.parent)
        return str(exe), args, workdir
    except Exception:
        return None


# ---------------------------------------------------------------------------
# SteamScanner - logika wykrywania gier Steam, manifestów, EXE
# ---------------------------------------------------------------------------
class SteamScanner:
    def __init__(self, steam_exe: str, extra_lib_dirs: list[str] | None = None,
                 use_libraryfolders_vdf: bool = True,
                 api_key: str | None = None, steam_id64: str | None = None,
                 use_web_api: bool = True):
        self.steam_exe = steam_exe
        self.extra_lib_dirs = list(extra_lib_dirs or [])
        self.use_libraryfolders_vdf = use_libraryfolders_vdf
        self.api_key = api_key
        self.steam_id64 = steam_id64
        self.use_web_api = use_web_api

    def steamapps_dirs(self) -> list[Path]:
        dirs: list[Path] = []
        seen: set[str] = set()

        def _add(p: Path) -> None:
            try:
                if p.is_dir():
                    k = str(p).lower()
                    if k not in seen:
                        seen.add(k)
                        dirs.append(p)
            except Exception:
                pass

        if self.steam_exe:
            _add(Path(self.steam_exe).parent / "steamapps")
            if self.use_libraryfolders_vdf:
                for lib in parse_libraryfolders_vdf(self.steam_exe):
                    _add(Path(lib))
        for part in self.extra_lib_dirs:
            _add(Path(part))
        return dirs

    def fetch_owned_games(self) -> list[dict]:
        if not (self.use_web_api and self.api_key and self.steam_id64):
            return []
        try:
            url = (f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
                   f"?key={self.api_key}&steamid={self.steam_id64}&include_appinfo=true&format=json")
            with urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
                timeout=30,
            ) as r:
                return json.loads(r.read()).get("response", {}).get("games", [])
        except Exception:
            return []

    def scan_installed(self) -> list[dict]:
        """Skanuje wszystkie appmanifest_*.acf w katalogach biblioteki."""
        games: list[dict] = []
        seen_appids: set[str] = set()
        for mdir in self.steamapps_dirs():
            try:
                for mf in sorted(mdir.glob("appmanifest_*.acf")):
                    try:
                        c = mf.read_text(encoding="utf-8", errors="replace")
                        ma = re.search(r'"appid"\s+"(\d+)"', c)
                        mn = re.search(r'"name"\s+"(.+?)"', c)
                        if not ma or not mn:
                            continue
                        appid = ma.group(1)
                        if appid in seen_appids:
                            continue
                        seen_appids.add(appid)
                        games.append({
                            "appid": appid, "name": mn.group(1), "content": c,
                            "game_dir": None, "source": "steam",
                            "sgdb_results": [], "sgdb_id": None, "ambiguous": False,
                            "candidates": [], "selected_idx": None,
                            "icons_loaded": False, "launch_exe": None, "enabled": True,
                        })
                    except Exception:
                        continue
            except Exception:
                continue
        games.sort(key=lambda g: g["name"].lower())
        return games

    def resolve_game_dir(self, game: dict) -> Path | None:
        m = re.search(r'"installdir"\s+"(.+?)"', game.get("content", ""))
        if not m:
            return None
        sub = m.group(1)
        for lib in self.steamapps_dirs():
            cand = Path(lib) / "common" / sub
            if cand.is_dir():
                return cand
        return None


# ---------------------------------------------------------------------------
# IconManager - SGDB, cache ICO, wybór kandydatów, filtry
# ---------------------------------------------------------------------------
class IconManager:
    def __init__(self, sgdb_key: str, min_size: int = DEFAULT_MIN_SIZE,
                 preferred_type: str = "any",
                 exe_skip_regex: str = DEFAULT_EXE_SKIP_REGEX,
                 shape_filter: str = "any",
                 max_icons: int = DEFAULT_MAX_ICONS):
        self.sgdb_key = sgdb_key
        self.min_size = int(min_size or DEFAULT_MIN_SIZE)
        self.preferred_type = preferred_type if preferred_type in ICON_TYPES else "any"
        self.shape_filter = shape_filter if shape_filter in ICON_SHAPES else "any"
        # max_icons: 0 lub wartość ujemna oznacza "max" (tylko cap bezpieczeństwa)
        self.max_icons = int(max_icons) if max_icons and int(max_icons) > 0 else 0
        try:
            self.skip_re = re.compile(exe_skip_regex, re.I)
        except re.error:
            self.skip_re = re.compile(DEFAULT_EXE_SKIP_REGEX, re.I)

    @property
    def effective_cap(self) -> int:
        """Efektywny limit ikon (dla 'max' używamy UNLIMITED_ICONS_CAP)."""
        return self.max_icons if self.max_icons > 0 else UNLIMITED_ICONS_CAP

    # -------- SGDB --------
    def sgdb_search(self, game_name: str, max_results: int = 8) -> list[dict]:
        if not self.sgdb_key:
            return []
        enc = urllib.request.quote(game_name)
        d = fetch_api(
            f"https://www.steamgriddb.com/api/v2/search/autocomplete/{enc}",
            hdrs={"Authorization": f"Bearer {self.sgdb_key}"},
        )
        if not d:
            return []
        try:
            return json.loads(d).get("data", [])[:max_results]
        except Exception:
            return []

    def sgdb_get_by_id(self, game_id: int) -> dict | None:
        """Pobierz metadane gry bezpośrednio po SGDB ID.

        Używane gdy autocomplete nie zwraca wyników dla rzadkich/starszych gier
        (np. Legaia 2, gry PS2), ale użytkownik zna URL strony SGDB.

        FIX v8.2: prawidłowy endpoint to GET /api/v2/games/id/{id}
        (poprzednio /api/v2/games/{id} zwracał 405 Method Not Allowed, przez co
        wklejenie URL-a typu steamgriddb.com/game/34233 kończyło się komunikatem
        "nie ma wpisu").
        """
        if not self.sgdb_key:
            return None
        d = fetch_api(
            f"https://www.steamgriddb.com/api/v2/games/id/{game_id}",
            hdrs={"Authorization": f"Bearer {self.sgdb_key}"},
        )
        if not d:
            return None
        try:
            obj = json.loads(d)
            if obj.get("success"):
                return obj.get("data")
        except Exception:
            pass
        return None

    def sgdb_search_with_fallback(self, query: str,
                                   max_results: int = 8) -> list[dict]:
        """Wyszukiwanie z automatycznym skracaniem zapytania gdy autocomplete zawodzi.

        SGDB autocomplete nie indeksuje wszystkich gier — szczególnie stare/rzadkie
        tytuły (PS1/PS2) często nie pojawiają się dla pełnego tytułu, ale już
        dla skróconego tak.

        Kolejność prób:
        1. Pełne zapytanie (jak dotychczas)
        2. Część przed " - "  (Legaia 2 - Duel Saga → Legaia 2)
        3. Część przed ": "   (Castlevania: SotN → Castlevania)
        4. Pierwsze 2 słowa   (Star Ocean - The Second Story → Star Ocean)
        5. Pierwsze słowo, ze stripem końcowej interpunkcji (ostateczność)

        UWAGA: Gdy nawet skrócone zapytania zawodzą (np. Legaia 2 nie zwraca
        wyników z autocomplete), użytkownik może wkleić URL ze SGDB —
        obsługiwane przez _manual_search_for_current jako tryb 2/3.
        """
        # Próba 1: pełne zapytanie
        results = self.sgdb_search(query, max_results)
        if results:
            return results

        seen: set[str] = {query}
        attempts: list[str] = []

        # Próba 2: przed " - "  →  "Legaia 2 - Duel Saga" → "Legaia 2"
        if " - " in query:
            attempts.append(query.split(" - ")[0].strip())

        # Próba 3: przed ": " lub ":"  →  "Castlevania: SotN" → "Castlevania"
        for sep in (": ", ":"):
            if sep in query:
                attempts.append(query.split(sep)[0].strip())
                break

        # Próba 4: pierwsze 2 słowa tokenizowane na spacjach
        words = query.split()
        if len(words) >= 3:
            first2 = " ".join(words[:2]).rstrip(":;,- ")
            attempts.append(first2)

        # Próba 5: pierwsze słowo bez końcowej interpunkcji
        if len(words) >= 2:
            first1 = words[0].rstrip(":;,- ")
            if len(first1) >= 4:
                attempts.append(first1)

        for attempt in attempts:
            if not attempt or attempt in seen:
                continue
            seen.add(attempt)
            print(f"[SGDB fallback] próba: {attempt!r}")
            results = self.sgdb_search(attempt, max_results)
            if results:
                print(f"[SGDB fallback] znaleziono {len(results)} wyników dla {attempt!r}")
                return results

        return []

    def sgdb_icons_for_id(self, sgdb_id) -> list[dict]:
        d = fetch_api(
            f"https://www.steamgriddb.com/api/v2/icons/game/{sgdb_id}",
            hdrs={"Authorization": f"Bearer {self.sgdb_key}"},
        )
        if not d:
            return []
        try:
            return json.loads(d).get("data", [])
        except Exception:
            return []

    def sgdb_icons_for_appid(self, appid) -> list[dict]:
        d = fetch_api(
            f"https://www.steamgriddb.com/api/v2/icons/steam/{appid}",
            hdrs={"Authorization": f"Bearer {self.sgdb_key}"},
        )
        if not d:
            return []
        try:
            return json.loads(d).get("data", [])
        except Exception:
            return []

    # -------- Square Grids (plakaty) --------
    def _fetch_grids(self, url_base: str, page: int, per_page: int) -> list[dict]:
        """Pobiera gridy z SGDB — KWADRATY oraz WSZYSTKIE wymiary, scalone.

        Historia: filtr tylko-kwadraty gubił ładne okładki 600x900 (portret);
        bez filtra SGDB zwraca top wg trafności = same portrety, a kwadraty (na
        ikonę) wypadają poza pierwsze `per_page`. Dlatego robimy DWA zapytania —
        kwadraty (512x512/1024x1024) i wszystkie wymiary — i scalamy (kwadraty
        pierwsze, potem reszta, bez duplikatów po id). Użytkownik ma jedno i drugie."""
        def _query(dims: str) -> list[dict]:
            url = f"{url_base}?"
            if dims:
                url += f"dimensions={dims}&"
            url += f"limit={per_page}&page={page}"
            print(f"[SGDB Grids] GET {url}")
            d = fetch_api(url, hdrs={"Authorization": f"Bearer {self.sgdb_key}"})
            if not d:
                print("[SGDB Grids] Brak odpowiedzi lub błąd HTTP")
                return []
            try:
                parsed = json.loads(d)
                print(f"[SGDB Grids] success={parsed.get('success')}, "
                      f"count={len(parsed.get('data', []))}")
                if not parsed.get("success"):
                    print(f"[SGDB Grids] API error: {parsed}")
                    return []
                return parsed.get("data", [])
            except Exception as e:
                print(f"[SGDB Grids] JSON parse error: {e}")
                return []

        squares = _query("512x512,1024x1024")   # kwadraty (na ikonę)
        alldim  = _query("")                     # wszystkie (okładki portret)
        out, seen = [], set()
        for it in squares + alldim:              # kwadraty pierwsze
            i = str(it.get("id", ""))
            if not i or i in seen:
                continue
            seen.add(i)
            out.append(it)
        print(f"[SGDB Grids] scalono: {len(squares)} kwadr. + "
              f"{len(alldim)} wsz. = {len(out)} unikalnych")
        return out

    def sgdb_grids_for_appid(self, appid, page: int = 0, per_page: int = 20) -> list[dict]:
        """Pobiera kwadratowe gridy dla gry Steam."""
        return self._fetch_grids(
            f"https://www.steamgriddb.com/api/v2/grids/steam/{appid}",
            page=page, per_page=per_page,
        )

    def sgdb_grids_for_id(self, sgdb_id, page: int = 0, per_page: int = 20) -> list[dict]:
        """Pobiera kwadratowe gridy dla gry po SGDB ID."""
        return self._fetch_grids(
            f"https://www.steamgriddb.com/api/v2/grids/game/{sgdb_id}",
            page=page, per_page=per_page,
        )

    def grids_to_cands(self, grids: list[dict]) -> list[dict]:
        """Konwertuje gridy SGDB na listę kandydatów z miniaturkami."""
        cands: list[dict] = []
        for ic in grids:
            full_url = ic.get("url", "")
            thumb_url = ic.get("thumb", "") or full_url
            if not thumb_url:
                print(f"[SGDB Grids] Brak URL w rekordzie: {ic}")
                continue
            print(f"[SGDB Grids] Pobieranie miniaturki: {thumb_url[:80]}")
            b = fetch(thumb_url)
            if not b:
                # fallback na pełny URL
                print(f"[SGDB Grids] thumb failed, próbuję pełny URL: {full_url[:80]}")
                b = fetch(full_url)
            if not b:
                print(f"[SGDB Grids] Pominięto (brak danych)")
                continue
            iw = ic.get("width", 0)
            ih = ic.get("height", 0)
            if PIL_OK:
                try:
                    iw, ih = Image.open(BytesIO(b)).size
                except Exception as e:
                    print(f"[SGDB Grids] PIL error: {e}")
            style = (ic.get("style") or "").lower()
            label = f"POSTER {iw}x{ih} [{style}]" if style else f"POSTER {iw}x{ih}"
            print(f"[SGDB Grids] OK -> {label}")
            cands.append({
                "type": "grid", "bytes": b, "w": iw, "h": ih,
                "style": style, "shape": "square",
                "label": label,
                "exe": None,
                "url": full_url,
                "remote_asset_id": str(ic.get("id", "")),
            })
        print(f"[SGDB Grids] Gotowe: {len(cands)}/{len(grids)} plakatów pobrane")
        return cands

    # -------- EXE scanning --------
    def find_exes(self, game_dir) -> list[Path]:
        found: list[Path] = []
        try:
            gd = Path(game_dir)
            for exe in gd.rglob("*.exe"):
                rel = exe.relative_to(gd)
                if len(rel.parts) > 5 or self.skip_re.search(exe.name):
                    continue
                found.append(exe)
        except Exception:
            pass
        found.sort(key=lambda f: f.stat().st_size if f.exists() else 0, reverse=True)
        return found

    # -------- Kandydaci --------
    def _icons_to_cands(self, icons: list[dict]) -> list[dict]:
        """Pobiera bajty ikon równolegle, filtruje po kształcie, ogranicza do max_icons.
        FIX: ThreadPoolExecutor zamiast sekwencyjnych fetch() + jeden Image.open() zamiast dwóch.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed as _as_completed
        cands: list[dict] = []
        icons = sorted(icons, key=lambda i: min(i.get("width", 0), i.get("height", 0)), reverse=True)
        cap = self.effective_cap
        scan_limit = min(len(icons), max(cap * 3, 30)) if self.shape_filter != "any" else min(len(icons), cap)
        icons_slice = icons[:scan_limit]

        # FIX: pobieramy równolegle (max 8 równoczesnych połączeń)
        def _fetch_one(ic):
            return ic, fetch(ic.get("url", ""))

        fetched: list[tuple] = []
        with ThreadPoolExecutor(max_workers=min(8, len(icons_slice) or 1)) as pool:
            futures = {pool.submit(_fetch_one, ic): ic for ic in icons_slice}
            # zachowaj oryginalną kolejność (posortowaną wg rozmiaru)
            results_map = {}
            for fut in _as_completed(futures):
                ic, b = fut.result()
                results_map[id(ic)] = (ic, b)
            fetched = [results_map[id(ic)] for ic in icons_slice if id(ic) in results_map]

        for ic, b in fetched:
            if len(cands) >= cap:
                break
            if not b:
                continue
            iw = ic.get("width", 0)
            ih = ic.get("height", 0)
            # FIX: jeden Image.open() dla rozmiaru I kształtu
            img_obj = None
            if PIL_OK:
                try:
                    img_obj = Image.open(BytesIO(b)).convert("RGBA")
                    iw, ih = img_obj.size
                except Exception:
                    img_obj = None
            # FIX: detect_icon_shape_img używa gotowego obiektu zamiast re-otwierać
            if self.shape_filter != "any":
                shape = detect_icon_shape_img(img_obj) if img_obj is not None else detect_icon_shape(b)
            else:
                shape = "unknown"
            if self.shape_filter != "any" and shape not in (self.shape_filter, "unknown"):
                continue
            if self.shape_filter == "square" and shape == "unknown" and iw and ih:
                if abs(iw - ih) > max(2, min(iw, ih) // 32):
                    continue
            style = (ic.get("style") or "").lower()
            tag = f" [{shape}]" if shape != "unknown" else (f" [{style}]" if style else "")
            cands.append({
                "type": "sgdb", "bytes": b,
                "url": ic.get("url", ""),   # v7.9: lazy-full re-download
                "remote_asset_id": str(ic.get("id", "")), "w": iw, "h": ih,
                "style": style, "shape": shape,
                "label": f"SGDB {iw}x{ih}{tag}",
                "exe": None,
            })
        return cands

    def candidates_for_steam(self, game: dict, scanner: SteamScanner) -> list[dict]:
        sgdb_cands = self._icons_to_cands(self.sgdb_icons_for_appid(game["appid"]))
        exe_cands: list[dict] = []
        game_dir = scanner.resolve_game_dir(game)
        if game_dir:
            for exe in self.find_exes(game_dir)[:3]:
                mb = exe.stat().st_size / 1024 / 1024
                exe_cands.append({
                    "type": "exe", "bytes": None, "w": 256, "h": 256,
                    "style": "exe", "shape": "square",
                    "label": f"EXE: {exe.name} ({mb:.1f}MB)",
                    "exe": str(exe),
                })
        return sgdb_cands + exe_cands

    def candidates_for_extra(self, game: dict, sgdb_id) -> list[dict]:
        sgdb_cands = self._icons_to_cands(self.sgdb_icons_for_id(sgdb_id)) if sgdb_id else []
        exe_cands: list[dict] = []
        game_dir = game.get("game_dir")
        if game_dir:
            for exe in self.find_exes(game_dir):
                mb = exe.stat().st_size / 1024 / 1024
                exe_cands.append({
                    "type": "exe", "bytes": None, "w": 256, "h": 256,
                    "style": "exe", "shape": "square",
                    "label": f"EXE: {exe.name} ({mb:.1f}MB)",
                    "exe": str(exe),
                })
        return sgdb_cands + exe_cands

    def best_idx(self, cands: list[dict]) -> int | None:
        """Wybierz najlepszą ikonę z uwzględnieniem preferowanego typu."""
        if not cands:
            return None
        # 1) preferowany typ + rozmiar OK
        if self.preferred_type != "any":
            for i, c in enumerate(cands):
                if (c["type"] == "sgdb" and self.preferred_type in (c.get("style") or "")
                        and min(c["w"], c["h"]) >= self.min_size):
                    return i
        # 2) dowolny SGDB >= min_size
        for i, c in enumerate(cands):
            if c["type"] == "sgdb" and min(c["w"], c["h"]) >= self.min_size:
                return i
        # 3) pierwszy EXE
        for i, c in enumerate(cands):
            if c["type"] == "exe":
                return i
        return 0

    def cache_ico(self, cache_dir: Path, uid: str, data: bytes,
                  platform: str = "", spine: bool = False,
                  side: str = "left", logo_dir: str = "") -> Path | None:
        if not PIL_OK:
            return None
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            img = Image.open(BytesIO(data)).convert("RGBA")
            if spine and platform:
                img = add_platform_spine(img, platform, side=side, logo_dir=logo_dir)
            ico_bytes = make_ico_bytes(img)
            # Nazwa z HASHEM treści: gdy ikona się ZMIENI, zmienia się ścieżka
            # → Windows nie serwuje starej z cache ikon (główna przyczyna „stara
            # grafika mimo nowej ikony", której nie naprawia nawet restart
            # explorera — bo per-ścieżkowy cache ikon zostaje). Ta sama treść =
            # ta sama nazwa (deterministycznie, bez zbędnych plików).
            h = hashlib.md5(ico_bytes).hexdigest()[:10]
            ico_file = cache_dir / f"{uid}_{h}.ico"
            # Sprzątnij poprzednie warianty tego uid (stare hashe + stara nazwa
            # bez hasha), żeby Cache nie puchło.
            for old in list(cache_dir.glob(f"{uid}_*.ico")) + [cache_dir / f"{uid}.ico"]:
                if old.name != ico_file.name:
                    try:
                        old.unlink(missing_ok=True)
                    except Exception:
                        pass
            ico_file.write_bytes(ico_bytes)
            if ico_max_size(str(ico_file)) >= self.min_size:
                return ico_file
        except Exception:
            pass
        return None


# ---------------------------------------------------------------------------
# ShortcutCreator - .lnk/.url/Epic/GOG/LaunchBox/Pegasus
# ---------------------------------------------------------------------------

# =============================================================================
#  DODATKOWE ŹRÓDŁA GRAFIK  (Steam CDN / Libretro / IGDB / ScreenScraper)
# =============================================================================

# Mapowanie skrótów platform → nazwy repozytoriów Libretro na GitHub
LIBRETRO_SYSTEM_MAP: dict[str, str] = {
    "PS1":      "Sony_-_PlayStation",
    "PS2":      "Sony_-_PlayStation_2",
    "PS3":      "Sony_-_PlayStation_3",
    "PSP":      "Sony_-_PlayStation_Portable",
    "N64":      "Nintendo_-_Nintendo_64",
    "SNES":     "Nintendo_-_Super_Nintendo_Entertainment_System",
    "NES":      "Nintendo_-_Nintendo_Entertainment_System",
    "GB":       "Nintendo_-_Game_Boy",
    "GBA":      "Nintendo_-_Game_Boy_Advance",
    "GBC":      "Nintendo_-_Game_Boy_Color",
    "NDS":      "Nintendo_-_Nintendo_DS",
    "GCN":      "Nintendo_-_GameCube",
    "WII":      "Nintendo_-_Wii",
    "SATURN":   "Sega_-_Saturn",
    "DC":       "Sega_-_Dreamcast",
    "MD":       "Sega_-_Mega_Drive_-_Genesis",
    "SMS":      "Sega_-_Master_System_-_Mark_III",
    "GG":       "Sega_-_Game_Gear",
    "ARCADE":   "MAME",
    "MAME":     "MAME",
    "NEOGEO":   "SNK_-_Neo_Geo",
    "NGP":      "SNK_-_Neo_Geo_Pocket",
    "ATARI2600":"Atari_-_2600",
    "ATARI7800":"Atari_-_7800",
    "3DO":      "3DO_Interactive_Multiplayer",
    "PCENGINE": "NEC_-_PC_Engine_-_TurboGrafx_16",
}

# Wbudowane szablony systemów ROM (nazwy zgodne z kluczami LIBRETRO_SYSTEM_MAP).
# Każdy preset to domyślna konfiguracja — użytkownik dostosowuje ścieżki.
# Dwie konwencje nazw folderów (obsługiwane równocześnie):
# • EmulationStation / Batocera:   ps2, n64, snes, megadrive, dreamcast …
# • No-Intro / Redump / Libretro:  Sony - PlayStation 2, Nintendo - Nintendo 64 …
# Przy auto-uzupełnianiu rom_dir program szuka pierwszego istniejącego folderu.

# ── RetroArch core → system mapping ──────────────────────────────────────────
# Klucz: stem pliku core (bez _libretro.dll/.so)
# Wartość: nazwa systemu (str) lub lista systemów (list[str])
RETROARCH_CORE_SYSTEMS: dict[str, str | list[str]] = {
    # PlayStation
    "mednafen_psx":           "PS1",
    "mednafen_psx_hw":        "PS1",
    "pcsx_rearmed":           "PS1",
    "swanstation":            "PS1",
    "duckstation":            "PS1",
    # PS2
    "pcsx2":                  "PS2",
    # PSP
    "ppsspp":                 "PSP",
    # NES
    "nestopia":               "NES",
    "fceumm":                 "NES",
    "mesen":                  "NES",
    "quicknes":               "NES",
    "mesen-s":                "SNES",
    # SNES
    "snes9x":                 "SNES",
    "snes9x2002":             "SNES",
    "snes9x2005":             "SNES",
    "snes9x2010":             "SNES",
    "bsnes":                  "SNES",
    "bsnes_hd_beta":          "SNES",
    "bsnes_mercury_accuracy": "SNES",
    "bsnes_mercury_balanced": "SNES",
    "bsnes_mercury_performance": "SNES",
    "mednafen_supafaust":     "SNES",
    # N64
    "mupen64plus_next":       "N64",
    "parallel_n64":           "N64",
    # GB / GBC
    "gambatte":               ["GB", "GBC"],
    "sameboy":                ["GB", "GBC"],
    "tgbdual":                ["GB", "GBC"],
    # GBA / GB / GBC
    "mgba":                   ["GBA", "GB", "GBC"],
    "vba_next":               ["GBA", "GB", "GBC"],
    "vbam":                   ["GBA", "GB", "GBC"],
    # NDS
    "desmume":                "NDS",
    "desmume2015":            "NDS",
    "melonds":                "NDS",
    # GameCube + Wii
    "dolphin":                ["GCN", "WII"],
    # Saturn
    "mednafen_saturn":        "SATURN",
    "yabause":                "SATURN",
    "yabasanshiro":           "SATURN",
    "kronos":                 "SATURN",
    # Dreamcast
    "flycast":                "DC",
    "flycast_gles2":          "DC",
    "redream":                "DC",
    # Mega Drive / Genesis
    "genesis_plus_gx":        "MD",
    "genesis_plus_gx_wide":   "MD",
    "picodrive":              ["MD", "SMS", "GG"],
    "blastem":                "MD",
    # Master System / Game Gear
    "gearsystem":             ["SMS", "GG"],
    # PC Engine
    "mednafen_pce":           "PCENGINE",
    "mednafen_pce_fast":      "PCENGINE",
    # MAME / Arcade
    "mame":                   "MAME",
    "mame2000":               "MAME",
    "mame2003":               "MAME",
    "mame2003_plus":          "MAME",
    "mame2010":               "MAME",
    "mame2015":               "MAME",
    "mame2016":               "MAME",
    # FinalBurn Neo (Arcade + Neo Geo)
    "fbneo":                  ["MAME", "NEOGEO"],
    "fbalpha2012":            ["MAME", "NEOGEO"],
    "fbalpha2012_neogeo":     "NEOGEO",
    # Atari
    "stella":                 "ATARI2600",
    "stella2014":             "ATARI2600",
    # 3DO
    "opera":                  "3DO",
    # Neo Geo Pocket
    "mednafen_ngp":           "NGP",
    "race":                   "NGP",
}

# Przyjazne nazwy corów (dla wyświetlania w dialogu)
RETROARCH_CORE_DISPLAY: dict[str, str] = {
    "mednafen_psx":           "Beetle PSX",
    "mednafen_psx_hw":        "Beetle PSX HW",
    "pcsx_rearmed":           "PCSX-ReARMed",
    "swanstation":            "SwanStation",
    "duckstation":            "DuckStation",
    "pcsx2":                  "PCSX2",
    "ppsspp":                 "PPSSPP",
    "nestopia":               "Nestopia UE",
    "fceumm":                 "FCEUmm",
    "mesen":                  "Mesen",
    "snes9x":                 "Snes9x",
    "bsnes":                  "bsnes",
    "bsnes_hd_beta":          "bsnes HD",
    "mednafen_supafaust":     "Supafaust",
    "mupen64plus_next":       "Mupen64Plus-Next",
    "parallel_n64":           "ParaLLEl N64",
    "gambatte":               "Gambatte",
    "sameboy":                "SameBoy",
    "mgba":                   "mGBA",
    "vba_next":               "VBA-Next",
    "melonds":                "melonDS",
    "desmume":                "DeSmuME",
    "dolphin":                "Dolphin",
    "mednafen_saturn":        "Beetle Saturn",
    "yabasanshiro":           "YabaSanshiro",
    "kronos":                 "Kronos",
    "flycast":                "Flycast",
    "genesis_plus_gx":        "Genesis Plus GX",
    "genesis_plus_gx_wide":   "Genesis Plus GX Wide",
    "picodrive":              "PicoDrive",
    "blastem":                "BlastEm",
    "gearsystem":             "GearSystem",
    "mednafen_pce":           "Beetle PCE",
    "mednafen_pce_fast":      "Beetle PCE Fast",
    "mame2003_plus":          "MAME 2003-Plus",
    "fbneo":                  "FinalBurn Neo",
    "stella":                 "Stella",
    "opera":                  "Opera (3DO)",
}


def _core_display(core_stem: str) -> str:
    """Przyjazna nazwa core do wyświetlania."""
    if core_stem in RETROARCH_CORE_DISPLAY:
        return RETROARCH_CORE_DISPLAY[core_stem]
    return core_stem.replace("_", " ").title()


def _exe_friendly_name(exe_path: str) -> str:
    """Przyjazna nazwa standalone emulatora na podstawie pliku exe."""
    stem = Path(exe_path).stem.lower()
    _MAP = {
        "duckstation":      "DuckStation",
        "duckstation-qt":   "DuckStation",
        "pcsx2":            "PCSX2",
        "pcsx2-qt":         "PCSX2",
        "epsxe":            "ePSXe",
        "ppsspp":           "PPSSPP",
        "ppsspp-qt":        "PPSSPP",
        "dolphin":          "Dolphin",
        "dolphin-emu":      "Dolphin",
        "project64":        "Project64",
        "mgba":             "mGBA",
        "mgba-qt":          "mGBA",
        "visualboyadvance-m": "VBA-M",
        "mednafen":         "Mednafen",
        "redream":          "redream",
        "flycast":          "Flycast",
        "rpcs3":            "RPCS3",
        "pcsx-r":           "PCSX-R",
        "mame":             "MAME",
        "cemu":             "Cemu (Wii U)",
        "citra":            "Citra (3DS)",
        "yuzu":             "yuzu (Switch)",
        "ryujinx":          "Ryujinx (Switch)",
        "snes9x":           "Snes9x",
        "fceux":            "FCEUX",
        "nestopia":         "Nestopia",
        "desmume":          "DeSmuME",
        "melonds":          "melonDS",
    }
    for key, display in _MAP.items():
        if key in stem:
            return display
    return Path(exe_path).stem   # fallback


def _rom_find_dir(base: str, dir_names: list[str]) -> str:
    """Zwróć pierwszą istniejącą ścieżkę base/name, lub base/dir_names[0] jako sugestię."""
    if not base:
        return ""
    for name in dir_names:
        p = Path(base) / name
        if p.is_dir():
            return str(p)
    return str(Path(base) / dir_names[0])  # nie znaleziono → sugestia


# ROM_SYSTEM_PRESETS → pylinks/roms/presets.py (import zwrotny).


class ExtraArtSources:
    """Dodatkowe źródła grafik uzupełniające SGDB.

    Wspierane serwisy
    ─────────────────
    Bez klucza API (włączone domyślnie):
      • Steam CDN      — oficjalne kapsułki/hero/library ze Steam Store
      • Libretro       — GitHub thumbnails dla emulatorów (box art, snap, title)

    Wymagają klucza / konta (domyślnie wyłączone):
      • IGDB            — Twitch IGDB API: box art, artworks, screenshots
                          klucz: Twitch Developer Console → Application
      • ScreenScraper   — retro-focused, świetny dla ROM-ów
                          klucz: darmowe konto na screenscraper.fr
    """

    LIBRETRO_BASE  = "https://raw.githubusercontent.com/libretro-thumbnails"
    IGDB_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    IGDB_API_URL   = "https://api.igdb.com/v4"
    SS_API_URL     = "https://www.screenscraper.fr/api2"

    # ScreenScraper numeric system IDs
    SS_SYSTEM_IDS: dict[str, int] = {
        "PS1": 57, "PS2": 58, "PS3": 59, "PSP": 61,
        "NES": 3,  "SNES": 4, "N64": 14, "GCN": 13, "WII": 16,
        "GB":  9,  "GBC": 10, "GBA": 12, "NDS": 15,
        "SATURN": 22, "DC": 23,
        "MD": 1, "SMS": 2, "GG": 21,
        "ARCADE": 75, "MAME": 75,
        "NEOGEO": 142,
    }

    def __init__(self, cfg: dict):
        src = cfg.get("extra_sources", {})
        self.use_steam_cdn      = bool(src.get("steam_cdn", True))
        self.use_libretro       = bool(src.get("libretro", True))
        self.use_igdb           = bool(src.get("igdb", False))
        self.igdb_client_id     = src.get("igdb_client_id", "").strip()
        self.igdb_client_secret = src.get("igdb_client_secret", "").strip()
        self.use_screenscraper  = bool(src.get("screenscraper", False))
        self.ss_user            = src.get("screenscraper_user", "").strip()
        self.ss_pass            = src.get("screenscraper_pass", "").strip()
        # devid/devpass: opcjonalne, rejestracja na screenscraper.fr → Compte → API
        # Jeśli puste — używamy ssid/sspassword jako fallback (niższy limit zapytań)
        self.ss_devid           = src.get("screenscraper_devid", "").strip()
        self.ss_devpass         = src.get("screenscraper_devpass", "").strip()
        self.use_tgdb           = bool(src.get("tgdb", False))
        self.tgdb_key           = src.get("tgdb_key", "").strip()
        self._igdb_tok: str     = ""
        self._igdb_tok_exp: float = 0.0
        self._lock = threading.Lock()

    # ──────────────────────────────────────────────────────────
    # TheGamesDB (wymaga klucza API — darmowa rejestracja na forum)
    # ──────────────────────────────────────────────────────────

    # Mapowanie platform na TGDB platform IDs
    TGDB_PLATFORM_IDS: dict[str, int] = {
        "PC": 1, "PS1": 10, "PS2": 11, "PS3": 12, "PS4": 4919,
        "PSP": 13, "PSVITA": 39,
        "N64": 3, "SNES": 6, "NES": 7, "GCN": 2, "WII": 9,
        "WIIU": 38, "NSW": 4971,
        "GB": 4, "GBC": 41, "GBA": 5, "NDS": 8, "3DS": 4912,
        "SATURN": 17, "DC": 16,
        "MD": 18, "SMS": 35, "GG": 20,
        "ARCADE": 23, "MAME": 23,
        "ATARI2600": 22, "ATARI7800": 30,
        "3DO": 25, "PCENGINE": 34,
        "NEOGEO": 24, "XBOX": 14, "X360": 15, "XONE": 4920,
    }

    # FIX v8.2: mapowanie platform na IGDB platform IDs — żeby wyszukiwanie było
    # świadome platformy (remake tego samego tytułu na inną platformę nie
    # przeszkadza). Klucze jak w rom_platform / TGDB_PLATFORM_IDS.
    IGDB_PLATFORM_IDS: dict[str, int] = {
        "PC": 6, "PS1": 7, "PS2": 8, "PS3": 9, "PS4": 48,
        "PSP": 38, "PSVITA": 46,
        "N64": 4, "SNES": 19, "NES": 18, "GCN": 21, "WII": 5,
        "WIIU": 41, "NSW": 130,
        "GB": 33, "GBC": 22, "GBA": 24, "NDS": 20, "3DS": 37,
        "SATURN": 32, "DC": 23,
        "MD": 29, "SMS": 64, "GG": 35,
        "ARCADE": 52, "MAME": 52,
        "ATARI2600": 59, "ATARI7800": 60,
        "3DO": 50, "PCENGINE": 86,
        "NEOGEO": 80, "XBOX": 11, "X360": 12, "XONE": 49,
    }

    def tgdb_candidates(self, title: str,
                         platform: str = "") -> list[dict]:
        """Wyszukaj w TheGamesDB i pobierz box art / fan art.

        Uzyskanie klucza API (darmowe):
        https://forums.thegamesdb.net/viewforum.php?f=10
        Wpisz w Ustawienia → Dodatkowe źródła → TheGamesDB API Key.
        """
        if not self.use_tgdb or not self.tgdb_key:
            return []
        enc   = urllib.request.quote(title)
        p_filter = ""
        if platform:
            pid = self.TGDB_PLATFORM_IDS.get(platform.upper())
            if pid:
                p_filter = f"&filter[platform]={pid}"
        url = (
            f"https://api.thegamesdb.net/v1/Games/ByGameName"
            f"?apikey={self.tgdb_key}&name={enc}"
            f"&fields=overview&include=boxart{p_filter}"
        )
        d = fetch_api(url, timeout=10)
        if not d:
            print(f"[TGDB] brak odpowiedzi dla {title!r}")
            return []
        try:
            resp = json.loads(d)
        except Exception:
            return []
        if resp.get("code") != 200:
            print(f"[TGDB] błąd API: code={resp.get('code')} "
                  f"status={resp.get('status')}")
            return []
        games = resp.get("data", {}).get("games", [])
        if not games:
            print(f"[TGDB] brak gier dla {title!r}")
            return []
        # FIX v8.2: wybierz najlepiej pasujący po nazwie (nie games[0]) i odrzuć
        # zbyt słabe dopasowanie — inaczej TGDB podstawia zupełnie inną grę.
        game = max(games, key=lambda gg: name_similarity(title, gg.get("game_title", "")))
        sim = name_similarity(title, game.get("game_title", ""))
        if sim < IGDB_TGDB_MATCH_MIN:
            print(f"[TGDB] odrzucono '{game.get('game_title','?')}' dla {title!r} "
                  f"(podobieństwo {sim:.2f} < {IGDB_TGDB_MATCH_MIN})")
            return []
        game_id = str(game.get("id", ""))
        print(f"[TGDB] {title!r} → {game.get('game_title','?')} "
              f"(id={game_id}, sim={sim:.2f})")

        boxart_block = resp.get("include", {}).get("boxart", {})
        base_url     = (boxart_block.get("base_url", {})
                        .get("original",
                             "https://cdn.thegamesdb.net/images/original/"))
        images       = boxart_block.get("data", {}).get(game_id, [])
        if not images:
            # fallback: second call to Games/Images endpoint
            img_url = (
                f"https://api.thegamesdb.net/v1/Games/Images"
                f"?apikey={self.tgdb_key}&games_id={game_id}"
            )
            d2 = fetch_api(img_url, timeout=10)
            if d2:
                try:
                    ir = json.loads(d2)
                    images   = ir.get("data", {}).get("images", {}).get(game_id, [])
                    base_url = (ir.get("data", {}).get("base_url", {})
                                .get("original", base_url))
                except Exception:
                    pass

        wanted = {"boxart", "fanart", "clearlogo", "banner"}
        cands: list[dict] = []
        for img in images:
            itype    = img.get("type", "")
            side     = img.get("side", "")
            filename = img.get("filename", "")
            if itype not in wanted or not filename:
                continue
            if itype == "boxart" and side not in ("", "front"):
                continue   # pomiń tył pudełka
            img_full = base_url + filename
            b = fetch(img_full, timeout=10)
            if not b:
                continue
            if PIL_OK:
                try:
                    w, h = Image.open(BytesIO(b)).size
                except Exception:
                    continue
            else:
                w = h = 0
            label = f"TGDB {itype}"
            if side:
                label += f" {side}"
            cands.append({
                "type":  "grid",
                "bytes": b, "w": w, "h": h,
                "style": "tgdb",
                "shape": ("square" if w and h
                          and abs(w - h) <= max(2, min(w, h) // 8)
                          else "unknown"),
                "label": f"{label} {w}x{h}",
                "exe":   None, "url": img_full,
                "remote_asset_id": f"tgdb_{game_id}_{img.get('id', '')}",
            })
        print(f"[TGDB] {len(cands)} grafik dla {title!r}")
        return cands

    # ──────────────────────────────────────────────────────────
    # Steam CDN (bez API key)
    # ──────────────────────────────────────────────────────────

    def steam_cdn_candidates(self, appid: str) -> list[dict]:
        """Pobierz grafiki Steam CDN dla gry Steam — brak potrzeby API key."""
        if not self.use_steam_cdn or not appid:
            return []
        base = f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}"
        urls = [
            (f"{base}/library_600x900_2x.jpg", "Steam library"),
            (f"{base}/header.jpg",             "Steam header"),
            (f"{base}/library_hero.jpg",        "Steam hero"),
            (f"{base}/capsule_616x353.jpg",     "Steam capsule"),
        ]
        cands = []
        for url, label in urls:
            b = fetch(url, timeout=8)
            if not b:
                continue
            w, h = 0, 0
            if PIL_OK:
                try:
                    w, h = Image.open(BytesIO(b)).size
                except Exception:
                    continue   # nie obraz (np. 404 HTML)
            cands.append({
                "type": "grid", "bytes": b, "w": w, "h": h,
                "style": "steam_cdn",
                "shape": ("square" if w and h
                          and abs(w - h) <= max(2, min(w, h) // 8)
                          else "unknown"),
                "label": f"{label} {w}x{h}",
                "exe": None, "url": url,
                "remote_asset_id": f"steamcdn_{appid}_{url.split('/')[-1]}",
            })
        print(f"[SteamCDN] appid={appid}: {len(cands)} grafik")
        return cands

    # ──────────────────────────────────────────────────────────
    # Libretro Thumbnails (GitHub, bez API key)
    # ──────────────────────────────────────────────────────────

    def libretro_candidates(self, platform: str, game_title: str) -> list[dict]:
        """Box art / snap ze zbiorów Libretro Thumbnails na GitHub.

        platform:   skrót np. "PS2" (musi być w LIBRETRO_SYSTEM_MAP)
        game_title: tytuł bez rozszerzenia i tagów regionalnych
        """
        if not self.use_libretro:
            return []
        system = LIBRETRO_SYSTEM_MAP.get(platform.upper(), "")
        if not system:
            print(f"[Libretro] nieznana platforma: {platform!r}")
            return []
        enc = urllib.request.quote(game_title, safe=" -.'()!")
        enc = enc.replace(" ", "%20")
        folders = [
            ("Named_Boxarts", "box art"),
            ("Named_Snaps",   "snap"),
            ("Named_Titles",  "title"),
        ]
        cands = []
        for folder, kind in folders:
            url = f"{self.LIBRETRO_BASE}/{system}/master/{folder}/{enc}.png"
            b = fetch(url, timeout=8)
            if not b:
                continue
            if PIL_OK:
                try:
                    img = Image.open(BytesIO(b))
                    w, h = img.size
                except Exception:
                    continue   # to był HTML 404, nie PNG
            else:
                w = h = 0
            cands.append({
                "type": "grid", "bytes": b, "w": w, "h": h,
                "style": "libretro",
                "shape": ("square" if w and h
                          and abs(w - h) <= max(2, min(w, h) // 8)
                          else "unknown"),
                "label": f"Libretro {kind} {w}x{h}",
                "exe": None, "url": url,
                "remote_asset_id": f"libretro_{system}_{folder}_{game_title[:40]}",
            })
        print(f"[Libretro] {platform}/{game_title!r}: {len(cands)} grafik")
        return cands

    # ──────────────────────────────────────────────────────────
    # IGDB (wymaga Twitch client_id + client_secret)
    # ──────────────────────────────────────────────────────────

    def _get_igdb_token(self) -> str:
        """Pobierz (lub odnów) OAuth Bearer token dla IGDB."""
        with self._lock:
            if self._igdb_tok and time.time() < self._igdb_tok_exp - 60:
                return self._igdb_tok
            if not (self.igdb_client_id and self.igdb_client_secret):
                return ""
            try:
                params = (
                    f"client_id={urllib.request.quote(self.igdb_client_id)}"
                    f"&client_secret={urllib.request.quote(self.igdb_client_secret)}"
                    f"&grant_type=client_credentials"
                )
                d = fetch_post(
                    f"{self.IGDB_TOKEN_URL}?{params}", b"",
                    hdrs={"Content-Type": "application/x-www-form-urlencoded"},
                )
                if not d:
                    return ""
                data = json.loads(d)
                self._igdb_tok = data["access_token"]
                self._igdb_tok_exp = time.time() + data.get("expires_in", 3600)
                print(f"[IGDB] nowy token (wygasa za {data.get('expires_in',0)//3600} h)")
                return self._igdb_tok
            except Exception as e:
                print(f"[IGDB] błąd tokenu: {e}")
                return ""

    def _igdb_query(self, endpoint: str, apicalypse: str) -> list[dict]:
        token = self._get_igdb_token()
        if not token:
            return []
        d = fetch_post(
            f"{self.IGDB_API_URL}/{endpoint}",
            apicalypse.encode(),
            hdrs={
                "Client-ID":     self.igdb_client_id,
                "Authorization": f"Bearer {token}",
                "Content-Type":  "text/plain",
            },
        )
        if not d:
            return []
        try:
            return json.loads(d)
        except Exception:
            return []

    def igdb_candidates(self, title: str, platform: str = "") -> list[dict]:
        """Wyszukaj w IGDB i pobierz cover + artworks.

        platform (opc.): klucz platformy (np. "PS2", "SNES") — gdy podany,
        wyszukiwanie PREFERUJE wynik na tej platformie, więc remake tego samego
        tytułu na innej platformie nie przeszkadza. Preferencja jest miękka:
        gdy brak trafienia na platformie, wybierany jest najlepszy po nazwie.

        Uzyskanie kluczy:
        1. Zaloguj się na dev.twitch.tv
        2. Utwórz Application (Category: Application)
        3. Skopiuj Client ID i wygeneruj Client Secret
        4. Wpisz w Ustawienia → Dodatkowe źródła → IGDB
        """
        if not self.use_igdb or not self.igdb_client_id:
            return []
        esc = title.replace('"', '\\"')
        games = self._igdb_query(
            "games",
            f'search "{esc}"; '
            f'fields id,name,platforms,cover.url,artworks.url,screenshots.url; '
            f'limit 12;'
        )
        if not games:
            print(f"[IGDB] brak wyników dla {title!r}")
            return []
        # FIX v8.2: NIE bierz games[0] na ślepo (IGDB potrafi zwrócić zły tytuł
        # jako pierwszy, np. "Turrican 2" dla "Final Fight 2"). Najpierw odsiej
        # po podobieństwie nazwy, potem PREFERUJ trafienie na właściwej platformie.
        named = [gg for gg in games
                 if name_similarity(title, gg.get("name", "")) >= IGDB_TGDB_MATCH_MIN]
        if not named:
            best = max(games, key=lambda gg: name_similarity(title, gg.get("name", "")))
            print(f"[IGDB] odrzucono '{best.get('name','?')}' dla {title!r} "
                  f"(najlepsze podobieństwo {name_similarity(title, best.get('name','')):.2f} "
                  f"< {IGDB_TGDB_MATCH_MIN})")
            return []
        pid = self.IGDB_PLATFORM_IDS.get((platform or "").upper())
        _sim = lambda gg: name_similarity(title, gg.get("name", ""))
        game = None
        if pid is not None:
            plat_matches = [gg for gg in named if pid in (gg.get("platforms") or [])]
            if plat_matches:
                game = max(plat_matches, key=_sim)
        if game is None:
            game = max(named, key=_sim)
        sim = _sim(game)
        plat_ok = (pid in (game.get("platforms") or [])) if pid is not None else None
        print(f"[IGDB] {title!r} [{platform or '-'}] → {game.get('name','?')} "
              f"(id={game.get('id')}, sim={sim:.2f}, platforma={'ok' if plat_ok else ('inna' if pid else 'n/d')})")

        def _fetch_img(raw_url: str, label: str, rid: str) -> dict | None:
            # IGDB daje URL do thumbnaila t_thumb; zamieniamy na HD
            for size in ("t_1080p", "t_cover_big", "t_720p"):
                url = raw_url.replace("t_thumb", size)
                if not url.startswith("http"):
                    url = "https:" + url
                b = fetch(url, timeout=10)
                if not b:
                    continue
                if PIL_OK:
                    try:
                        w, h = Image.open(BytesIO(b)).size
                    except Exception:
                        continue
                else:
                    w = h = 0
                return {
                    "type": "grid", "bytes": b, "w": w, "h": h,
                    "style": "igdb",
                    "shape": ("square" if w and h
                              and abs(w - h) <= max(2, min(w, h) // 8)
                              else "unknown"),
                    "label": f"IGDB {label} {w}x{h}",
                    "exe": None, "url": url,
                    "remote_asset_id": f"igdb_{rid}",
                }
            return None

        cands = []
        if (cover := game.get("cover")) and cover.get("url"):
            c = _fetch_img(cover["url"], "cover", f"cover_{game['id']}")
            if c:
                cands.append(c)
        for i, art in enumerate((game.get("artworks") or [])[:4]):
            if art.get("url"):
                c = _fetch_img(art["url"], f"art#{i+1}", f"art_{game['id']}_{i}")
                if c:
                    cands.append(c)
        for i, ss in enumerate((game.get("screenshots") or [])[:3]):
            if ss.get("url"):
                c = _fetch_img(ss["url"], f"ss#{i+1}", f"ss_{game['id']}_{i}")
                if c:
                    cands.append(c)
        print(f"[IGDB] {len(cands)} grafik dla {title!r}")
        return cands

    # ──────────────────────────────────────────────────────────
    # ScreenScraper (wymaga konta na screenscraper.fr)
    # ──────────────────────────────────────────────────────────

    def screenscraper_candidates(self, platform: str,
                                  game_title: str,
                                  rom_path: str = "") -> list[dict]:
        """Pobierz box art / screenshot ze ScreenScraper.fr.

        Rejestracja: https://www.screenscraper.fr/membreinscription.php
        Wpisz login i hasło w Ustawienia → Dodatkowe źródła → ScreenScraper.
        """
        if not self.use_screenscraper or not (self.ss_user and self.ss_pass):
            return []
        sys_id = self.SS_SYSTEM_IDS.get(platform.upper())
        if not sys_id:
            print(f"[ScreenScraper] nieznana platforma: {platform!r}")
            return []
        rom_name = (Path(rom_path).name if rom_path
                    else f"{game_title}.rom")
        # devid/devpass: jeśli nie podano własnych, użyj konta użytkownika
        # jako fallback (słabszy limit, ale działa dla małego użytku)
        devid   = self.ss_devid   or self.ss_user
        devpass = self.ss_devpass or self.ss_pass
        params: dict[str, str] = {
            "devid":      devid,
            "devpassword": devpass,
            "softname":   "PyLinks",
            "ssid":       self.ss_user,
            "sspassword": self.ss_pass,
            "systemeid":  str(sys_id),
            "romnom":     urllib.request.quote(rom_name),
            "output":     "json",
        }
        if rom_path and Path(rom_path).exists():
            try:
                import zlib
                with open(rom_path, "rb") as f:
                    data = f.read()
                params["crc"] = format(zlib.crc32(data) & 0xFFFFFFFF, "08X")
            except Exception:
                pass
        url = (f"{self.SS_API_URL}/jeuInfos.php?"
               + "&".join(f"{k}={v}" for k, v in params.items()))
        # fetch_api: bez filtru 200B — żeby parsować krótkie odpowiedzi błędów
        d = fetch_api(url, timeout=20)
        if not d:
            print(f"[ScreenScraper] brak odpowiedzi dla {game_title!r}")
            return []
        try:
            parsed = json.loads(d)
        except Exception:
            print(f"[ScreenScraper] błąd JSON dla {game_title!r}: {d[:120]}")
            return []
        # Sprawdź błąd API
        err = (parsed.get("header", {}).get("Error")
               or parsed.get("response", {}).get("error", ""))
        if err:
            print(f"[ScreenScraper] błąd API: {err}")
            return []
        resp = parsed.get("response", {}).get("jeu", {})
        wanted = {"box-2D", "box-2D-side", "ss", "sstitle"}
        ok_regions = {"", "wor", "eu", "us", "uk", "fr"}
        cands = []
        for media in resp.get("medias", []):
            if media.get("type") not in wanted:
                continue
            if media.get("region", "") not in ok_regions:
                continue
            img_url = media.get("url", "")
            if not img_url:
                continue
            b = fetch(img_url, timeout=12)
            if not b:
                continue
            if PIL_OK:
                try:
                    w, h = Image.open(BytesIO(b)).size
                except Exception:
                    continue
            else:
                w = h = 0
            mtype  = media.get("type", "")
            region = media.get("region", "")
            cands.append({
                "type": "grid", "bytes": b, "w": w, "h": h,
                "style": "screenscraper",
                "shape": ("square" if w and h
                          and abs(w - h) <= max(2, min(w, h) // 8)
                          else "unknown"),
                "label": f"SS {mtype} {region} {w}x{h}".strip(),
                "exe": None, "url": img_url,
                "remote_asset_id": (
                    f"ss_{platform}_{mtype}_{game_title[:30]}"),
            })
        print(f"[ScreenScraper] {len(cands)} grafik dla {game_title!r}")
        return cands

    # ──────────────────────────────────────────────────────────
    # Punkt wejścia: zbierz kandydatów ze wszystkich aktywnych źródeł
    # ──────────────────────────────────────────────────────────

    def candidates_for_game(self, game: dict,
                            include_rom_scrapers: bool = True) -> list[dict]:
        """Zbierz dodatkowych kandydatów dla jednej gry ze wszystkich źródeł.

        Wyniki dołącz do listy SGDB — nie zastępują jej.
        FIX v7.3: include_rom_scrapers=False pomija Libretro/ScreenScraper
        (zawodne) — używane przez auto-pobieranie grafik dla ROM-ów,
        które wtedy bierze tylko SGDB + IGDB/TGDB.
        """
        cands: list[dict] = []
        src    = game.get("source", "")
        appid  = game.get("appid", "")
        name   = game.get("name", "")
        plat   = (game.get("rom_platform") or "").upper()
        rom_p  = game.get("rom_path", "")
        # Tytuł bez tagów regionalnych (dla Libretro/SS)
        rom_title = (
            re.sub(r"\s*\([^)]*\)$", "", Path(rom_p).stem).strip()
            if rom_p else name
        )

        # Steam CDN — tylko dla gier Steam
        if src == "steam" and appid:
            cands += self.steam_cdn_candidates(appid)

        # Libretro — dla ROM-ów z rozpoznaną platformą
        if include_rom_scrapers and src == "rom" and plat:
            cands += self.libretro_candidates(plat, rom_title)

        # ScreenScraper — dla ROM-ów
        if include_rom_scrapers and src == "rom" and plat:
            cands += self.screenscraper_candidates(plat, rom_title, rom_p)

        # IGDB — dla wszystkich gier (gdy włączone i jest klucz). Platforma:
        # dla ROM-ów rom_platform, dla gier PC ("extra"/steam/gog/epic) → "PC".
        igdb_plat = plat if plat else ("PC" if src in ("steam", "extra", "gog", "epic") else "")
        if self.use_igdb and self.igdb_client_id and name:
            cands += self.igdb_candidates(name, platform=igdb_plat)

        # TheGamesDB — dla wszystkich gier (gdy włączone i jest klucz)
        if self.use_tgdb and self.tgdb_key and name:
            cands += self.tgdb_candidates(name, platform=plat or "")

        return cands


# =============================================================================
#  LOCAL CACHE LAYER
# =============================================================================
import sqlite3
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS games (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source      TEXT NOT NULL,
    appid       TEXT,
    sgdb_id     TEXT,
    name        TEXT NOT NULL,
    last_sync   REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS assets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id         INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    asset_type      TEXT NOT NULL,
    remote_asset_id TEXT NOT NULL,
    local_path      TEXT NOT NULL,
    width           INTEGER DEFAULT 0,
    height          INTEGER DEFAULT 0,
    checksum        TEXT DEFAULT '',
    last_sync       REAL DEFAULT 0,
    UNIQUE(game_id, asset_type, remote_asset_id)
);
CREATE INDEX IF NOT EXISTS idx_assets_game ON assets(game_id);
CREATE INDEX IF NOT EXISTS idx_games_appid  ON games(appid);
CREATE INDEX IF NOT EXISTS idx_games_sgdbid ON games(sgdb_id);
CREATE TABLE IF NOT EXISTS stubs (
    game_id   INTEGER PRIMARY KEY REFERENCES games(id),
    data      BLOB NOT NULL,
    rom_phash TEXT,
    stub_date REAL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_stubs_phash ON stubs(rom_phash);
"""


class AssetStore:
    """Lokalny cache assetow na dysku + SQLite metadata."""

    ASSET_TYPES = ("icons", "grids", "heroes", "logos", "covers")

    def __init__(self, cache_root: str | Path):
        self.root = Path(cache_root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.assets_dir = self.root / "assets"
        self.assets_dir.mkdir(exist_ok=True)
        db_path = self.root / "metadata.db"
        self._db = sqlite3.connect(str(db_path), check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")   # FIX: WAL eliminuje lock contention przy multi-thread sync
        self._db.execute("PRAGMA synchronous=NORMAL") # FIX: bezpieczne przyspieszenie zapisu
        self._db.row_factory = sqlite3.Row
        self._db.executescript(_DB_SCHEMA)
        self._db.commit()
        # v7.9 (cache-diet): migracja schematu — kolumny url (źródło do
        # ponownego pobrania pełnej wersji) i tier ('full' | 'thumb').
        # Stare bazy dostają kolumny w locie; istniejące wiersze = 'full'.
        for _ddl in ("ALTER TABLE assets ADD COLUMN url TEXT DEFAULT ''",
                     "ALTER TABLE assets ADD COLUMN tier TEXT DEFAULT 'full'"):
            try:
                self._db.execute(_ddl)
                self._db.commit()
            except sqlite3.OperationalError:
                pass   # kolumna już istnieje
        # FIX v7: jedno połączenie współdzielone przez wątki (scan / extra-art / UI)
        # — wszystkie zapisy serializujemy przez RLock
        self._lock = threading.RLock()

    def commit(self):
        """FIX v7: bezpieczny commit z lockiem (do batchy z commit=False)."""
        with self._lock:
            self._db.commit()

    # ------------------------------------------------------------------
    # Game records
    # ------------------------------------------------------------------
    def upsert_game(self, source: str, appid: str | None, sgdb_id: str | None,
                    name: str, commit: bool = True) -> int:
        """Insert or update gry; zwraca game_id.

        PERF v7.8: commit=False pozwala wsadowo upsertnąć całą bibliotekę
        w jednej transakcji (jeden fsync zamiast jednego na grę).
        Po pętli wywołaj self.commit().
        """
        with self._lock:  # FIX v7
            return self._upsert_game_locked(source, appid, sgdb_id, name,
                                            commit=commit)

    def _upsert_game_locked(self, source, appid, sgdb_id, name,
                            commit: bool = True) -> int:
        row = None
        if appid:
            cur = self._db.execute(
                "SELECT id FROM games WHERE source=? AND appid=? LIMIT 1",
                (source, appid),
            )
            row = cur.fetchone()
        # FIX v8.2: gry BEZ appid (ROM/extra/gog) — stabilny klucz to (source,
        # name). Wcześniej dopasowanie szło najpierw po sgdb_id, który przy
        # skanie bywa raz pusty, raz ustawiony → ten sam ROM dostawał NOWY
        # game_id (duplikaty i osierocone grafiki w cache). Teraz nazwa ma
        # priorytet, sgdb_id tylko jako fallback.
        if row is None and not appid:
            cur = self._db.execute(
                "SELECT id FROM games WHERE source=? AND name=? LIMIT 1",
                (source, name),
            )
            row = cur.fetchone()
        if row is None and sgdb_id:
            cur = self._db.execute(
                "SELECT id FROM games WHERE sgdb_id=? LIMIT 1",
                (str(sgdb_id),),
            )
            row = cur.fetchone()
        if row:
            # zaktualizuj sgdb_id tylko gdy podany (nie kasuj istniejącego)
            if sgdb_id:
                self._db.execute(
                    "UPDATE games SET name=?,sgdb_id=?,last_sync=? WHERE id=?",
                    (name, str(sgdb_id), time.time(), row["id"]),
                )
            else:
                self._db.execute(
                    "UPDATE games SET name=?,last_sync=? WHERE id=?",
                    (name, time.time(), row["id"]),
                )
            if commit:
                self._db.commit()
            return row["id"]
        cur = self._db.execute(
            "INSERT INTO games(source,appid,sgdb_id,name,last_sync) VALUES(?,?,?,?,?)",
            (source, appid or "", sgdb_id or "", name, time.time()),
        )
        if commit:
            self._db.commit()
        return cur.lastrowid

    def game_id_for(self, source: str, appid: str | None,
                    sgdb_id: str | None) -> int | None:
        with self._lock:  # FIX v7.4: odczyty też serializowane
            row = None
            if appid:
                row = self._db.execute(
                    "SELECT id FROM games WHERE source=? AND appid=? LIMIT 1",
                    (source, appid)).fetchone()
            if row is None and sgdb_id:
                row = self._db.execute(
                    "SELECT id FROM games WHERE sgdb_id=? LIMIT 1",
                    (str(sgdb_id),)).fetchone()
            return row["id"] if row else None

    def get_sgdb_id(self, game_id: int) -> str | None:
        """Odczytaj sgdb_id zapisane w SQLite dla danego game_id.

        Używane gdy ikony są ładowane z cache — sgdb_id nie jest wtedy
        zwracane przez SGDB API, ale jest zapisane w tabeli games z
        poprzedniego skanu. Potrzebne do pobierania plakatów (grids).
        """
        row = None
        with self._lock:  # FIX v7.4
            row = self._db.execute(
                "SELECT sgdb_id FROM games WHERE id=? LIMIT 1", (game_id,)
            ).fetchone()
        val = row["sgdb_id"] if row else None
        return val if val else None

    def sgdb_ids_bulk(self, game_ids: "list[int]") -> "dict[int, str]":
        """PERF v7.8: sgdb_id dla wielu gier jednym zapytaniem."""
        ids = [int(g) for g in game_ids if g]
        out: dict[int, str] = {}
        if not ids:
            return out
        CHUNK = 500
        with self._lock:
            for i in range(0, len(ids), CHUNK):
                chunk = ids[i:i + CHUNK]
                ph = ",".join("?" * len(chunk))
                for row in self._db.execute(
                        f"SELECT id, sgdb_id FROM games WHERE id IN ({ph})",
                        chunk).fetchall():
                    if row["sgdb_id"]:
                        out[row["id"]] = row["sgdb_id"]
        return out

    # ------------------------------------------------------------------
    # Asset records
    # ------------------------------------------------------------------
    def asset_exists(self, game_id: int, asset_type: str,
                     remote_id: str) -> bool:
        with self._lock:  # FIX v7.4
            cur = self._db.execute(
                "SELECT local_path FROM assets "
                "WHERE game_id=? AND asset_type=? AND remote_asset_id=? LIMIT 1",
                (game_id, asset_type, str(remote_id)),
            )
            row = cur.fetchone()
        if not row:
            return False
        return Path(row["local_path"]).exists()

    def get_assets(self, game_id: int,
                   asset_type: str) -> list[sqlite3.Row]:
        with self._lock:  # FIX v7.4: tu wystąpił InterfaceError z 3 wątków autoart
            cur = self._db.execute(
                "SELECT * FROM assets WHERE game_id=? AND asset_type=? "
                "ORDER BY width DESC",
                (game_id, asset_type),
            )
            return cur.fetchall()

    def all_assets(self, game_id: int) -> list[sqlite3.Row]:
        with self._lock:  # FIX v7.4
            cur = self._db.execute(
                "SELECT * FROM assets WHERE game_id=? ORDER BY asset_type,width DESC",
                (game_id,),
            )
            return cur.fetchall()

    def has_asset_prefix(self, game_id: int, asset_type: str,
                         prefix: str) -> bool:
        """FIX v7.4: czy gra ma już w cache asset o remote_asset_id
        zaczynającym się od prefiksu (np. 'igdb_', 'tgdb_').
        Używane przez SYNC do pomijania zbędnych zapytań API."""
        with self._lock:
            row = self._db.execute(
                "SELECT 1 FROM assets WHERE game_id=? AND asset_type=? "
                "AND remote_asset_id LIKE ? LIMIT 1",
                (game_id, asset_type, prefix + "%"),
            ).fetchone()
        return row is not None

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------
    def asset_dir(self, sgdb_id_or_key: str, asset_type: str) -> Path:
        d = self.assets_dir / str(sgdb_id_or_key) / asset_type
        d.mkdir(parents=True, exist_ok=True)
        return d

    def asset_path(self, sgdb_id_or_key: str, asset_type: str,
                   remote_id: str, ext: str = ".png") -> Path:
        return self.asset_dir(sgdb_id_or_key, asset_type) / f"{remote_id}{ext}"

    def thumb_path(self, sgdb_id_or_key: str, asset_type: str,
                   remote_id: str, size: int = 128) -> Path:
        d = self.asset_dir(sgdb_id_or_key, asset_type) / "thumbs"
        d.mkdir(exist_ok=True)
        return d / f"{remote_id}_{size}.webp"

    # ── PERF v7.8: wersje read-only (bez mkdir) — ścieżka odczytu z cache ──
    # thumb_path()/asset_dir() robiły mkdir(parents=True) przy KAŻDYM wywołaniu.
    # Przy 500 grach × 10 assetów to tysiące syscalli tylko po to, żeby
    # policzyć ścieżkę do sprawdzenia. Na odczycie katalogów nie tworzymy.
    def asset_dir_ro(self, sgdb_id_or_key: str, asset_type: str) -> Path:
        return self.assets_dir / str(sgdb_id_or_key) / asset_type

    def thumb_path_ro(self, sgdb_id_or_key: str, asset_type: str,
                      remote_id: str, size: int = 128) -> Path:
        return (self.asset_dir_ro(sgdb_id_or_key, asset_type)
                / "thumbs" / f"{remote_id}_{size}.webp")

    @staticmethod
    def _dir_listing(dir_cache: dict, d: Path) -> set:
        """PERF v7.8: jeden os.listdir() na katalog zamiast Path.exists()
        per plik. dir_cache jest współdzielony w obrębie jednej operacji
        (np. całego startu z cache) — istnienie pliku to lookup w secie."""
        key = str(d)
        got = dir_cache.get(key)
        if got is None:
            try:
                got = set(os.listdir(d))
            except OSError:
                got = set()
            dir_cache[key] = got
        return got

    def ico_path(self, sgdb_id_or_key: str, remote_id: str) -> Path:
        d = self.assets_dir / str(sgdb_id_or_key) / "icons"
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{remote_id}.ico"

    # ------------------------------------------------------------------
    # Save asset
    # ------------------------------------------------------------------
    THUMB_TIER_PX  = 256   # maks. bok pliku tier='thumb'
    WEBP_Q_FULL    = 88    # jakość WEBP pełnych gridów/plakatów
    WEBP_Q_THUMB   = 85    # jakość WEBP miniatur-kandydatów

    @classmethod
    def _recompress_bytes(cls, data: bytes, asset_type: str,
                          tier: str) -> tuple[bytes, str]:
        """v7.9 (cache-diet): rekompresja przy zapisie.

        tier='thumb' → zmniejszenie do 256 px + WEBP q85 (kandydat do
                       przeglądania; pełna wersja pobierana lazy z url).
        tier='full'  → ikony: lossless WEBP (bez straty, ~30-40% mniej niż
                       PNG); gridy/plakaty: WEBP q88 (wizualnie
                       nieodróżnialne, ~60-75% mniej).
        Zwraca (bytes, ext). Gdy PIL niedostępny / konwersja się nie
        opłaca / plik nie jest obrazem — oryginalne bajty i '.png'.
        """
        if not PIL_OK:
            return data, ".png"
        try:
            img = Image.open(BytesIO(data))
            img.load()
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")
            buf = BytesIO()
            if tier == "thumb":
                img.thumbnail((cls.THUMB_TIER_PX, cls.THUMB_TIER_PX),
                              Image.LANCZOS)
                img.save(buf, "WEBP", quality=cls.WEBP_Q_THUMB, method=4)
            elif asset_type == "icons":
                img.save(buf, "WEBP", lossless=True, quality=100, method=4)
            else:
                img.save(buf, "WEBP", quality=cls.WEBP_Q_FULL, method=4)
            out = buf.getvalue()
            # Gdy WEBP wyszedł większy (rzadkie: małe/już skompresowane
            # pliki) — zostaw oryginał.
            if tier != "thumb" and len(out) >= len(data):
                return data, ".png"
            return out, ".webp"
        except Exception:
            return data, ".png"

    def save_asset(self, game_id: int, asset_type: str,
                   remote_id: str, data: bytes,
                   width: int = 0, height: int = 0,
                   sgdb_key: str = "",
                   commit: bool = True,
                   url: str = "",
                   tier: str = "full") -> Path | None:
        """Zapisuje asset na dysk + metadane do SQLite.

        FIX: parametr commit=False pozwala grupować wiele assetów
        w jeden commit (batch) zamiast commit per-asset.

        v7.9 (cache-diet):
        - url:  źródłowy adres pełnej wersji (do lazy-fetch przy wyborze)
        - tier: 'thumb' = miniatura 256px WEBP (domyślne dla kandydatów),
                'full'  = pełny plik (rekompresowany do WEBP)
        """
        key = str(game_id)
        if PIL_OK:
            try:
                w, h = Image.open(BytesIO(data)).size
                width, height = w, h
            except Exception:
                pass
        data, ext = self._recompress_bytes(data, asset_type, tier)
        p = self.asset_path(key, asset_type, str(remote_id), ext)
        # Sprzątnij ewentualny stary plik pod innym rozszerzeniem
        _old = p.with_suffix(".png" if ext == ".webp" else ".webp")
        if _old.exists():
            try:
                _old.unlink()
            except Exception:
                pass
        p.write_bytes(data)
        chk = hashlib.md5(data).hexdigest()
        with self._lock:  # FIX v7: serializacja zapisów z wielu wątków
            self._db.execute(
                "INSERT OR REPLACE INTO assets"
                "(game_id,asset_type,remote_asset_id,local_path,width,height,"
                "checksum,last_sync,url,tier)"
                " VALUES(?,?,?,?,?,?,?,?,?,?)",
                (game_id, asset_type, str(remote_id), str(p),
                 width, height, chk, time.time(), url or "", tier),
            )
            # FIX: commit tylko jeśli nie jesteśmy w trybie batch
            if commit:
                self._db.commit()
        self._generate_thumb(p, key, asset_type, str(remote_id), 128)
        if tier != "thumb":
            # tier='thumb' sam jest ≤256px — 256-tka i ICO byłyby duplikatem;
            # ICO generowane dopiero przy promocji do 'full' (wybór ikony).
            self._generate_thumb(p, key, asset_type, str(remote_id), 256)
            if asset_type == "icons":
                self._generate_ico(p, key, str(remote_id))
        return p

    def ensure_full_asset(self, game_id: int, asset_type: str,
                          remote_id: str, fetch_fn=None) -> str | None:
        """v7.9: dostarcz pełną wersję assetu (promocja tier thumb→full).

        Zwraca ścieżkę do pełnego pliku. Gdy w cache jest tylko miniatura,
        pobiera oryginał z zapisanego url (fetch_fn), rekompresuje do WEBP
        i podmienia plik + rekord. Gdy sieć zawiedzie — zwraca miniaturę
        (256px nadal daje akceptowalne .ico) albo None gdy nic nie ma.
        """
        with self._lock:
            row = self._db.execute(
                "SELECT * FROM assets WHERE game_id=? AND asset_type=? "
                "AND remote_asset_id=? LIMIT 1",
                (game_id, asset_type, str(remote_id)),
            ).fetchone()
        if not row:
            return None
        lp = Path(row["local_path"])
        if row["tier"] != "thumb":
            return str(lp) if lp.exists() else None
        url = row["url"] or ""
        if url and fetch_fn:
            try:
                data = fetch_fn(url)
            except Exception:
                data = None
            if data:
                p = self.save_asset(game_id, asset_type, str(remote_id),
                                    data, sgdb_key="", commit=True,
                                    url=url, tier="full")
                if p:
                    print(f"[Tier] full pobrany: gid={game_id} "
                          f"{asset_type}/{remote_id}")
                    return str(p)
        # Fallback: miniatura (lepsza niż nic)
        return str(lp) if lp.exists() else None

    # ------------------------------------------------------------------
    # Generate thumbs + ICO (only once, skip if file exists)
    # ------------------------------------------------------------------
    def _generate_thumb(self, src: Path, key: str, asset_type: str,
                        remote_id: str, size: int):
        if not PIL_OK:
            return
        tp = self.thumb_path(key, asset_type, remote_id, size)
        if tp.exists():
            return
        try:
            img = Image.open(src).convert("RGBA")
            img.thumbnail((size, size), Image.LANCZOS)
            bg = Image.new("RGBA", (size, size), (30, 30, 46, 255))
            bg.paste(img, ((size - img.width) // 2, (size - img.height) // 2), img)
            bg.convert("RGB").save(str(tp), "WEBP", quality=85)
        except Exception:
            pass

    def _generate_ico(self, src: Path, key: str, remote_id: str):
        if not PIL_OK:
            return
        ip = self.ico_path(key, remote_id)
        if ip.exists():
            return
        try:
            img = Image.open(src).convert("RGBA")
            ip.write_bytes(make_ico_bytes(img))
        except Exception:
            pass

    def load_thumb(self, game_id: int, asset_type: str,
                   size: int = 128) -> "ImageTk.PhotoImage | None":
        if not PIL_OK:
            return None
        rows = self.get_assets(game_id, asset_type)
        for row in rows:
            key = str(game_id)
            tp = self.thumb_path(key, asset_type, row["remote_asset_id"], size)
            if tp.exists():
                try:
                    return thumb_cached(str(tp), size)  # FIX: LRU cache
                except Exception:
                    pass
            elif Path(row["local_path"]).exists():
                try:
                    return thumb_cached(row["local_path"], size)  # FIX: path zamiast bytes
                except Exception:
                    pass
        return None

    # ------------------------------------------------------------------
    # Candidates from local cache (replaces IconManager.candidates_for_*)
    # ------------------------------------------------------------------
    _CAND_TYPE_MAP = {"icons": "sgdb", "grids": "grid", "heroes": "grid",
                      "logos": "sgdb", "covers": "grid"}

    def candidates_from_cache(self, game_id: int,
                               asset_type: str = "icons",
                               dir_cache: dict | None = None,
                               rows: "list[sqlite3.Row] | None" = None
                               ) -> list[dict]:
        """FIX: Zwraca kandydatów z cache BEZ ładowania bajtów do RAM.
        Bajty są ładowane lazy (tylko przy rysowaniu / tworzeniu skrótu).
        Dzięki temu 500 gier × 10 ikon × ~100 KB = 500 MB RAM → ~0 MB.

        PERF v7.8:
        - dir_cache: współdzielony cache listingów katalogów — istnienie
          pliku assetu i miniatury to lookup w secie zamiast 2× stat() na wiersz.
        - rows: prefetchowane wiersze (z assets_bulk) — brak zapytania SQL
          per gra przy starcie.
        - ścieżki liczone helperami *_ro (zero mkdir na odczycie).
        """
        if rows is None:
            rows = self.get_assets(game_id, asset_type)
        if not rows:
            return []
        if dir_cache is None:
            dir_cache = {}
        cands = []
        _ctype = self._CAND_TYPE_MAP.get(asset_type, asset_type)
        key = str(game_id)
        thumb_dir = self.asset_dir_ro(key, asset_type) / "thumbs"
        thumb_names = self._dir_listing(dir_cache, thumb_dir)
        for row in rows:
            lp = Path(row["local_path"])
            if lp.name not in self._dir_listing(dir_cache, lp.parent):
                continue
            # FIX v7: PERF — jeśli istnieje wygenerowana miniatura (WEBP 128px),
            # podaj jej ścieżkę. _draw_detail dekoduje wtedy mały plik zamiast
            # pełnego obrazka (główna przyczyna zamulania przy klikaniu gier).
            rid = row["remote_asset_id"]
            tname = f"{rid}_128.webp"
            try:                       # v7.9: kolumny po migracji
                _url, _tier = row["url"] or "", row["tier"] or "full"
            except (IndexError, KeyError):
                _url, _tier = "", "full"
            cands.append({
                "type": _ctype,
                "bytes": None,          # FIX: lazy-load, nie ładujemy do RAM na start
                "local_path": str(lp),  # FIX: używany przez thumb_cached i _create_thread
                "thumb_path": str(thumb_dir / tname) if tname in thumb_names else "",
                "w": row["width"] or 0,
                "h": row["height"] or 0,
                "style": "",
                "shape": "square" if asset_type in ("icons", "grids") else "unknown",
                "label": f"{asset_type.upper()} {row['width']}x{row['height']} [cache]",
                "exe": None,
                "remote_asset_id": rid,
                "url": _url,                 # v7.9: lazy-fetch pełnej wersji
                "tier": _tier,               # v7.9: 'thumb' | 'full'
                "asset_type": asset_type,    # v7.9: dla ensure_full_asset
            })
        return cands

    def reconcile_from_disk(self, progress=None) -> "tuple[int, int]":
        """v8.2: odbudowa BRAKUJĄCYCH wpisów tabeli `assets` z plików już
        obecnych na dysku. Naprawia desync (pliki są, ale w bazie brak wpisów →
        gry pokazują się bez grafik mimo cache). Nie rusza plików ani
        istniejących wpisów. Zwraca (dodane_wpisy, gry_odzyskane)."""
        added = 0
        recov: set = set()
        IMG_EXT = {".png", ".webp", ".jpg", ".jpeg", ".ico", ".gif"}
        with self._lock:
            valid = {r["id"] for r in self._db.execute("SELECT id FROM games")}
            existing = set()
            for r in self._db.execute(
                    "SELECT game_id, asset_type, remote_asset_id FROM assets"):
                existing.add((r["game_id"], r["asset_type"], r["remote_asset_id"]))
            now = time.time()
            try:
                gdirs = list(self.assets_dir.iterdir())
            except Exception:
                gdirs = []
            for gdir in gdirs:
                if not gdir.is_dir() or not gdir.name.isdigit():
                    continue
                gid = int(gdir.name)
                if gid not in valid:
                    continue                      # osierocony folder (brak gry)
                try:
                    at_dirs = list(gdir.iterdir())
                except Exception:
                    continue
                for at_dir in at_dirs:
                    if not at_dir.is_dir() or at_dir.name not in self.ASSET_TYPES:
                        continue
                    atype = at_dir.name
                    try:
                        files = list(at_dir.iterdir())
                    except Exception:
                        continue
                    for f in files:
                        if not f.is_file() or f.suffix.lower() not in IMG_EXT:
                            continue
                        rid = f.stem
                        k = (gid, atype, rid)
                        if k in existing:
                            continue
                        w = h = 0
                        if PIL_OK:
                            try:
                                with Image.open(f) as _im:
                                    w, h = _im.size
                            except Exception:
                                pass
                        try:
                            self._db.execute(
                                "INSERT OR IGNORE INTO assets(game_id,asset_type,"
                                "remote_asset_id,local_path,width,height,checksum,"
                                "last_sync,url,tier) VALUES(?,?,?,?,?,?,?,?,?,?)",
                                (gid, atype, rid, str(f), w, h, "", now, "", "full"))
                            existing.add(k)
                            added += 1
                            recov.add(gid)
                            if progress and added % 300 == 0:
                                progress(added, len(recov))
                        except Exception:
                            pass
            self._db.commit()
        return added, len(recov)

    def assets_bulk(self, game_ids: "list[int]",
                    asset_types: tuple = ("icons", "grids")
                    ) -> "dict[tuple[int, str], list[sqlite3.Row]]":
        """PERF v7.8: pobierz wiersze assets dla WIELU gier jednym zapytaniem.

        Zamiast 2 zapytań SQL (icons + grids) per gra przy starcie
        (500 gier = 1000 round-tripów pod lockiem), jedno zapytanie
        z IN(...) — wynik pogrupowany po (game_id, asset_type).
        """
        out: dict[tuple[int, str], list] = {}
        ids = [int(g) for g in game_ids if g]
        if not ids:
            return out
        CHUNK = 500          # limit parametrów SQLite (999)
        with self._lock:
            for i in range(0, len(ids), CHUNK):
                chunk = ids[i:i + CHUNK]
                ph_ids = ",".join("?" * len(chunk))
                ph_typ = ",".join("?" * len(asset_types))
                cur = self._db.execute(
                    f"SELECT * FROM assets WHERE game_id IN ({ph_ids}) "
                    f"AND asset_type IN ({ph_typ}) "
                    "ORDER BY game_id, asset_type, width DESC",
                    (*chunk, *asset_types),
                )
                for row in cur.fetchall():
                    out.setdefault(
                        (row["game_id"], row["asset_type"]), []
                    ).append(row)
        return out

    # ------------------------------------------------------------------
    # Cleanup (remove orphaned files)
    # ------------------------------------------------------------------
    def prune_orphans(self):
        with self._lock:  # FIX v7.4
            cur = self._db.execute("SELECT local_path FROM assets")
            known = {row["local_path"] for row in cur.fetchall()}
        removed = 0
        for p in self.assets_dir.rglob("*"):
            if p.is_file() and str(p) not in known:
                try:
                    p.unlink()
                    removed += 1
                except Exception:
                    pass
        return removed

    # ── Stub management ────────────────────────────────────────────────────────

    def save_stub(self, game_id: int, stub_data: dict,
                  rom_phash: str | None = None) -> None:
        """Zapisz skompresowany stub metadanych do SQLite."""
        import json, time
        raw = json.dumps(stub_data, ensure_ascii=False).encode("utf-8")
        blob = compress_stub(raw)
        with self._lock:  # FIX v7
            self._db.execute(
                "INSERT OR REPLACE INTO stubs(game_id, data, rom_phash, stub_date)"
                " VALUES(?,?,?,?)",
                (game_id, blob, rom_phash, time.time()),
            )
            self._db.commit()

    def load_stub(self, game_id: int) -> dict | None:
        """Wczytaj stub dla gry (None jeśli brak)."""
        import json
        with self._lock:  # FIX v7.4
            row = self._db.execute(
                "SELECT data FROM stubs WHERE game_id=? LIMIT 1", (game_id,)
            ).fetchone()
        if not row:
            return None
        try:
            return json.loads(decompress_stub(row[0]))
        except Exception:
            return None

    def lookup_stub_by_phash(self, phash: str) -> dict | None:
        """Znajdź stub ROM po pseudo-hashu pliku.
        Zwraca {'_game_id': int, 'sgdb_id': str, ...} lub None.
        """
        import json
        with self._lock:  # FIX v7.4
            row = self._db.execute(
                "SELECT game_id, data FROM stubs WHERE rom_phash=? LIMIT 1",
                (phash,),
            ).fetchone()
        if not row:
            return None
        try:
            data = json.loads(decompress_stub(row["data"]))
            data["_game_id"] = row["game_id"]
            return data
        except Exception:
            return None

    # ------------------------------------------------------------------
    # v7.9 (cache-diet): rozmiar, eksmisja LRU, kompaktowanie
    # ------------------------------------------------------------------
    def cache_size_bytes(self) -> int:
        """Łączny rozmiar katalogu assets/ w bajtach (rekurencyjnie)."""
        total = 0
        stack = [self.assets_dir]
        while stack:
            d = stack.pop()
            try:
                with os.scandir(d) as it:
                    for e in it:
                        if e.is_dir(follow_symlinks=False):
                            stack.append(Path(e.path))
                        else:
                            try:
                                total += e.stat().st_size
                            except OSError:
                                pass
            except OSError:
                pass
        return total

    def _asset_files_for_row(self, row) -> list[Path]:
        """Wszystkie pliki należące do jednego wiersza assets
        (oryginał + miniatury 128/256 + .ico)."""
        key = str(row["game_id"])
        rid = str(row["remote_asset_id"])
        at  = row["asset_type"]
        base = self.asset_dir_ro(key, at)
        return [
            Path(row["local_path"]),
            base / "thumbs" / f"{rid}_128.webp",
            base / "thumbs" / f"{rid}_256.webp",
            self.assets_dir / key / "icons" / f"{rid}.ico",
        ]

    def evict_lru(self, limit_bytes: int,
                  keep: "set[tuple[int, str]]") -> int:
        """v7.9 (D): eksmisja LRU — trzymaj cache poniżej limitu.

        Gdy assets/ przekracza limit_bytes, usuwa NIE-wybrane assety gier
        w kolejności od najdawniej używanych (games.last_sync rośnie przy
        każdym skanie, więc aktualna biblioteka wypada ostatnia).
        keep = zbiór (game_id, remote_asset_id) wybranych ikon — te pliki
        nigdy nie są ruszane (skrót .lnk wskazuje ich .ico).
        Zwraca liczbę zwolnionych bajtów. Odtworzenie: url w wierszu /
        stub / SYNC.
        """
        if limit_bytes <= 0:
            return 0
        total = self.cache_size_bytes()
        if total <= limit_bytes:
            return 0
        freed = 0
        with self._lock:
            games = self._db.execute(
                "SELECT id FROM games ORDER BY last_sync ASC").fetchall()
        for grow in games:
            if total - freed <= limit_bytes:
                break
            gid = grow["id"]
            with self._lock:
                rows = self._db.execute(
                    "SELECT * FROM assets WHERE game_id=?", (gid,)).fetchall()
            victims = [r for r in rows
                       if (gid, str(r["remote_asset_id"])) not in keep]
            if not victims:
                continue
            with self._lock:
                for r in victims:
                    for f in self._asset_files_for_row(r):
                        try:
                            if f.exists():
                                freed += f.stat().st_size
                                f.unlink()
                        except OSError:
                            pass
                    self._db.execute(
                        "DELETE FROM assets WHERE game_id=? AND "
                        "asset_type=? AND remote_asset_id=?",
                        (gid, r["asset_type"], r["remote_asset_id"]))
                self._db.commit()
        if freed:
            print(f"[LRU] zwolniono {freed/1024/1024:.1f} MB "
                  f"(limit {limit_bytes/1024/1024:.0f} MB)")
        return freed

    def compact(self, keep: "set[tuple[int, str]]",
                progress_cb=None) -> tuple[int, int]:
        """v7.9 (migracja A+B dla starego cache): jednorazowe odchudzenie.

        - assety NIE-wybrane → degradacja do tier='thumb' (256px WEBP,
          kasacja miniatury 256 i .ico — pełna wersja wróci lazy z url),
        - assety wybrane (keep) → rekompresja do WEBP w pełnym rozmiarze
          (ikony lossless, gridy q88), tier='full'.
        Zwraca (zwolnione_bajty, liczba_przetworzonych). Bezstratne dla
        funkcjonalności: podglądy rysują z miniatur, skróty z .ico
        wybranych ikon.
        """
        if not PIL_OK:
            return 0, 0
        with self._lock:
            rows = self._db.execute("SELECT * FROM assets").fetchall()
        freed, done = 0, 0
        for n, row in enumerate(rows):
            gid = row["game_id"]
            rid = str(row["remote_asset_id"])
            lp  = Path(row["local_path"])
            if not lp.exists():
                continue
            selected = (gid, rid) in keep
            try:
                cur_tier = row["tier"] or "full"
            except (IndexError, KeyError):
                cur_tier = "full"
            # thumb już jest mały; wybrany WEBP-full też — pomiń
            if (not selected and cur_tier == "thumb") or \
               (selected and cur_tier == "full" and lp.suffix == ".webp"):
                continue
            try:
                old_size = lp.stat().st_size
                data = lp.read_bytes()
                new_tier = "full" if selected else "thumb"
                out, ext = self._recompress_bytes(data, row["asset_type"],
                                                  new_tier)
                new_p = self.asset_path(str(gid), row["asset_type"], rid, ext)
                new_p.write_bytes(out)
                if new_p != lp:
                    lp.unlink(missing_ok=True)
                extra = 0
                if new_tier == "thumb":
                    # 256-tka i .ico zbędne dla miniatur-kandydatów
                    for f in (self.asset_dir_ro(str(gid), row["asset_type"])
                              / "thumbs" / f"{rid}_256.webp",
                              self.assets_dir / str(gid) / "icons"
                              / f"{rid}.ico"):
                        try:
                            if f.exists():
                                extra += f.stat().st_size
                                f.unlink()
                        except OSError:
                            pass
                with self._lock:
                    self._db.execute(
                        "UPDATE assets SET local_path=?, tier=?, "
                        "checksum=?, last_sync=? WHERE game_id=? AND "
                        "asset_type=? AND remote_asset_id=?",
                        (str(new_p), new_tier,
                         hashlib.md5(out).hexdigest(), time.time(),
                         gid, row["asset_type"], rid))
                    if n % 50 == 0:
                        self._db.commit()
                freed += max(0, old_size - len(out)) + extra
                done += 1
                if progress_cb and n % 10 == 0:
                    progress_cb(n + 1, len(rows), freed)
            except Exception as e:
                print(f"[Compact] {gid}/{rid}: {e}")
        with self._lock:
            self._db.commit()
        return freed, done

    def delete_assets_for_game(self, game_id: int) -> None:
        """Usuń pliki obrazów + rekordy assets dla gry.
        Zachowuje: rekord w tabeli games, stub.
        """
        import shutil
        # usuń pliki
        asset_dir = self.assets_dir / str(game_id)
        if asset_dir.exists():
            shutil.rmtree(asset_dir, ignore_errors=True)
        # usuń rekordy DB
        with self._lock:  # FIX v7
            self._db.execute("DELETE FROM assets WHERE game_id=?", (game_id,))
            self._db.commit()

    def close(self):
        try:
            self._db.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------

class SyncManager:
    """Synchronizuje SGDB -> lokalny AssetStore. Nie dotyka GUI."""

    ASSET_ENDPOINTS = {
        "icons":  "icons",
        "grids":  "grids",
        "heroes": "heroes",
        "logos":  "logos",
        "covers": "grids",     # covers to grids 600x900
    }

    def __init__(self, store: AssetStore, sgdb_key: str,
                 max_workers: int = 6):
        self.store = store
        self.sgdb_key = sgdb_key
        self.max_workers = max_workers
        self._stop = threading.Event()
        self._q: queue.Queue = queue.Queue()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def stop(self):
        self._stop.set()

    def reset_stop(self):
        self._stop.clear()

    @property
    def out_queue(self) -> queue.Queue:
        return self._q

    def sync_game(self, game: dict,
                  asset_types: tuple = ("icons", "grids"),
                  progress_cb=None):
        """
        Synchronizuje assety dla jednej gry.
        Wywoluj w watku. Wyniki przez self._q.
        """
        appid   = game.get("appid")
        sgdb_id = game.get("sgdb_id")
        name    = game.get("name", "")
        source  = game.get("source", "extra")

        # --- auto-resolve sgdb_id dla gier bez appid (Extra/Epic/GOG) ---
        if not appid and not sgdb_id and self.sgdb_key and name:
            print(f"[SYNC search] {name!r} – brak appid/sgdb_id, szukam w SGDB...")
            results = self._sgdb_search(name)
            if results:
                sgdb_id = str(results[0]["id"])
                game["sgdb_id"] = sgdb_id
                print(f"[SYNC search] {name!r} => sgdb_id={sgdb_id} ({results[0].get('name','?')})")
            else:
                print(f"[SYNC search] {name!r} => brak wyników SGDB, pomijam")

        game_id = self.store.upsert_game(source, appid, sgdb_id, name)
        print(f"[SYNC] {name!r} game_id={game_id} appid={appid} sgdb_id={sgdb_id}")
        total_new = 0

        for atype in asset_types:
            if self._stop.is_set():
                break
            new = self._sync_asset_type(game_id, atype, appid, sgdb_id,
                                        name, progress_cb)
            total_new += new
            print(f"[SYNC] {name!r} {atype}: +{new} nowych")

        return game_id, total_new

    def sync_all(self, games: list[dict],
                 asset_types: tuple = ("icons", "grids"),
                 progress_cb=None):
        """
        Pelna synchronizacja dla listy gier.
        Uruchamia ThreadPoolExecutor; wyniki przez self._q.
        """
        self.reset_stop()
        self._q.put(("sync_start", len(games)))

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {
                pool.submit(self.sync_game, g, asset_types, progress_cb): g
                for g in games
            }
            done = 0
            for fut in as_completed(futures):
                g = futures[fut]
                done += 1
                if self._stop.is_set():
                    break
                try:
                    gid, n_new = fut.result()
                    self._q.put(("sync_game_done", g["name"], gid, n_new, done, len(games)))
                except Exception as e:
                    self._q.put(("sync_game_err", g.get("name","?"), str(e), done, len(games)))

        self._q.put(("sync_done", done))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _fetch_asset_list(self, endpoint: str,
                          appid: str | None,
                          sgdb_id: str | None) -> list[dict]:
        """Pobiera liste assetow z SGDB API."""
        if not self.sgdb_key:
            return []
        hdrs = {"Authorization": f"Bearer {self.sgdb_key}"}
        if appid and endpoint in ("icons", "grids", "heroes", "logos"):
            url = f"https://www.steamgriddb.com/api/v2/{endpoint}/steam/{appid}"
        elif sgdb_id:
            url = f"https://www.steamgriddb.com/api/v2/{endpoint}/game/{sgdb_id}"
        else:
            return []
        try:
            d = fetch_api(url, hdrs=hdrs)
            if not d:
                return []
            parsed = json.loads(d)
            if not parsed.get("success"):
                return []
            return parsed.get("data", [])
        except Exception:
            return []

    def _sgdb_search(self, name: str, max_results: int = 3) -> list[dict]:
        """Szuka gry w SGDB po nazwie – dla gier bez appid w sync."""
        if not self.sgdb_key:
            return []
        import urllib.parse
        enc = urllib.parse.quote(name)
        d = fetch_api(
            f"https://www.steamgriddb.com/api/v2/search/autocomplete/{enc}",
            hdrs={"Authorization": f"Bearer {self.sgdb_key}"},
        )
        if not d:
            return []
        try:
            return json.loads(d).get("data", [])[:max_results]
        except Exception:
            return []

    def _sync_asset_type(self, game_id: int, asset_type: str,
                         appid: str | None, sgdb_id: str | None,
                         name: str, progress_cb) -> int:
        """
        Delta-sync jednego typu assetow.
        Pobiera tylko te remote_asset_id, ktorych nie ma lokalnie.
        """
        endpoint = self.ASSET_ENDPOINTS.get(asset_type, asset_type)
        if not appid and not sgdb_id:
            print(f"[SYNC asset] {name!r} {asset_type}: brak kluczy – pomijam")
            return 0
        remote_list = self._fetch_asset_list(endpoint, appid, sgdb_id)
        print(f"[SYNC asset] {name!r} {asset_type}: remote={len(remote_list)}")
        if not remote_list:
            return 0

        new_count = 0
        for item in remote_list:
            if self._stop.is_set():
                break
            remote_id = str(item.get("id", ""))
            if not remote_id:
                continue
            # Delta: pomijamy jesli juz mamy lokalnie
            if self.store.asset_exists(game_id, asset_type, remote_id):
                continue
            url = item.get("url") or item.get("thumb", "")
            if not url:
                continue
            data = fetch(url)
            if not data:
                continue
            key = sgdb_id or str(game_id)
            self.store.save_asset(
                game_id, asset_type, remote_id, data,
                width=item.get("width", 0),
                height=item.get("height", 0),
                sgdb_key=key,
                url=item.get("url", "") or url,   # v7.9: lazy-full
                tier="thumb",                      # v7.9: kandydat = miniatura
            )
            new_count += 1
            if progress_cb:
                progress_cb(name, asset_type, new_count)

        return new_count


# ---------------------------------------------------------------------------
# Strzałki nakładki na skrótach (.lnk) — SYSTEMOWE ustawienie Windows.
# HKLM\...\Explorer\Shell Icons\29 = ścieżka do (pustej) ikony. Dotyczy
# WSZYSTKICH skrótów, wymaga admina (UAC) i restartu Eksploratora. Odwracalne.
# ---------------------------------------------------------------------------
_SHELL_ICONS_KEY = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Icons"


def _blank_arrow_ico_path() -> str:
    """Zwraca ścieżkę do przezroczystej ikony (w stałej lokalizacji, niezależnej
    od położenia programu). Tworzy ją raz. Pusta = brak strzałki."""
    try:
        base = Path(os.environ.get("LOCALAPPDATA") or SCRIPT_DIR) / "PyLinks"
        base.mkdir(parents=True, exist_ok=True)
        p = base / "blank_arrow.ico"
        if not p.exists() and PIL_OK:
            p.write_bytes(make_ico_bytes(Image.new("RGBA", (256, 256), (0, 0, 0, 0))))
        return str(p) if p.exists() else ""
    except Exception:
        return ""


def shortcut_arrows_state() -> bool:
    """True jeśli strzałki są AKTUALNIE usunięte (wartość 29 ustawiona)."""
    if not (IS_WIN and WINREG_OK):
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _SHELL_ICONS_KEY) as k:
            val, _ = winreg.QueryValueEx(k, "29")
            return bool(val)
    except Exception:
        return False


def set_shortcut_arrows(remove: bool) -> "tuple[bool, str]":
    """Usuwa (remove=True) lub przywraca strzałki na skrótach. Zmiana rejestru
    HKLM idzie z podniesieniem uprawnień (UAC). Zwraca (ok, komunikat).
    Restart Eksploratora rób osobno (restart_explorer())."""
    if not IS_WIN:
        return False, "Ta opcja działa tylko w Windows."
    import ctypes
    if remove:
        # FIX: pusty slot ikony SYSTEMOWEJ — nic nie widać. Własna przezroczysta
        # .ico bywa renderowana przez Windows jako CZARNY KWADRAT (błędna
        # obsługa maski nakładki). imageres.dll,197 to gwarantowany blank.
        blank = r"%SystemRoot%\System32\imageres.dll,197"
        args = f'add "HKLM\\{_SHELL_ICONS_KEY}" /v 29 /t REG_EXPAND_SZ /d "{blank}" /f'
    else:
        args = f'delete "HKLM\\{_SHELL_ICONS_KEY}" /v 29 /f'
    try:
        # reg.exe z podniesieniem — UAC potwierdza tylko tę jedną zmianę
        rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", "reg.exe",
                                                 args, None, 0)
        if rc <= 32:
            return False, f"Anulowano lub brak zgody UAC (kod {rc})."
        return True, ("Strzałki usunięte." if remove else "Strzałki przywrócone.")
    except Exception as e:
        return False, f"Błąd: {e}"


def restart_explorer() -> None:
    """Restart Eksploratora Windows, aby zastosować zmianę ikon (bez admina)."""
    if not IS_WIN:
        return
    try:
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"],
                       capture_output=True, timeout=10)
    except Exception:
        pass
    try:
        subprocess.Popen("explorer.exe")
    except Exception:
        pass


def read_lnk_target(path) -> "tuple[str, str, str]":
    """Czyta skrót .lnk i zwraca (TargetPath, Arguments, WorkingDirectory).

    Używane do eksportu ROM-ów uruchamianych przez .lnk (np. PS3/RPCS3) do
    Steam — Steam potrzebuje prawdziwego EXE, więc rozwijamy .lnk na jego
    docelowy plik + argumenty + katalog roboczy. Zwraca ('','','') gdy się nie
    uda / brak pywin32."""
    if not (IS_WIN and WIN32COM):
        return "", "", ""
    _co = False
    try:
        import pythoncom  # type: ignore
        pythoncom.CoInitialize()
        _co = True
    except Exception:
        pass
    try:
        sh = win32com.client.Dispatch("WScript.Shell")
        sc = sh.CreateShortcut(str(path))
        return (sc.TargetPath or "", sc.Arguments or "", sc.WorkingDirectory or "")
    except Exception:
        return "", "", ""
    finally:
        if _co:
            try:
                import pythoncom  # type: ignore
                pythoncom.CoUninitialize()
            except Exception:
                pass


# =============================================================================
class ShortcutCreator:
    def __init__(self, steam_exe: str):
        self.steam_exe = steam_exe

    def make_lnk(self, dst: str, target: str, args: str, icon: str,
                 work_dir: str = "") -> bool:
        if not WIN32COM:
            print(f"[LNK] WIN32COM unavailable: dst={dst}, target={target}, args={args}")
            return False
        # FIX v7.1: make_lnk jest wywoływany z wątku roboczego (_create_thread),
        # a COM wymaga inicjalizacji per-wątek — bez tego:
        # com_error -2147221008 "Funkcja CoInitialize nie została wywołana."
        _co_init = False
        try:
            import pythoncom  # type: ignore
            pythoncom.CoInitialize()
            _co_init = True
        except Exception:
            pass
        try:
            sh = win32com.client.Dispatch("WScript.Shell")
            sc = sh.CreateShortcut(dst)
            sc.TargetPath = target
            sc.Arguments = args
            sc.IconLocation = icon
            if work_dir:
                sc.WorkingDirectory = work_dir
            sc.Save()
            print(f"[LNK] OK dst={dst} target={target} args={args} workdir={work_dir}")
            return True
        except Exception as e:
            print(f"[LNK] ERROR dst={dst} target={target} args={args} icon={icon} err={e}")
            import traceback; traceback.print_exc()
            return False
        finally:
            if _co_init:
                try:
                    import pythoncom  # type: ignore
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

    def copy_lnk_with_icon(self, src: str, dst: str, icon: str) -> bool:
        """v7.9.2 (PS3/RPCS3): skopiuj skrót .lnk i podmień ikonę — bezpiecznie.

        RPCS3 tworzy .lnk z kompletną komendą uruchamiania gry (target,
        argumenty, katalog roboczy) — nie odtwarzamy jej, tylko kopiujemy
        plik 1:1 i nadpisujemy w KOPII IconLocation. Oryginał w roms/
        pozostaje nietknięty.

        FIX v7.9.2 (duplikaty .lnk + losowo niezmienione ikony):
        Poprzednio kopiowaliśmy plik prosto pod docelową nazwę i od razu
        kazaliśmy WScript.Shell pisać po tym samym pliku. Dwa problemy:
        1. Świeżo skopiowany plik bywa chwilowo zablokowany przez
           Defender/indexer → Save() padał, a my zwracaliśmy True →
           w LINKS zostawała kopia ze STARĄ ikoną (losowo, wg timingu).
        2. WScript.Shell przy nazwach z nietypowymi znakami (™, myślniki
           unicode, kropki/spacje) potrafi zapisać wynik pod ścieżką
           znormalizowaną przez Win32 inaczej niż zapisał ją Python →
           w katalogu lądowały DWA pliki: kopia (stara ikona) + wersja
           zapisana przez COM (nowa ikona).
        Rozwiązanie: cała modyfikacja odbywa się na pliku TYMCZASOWYM o
        czysto ASCII-owej nazwie (COM nie ma czego przekręcić), w katalogu
        DOCELOWYM (ten sam wolumin → atomowy os.replace). Save() ma retry
        na blokady AV, ikona jest WERYFIKOWANA ponownym odczytem, i dopiero
        gotowy plik jest atomowo podmieniany pod docelową nazwą. W LINKS
        nigdy nie ma pliku w stanie pośrednim.
        """
        dst_p = Path(dst)
        tmp_p = dst_p.parent / f"~lnkwork_{os.getpid()}_{uuid.uuid4().hex[:8]}.lnk"
        try:
            dst_p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, tmp_p)
        except Exception as e:
            print(f"[LNK-COPY] ERROR copy {src} -> {tmp_p}: {e}")
            tmp_p.unlink(missing_ok=True)
            return False

        icon_ok = False
        if WIN32COM:
            _co_init = False
            try:
                import pythoncom  # type: ignore
                pythoncom.CoInitialize()
                _co_init = True
            except Exception:
                pass
            try:
                sh = win32com.client.Dispatch("WScript.Shell")
                # Retry: świeży plik bywa trzymany przez AV/indexer
                last_err = None
                for attempt in range(3):
                    try:
                        sc = sh.CreateShortcut(str(tmp_p))  # wczytuje pola
                        sc.IconLocation = icon
                        sc.Save()
                        # WERYFIKACJA: odczytaj ponownie i porównaj —
                        # Save() potrafi "przejść" nie zapisując ikony
                        sc2 = sh.CreateShortcut(str(tmp_p))
                        got = str(sc2.IconLocation or "")
                        want_path = icon.split(",")[0].strip().lower()
                        if want_path and want_path in got.lower():
                            icon_ok = True
                            break
                        last_err = f"weryfikacja: IconLocation={got!r}"
                    except Exception as e:
                        last_err = e
                    time.sleep(0.25 * (attempt + 1))
                if not icon_ok:
                    print(f"[LNK-COPY] ikona NIE ustawiona po 3 próbach "
                          f"({dst_p.name}): {last_err}")
            except Exception as e:
                print(f"[LNK-COPY] ERROR COM {tmp_p} icon={icon} err={e}")
                import traceback; traceback.print_exc()
            finally:
                if _co_init:
                    try:
                        import pythoncom  # type: ignore
                        pythoncom.CoUninitialize()
                    except Exception:
                        pass
        else:
            print(f"[LNK-COPY] WIN32COM unavailable — kopiuję bez podmiany ikony: {dst}")

        # Atomowa podmiana pod docelową nazwą (nadpisuje istniejący plik).
        # Retry na wypadek gdy COM/AV jeszcze przez moment trzyma handle.
        for attempt in range(4):
            try:
                os.replace(tmp_p, dst_p)
                print(f"[LNK-COPY] OK {src} -> {dst} icon={icon} "
                      f"(icon_ok={icon_ok})")
                return True
            except OSError as e:
                if attempt == 3:
                    print(f"[LNK-COPY] ERROR replace -> {dst}: {e}")
                    tmp_p.unlink(missing_ok=True)
                    return False
                time.sleep(0.3 * (attempt + 1))
        return False

    def make_url(self, dst: str, appid: str, icon: str) -> bool:
        try:
            Path(dst).write_text(
                f"[InternetShortcut]\nURL=steam://rungameid/{appid}\nIconFile={icon}\nIconIndex=0\n",
                encoding="utf-8",
            )
            return True
        except Exception:
            return False

    def make_steam_shortcut(self, out_dir: Path, game: dict, icon: str) -> bool:
        safe = safe_name(game["name"])
        appid = game["appid"]
        lnk = str(out_dir / f"{safe}.lnk")
        url_f = str(out_dir / f"{safe}.url")
        if self.make_lnk(lnk, self.steam_exe, f"-applaunch {appid}", icon):
            return True
        return self.make_url(url_f, appid, icon)

    def make_extra_shortcut(self, out_dir: Path, game: dict, launch_exe: str,
                            icon: str, args: str = "", work_dir: str = "") -> bool:
        if not launch_exe:
            return False
        safe = safe_name(game["name"])
        lnk = str(out_dir / f"{safe}.lnk")
        # Katalog roboczy: podany (GOG playTask) lub folder EXE — pomaga grze
        # znaleźć swoje zasoby/konfigi (dla DOSBoxa: gdzie leżą .conf).
        wd = work_dir or str(Path(launch_exe).parent)
        return self.make_lnk(lnk, launch_exe, args, icon, work_dir=wd)

    def make_epic_shortcut(self, out_dir: Path, game: dict, icon: str) -> bool:
        """Skrót .url do Epic launchera: com.epicgames.launcher://apps/<AppName>"""
        app_name = game.get("epic_app_name")
        if not app_name:
            return False
        safe = safe_name(game["name"])
        url_f = out_dir / f"{safe}.url"
        try:
            url_f.write_text(
                f"[InternetShortcut]\n"
                f"URL=com.epicgames.launcher://apps/{app_name}?action=launch&silent=true\n"
                f"IconFile={icon}\nIconIndex=0\n",
                encoding="utf-8",
            )
            return True
        except Exception:
            return False

    def make_gog_shortcut(self, out_dir: Path, game: dict, icon: str) -> bool:
        """Skrót .lnk do gry GOG.

        Najpierw czyta goggame-*.info (primary playTask: path+arguments+
        workingDir) — dzięki temu gry DOSBox/ScummVM dostają -conf i katalog
        roboczy, a nie goły dosbox.exe bez configu. Fallback: launch_exe
        z rejestru (bez argumentów), gdy brak/nieczytelny goggame-*.info."""
        launch_exe = game.get("launch_exe") or ""
        args = ""
        work_dir = ""
        pt = gog_playtask(game.get("game_dir", "") or "")
        if pt:
            launch_exe, args, work_dir = pt
        if not launch_exe:
            return False
        safe = safe_name(game["name"])
        lnk = str(out_dir / f"{safe}.lnk")
        wd = work_dir or str(Path(launch_exe).parent)
        return self.make_lnk(lnk, launch_exe, args, icon, work_dir=wd)

    # -------- Eksport do front-endów --------
    def export_launchbox(self, games: list[dict], out_dir: Path) -> Path:
        """Generuje plik XML kompatybilny z LaunchBoxem (Platforms/Games.xml)."""
        out_dir.mkdir(parents=True, exist_ok=True)
        root = ET.Element("LaunchBox")
        for g in games:
            if not g.get("enabled", True):
                continue
            ge = ET.SubElement(root, "Game")
            ET.SubElement(ge, "Title").text = g.get("name", "")
            ET.SubElement(ge, "Platform").text = {
                "steam": "Steam", "epic": "Epic Games", "gog": "GOG.com"
            }.get(g.get("source", "extra"), "Windows")
            if g.get("source") == "steam" and g.get("appid"):
                ET.SubElement(ge, "ApplicationPath").text = self.steam_exe
                ET.SubElement(ge, "CommandLine").text = f"-applaunch {g['appid']}"
            elif g.get("source") == "epic" and g.get("epic_app_name"):
                ET.SubElement(ge, "ApplicationPath").text = (
                    f"com.epicgames.launcher://apps/{g['epic_app_name']}?action=launch&silent=true"
                )
            else:
                ET.SubElement(ge, "ApplicationPath").text = g.get("launch_exe") or ""
        tree = ET.ElementTree(root)
        path = out_dir / "LaunchBox_Games.xml"
        tree.write(path, encoding="utf-8", xml_declaration=True)
        return path

    def export_pegasus(self, games: list[dict], out_dir: Path) -> Path:
        """Generuje metadata.txt kompatybilny z Pegasus Frontend."""
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "metadata.pegasus.txt"
        lines = [
            "collection: PC Games",
            "shortname: pc",
            "extensions: lnk, url, exe",
            "",
        ]
        for g in games:
            if not g.get("enabled", True):
                continue
            name = g.get("name", "")
            safe = safe_name(name)
            lines.append(f"game: {name}")
            lines.append(f"file: {safe}.lnk")
            src = g.get("source", "extra")
            if src == "steam" and g.get("appid"):
                lines.append(
                    f"launch: \"{self.steam_exe}\" -applaunch {g['appid']}"
                )
            elif src == "epic" and g.get("epic_app_name"):
                lines.append(
                    f"launch: cmd /c start \"\" \"com.epicgames.launcher://apps/{g['epic_app_name']}?action=launch&silent=true\""
                )
            elif g.get("launch_exe"):
                lines.append(f"launch: \"{g['launch_exe']}\"")
            lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
        return path


# ---------------------------------------------------------------------------
# Raport HTML / TXT
# ---------------------------------------------------------------------------
def write_report(out_dir: Path, entries: list[dict], fmt: str = "html") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if fmt == "txt":
        path = out_dir / f"shortcuts_report_{ts}.txt"
        lines = [f"Raport tworzenia skrótów - {ts}", "=" * 60]
        for e in entries:
            status = "OK " if e.get("ok") else "ERR"
            lines.append(f"[{status}] {e.get('name','')}")
            lines.append(f"  source  : {e.get('source','')}")
            lines.append(f"  file    : {e.get('file','')}")
            lines.append(f"  icon    : {e.get('icon','')}")
            lines.append(f"  target  : {e.get('target','')}")
            if e.get("error"):
                lines.append(f"  error   : {e['error']}")
            lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
        return path
    path = out_dir / f"shortcuts_report_{ts}.html"
    rows = []
    for e in entries:
        cls = "ok" if e.get("ok") else "err"
        rows.append(
            f"<tr class='{cls}'>"
            f"<td>{html.escape(e.get('name',''))}</td>"
            f"<td>{html.escape(e.get('source',''))}</td>"
            f"<td>{html.escape(e.get('file',''))}</td>"
            f"<td>{html.escape(e.get('icon',''))}</td>"
            f"<td>{html.escape(e.get('target',''))}</td>"
            f"<td>{html.escape(e.get('error',''))}</td>"
            f"</tr>"
        )
    n_ok = sum(1 for e in entries if e.get("ok"))
    n_err = len(entries) - n_ok
    html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Raport skrótów {ts}</title>
<style>
 body {{ font-family: Segoe UI, Arial, sans-serif; background:#1e1e2e; color:#cdd6f4; padding:24px; }}
 table {{ width:100%; border-collapse:collapse; margin-top:12px; }}
 th, td {{ padding:6px 10px; border-bottom:1px solid #313244; text-align:left; font-size:13px; }}
 th {{ color:#89b4fa; }}
 tr.ok td:first-child {{ border-left:4px solid #a6e3a1; }}
 tr.err td:first-child {{ border-left:4px solid #f38ba8; }}
 .summary {{ font-size:14px; margin-bottom:8px; }}
 .ok-c {{ color:#a6e3a1; }}
 .err-c {{ color:#f38ba8; }}
</style></head>
<body>
<h1>Raport tworzenia skrótów</h1>
<div class="summary">Data: {ts} &nbsp;|&nbsp;
<span class="ok-c">OK: {n_ok}</span> &nbsp;|&nbsp;
<span class="err-c">Błędy: {n_err}</span></div>
<table><thead><tr>
<th>Gra</th><th>Źródło</th><th>Plik</th><th>Ikona</th><th>Target</th><th>Błąd</th>
</tr></thead><tbody>{''.join(rows)}</tbody></table>
</body></html>"""
    path.write_text(html_doc, encoding="utf-8")
    return path


def write_steam_report(out_dir: Path, rows: list[dict], meta: dict,
                       fmt: str = "html") -> Path:
    """Raport eksportu do biblioteki Steam (shortcuts.vdf).

    rows: po jednym wpisie na WYBRANĄ grę, z polami:
      name, source, platform, outcome (dodane/zaktualizowane/
      pominięte — bez zmian/pominięte — błąd), exe, args, appid, tags, reason.
    meta: podsumowanie (plik, backup, liczby, kolekcje, grafiki).
    Zwraca ścieżkę zapisanego pliku.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _cnt(o):
        return sum(1 for r in rows if r.get("outcome") == o)
    n_add = _cnt("dodane")
    n_upd = _cnt("zaktualizowane")
    n_skip = _cnt("pominięte — bez zmian")
    n_err = _cnt("pominięte — błąd")
    n_dup = _cnt("usunięty duplikat")

    if fmt == "txt":
        path = out_dir / f"steam_export_report_{ts}.txt"
        L = [f"Raport eksportu do Steam - {ts}", "=" * 60,
             f"plik shortcuts.vdf : {meta.get('vdf','')}",
             f"kopia zapasowa     : {meta.get('backup') or '(brak)'}",
             f"wpisy w pliku łącznie: {meta.get('total','')}",
             f"dodane {n_add} | zaktualizowane {n_upd} | "
             f"pominięte(bez zmian) {n_skip} | błędy {n_err} | "
             f"usunięte duplikaty {n_dup}",
             f"kolekcje           : {meta.get('collections') or '(brak/wyłączone)'}",
             f"grafiki SGDB       : {meta.get('art') or '(wyłączone)'}",
             "=" * 60, ""]
        for r in rows:
            L.append(f"[{r.get('outcome','')}] {r.get('name','')}")
            L.append(f"  źródło : {r.get('source','')} / {r.get('platform','') or '-'}")
            L.append(f"  appid  : {r.get('appid','') or '-'}")
            L.append(f"  exe    : {r.get('exe','') or '-'}")
            if r.get("args"):
                L.append(f"  args   : {r.get('args','')}")
            if r.get("tags"):
                L.append(f"  tagi   : {r.get('tags','')}")
            if r.get("reason"):
                L.append(f"  powód  : {r.get('reason','')}")
            L.append("")
        path.write_text("\n".join(L), encoding="utf-8")
        return path

    path = out_dir / f"steam_export_report_{ts}.html"
    _cls = {"dodane": "add", "zaktualizowane": "upd",
            "pominięte — bez zmian": "skip", "pominięte — błąd": "err",
            "usunięty duplikat": "dup"}
    trs = []
    for r in rows:
        cls = _cls.get(r.get("outcome", ""), "skip")
        trs.append(
            f"<tr class='{cls}'>"
            f"<td>{html.escape(str(r.get('outcome','')))}</td>"
            f"<td>{html.escape(str(r.get('name','')))}</td>"
            f"<td>{html.escape(str(r.get('source','')))}"
            f"{(' / ' + html.escape(str(r.get('platform','')))) if r.get('platform') else ''}</td>"
            f"<td>{html.escape(str(r.get('appid','')))}</td>"
            f"<td class='mono'>{html.escape(str(r.get('exe','')))}</td>"
            f"<td class='mono'>{html.escape(str(r.get('args','')))}</td>"
            f"<td>{html.escape(str(r.get('tags','')))}</td>"
            f"<td>{html.escape(str(r.get('reason','')))}</td>"
            f"</tr>"
        )
    html_doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Raport eksportu Steam {ts}</title>
<style>
 body {{ font-family: Segoe UI, Arial, sans-serif; background:#1e1e2e; color:#cdd6f4; padding:24px; }}
 table {{ width:100%; border-collapse:collapse; margin-top:12px; }}
 th, td {{ padding:6px 10px; border-bottom:1px solid #313244; text-align:left; font-size:13px; vertical-align:top; }}
 th {{ color:#89b4fa; }}
 td.mono {{ font-family: Consolas, monospace; font-size:12px; word-break:break-all; }}
 tr.add td:first-child {{ border-left:4px solid #a6e3a1; }}
 tr.upd td:first-child {{ border-left:4px solid #89b4fa; }}
 tr.skip td:first-child {{ border-left:4px solid #6c7086; }}
 tr.err td:first-child {{ border-left:4px solid #f38ba8; }}
 tr.dup td:first-child {{ border-left:4px solid #f9e2af; }}
 .summary {{ font-size:14px; margin-bottom:8px; line-height:1.7; }}
 .k {{ color:#89b4fa; }}
 .add-c {{ color:#a6e3a1; }} .upd-c {{ color:#89b4fa; }}
 .skip-c {{ color:#a6adc8; }} .err-c {{ color:#f38ba8; }} .dup-c {{ color:#f9e2af; }}
</style></head>
<body>
<h1>Raport eksportu do biblioteki Steam</h1>
<div class="summary">
Data: {ts}<br>
<span class="add-c">Dodane: {n_add}</span> &nbsp;|&nbsp;
<span class="upd-c">Zaktualizowane: {n_upd}</span> &nbsp;|&nbsp;
<span class="skip-c">Pominięte (bez zmian): {n_skip}</span> &nbsp;|&nbsp;
<span class="err-c">Błędy: {n_err}</span> &nbsp;|&nbsp;
<span class="dup-c">Usunięte duplikaty: {n_dup}</span><br>
<span class="k">plik shortcuts.vdf:</span> {html.escape(str(meta.get('vdf','')))}<br>
<span class="k">kopia zapasowa:</span> {html.escape(str(meta.get('backup') or '(brak)'))}<br>
<span class="k">wpisy w pliku łącznie:</span> {html.escape(str(meta.get('total','')))}<br>
<span class="k">kolekcje:</span> {html.escape(str(meta.get('collections') or '(brak/wyłączone)'))}<br>
<span class="k">grafiki SGDB:</span> {html.escape(str(meta.get('art') or '(wyłączone)'))}
</div>
<table><thead><tr>
<th>Wynik</th><th>Gra</th><th>Źródło</th><th>AppID</th>
<th>Exe</th><th>Argumenty</th><th>Tagi</th><th>Uwagi</th>
</tr></thead><tbody>{''.join(trs)}</tbody></table>
</body></html>"""
    path.write_text(html_doc, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Dialogi - istniejące (zachowane + drobne poprawki)
# ---------------------------------------------------------------------------
class PathListDialog(tk.Toplevel):
    def __init__(self, parent, title, note, init_paths):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.grab_set()
        self.result = None
        tk.Label(self, text=title, bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 11, "bold")).pack(padx=12, pady=(10, 4), anchor="w")
        self._listbox = tk.Listbox(self, selectmode="extended", bg=C["bg3"], fg=C["fg"],
                                   highlightthickness=0, selectbackground=C["acc"],
                                   font=("Segoe UI", 9))
        self._listbox.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        for p in init_paths:
            self._listbox.insert("end", p)
        btn_frame = tk.Frame(self, bg=C["bg"])
        btn_frame.pack(fill="x", padx=12, pady=(0, 4))
        tk.Button(btn_frame, text="Dodaj", command=self._add, bg=C["bg3"], fg=C["fg"],
                  relief="flat", padx=8, pady=3, cursor="hand2").pack(side="left", padx=(0, 4))
        tk.Button(btn_frame, text="Edytuj", command=self._edit, bg=C["bg3"], fg=C["fg"],
                  relief="flat", padx=8, pady=3, cursor="hand2").pack(side="left", padx=4)
        tk.Button(btn_frame, text="Usuń", command=self._remove, bg=C["bg3"], fg=C["fg"],
                  relief="flat", padx=8, pady=3, cursor="hand2").pack(side="left", padx=4)
        tk.Label(self, text=note, bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 8, "italic"), justify="left").pack(fill="x", padx=12, pady=(0, 4))
        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=12, pady=(0, 10))
        tk.Button(bot, text="OK", command=self._ok, bg=C["acc"], fg=C["bg"],
                  relief="flat", padx=12, pady=4, cursor="hand2").pack(side="right", padx=(4, 0))
        tk.Button(bot, text="Anuluj", command=self._cancel, bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=10, pady=4, cursor="hand2").pack(side="right")
        self._center(parent)
        self.wait_window(self)

    def _center(self, parent):
        self.update_idletasks()
        pw, ph = parent.winfo_x(), parent.winfo_y()
        pw2, ph2 = parent.winfo_width(), parent.winfo_height()
        dw, dh = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw+(pw2-dw)//2}+{ph+(ph2-dh)//2}")

    def _add(self):
        path = filedialog.askdirectory(parent=self, title="Wybierz katalog")
        if path:
            self._listbox.insert("end", path)

    def _edit(self):
        sel = list(self._listbox.curselection())
        if not sel:
            return
        idx = sel[0]
        old = self._listbox.get(idx)
        path = filedialog.askdirectory(
            parent=self, title="Wybierz katalog",
            initialdir=old if os.path.isdir(old) else None,
        )
        if path:
            self._listbox.delete(idx)
            self._listbox.insert(idx, path)

    def _remove(self):
        for idx in reversed(list(self._listbox.curselection())):
            self._listbox.delete(idx)

    def _ok(self):
        self.result = [self._listbox.get(i) for i in range(self._listbox.size())]
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


# ---------------------------------------------------------------------------
# Grafiki Steam (grid folder) — wspólne helpery dla eksportu i edytora obrazów
# ---------------------------------------------------------------------------
# Nazwy plików bazują na appid skrótu non-Steam (to samo appid co w
# shortcuts.vdf). Steam czyta te pliki z userdata\<ID>\config\grid\.
#   klucz   etykieta            plik              endpoint listy SGDB (po game id)                            ikona?
STEAM_ART_TYPES = [
    ("cover", "Okładka 600×900", "{appid}p.png",
     "grids/game/{gid}?dimensions=600x900&types=static&limit={lim}", False),
    ("grid",  "Pozioma 460×215", "{appid}.png",
     "grids/game/{gid}?dimensions=460x215&types=static&limit={lim}", False),
    ("hero",  "Hero (tło)",      "{appid}_hero.png",
     "heroes/game/{gid}?types=static&limit={lim}", False),
    ("logo",  "Logo",            "{appid}_logo.png",
     "logos/game/{gid}?limit={lim}", False),
    ("icon",  "Ikona",           "{appid}.ico",
     "icons/game/{gid}?limit={lim}", True),
]
_STEAM_ART_BASE = "https://www.steamgriddb.com/api/v2"
# Trwały cache pobranych grafik SGDB (obrazy + listy) — w katalogu Cache programu.
_STEAM_ART_CACHE_DIR = CACHE_DIR / "steam_art"
_STEAM_ART_LIST_DIR = _STEAM_ART_CACHE_DIR / "_lists"


def _steam_cache_path(url: str) -> Path:
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return _STEAM_ART_CACHE_DIR / h[:2] / h


def steam_fetch_cached(url: str, timeout: int = 25):
    """Pobiera obraz z URL z TRWAŁYM cache na dysku (Cache/steam_art).

    Ponowne wyświetlenie/eksport tej samej grafiki nie pobiera jej z sieci.
    Zwraca bajty (z dysku lub świeżo pobrane) albo None."""
    if not url:
        return None
    p = _steam_cache_path(url)
    try:
        if p.is_file():
            return p.read_bytes()
    except Exception:
        pass
    b = fetch_api(url, timeout=timeout)
    if b:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_name(p.name + f".tmp-{uuid.uuid4().hex}")
            tmp.write_bytes(b)
            os.replace(tmp, p)
        except Exception:
            pass
    return b


def steam_sgdb_list(gid, type_key: str, sgdb_key: str, limit: int = 30,
                    use_cache: bool = True) -> list:
    """Lista grafik danego typu dla gry SGDB (elementy z polami url/thumb).

    Wynik cache'owany na dysku per (gid, typ) — kolejne otwarcia tej samej gry
    nie odpytują API. use_cache=False wymusza świeże pobranie."""
    tpl = next((e[3] for e in STEAM_ART_TYPES if e[0] == type_key), None)
    if not tpl or not gid or not sgdb_key:
        return []
    cache_p = _STEAM_ART_LIST_DIR / f"{gid}_{type_key}_{limit}.json"
    if use_cache:
        try:
            if cache_p.is_file():
                return json.loads(cache_p.read_text(encoding="utf-8"))
        except Exception:
            pass
    url = f"{_STEAM_ART_BASE}/" + tpl.format(gid=gid, lim=limit)
    d = fetch_api(url, hdrs={"Authorization": f"Bearer {sgdb_key}"})
    if not d:
        return []
    try:
        obj = json.loads(d)
        data = obj.get("data", []) if obj.get("success") else []
    except Exception:
        return []
    if data:
        try:
            cache_p.parent.mkdir(parents=True, exist_ok=True)
            cache_p.write_text(json.dumps(data), encoding="utf-8")
        except Exception:
            pass
    return data


def steam_download_game_art(target: dict, grid_dir, sgdb_key: str, im=None):
    """Pobiera komplet grafik dla jednej gry i zapisuje do grid_dir.

    target: {"appid", "name", "sgdb_id"(opc.), "art"(opc. {typ: url})}.
    Preferuje sgdb_id (wspólny z modułem .lnk); jak brak — szuka po nazwie.
    Dla obrazów wybranych ręcznie (target["art"][typ]) NADPISUJE plik; dla
    trybu auto NIE nadpisuje istniejących (nie kasuje własnych grafik).
    Zwraca (got_any: bool, gid)."""
    appid = target.get("appid")
    name = target.get("name", "")
    gid = target.get("sgdb_id")
    art = target.get("art") or {}
    grid_dir = Path(grid_dir)
    try:
        grid_dir.mkdir(parents=True, exist_ok=True)
    except Exception as ex:
        print(f"[Art] nie można utworzyć {grid_dir}: {ex}")
        return False, gid
    if not gid:
        if im is None:
            im = IconManager(sgdb_key)
        try:
            results = im.sgdb_search_with_fallback(str(name))
            gid = results[0].get("id") if results else None
        except Exception:
            gid = None
    got = False
    for key, _label, fname_t, _ep, is_icon in STEAM_ART_TYPES:
        dst = grid_dir / fname_t.format(appid=appid)
        chosen = art.get(key)
        if not chosen:
            if dst.exists():
                continue  # auto: nie nadpisuj istniejących
            if not gid:
                continue
            # limit=30 (nie 1) — współdzieli cache listy z edytorem grafik
            items = steam_sgdb_list(gid, key, sgdb_key, limit=30)
            chosen = items[0].get("url") if items else None
        if not chosen:
            continue
        raw = steam_fetch_cached(chosen, timeout=25)  # trwały cache po URL
        if not raw:
            continue
        try:
            if is_icon and PIL_OK:
                dst.write_bytes(make_ico_bytes(Image.open(BytesIO(raw))))
            else:
                dst.write_bytes(raw)
            got = True
        except Exception as ex:
            print(f"[Art] zapis {dst.name} nieudany: {ex}")
    return got, gid


class PlatformSpineDialog(tk.Toplevel):
    """Wybór logotypu grzbietu per platforma + kolorystyka (z pakietu online).

    - Kolorystyka: białe / kolorowe / czarne + „Zastosuj do wszystkich".
    - Per platforma: siatka wariantów logo — klik ustawia <KEY>.png w logo_dir.
    """
    def __init__(self, parent, cfg: dict, logo_dir):
        super().__init__(parent)
        self.title("Grzbiety platform — logo i kolorystyka")
        self.configure(bg=C["bg"])
        self.grab_set()
        self._cfg = cfg
        self._logo_dir = str(logo_dir)
        self._thumb_refs = []
        self._cur_key = None
        self._load_token = 0
        _style = cfg.get("spine_logo_style", _SPINE_STYLE_DEFAULT)

        top = tk.Frame(self, bg=C["bg"])
        top.pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(top, text="Kolorystyka:", bg=C["bg"], fg=C["fg2"]).pack(side="left")
        self.v_style = tk.StringVar()
        _disp = next((k for k, v in SPINE_LOGO_STYLES.items() if v == _style),
                     list(SPINE_LOGO_STYLES)[0])
        self.v_style.set(_disp)
        ttk.Combobox(top, textvariable=self.v_style, values=list(SPINE_LOGO_STYLES),
                     state="readonly", width=26).pack(side="left", padx=6)
        tk.Button(top, text="Zastosuj do wszystkich (pobierz)", command=self._apply_all,
                  bg=C["acc"], fg=C["bg"], relief="flat", padx=8,
                  cursor="hand2").pack(side="left", padx=6)
        self.v_status = tk.StringVar(value="")
        tk.Label(top, textvariable=self.v_status, bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 8)).pack(side="left", padx=6)

        main = tk.Frame(self, bg=C["bg"])
        main.pack(fill="both", expand=True)
        left = tk.Frame(main, bg=C["bg2"], highlightthickness=1,
                        highlightbackground=C["bg3"])
        left.pack(side="left", fill="y", padx=(12, 4), pady=(0, 10))
        self._lb = tk.Listbox(left, bg=C["bg3"], fg=C["fg"], width=20, height=24,
                              selectbackground=C["acc"], selectforeground=C["bg"],
                              font=("Segoe UI", 9), relief="flat", activestyle="none")
        self._lb.pack(fill="both", expand=True, padx=6, pady=6)
        # Lista platform: mapowane logo + WSZYSTKIE systemy ROM (np. SNESMSU1),
        # żeby dało się przypisać własne logo także wariantom/rozszerzeniom.
        _keys = list(PLATFORM_LOGO_TARGET.keys())
        _seen = {k.upper() for k in _keys}
        try:
            for _preset in ROM_SYSTEM_PRESETS:
                _nm = str(_preset.get("name", "")).upper()
                if _nm and _nm not in _seen:
                    _keys.append(_nm)
                    _seen.add(_nm)
        except Exception:
            pass
        for key in _keys:
            self._lb.insert("end", key)
        self._lb.bind("<<ListboxSelect>>", self._on_pick)

        right = tk.Frame(main, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(4, 12), pady=(0, 10))
        self.v_title = tk.StringVar(value="Wybierz platformę z listy po lewej")
        tk.Label(right, textvariable=self.v_title, bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(right, text="Kliknij wariant, aby ustawić grzbiet tej platformy:",
                 bg=C["bg"], fg=C["fg2"], font=("Segoe UI", 8)).pack(anchor="w")
        wrap = tk.Frame(right, bg=C["bg2"], highlightthickness=1,
                        highlightbackground=C["bg3"])
        wrap.pack(fill="both", expand=True, pady=(4, 4))
        self._canvas = tk.Canvas(wrap, bg=C["bg2"], highlightthickness=0)
        vsb = tk.Scrollbar(wrap, orient="vertical", command=self._canvas.yview,
                           bg=C["bg3"], width=8, relief="flat")
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._inner = tk.Frame(self._canvas, bg=C["bg2"])
        self._cw = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")
        self._inner.bind("<Configure>",
                         lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(self._cw, width=e.width))
        self.v_vstatus = tk.StringVar(value="")
        tk.Label(right, textvariable=self.v_vstatus, bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 8)).pack(anchor="w")

        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=12, pady=(0, 12))
        tk.Button(bot, text="Zamknij", command=self.destroy, bg=C["bg3"],
                  fg=C["fg2"], relief="flat", padx=12, pady=6).pack(side="right")
        tk.Button(bot, text="Wybierz plik z dysku…", command=self._pick_local_file,
                  bg=C["bg3"], fg=C["acc"], font=("Segoe UI", 9), relief="flat",
                  padx=10, pady=6, cursor="hand2").pack(side="left")
        tk.Label(bot, text="  (dowolny format: PNG/WEBP/JPG/ICO → zapis jako PNG)",
                 bg=C["bg"], fg=C["fg2"], font=("Segoe UI", 8)).pack(side="left")

        self.geometry("880x600")
        self.update_idletasks()
        try:
            pw, ph = parent.winfo_x(), parent.winfo_y()
            pw2, ph2 = parent.winfo_width(), parent.winfo_height()
            self.geometry(f"+{pw+(pw2-880)//2}+{ph+(ph2-600)//2}")
        except Exception:
            pass

    def _cur_style_folder(self):
        return SPINE_LOGO_STYLES.get(self.v_style.get(), _SPINE_STYLE_DEFAULT)

    def _apply_all(self):
        style = self._cur_style_folder()
        self._cfg["spine_logo_style"] = style
        self.v_status.set("Pobieram wszystkie…")

        def _work():
            try:
                n = download_platform_logos(self._logo_dir, style=style, overwrite=True)
                self.after(0, lambda: self.v_status.set(
                    f"Pobrano {n} logotypów ({self.v_style.get()})."))
                if self._cur_key:
                    self.after(0, lambda: self._load_variants(self._cur_key))
            except Exception as ex:
                self.after(0, lambda: self.v_status.set(f"Błąd: {ex}"))

        threading.Thread(target=_work, daemon=True).start()

    def _on_pick(self, _e=None):
        sel = self._lb.curselection()
        if not sel:
            return
        key = self._lb.get(sel[0])
        self._cur_key = key
        self.v_title.set(f"{key} — {PLATFORM_LOGO_TARGET.get(key, '')}")
        self._load_variants(key)

    def _load_variants(self, key):
        for w in self._inner.winfo_children():
            w.destroy()
        self._thumb_refs = []
        self.v_vstatus.set("Ładowanie wariantów…")
        self._load_token += 1
        token = self._load_token
        style = self._cur_style_folder()
        threading.Thread(target=self._variants_worker,
                         args=(key, style, token), daemon=True).start()

    def _variants_worker(self, key, style, token):
        variants = list_platform_logo_variants(key, style=style)

        def _build():
            if token != self._load_token:
                return
            if not variants:
                self.v_vstatus.set("Brak wariantów dla tej platformy w tej kolorystyce.")
                return
            self.v_vstatus.set(f"{len(variants)} wariantów — kliknij, aby ustawić.")
            cols = 3
            for idx, (nm, url) in enumerate(variants):
                r, c = divmod(idx, cols)
                cell = tk.Frame(self._inner, bg=C["bg3"])
                cell.grid(row=r, column=c, padx=6, pady=6, sticky="n")
                lbl = tk.Label(cell, bg="#101014", width=24, height=5, cursor="hand2")
                lbl.pack(padx=3, pady=3)
                cbk = lambda e, u=url, k=key: self._choose(u, k)
                lbl.bind("<Button-1>", cbk)
                cell.bind("<Button-1>", cbk)
                self.after(40 * idx,
                           lambda l=lbl, u=url, tok=token: self._load_thumb(l, u, tok))

        self.after(0, _build)

    def _load_thumb(self, label, url, token):
        if token != self._load_token:
            return
        try:
            b = fetch(url)
            if not b or not PIL_OK:
                return
            im = Image.open(BytesIO(b)).convert("RGBA")
            bg = Image.new("RGBA", (190, 70), (16, 16, 20, 255))
            im.thumbnail((182, 62), Image.LANCZOS)
            bg.alpha_composite(im, ((190 - im.width) // 2, (70 - im.height) // 2))
            ph = ImageTk.PhotoImage(bg)
            if label.winfo_exists() and token == self._load_token:
                self._thumb_refs.append(ph)
                label.config(image=ph, width=ph.width(), height=ph.height())
        except Exception:
            pass

    def _choose(self, url, key):
        self.v_vstatus.set(f"Ustawiam grzbiet {key}…")

        def _work():
            ok = install_logo_from_url(url, self._logo_dir, key)
            self.after(0, lambda: self.v_vstatus.set(
                f"Ustawiono grzbiet {key}. (odśwież ikony)" if ok
                else "Nie udało się pobrać wariantu."))

        threading.Thread(target=_work, daemon=True).start()

    def _pick_local_file(self):
        """Wybierz WŁASNY plik logo z dysku (dowolny format/nazwa, np. WEBP) i
        ustaw go dla wybranej platformy. Konwertujemy do <KEY>.png."""
        if not self._cur_key:
            self.v_vstatus.set("Najpierw wybierz platformę z listy po lewej.")
            return
        p = filedialog.askopenfilename(
            parent=self, title=f"Wybierz plik logo dla: {self._cur_key}",
            filetypes=[("Obrazy", "*.png *.webp *.jpg *.jpeg *.bmp *.ico *.gif *.tiff"),
                       ("Wszystkie pliki", "*.*")])
        if not p:
            return
        try:
            ld = Path(self._logo_dir)
            ld.mkdir(parents=True, exist_ok=True)
            out = ld / f"{self._cur_key.upper()}.png"
            if out.exists():
                try:
                    shutil.copy2(out, out.with_suffix(".png.bak"))
                except Exception:
                    pass
            if PIL_OK:
                Image.open(p).convert("RGBA").save(out, "PNG")   # WEBP/JPG/… → PNG
            else:
                shutil.copy2(p, out)
            self.v_vstatus.set(f"Ustawiono własne logo dla {self._cur_key}. "
                               "(odśwież ikony)")
        except Exception as e:
            self.v_vstatus.set(f"Błąd wczytania pliku: {e}")


class ManualSearchDialog(tk.Toplevel):
    """Okno ręcznego wyszukiwania na SGDB.

    FIX v4-3: Akceptuje trzy formaty wejścia:
    1. Tytuł gry — wyszukiwanie autocomplete z automatycznym fallbackiem
    2. URL SGDB — np. https://www.steamgriddb.com/game/5254926
    3. Samo ID SGDB — np. 5254926

    Dzięki temu gry nieindeksowane przez autocomplete (np. Legaia 2, stare PS2)
    można znaleźć kopiując URL ze strony SGDB.
    """
    def __init__(self, parent, initial_title):
        super().__init__(parent)
        self.title("Ręczne wyszukiwanie")
        self.configure(bg=C["bg"])
        self.resizable(True, False)
        self.grab_set()
        self.result = None
        self.var = tk.StringVar(value=initial_title)
        tk.Label(self, text="Ręczne wyszukiwanie tytułu w SteamGridDB",
                 bg=C["bg"], fg=C["acc"], font=("Segoe UI", 11, "bold")).pack(fill="x", padx=12, pady=(12, 4))
        tk.Label(self,
                 text="Wpisz tytuł lub wklej URL/ID ze strony SteamGridDB  "
                      "(np. steamgriddb.com/game/5254926)",
                 bg=C["bg"], fg=C["fg2"], font=("Segoe UI", 8)).pack(fill="x", padx=12, pady=(0, 8))
        row = tk.Frame(self, bg=C["bg"])
        row.pack(fill="x", padx=12, pady=(0, 8))
        ent = tk.Entry(row, textvariable=self.var, bg=C["bg3"], fg=C["fg"],
                       insertbackground="white", relief="flat", font=("Segoe UI", 10))
        ent.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ent.focus_set()
        ent.selection_range(0, "end")
        tk.Button(row, text="Szukaj", command=self._ok, bg=C["acc"], fg=C["bg"],
                  relief="flat", padx=12, pady=4, cursor="hand2").pack(side="left")
        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=12, pady=(0, 12))
        tk.Button(bot, text="Anuluj", command=self._cancel, bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=10, pady=4, cursor="hand2").pack(side="right")
        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self._cancel())
        self.update_idletasks()
        pw, ph = parent.winfo_x(), parent.winfo_y()
        pw2, ph2 = parent.winfo_width(), parent.winfo_height()
        dw, dh = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw+(pw2-dw)//2}+{ph+(ph2-dh)//2}")
        self.wait_window(self)

    def _ok(self):
        q = self.var.get().strip()
        if q:
            self.result = q
            self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class SgdbPickDialog(tk.Toplevel):
    def __init__(self, parent, game_name, results, sgdb_key: str):
        super().__init__(parent)
        self.title(f"Wybierz grę — {game_name}")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.grab_set()
        self.result_id = None
        self.result_name = None
        self._refs = []
        self._sgdb_key = sgdb_key
        tk.Label(self, text=f'Niejednoznaczny wynik dla: "{game_name}"', bg=C["bg"],
                 fg=C["yel"], font=("Segoe UI", 10, "bold")).pack(padx=16, pady=(14, 4))
        tk.Label(self, text="Wybierz właściwą grę ze znalezionych wyników SteamGridDB:",
                 bg=C["bg"], fg=C["fg2"], font=("Segoe UI", 8)).pack(padx=16, pady=(0, 8))
        frame = tk.Frame(self, bg=C["bg"])
        frame.pack(padx=16, pady=4)
        for idx, r in enumerate(results):
            rid, rname = r.get("id"), r.get("name", "?")
            rtypes = ", ".join(r.get("types", [])) if r.get("types") else ""
            score = name_similarity(game_name, rname)
            row = tk.Frame(frame, bg=C["bg2"], highlightthickness=1, highlightbackground=C["bg3"])
            row.pack(fill="x", pady=3)
            cover_lbl = tk.Label(row, bg=C["bg3"], width=8, height=4)
            cover_lbl.pack(side="left", padx=(8, 6), pady=6)
            self.after(50 * idx, lambda lbl=cover_lbl, gid=rid: self._load_cover(lbl, gid))
            info = tk.Frame(row, bg=C["bg2"])
            info.pack(side="left", fill="x", expand=True, pady=6)
            tk.Label(info, text=rname, bg=C["bg2"], fg=C["fg"],
                     font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x")
            det = f"ID: {rid}"
            if rtypes:
                det += f" | {rtypes}"
            det += f" | dopasowanie: {score*100:.0f}%"
            tk.Label(info, text=det, bg=C["bg2"], fg=C["fg2"],
                     font=("Segoe UI", 8), anchor="w").pack(fill="x")
            tk.Button(row, text="Wybierz",
                      command=lambda _id=rid, _n=rname: self._pick(_id, _n),
                      bg=C["acc"], fg=C["bg"], font=("Segoe UI", 9, "bold"),
                      relief="flat", padx=10, pady=4, cursor="hand2").pack(side="right", padx=8, pady=6)
        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=16, pady=(8, 14))
        tk.Button(bot, text="Pomiń — użyj tylko EXE", command=self._skip,
                  bg=C["bg3"], fg=C["fg2"], font=("Segoe UI", 9),
                  relief="flat", padx=10, pady=4, cursor="hand2").pack(side="right")
        self.update_idletasks()
        pw, ph = parent.winfo_x(), parent.winfo_y()
        pw2, ph2 = parent.winfo_width(), parent.winfo_height()
        dw, dh = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw+(pw2-dw)//2}+{ph+(ph2-dh)//2}")
        self.wait_window(self)

    def _load_cover(self, label, sgdb_id):
        if not sgdb_id:
            return
        try:
            d = fetch_api(
                f"https://www.steamgriddb.com/api/v2/grids/game/{sgdb_id}?dimensions=460x215&limit=1",
                hdrs={"Authorization": f"Bearer {self._sgdb_key}"},
            )
            if d:
                items = json.loads(d).get("data", [])
                if items:
                    b = fetch(items[0].get("url", ""))
                    if b:
                        ph = thumb_from_bytes(b, 60)
                        if ph:
                            self._refs.append(ph)
                            label.config(image=ph, bg=C["bg3"])
        except Exception:
            pass

    def _pick(self, sgdb_id, name):
        self.result_id = sgdb_id
        self.result_name = name
        self.destroy()

    def _skip(self):
        self.result_id = None
        self.result_name = None
        self.destroy()


class _ArtProgressDialog(tk.Toplevel):
    """Pasek postępu pobierania grafik Steam (SGDB) dla wielu gier.

    Niemodalne okno; pobieranie w wątku roboczym, aktualizacje przez after().
    Można anulować w trakcie."""
    def __init__(self, parent, targets, grid_dir, sgdb_key: str):
        super().__init__(parent)
        self.title("Pobieranie grafik Steam")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self._targets = list(targets)
        self._grid_dir = Path(grid_dir)
        self._sgdb_key = sgdb_key
        self._cancel = False
        total = len(self._targets)
        tk.Label(self, text="Pobieranie grafik ze SteamGridDB…",
                 bg=C["bg"], fg=C["acc"], font=("Segoe UI", 10, "bold")
                 ).pack(anchor="w", padx=14, pady=(12, 6))
        self.v_cur = tk.StringVar(value="")
        tk.Label(self, textvariable=self.v_cur, bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 9), anchor="w", width=54,
                 justify="left").pack(fill="x", padx=14)
        self.pb = ttk.Progressbar(self, mode="determinate",
                                  maximum=max(total, 1), length=440)
        self.pb.pack(padx=14, pady=8)
        self.v_count = tk.StringVar(value=f"0 / {total}")
        tk.Label(self, textvariable=self.v_count, bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 8)).pack(padx=14)
        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=14, pady=(6, 12))
        self.btn = tk.Button(bot, text="Anuluj", command=self._do_cancel,
                             bg=C["bg3"], fg=C["fg2"], relief="flat",
                             padx=12, pady=5, cursor="hand2")
        self.btn.pack(side="right")
        self.protocol("WM_DELETE_WINDOW", self._do_cancel)
        self.update_idletasks()
        try:
            pw, ph = parent.winfo_x(), parent.winfo_y()
            pw2, ph2 = parent.winfo_width(), parent.winfo_height()
            dw, dh = self.winfo_width(), self.winfo_height()
            self.geometry(f"+{pw+(pw2-dw)//2}+{ph+(ph2-dh)//2}")
        except Exception:
            pass
        threading.Thread(target=self._worker, daemon=True).start()

    def _do_cancel(self):
        self._cancel = True
        self.v_cur.set("Przerywanie po bieżącej grze…")

    def _worker(self):
        im = IconManager(self._sgdb_key)
        ok = miss = 0
        total = len(self._targets)
        for i, t in enumerate(self._targets, 1):
            if self._cancel:
                break
            nm = t.get("name", "")
            self.after(0, lambda i=i, nm=nm, total=total: (
                self.v_cur.set(f"[{i}/{total}] {nm}"),
                self.v_count.set(f"{i} / {total}"),
                self.pb.config(value=i)))
            try:
                got, _gid = steam_download_game_art(
                    t, self._grid_dir, self._sgdb_key, im)
                if got:
                    ok += 1
                else:
                    miss += 1
                print(f"[Art] {'OK' if got else 'brak'}: {nm}")
            except Exception as ex:
                miss += 1
                print(f"[Art] błąd {nm}: {ex}")
        self.after(0, lambda: self._done(ok, miss, total))

    def _done(self, ok, miss, total):
        state = "przerwano" if self._cancel else "zakończono"
        self.v_cur.set(f"Grafiki: {state}. Z grafiką: {ok}, bez: {miss}.")
        try:
            self.pb.config(value=total)
        except Exception:
            pass
        self.v_count.set(f"{ok+miss} / {total}")
        self.btn.config(text="Zamknij", command=self.destroy)
        print(f"[Art] {state}: {ok} z grafiką, {miss} bez. Folder: {self._grid_dir}")


class ExePickDialog(tk.Toplevel):
    def __init__(self, parent, game_name, exe_list):
        super().__init__(parent)
        self.title(f"Wybierz EXE — {game_name}")
        self.configure(bg=C["bg"])
        self.resizable(True, False)
        self.grab_set()
        self.result_exe = None
        self._refs = []
        tk.Label(self, text=f'Wybierz plik uruchamiający grę: "{game_name}"',
                 bg=C["bg"], fg=C["acc"], font=("Segoe UI", 10, "bold")).pack(padx=16, pady=(14, 4))
        tk.Label(self, text="Lista wykrytych plików EXE (posortowane od największego):",
                 bg=C["bg"], fg=C["fg2"], font=("Segoe UI", 8)).pack(padx=16, pady=(0, 6))
        list_frame = tk.Frame(self, bg=C["bg"])
        list_frame.pack(fill="both", expand=True, padx=16, pady=4)
        canvas = tk.Canvas(list_frame, bg=C["bg"], highlightthickness=0, height=320)
        vsb = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview,
                           bg=C["bg3"], width=8, relief="flat")
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=C["bg"])
        cw = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
        for exe_path in exe_list:
            p = Path(exe_path)
            try:
                mb = p.stat().st_size / 1024 / 1024
            except Exception:
                mb = 0
            rel = str(p)
            row = tk.Frame(inner, bg=C["bg2"], highlightthickness=1, highlightbackground=C["bg3"])
            row.pack(fill="x", pady=2, padx=2)
            ico_lbl = tk.Label(row, bg=C["bg2"], width=5, height=3)
            ico_lbl.pack(side="left", padx=(6, 4), pady=4)
            self.after(0, lambda lbl=ico_lbl, ep=exe_path: self._load_exe_icon(lbl, ep))
            info_f = tk.Frame(row, bg=C["bg2"])
            info_f.pack(side="left", fill="x", expand=True, pady=4)
            tk.Label(info_f, text=p.name, bg=C["bg2"], fg=C["fg"],
                     font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
            tk.Label(info_f, text=f"{rel} ({mb:.1f} MB)", bg=C["bg2"], fg=C["fg2"],
                     font=("Segoe UI", 7), anchor="w").pack(fill="x")
            tk.Button(row, text="Wybierz", command=lambda ep=exe_path: self._pick(ep),
                      bg=C["acc"], fg=C["bg"], font=("Segoe UI", 9, "bold"),
                      relief="flat", padx=10, pady=3, cursor="hand2").pack(side="right", padx=8, pady=4)
        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=16, pady=(6, 14))
        tk.Button(bot, text="Przeglądaj ręcznie...", command=self._browse,
                  bg=C["bg3"], fg=C["fg"], font=("Segoe UI", 9),
                  relief="flat", padx=10, pady=4, cursor="hand2").pack(side="left")
        tk.Button(bot, text="Anuluj", command=self.destroy, bg=C["bg3"], fg=C["fg2"],
                  font=("Segoe UI", 9), relief="flat", padx=10, pady=4, cursor="hand2").pack(side="right")
        self.update_idletasks()
        pw, ph = parent.winfo_x(), parent.winfo_y()
        pw2, ph2 = parent.winfo_width(), parent.winfo_height()
        dw, dh = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw+(pw2-dw)//2}+{ph+(ph2-dh)//2}")
        self.wait_window(self)

    def _load_exe_icon(self, label, exe_path):
        try:
            th = thumb_from_exe(exe_path, 40)
            if th:
                self._refs.append(th)
                label.config(image=th)
        except Exception:
            pass

    def _pick(self, exe_path):
        self.result_exe = exe_path
        self.destroy()

    def _browse(self):
        p = filedialog.askopenfilename(
            title="Wybierz plik EXE gry",
            filetypes=[("Executable", "*.exe"), ("Wszystkie", "*.*")],
        )
        if p:
            self.result_exe = p
            self.destroy()


# ---------------------------------------------------------------------------
# Nowe dialogi: SettingsDialog, DryRunDialog, ProfileDialog
# ---------------------------------------------------------------------------
class SettingsDialog(tk.Toplevel):
    """Okno ustawień — przewijane, z sekcją Dodatkowe źródła grafik."""

    def __init__(self, parent, cfg: dict):
        super().__init__(parent)
        self.title("Ustawienia")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.grab_set()
        self.result: dict | None = None
        self._cfg = cfg

        api = cfg.get("api_keys", {})
        flt = cfg.get("filters", {})
        src = cfg.get("extra_sources", {})

        # ── Zmienne stanu ──────────────────────────────────────
        self.v_steam_key  = tk.StringVar(value=api.get("steam_api_key", ""))
        self.v_sgdb_key   = tk.StringVar(value=api.get("sgdb_key", ""))
        self.v_steam_id   = tk.StringVar(value=api.get("steam_id64", ""))
        self.v_use_web    = tk.BooleanVar(value=cfg.get("use_steam_web_api", True))
        self.v_exe_re     = tk.StringVar(value=flt.get("exe_skip_regex", DEFAULT_EXE_SKIP_REGEX))
        self.v_min_size   = tk.IntVar(value=int(flt.get("min_icon_size", DEFAULT_MIN_SIZE)))
        self.v_type       = tk.StringVar(value=flt.get("preferred_icon_type", "any"))
        self.v_shape      = tk.StringVar(value=flt.get("icon_shape", "any"))
        self.v_max_icons  = tk.StringVar(value=self._max_to_choice(flt.get("max_icons_per_game", DEFAULT_MAX_ICONS)))
        self.v_use_vdf    = tk.BooleanVar(value=cfg.get("use_libraryfolders_vdf", True))
        self.v_icon_spine = tk.BooleanVar(value=bool(cfg.get("icon_platform_spine", False)))
        self.v_spine_side = tk.StringVar(value=cfg.get("icon_spine_side", "left"))
        self.v_scan_epic  = tk.BooleanVar(value=cfg.get("scan_epic", True))
        self.v_scan_gog     = tk.BooleanVar(value=cfg.get("scan_gog", True))
        self.v_scan_startup = tk.BooleanVar(value=cfg.get("scan_on_startup", False))
        self.v_cache_limit = tk.IntVar(value=int(cfg.get("cache_limit_mb", 2048)))
        # Extra sources
        self.v_steam_cdn  = tk.BooleanVar(value=bool(src.get("steam_cdn", True)))
        self.v_libretro   = tk.BooleanVar(value=bool(src.get("libretro", True)))
        self.v_igdb       = tk.BooleanVar(value=bool(src.get("igdb", False)))
        self.v_igdb_id    = tk.StringVar(value=src.get("igdb_client_id", ""))
        self.v_igdb_sec   = tk.StringVar(value=src.get("igdb_client_secret", ""))
        self.v_tgdb       = tk.BooleanVar(value=bool(src.get("tgdb", False)))
        self.v_tgdb_key   = tk.StringVar(value=src.get("tgdb_key", ""))
        self.v_ss         = tk.BooleanVar(value=bool(src.get("screenscraper", False)))
        self.v_ss_user    = tk.StringVar(value=src.get("screenscraper_user", ""))
        self.v_ss_pass    = tk.StringVar(value=src.get("screenscraper_pass", ""))
        self.v_ss_devid   = tk.StringVar(value=src.get("screenscraper_devid", ""))
        self.v_ss_devpass = tk.StringVar(value=src.get("screenscraper_devpass", ""))

        # ── Przewijany kontener ────────────────────────────────
        outer = tk.Frame(self, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        vsb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview,
                           bg=C["bg3"], width=8, relief="flat")
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=C["bg"])
        cw = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(cw, width=e.width))
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        # FIX v7.4: kółko działa też nad widgetami wewnątrz okna ustawień
        def _set_scroll_lin_up(e):
            canvas.yview_scroll(-1, "units")
        def _set_scroll_lin_dn(e):
            canvas.yview_scroll(1, "units")
        canvas.bind("<Button-4>", _set_scroll_lin_up)
        canvas.bind("<Button-5>", _set_scroll_lin_dn)
        def _on_set_enter(_e):
            canvas.bind_all("<MouseWheel>",
                lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
            canvas.bind_all("<Button-4>", _set_scroll_lin_up)
            canvas.bind_all("<Button-5>", _set_scroll_lin_dn)
        def _on_set_leave(_e):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        self.bind("<Enter>", _on_set_enter)
        self.bind("<Leave>", _on_set_leave)
        self.bind("<Destroy>", lambda _e: _on_set_leave(None))

        pad = {"padx": 12, "pady": 4}
        P = inner   # alias dla pack calls

        # ── Sekcja: Klucze API i konto ─────────────────────────
        self._hdr(P, "Klucze API i konto")
        self._row(P, "Steam Web API Key:",    self.v_steam_key)
        self._row(P, "SteamID64:",            self.v_steam_id)
        # SGDB row + inline test button
        r_sgdb = tk.Frame(P, bg=C["bg"])
        r_sgdb.pack(fill="x", padx=12, pady=3)
        tk.Label(r_sgdb, text="SteamGridDB API Key:", bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 9), width=24, anchor="w").pack(side="left")
        tk.Entry(r_sgdb, textvariable=self.v_sgdb_key, width=36,
                 bg=C["bg3"], fg=C["fg"], insertbackground="white",
                 relief="flat", font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))
        self._lbl_sgdb_test = tk.Label(r_sgdb, text="", bg=C["bg"],
                                       fg=C["fg2"], font=("Segoe UI", 9))
        self._lbl_sgdb_test.pack(side="left", padx=(0, 6))
        tk.Button(r_sgdb, text="⬡ Test", cursor="hand2",
                  command=lambda: self._test_sgdb(self._lbl_sgdb_test),
                  bg=C["bg3"], fg=C["acc"],
                  relief="flat", padx=8, pady=2).pack(side="left")
        self._chk(P, "Używaj Steam Web API (lista posiadanych gier)",
                  self.v_use_web)

        # ── Sekcja: Filtry skanowania ──────────────────────────
        self._hdr(P, "Filtry skanowania")
        self._row(P, "Regex pomijanych EXE:",         self.v_exe_re, width=60)
        self._row_int(P, "Min. rozdzielczość ikony:", self.v_min_size)
        self._row_combo(P, "Preferowany typ ikony:",  self.v_type,       ICON_TYPES)
        self._row_combo(P, "Filtr kształtu:",         self.v_shape,      ICON_SHAPES)
        self._row_combo(P, "Max ikon na grę:",        self.v_max_icons,  MAX_ICONS_CHOICES)
        self._chk(P, "Grzbiet platformy na ikonie ROM-a "
                     "(odróżnia te same tytuły na PS1/PS2/GameCube…)", self.v_icon_spine)
        self._row_combo(P, "Strona grzbietu:", self.v_spine_side, ["left", "right"])
        _spine_row = tk.Frame(P, bg=C["bg"])
        _spine_row.pack(fill="x", **pad)
        tk.Button(_spine_row, text="Grzbiety platform: wybór logo i kolorystyki…",
                  command=self._open_spine_picker, bg=C["bg3"], fg=C["acc"],
                  font=("Segoe UI", 9), relief="flat", padx=10, pady=4,
                  cursor="hand2").pack(side="left")

        # ── Sekcja: Windows — strzałki na skrótach ─────────────
        self._hdr(P, "Windows — strzałki na skrótach")
        _arr = tk.Frame(P, bg=C["bg"])
        _arr.pack(fill="x", **pad)
        tk.Button(_arr, text="Usuń strzałki ze skrótów",
                  command=lambda: self._shortcut_arrows(True), bg=C["bg3"],
                  fg=C["orn"], font=("Segoe UI", 9), relief="flat",
                  padx=10, pady=4, cursor="hand2").pack(side="left")
        tk.Button(_arr, text="Przywróć strzałki",
                  command=lambda: self._shortcut_arrows(False), bg=C["bg3"],
                  fg=C["grn"], font=("Segoe UI", 9), relief="flat",
                  padx=10, pady=4, cursor="hand2").pack(side="left", padx=(6, 0))
        tk.Label(P, text="Zmiana SYSTEMOWA (wszystkie skróty w Windows), wymaga "
                         "administratora (UAC) i restartu Eksploratora. Odwracalne.",
                 bg=C["bg"], fg=C["fg2"], font=("Segoe UI", 8),
                 wraplength=560, justify="left").pack(anchor="w", padx=12)

        # ── Sekcja: Integracje ─────────────────────────────────
        self._hdr(P, "Integracje")
        self._chk(P, "Parsuj libraryfolders.vdf (biblioteki Steam)",  self.v_use_vdf)
        self._chk(P, "Skanuj gry Epic Games (LauncherInstalled.dat)", self.v_scan_epic)
        self._chk(P, "Skanuj gry GOG.com (rejestr Windows)",          self.v_scan_gog)
        self._chk(P, "Sprawdzaj zmiany ROM-ów przy starcie programu", self.v_scan_startup)
        # v7.9 (D): limit rozmiaru cache assetów (eksmisja LRU po skanie)
        self._row_int(P, "Limit cache assetów (MB, 0 = bez limitu):", self.v_cache_limit)

        # ── Sekcja: Dodatkowe źródła grafik ───────────────────
        self._hdr(P, "Dodatkowe źródła grafik")
        tk.Label(P, text="Zaznacz źródło i wpisz dane dostępowe — pola są zawsze widoczne.",
                 bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 8, "italic")).pack(anchor="w", padx=14, pady=(0, 6))

        # ── Steam CDN (bez klucza) ─────────────────────────────
        self._src_block(P,
            chk_var=self.v_steam_cdn,
            title="Steam CDN",
            subtitle="Oficjalne grafiki Steam — nie wymaga klucza, działa automatycznie dla gier Steam",
            color=C["grn"],
            fields=[],          # brak pól do wpisania
        )

        # ── Libretro Thumbnails (bez klucza) ──────────────────
        self._src_block(P,
            chk_var=self.v_libretro,
            title="Libretro Thumbnails",
            subtitle="Box art z GitHub dla emulatorów — nie wymaga klucza, działa automatycznie dla ROM-ów",
            color=C["grn"],
            fields=[],
        )

        # ── IGDB ──────────────────────────────────────────────
        self._src_block(P,
            chk_var=self.v_igdb,
            title="IGDB (Internet Game Database)",
            subtitle="Box art, artworki, screenshoty  ·  Klucz: dev.twitch.tv → My Applications → New App",
            color=C["acc"],
            fields=[
                ("Client ID:",     self.v_igdb_id,  50, False),
                ("Client Secret:", self.v_igdb_sec, 50, True),
            ],
            test_fn=self._test_igdb,
        )

        # ── TheGamesDB ────────────────────────────────────────
        self._src_block(P,
            chk_var=self.v_tgdb,
            title="TheGamesDB",
            subtitle="Box art, fan art, bannery  ·  Klucz: forums.thegamesdb.net → darmowe konto",
            color=C["acc"],
            fields=[
                ("API Key:", self.v_tgdb_key, 50, False),
            ],
            test_fn=self._test_tgdb,
        )

        # ── ScreenScraper ─────────────────────────────────────
        self._src_block(P,
            chk_var=self.v_ss,
            title="ScreenScraper",
            subtitle=(
                "Najlepszy dla retro / ROM-ów  ·  Konto: screenscraper.fr\n"
                "Dev ID/Pass (opcjonalne): screenscraper.fr → Mon Compte → API — "
                "wyższy limit zapytań. Jeśli puste, użyte będą dane konta."
            ),
            color=C["orn"],
            fields=[
                ("Login:",          self.v_ss_user,   30, False),
                ("Hasło:",          self.v_ss_pass,   30, True),
                ("Dev ID:",         self.v_ss_devid,  30, False),
                ("Dev Password:",   self.v_ss_devpass,30, True),
            ],
            test_fn=self._test_ss,
        )

        tk.Frame(P, bg=C["bg3"], height=1).pack(fill="x", padx=12, pady=(8, 4))

        # ── Stopka z przyciskami ───────────────────────────────
        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=12, pady=(4, 10))
        tk.Button(bot, text="Przywróć domyślne", command=self._defaults,
                  bg=C["bg3"], fg=C["yel"], relief="flat", padx=10, pady=4,
                  cursor="hand2").pack(side="left")
        tk.Button(bot, text="OK", command=self._ok, bg=C["acc"], fg=C["bg"],
                  relief="flat", padx=14, pady=4, cursor="hand2").pack(side="right", padx=(4, 0))
        tk.Button(bot, text="Anuluj", command=self.destroy, bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=10, pady=4, cursor="hand2").pack(side="right")

        self.geometry("700x640")
        self.update_idletasks()
        pw = parent.winfo_x() + (parent.winfo_width() - 700) // 2
        ph = parent.winfo_y() + (parent.winfo_height() - 640) // 2
        self.geometry(f"+{pw}+{ph}")
        self.wait_window(self)

    def _hdr(self, parent, text):
        tk.Label(parent, text=text, bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(12, 4))

    def _open_spine_picker(self):
        logo_dir = (self._cfg.get("platform_logo_dir")
                    or str(SCRIPT_DIR / "platform_logos"))
        PlatformSpineDialog(self, self._cfg, logo_dir)

    def _shortcut_arrows(self, remove: bool):
        if not messagebox.askyesno(
                "Strzałki na skrótach",
                ("Usunąć strzałki ze WSZYSTKICH skrótów w Windows?"
                 if remove else "Przywrócić domyślne strzałki na skrótach?")
                + "\n\nTo zmiana SYSTEMOWA. Pojawi się prośba o uprawnienia "
                  "administratora (UAC), a Eksplorator zostanie zrestartowany "
                  "(mignie pasek zadań). Zmiana jest odwracalna."):
            return
        ok, msg = set_shortcut_arrows(remove)
        if not ok:
            messagebox.showerror("Strzałki na skrótach", msg)
            return
        if messagebox.askyesno("Strzałki na skrótach",
                msg + "\n\nZrestartować teraz Eksploratora, aby zastosować zmianę?"):
            self.after(1200, restart_explorer)

    def _chk(self, parent, text, var, **kw):
        tk.Checkbutton(parent, text=text, variable=var,
                       bg=C["bg"], fg=C["fg"], activebackground=C["bg"],
                       selectcolor=C["bg3"], font=("Segoe UI", 9),
                       **kw).pack(anchor="w", padx=12, pady=3)

    def _src_block(self, parent, chk_var, title, subtitle, color, fields,
                   test_fn=None):
        """Blok jednego źródła grafik: checkbox + opis + pola + przycisk Test.

        Pola są ZAWSZE widoczne.
        fields: lista krotek (label, var, width, is_password)
        test_fn: opcjonalna funkcja (status_label) → None — testuje połączenie.
        """
        wrap = tk.Frame(parent, bg=C["bg2"],
                        highlightthickness=2,
                        highlightbackground=C["bg3"])
        wrap.pack(fill="x", padx=12, pady=(4, 2))

        hdr = tk.Frame(wrap, bg=C["bg2"])
        hdr.pack(fill="x", padx=8, pady=(6, 2))
        tk.Label(hdr, text="●", bg=C["bg2"], fg=color,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 4))
        tk.Checkbutton(hdr, text=title, variable=chk_var,
                       bg=C["bg2"], fg=C["fg"],
                       activebackground=C["bg2"], selectcolor=C["bg3"],
                       font=("Segoe UI", 9, "bold")).pack(side="left")

        tk.Label(wrap, text=subtitle, bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 7, "italic"),
                 anchor="w", wraplength=560).pack(fill="x", padx=12, pady=(0, 4))

        if fields:
            fields_frame = tk.Frame(wrap, bg=C["bg2"])
            fields_frame.pack(fill="x", padx=8, pady=(2, 2))
            for label, var, width, is_pass in fields:
                r = tk.Frame(fields_frame, bg=C["bg2"])
                r.pack(fill="x", pady=2)
                tk.Label(r, text=label, bg=C["bg2"], fg=C["fg2"],
                         font=("Segoe UI", 9), width=16, anchor="w").pack(side="left")
                show = "*" if is_pass else ""
                tk.Entry(r, textvariable=var, width=width, show=show,
                         bg=C["bg3"], fg=C["fg"],
                         insertbackground="white", relief="flat",
                         font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True)
            # Przycisk "Test połączenia" + status
            if test_fn:
                test_row = tk.Frame(fields_frame, bg=C["bg2"])
                test_row.pack(fill="x", pady=(4, 2))
                # 16-char szeroka pusta etykieta = wyrównanie z polem Entry
                tk.Label(test_row, text="", bg=C["bg2"],
                         width=16).pack(side="left")
                status_lbl = tk.Label(test_row, text="", bg=C["bg2"],
                                      fg=C["fg2"], font=("Segoe UI", 9))
                status_lbl.pack(side="left", padx=(0, 10))
                tk.Button(test_row, text="⬡ Test połączenia",
                          command=lambda fn=test_fn, lbl=status_lbl: fn(lbl),
                          bg=C["bg3"], fg=C["acc"],
                          relief="flat", padx=8, pady=2,
                          cursor="hand2").pack(side="left")
            tk.Frame(wrap, bg=C["bg3"], height=1).pack(fill="x",
                                                        padx=8, pady=(4, 0))
            tk.Frame(wrap, bg=C["bg2"], height=4).pack()
        else:
            tk.Label(wrap, text="✓ Nie wymaga konfiguracji",
                     bg=C["bg2"], fg=color,
                     font=("Segoe UI", 8)).pack(anchor="w", padx=12, pady=(0, 6))

    # ── Metody testujące połączenia z API ─────────────────────────────

    def _run_test(self, lbl, fn):
        """Uruchom test w tle, pokaż spinner → wynik."""
        lbl.config(text="⏳ testowanie…", fg=C["yel"])
        lbl.update_idletasks()
        def _worker():
            try:
                ok, msg = fn()
            except Exception as e:
                ok, msg = False, str(e)[:60]
            self.after(0, lambda: lbl.config(
                text=f"✓ {msg}" if ok else f"✗ {msg}",
                fg=C["grn"] if ok else C["red"],
            ))
        threading.Thread(target=_worker, daemon=True).start()

    def _test_sgdb(self, lbl):
        key = self.v_sgdb_key.get().strip()
        if not key:
            lbl.config(text="✗ Wpisz klucz", fg=C["red"]); return
        def _check():
            d = fetch_api(
                "https://www.steamgriddb.com/api/v2/search/autocomplete/test",
                hdrs={"Authorization": f"Bearer {key}"}, timeout=8,
            )
            if not d:
                return False, "brak odpowiedzi"
            try:
                j = json.loads(d)
                return j.get("success", False), ("OK" if j.get("success") else j.get("errors", ["błąd"])[0])
            except Exception:
                return False, "błąd JSON"
        self._run_test(lbl, _check)

    def _test_igdb(self, lbl):
        cid = self.v_igdb_id.get().strip()
        sec = self.v_igdb_sec.get().strip()
        if not cid or not sec:
            lbl.config(text="✗ Wpisz Client ID i Secret", fg=C["red"]); return
        def _check():
            params = (f"client_id={urllib.request.quote(cid)}"
                      f"&client_secret={urllib.request.quote(sec)}"
                      f"&grant_type=client_credentials")
            d = fetch_post(f"https://id.twitch.tv/oauth2/token?{params}", b"",
                           hdrs={"Content-Type": "application/x-www-form-urlencoded"})
            if not d:
                return False, "brak odpowiedzi Twitch"
            try:
                data = json.loads(d)
            except Exception:
                return False, "błąd JSON"
            token = data.get("access_token", "")
            if not token:
                return False, data.get("message", "brak tokenu")[:50]
            # Test IGDB query
            d2 = fetch_post("https://api.igdb.com/v4/games",
                            b"fields name; limit 1;",
                            hdrs={"Client-ID": cid,
                                  "Authorization": f"Bearer {token}",
                                  "Content-Type": "text/plain"})
            if not d2:
                return False, "token OK, ale API nie odpowiada"
            try:
                rows = json.loads(d2)
                return True, f"token OK, gier w bazie: {rows[0].get('name','?')!r}"
            except Exception:
                return False, "błąd odpowiedzi API"
        self._run_test(lbl, _check)

    def _test_tgdb(self, lbl):
        key = self.v_tgdb_key.get().strip()
        if not key:
            lbl.config(text="✗ Wpisz API Key", fg=C["red"]); return
        def _check():
            d = fetch_api(
                f"https://api.thegamesdb.net/v1/Games/ByGameName"
                f"?apikey={urllib.request.quote(key)}&name=test&fields=overview",
                timeout=8,
            )
            if not d:
                return False, "brak odpowiedzi"
            try:
                j = json.loads(d)
                code = j.get("code", 0)
                if code == 200:
                    count = j.get("data", {}).get("count", "?")
                    return True, f"OK — znaleziono {count} wyników"
                return False, j.get("status", f"kod {code}")[:60]
            except Exception:
                return False, "błąd JSON"
        self._run_test(lbl, _check)

    def _test_ss(self, lbl):
        user = self.v_ss_user.get().strip()
        pwd  = self.v_ss_pass.get().strip()
        if not user or not pwd:
            lbl.config(text="✗ Wpisz login i hasło", fg=C["red"]); return
        src     = self._cfg.get("extra_sources", {})
        devid   = src.get("screenscraper_devid", "").strip()  or user
        devpass = src.get("screenscraper_devpass","").strip()  or pwd
        def _check():
            url = (
                f"https://www.screenscraper.fr/api2/ssuserInfos.php"
                f"?devid={urllib.request.quote(devid)}"
                f"&devpassword={urllib.request.quote(devpass)}"
                f"&softname=PyLinks"
                f"&ssid={urllib.request.quote(user)}"
                f"&sspassword={urllib.request.quote(pwd)}"
                f"&output=json"
            )
            # fetch_api: bez filtru 200B — krótkie odpowiedzi błędów są < 200 B
            d = fetch_api(url, timeout=12)
            if not d:
                return False, "brak odpowiedzi (sprawdź połączenie z siecią)"
            try:
                j = json.loads(d)
            except Exception:
                return False, f"błąd JSON: {(d or b'')[:80].decode(errors='replace')}"
            # ScreenScraper v2: błąd w header.Error lub response.error
            err = (j.get("header", {}).get("Error")
                   or j.get("response", {}).get("error", ""))
            if err:
                return False, str(err)[:80]
            ss = (j.get("response", {}) or {}).get("ssuser", {})
            if ss:
                maxth = ss.get("maxthreads", "?")
                req   = ss.get("requeststoday", "?")
                lim   = ss.get("maxrequestsperday", "?")
                return True, f"OK — wątki: {maxth}, req dziś: {req}/{lim}"
            return False, f"nieznana odpowiedź: {str(j)[:80]}"
        self._run_test(lbl, _check)

    def _row(self, parent, label, var, width=40):
        r = tk.Frame(parent, bg=C["bg"])
        r.pack(fill="x", padx=12, pady=3)
        tk.Label(r, text=label, bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 9), width=24, anchor="w").pack(side="left")
        tk.Entry(r, textvariable=var, width=width, bg=C["bg3"], fg=C["fg"],
                 insertbackground="white", relief="flat",
                 font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True)

    def _row_int(self, parent, label, var):
        r = tk.Frame(parent, bg=C["bg"])
        r.pack(fill="x", padx=12, pady=3)
        tk.Label(r, text=label, bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 9), width=24, anchor="w").pack(side="left")
        tk.Spinbox(r, from_=16, to=512, increment=16, textvariable=var, width=8,
                   bg=C["bg3"], fg=C["fg"], buttonbackground=C["bg3"],
                   relief="flat", font=("Segoe UI", 9)).pack(side="left")

    def _row_combo(self, parent, label, var, values):
        r = tk.Frame(parent, bg=C["bg"])
        r.pack(fill="x", padx=12, pady=3)
        tk.Label(r, text=label, bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 9), width=24, anchor="w").pack(side="left")
        ttk.Combobox(r, textvariable=var, values=values,
                     state="readonly", width=15).pack(side="left")

    def _defaults(self):
        self.v_steam_key.set(DEFAULT_STEAM_API_KEY)
        self.v_sgdb_key.set(DEFAULT_SGDB_KEY)
        self.v_steam_id.set(DEFAULT_STEAM_ID64)
        self.v_use_web.set(True)
        self.v_exe_re.set(DEFAULT_EXE_SKIP_REGEX)
        self.v_min_size.set(DEFAULT_MIN_SIZE)
        self.v_type.set("any")
        self.v_shape.set("any")
        self.v_max_icons.set(self._max_to_choice(DEFAULT_MAX_ICONS))
        self.v_use_vdf.set(True)
        self.v_scan_epic.set(True)
        self.v_scan_gog.set(True)
        self.v_steam_cdn.set(True)
        self.v_libretro.set(True)
        self.v_igdb.set(False)
        self.v_igdb_id.set("")
        self.v_igdb_sec.set("")
        self.v_tgdb.set(False)
        self.v_tgdb_key.set("")
        self.v_ss.set(False)
        self.v_ss_user.set("")
        self.v_ss_pass.set("")
        self.v_ss_devid.set("")
        self.v_ss_devpass.set("")

    @staticmethod
    def _max_to_choice(val) -> str:
        try:
            n = int(val)
        except (TypeError, ValueError):
            return str(DEFAULT_MAX_ICONS)
        if n <= 0:
            return "max"
        if n >= UNLIMITED_ICONS_CAP:
            return "max"
        return str(n) if str(n) in MAX_ICONS_CHOICES else str(DEFAULT_MAX_ICONS)

    @staticmethod
    def _choice_to_max(choice: str) -> int:
        if not choice or choice == "max":
            return 0  # 0 = unlimited (cap = UNLIMITED_ICONS_CAP)
        try:
            return int(choice)
        except ValueError:
            return DEFAULT_MAX_ICONS

    def _ok(self):
        try:
            re.compile(self.v_exe_re.get())
        except re.error as e:
            messagebox.showerror("Błąd regex", f"Niepoprawne wyrażenie regularne:\n{e}")
            return
        self.result = {
            "api_keys": {
                "steam_api_key": self.v_steam_key.get().strip(),
                "sgdb_key": self.v_sgdb_key.get().strip(),
                "steam_id64": self.v_steam_id.get().strip(),
            },
            "use_steam_web_api": bool(self.v_use_web.get()),
            "filters": {
                "exe_skip_regex": self.v_exe_re.get().strip() or DEFAULT_EXE_SKIP_REGEX,
                "min_icon_size": int(self.v_min_size.get() or DEFAULT_MIN_SIZE),
                "preferred_icon_type": self.v_type.get() or "any",
                "icon_shape": self.v_shape.get() or "any",
                "max_icons_per_game": self._choice_to_max(self.v_max_icons.get()),
            },
            "use_libraryfolders_vdf": bool(self.v_use_vdf.get()),
            "icon_platform_spine": bool(self.v_icon_spine.get()),
            "icon_spine_side": (self.v_spine_side.get() or "left"),
            "scan_epic": bool(self.v_scan_epic.get()),
            "scan_gog":        bool(self.v_scan_gog.get()),
            "scan_on_startup": bool(self.v_scan_startup.get()),
            "cache_limit_mb": max(0, int(self.v_cache_limit.get() or 0)),
            "extra_sources": {
                "steam_cdn":            bool(self.v_steam_cdn.get()),
                "libretro":             bool(self.v_libretro.get()),
                "igdb":                 bool(self.v_igdb.get()),
                "igdb_client_id":       self.v_igdb_id.get().strip(),
                "igdb_client_secret":   self.v_igdb_sec.get().strip(),
                "tgdb":                 bool(self.v_tgdb.get()),
                "tgdb_key":             self.v_tgdb_key.get().strip(),
                "screenscraper":        bool(self.v_ss.get()),
                "screenscraper_user":   self.v_ss_user.get().strip(),
                "screenscraper_pass":   self.v_ss_pass.get().strip(),
                "screenscraper_devid":  self.v_ss_devid.get().strip(),
                "screenscraper_devpass":self.v_ss_devpass.get().strip(),
            },
        }
        self.destroy()


class ProfileDialog(tk.Toplevel):
    """Okno zarządzania profilami."""

    def __init__(self, parent, profiles: dict, current: str):
        super().__init__(parent)
        self.title("Profile skrótów")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.grab_set()
        self.result: dict | None = None
        self._profiles = {k: dict(v) for k, v in profiles.items()}
        self._current = current

        tk.Label(self, text="Profile", bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(12, 4))
        self._lb = tk.Listbox(self, bg=C["bg3"], fg=C["fg"], highlightthickness=0,
                              selectbackground=C["acc"], font=("Segoe UI", 9),
                              width=30, height=6)
        self._lb.pack(fill="x", padx=12, pady=4)
        self._refresh()

        row = tk.Frame(self, bg=C["bg"])
        row.pack(fill="x", padx=12, pady=4)
        tk.Button(row, text="Nowy...", command=self._add, bg=C["bg3"], fg=C["grn"],
                  relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left", padx=(0, 4))
        tk.Button(row, text="Zmień nazwę...", command=self._rename, bg=C["bg3"], fg=C["yel"],
                  relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left", padx=4)
        tk.Button(row, text="Usuń", command=self._del, bg=C["bg3"], fg=C["red"],
                  relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left", padx=4)
        tk.Button(row, text="Zmień output dir...", command=self._edit_out,
                  bg=C["bg3"], fg=C["fg"], relief="flat", padx=10, pady=3,
                  cursor="hand2").pack(side="left", padx=4)

        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=12, pady=(10, 12))
        tk.Button(bot, text="Wybierz jako aktywny", command=self._use, bg=C["acc"],
                  fg=C["bg"], relief="flat", padx=12, pady=4,
                  cursor="hand2").pack(side="right", padx=(4, 0))
        tk.Button(bot, text="Anuluj", command=self.destroy, bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=10, pady=4, cursor="hand2").pack(side="right")

        self.update_idletasks()
        pw, ph = parent.winfo_x(), parent.winfo_y()
        pw2, ph2 = parent.winfo_width(), parent.winfo_height()
        dw, dh = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw+(pw2-dw)//2}+{ph+(ph2-dh)//2}")
        self.wait_window(self)

    def _refresh(self):
        self._lb.delete(0, "end")
        for name in self._profiles:
            out = self._profiles[name].get("output_dir", "")
            marker = " ◄ aktywny" if name == self._current else ""
            self._lb.insert("end", f"{name}   [{out}]{marker}")

    def _sel_name(self) -> str | None:
        sel = self._lb.curselection()
        if not sel:
            return None
        return list(self._profiles.keys())[sel[0]]

    def _add(self):
        name = _ask_string(self, "Nowy profil", "Nazwa profilu:")
        if not name:
            return
        if name in self._profiles:
            messagebox.showerror("Błąd", "Profil o tej nazwie już istnieje.")
            return
        out = filedialog.askdirectory(parent=self, title="Katalog wyjściowy dla nowego profilu")
        if not out:
            return
        self._profiles[name] = {"output_dir": out, "enabled_keys": [], "selected_indices": {}}
        self._refresh()

    def _rename(self):
        old = self._sel_name()
        if not old:
            return
        new = _ask_string(self, "Zmień nazwę", "Nowa nazwa:", old)
        if not new or new == old:
            return
        if new in self._profiles:
            messagebox.showerror("Błąd", "Profil o tej nazwie już istnieje.")
            return
        self._profiles[new] = self._profiles.pop(old)
        if self._current == old:
            self._current = new
        self._refresh()

    def _del(self):
        name = self._sel_name()
        if not name:
            return
        if len(self._profiles) <= 1:
            messagebox.showerror("Błąd", "Musi istnieć co najmniej jeden profil.")
            return
        if not messagebox.askyesno("Potwierdź", f"Usunąć profil '{name}'?"):
            return
        self._profiles.pop(name)
        if self._current == name:
            self._current = next(iter(self._profiles))
        self._refresh()

    def _edit_out(self):
        name = self._sel_name()
        if not name:
            return
        out = filedialog.askdirectory(
            parent=self, title=f"Katalog wyjściowy dla '{name}'",
            initialdir=self._profiles[name].get("output_dir", ""),
        )
        if out:
            self._profiles[name]["output_dir"] = out
            self._refresh()

    def _use(self):
        name = self._sel_name() or self._current
        self.result = {"profiles": self._profiles, "current_profile": name}
        self.destroy()


class DryRunDialog(tk.Toplevel):
    """Podgląd operacji przed utworzeniem skrótów."""

    def __init__(self, parent, plan: list[dict]):
        super().__init__(parent)
        self.title("Dry run — podgląd operacji")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.grab_set()
        self.confirm = False
        tk.Label(self, text=f"Plan tworzenia skrótów ({len(plan)} elementów)",
                 bg=C["bg"], fg=C["acc"], font=("Segoe UI", 11, "bold")).pack(padx=12, pady=(10, 4), anchor="w")
        cols = ("name", "source", "action", "target", "icon", "file")
        tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        for col, label, w in [
            ("name", "Gra", 220), ("source", "Źródło", 70),
            ("action", "Akcja", 90), ("target", "Cel uruchomienia", 280),
            ("icon", "Ikona", 220), ("file", "Plik skrótu", 260),
        ]:
            tree.heading(col, text=label)
            tree.column(col, width=w, anchor="w")
        for p in plan:
            tree.insert("", "end", values=(
                p.get("name", ""),
                p.get("source", ""),
                p.get("action", ""),
                p.get("target", ""),
                p.get("icon", ""),
                p.get("file", ""),
            ))
        tree.pack(fill="both", expand=True, padx=12, pady=6)
        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=12, pady=(4, 12))
        tk.Button(bot, text="Anuluj", command=self.destroy, bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=10, pady=4, cursor="hand2").pack(side="right")
        tk.Button(bot, text="Kontynuuj — twórz skróty", command=self._ok,
                  bg=C["grn"], fg=C["bg"], relief="flat", padx=14, pady=4,
                  cursor="hand2").pack(side="right", padx=(4, 4))
        self.geometry("1150x600")
        self.wait_window(self)

    def _ok(self):
        self.confirm = True
        self.destroy()


def _ask_string(parent, title: str, prompt: str, initial: str = "") -> str | None:
    """Prosty zamiennik tkinter.simpledialog.askstring z naszym stylem."""
    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.configure(bg=C["bg"])
    dlg.resizable(False, False)
    dlg.grab_set()
    tk.Label(dlg, text=prompt, bg=C["bg"], fg=C["fg"],
             font=("Segoe UI", 10)).pack(padx=16, pady=(14, 4))
    var = tk.StringVar(value=initial)
    ent = tk.Entry(dlg, textvariable=var, bg=C["bg3"], fg=C["fg"],
                   insertbackground="white", relief="flat", font=("Segoe UI", 10), width=40)
    ent.pack(padx=16, pady=4)
    ent.focus_set()
    ent.selection_range(0, "end")
    result: list[str | None] = [None]

    def _ok():
        result[0] = var.get().strip() or None
        dlg.destroy()

    def _cancel():
        result[0] = None
        dlg.destroy()

    dlg.bind("<Return>", lambda e: _ok())
    dlg.bind("<Escape>", lambda e: _cancel())
    bot = tk.Frame(dlg, bg=C["bg"])
    bot.pack(fill="x", padx=16, pady=(6, 14))
    tk.Button(bot, text="OK", command=_ok, bg=C["acc"], fg=C["bg"],
              relief="flat", padx=12, pady=3).pack(side="right", padx=(4, 0))
    tk.Button(bot, text="Anuluj", command=_cancel, bg=C["bg3"], fg=C["fg2"],
              relief="flat", padx=10, pady=3).pack(side="right")
    dlg.update_idletasks()
    pw, ph = parent.winfo_x(), parent.winfo_y()
    pw2, ph2 = parent.winfo_width(), parent.winfo_height()
    dw, dh = dlg.winfo_width(), dlg.winfo_height()
    dlg.geometry(f"+{pw+(pw2-dw)//2}+{ph+(ph2-dh)//2}")
    dlg.wait_window(dlg)
    return result[0]


# ---------------------------------------------------------------------------
# App (GUI) - trzyma tylko UI i sklejanie komponentów
# ---------------------------------------------------------------------------
class _M3uDialog(tk.Toplevel):
    """Dialog generatora M3U — pokazuje znalezione grupy multi-disc, tworzy pliki."""

    def __init__(self, parent, groups: list[dict]):
        super().__init__(parent)
        self.title("Generator M3U — multi-disc")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.grab_set()

        tk.Label(self,
                 text=f"Znaleziono {len(groups)} grup multi-disc.",
                 bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        tk.Label(self,
                 text="Zaznacz gry dla których chcesz wygenerować pliki M3U.",
                 bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 8)).pack(anchor="w", padx=14, pady=(0, 6))

        # Tabela
        wrap = tk.Frame(self, bg=C["bg2"],
                        highlightthickness=1, highlightbackground=C["bg3"])
        wrap.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        canvas = tk.Canvas(wrap, bg=C["bg2"], highlightthickness=0, height=340)
        vsb = tk.Scrollbar(wrap, orient="vertical", command=canvas.yview,
                           bg=C["bg3"], width=8, relief="flat")
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=C["bg2"])
        cw = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        # Header
        hdr = tk.Frame(inner, bg=C["bg3"])
        hdr.pack(fill="x", padx=2, pady=(2, 0))
        for txt, w in [("☑", 3), ("Platforma", 8), ("Tytuł", 34), ("Dysków", 6), ("Status", 10)]:
            tk.Label(hdr, text=txt, bg=C["bg3"], fg=C["acc"],
                     font=("Segoe UI", 8, "bold"), width=w, anchor="w",
                     padx=4).pack(side="left")

        self._vars: list[tk.BooleanVar] = []
        for i, g in enumerate(groups):
            bg = C["bg"] if i % 2 == 0 else C["bg2"]
            row = tk.Frame(inner, bg=bg)
            row.pack(fill="x", padx=2, pady=1)
            v = tk.BooleanVar(value=not g["exists"])  # auto-select new M3U
            self._vars.append(v)
            tk.Checkbutton(row, variable=v, bg=bg, activebackground=bg,
                           selectcolor=C["bg3"], width=2).pack(side="left")
            tk.Label(row, text=g["plat"], bg=bg, fg=C["ext"],
                     font=("Segoe UI", 8), width=8, anchor="w",
                     padx=4).pack(side="left")
            tk.Label(row, text=g["title"], bg=bg, fg=C["fg"],
                     font=("Segoe UI", 9), width=34, anchor="w",
                     padx=4).pack(side="left")
            tk.Label(row, text=str(len(g["discs"])), bg=bg, fg=C["fg2"],
                     font=("Segoe UI", 8), width=6, anchor="w").pack(side="left")
            status_txt = "istnieje" if g["exists"] else "nowy"
            status_col = C["yel"] if g["exists"] else C["grn"]
            tk.Label(row, text=status_txt, bg=bg, fg=status_col,
                     font=("Segoe UI", 8), width=10, anchor="w").pack(side="left")

        # Buttons
        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=14, pady=(0, 12))
        n_new = sum(1 for g in groups if not g["exists"])
        tk.Button(bot,
                  text=f"Generuj zaznaczone",
                  command=lambda: self._generate(groups),
                  bg=C["grn"], fg=C["bg"],
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=14, pady=6,
                  cursor="hand2").pack(side="right", padx=(4, 0))
        tk.Button(bot, text="Anuluj", command=self.destroy,
                  bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=10, pady=6,
                  cursor="hand2").pack(side="right")
        tk.Button(bot, text="Zaznacz wszystkie",
                  command=lambda: [v.set(True) for v in self._vars],
                  bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=8, pady=6).pack(side="left")
        tk.Button(bot, text="Odznacz istniej.",
                  command=lambda: [v.set(False) for v, g in zip(self._vars, groups)
                                   if g["exists"]],
                  bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=8, pady=6).pack(side="left", padx=4)

        self.geometry("760x500")
        self.update_idletasks()
        pw = parent.winfo_x() + (parent.winfo_width()  - 760) // 2
        ph = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.geometry(f"+{pw}+{ph}")

    def _generate(self, groups: list[dict]):
        created = 0
        skipped = 0
        for v, g in zip(self._vars, groups):
            if not v.get():
                continue
            m3u = Path(g["m3u_path"])
            content = "\n".join(g["discs"]) + "\n"
            m3u.write_text(content, encoding="utf-8")
            created += 1
        self.destroy()
        messagebox.showinfo("M3U", f"Wygenerowano {created} pliki M3U.")


class _SteamExportDialog(tk.Toplevel):
    """Dialog eksportu gier jako non-Steam shortcuts (shortcuts.vdf)."""

    def __init__(self, parent, games: list[dict], cfg: dict):
        super().__init__(parent)
        self.title("Eksport → Steam (non-Steam)")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.grab_set()
        self._games = games
        self._cfg   = cfg
        self._parent_app = parent   # ref do głównego okna (po destroy dialogu)

        # Znajdź userdata Steam
        userdata_dirs = self._find_steam_userdata(
            cfg.get("steam_userdata_dir", ""))
        self._userdata_dirs = userdata_dirs

        tk.Label(self,
                 text="Eksport gier do Steam jako non-Steam shortcuts",
                 bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(12, 2))
        tk.Label(self,
                 text="Dodane gry pojawią się w bibliotece Steam z własną okładką.\n"
                      "Wymagany restart Steam po eksporcie.",
                 bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 8)).pack(anchor="w", padx=14, pady=(0, 8))

        # Wybór profilu Steam
        prof_f = tk.Frame(self, bg=C["bg2"],
                          highlightthickness=1, highlightbackground=C["bg3"])
        prof_f.pack(fill="x", padx=14, pady=(0, 8))
        tk.Label(prof_f, text="Profil Steam:", bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 9)).pack(side="left", padx=8, pady=6)
        self.v_profile = tk.StringVar()
        profile_opts = [str(p) for p in userdata_dirs] if userdata_dirs else ["(nie znaleziono)"]
        if userdata_dirs:
            self.v_profile.set(profile_opts[0])
        cb = ttk.Combobox(prof_f, textvariable=self.v_profile,
                          values=profile_opts, state="readonly", width=60)
        cb.pack(side="left", padx=4, pady=6)
        tk.Button(prof_f, text="…", command=self._browse_userdata,
                  bg=C["bg3"], fg=C["acc"], relief="flat", padx=6).pack(side="left", pady=6)

        # Filtry eksportu
        filter_f = tk.Frame(self, bg=C["bg"])
        filter_f.pack(fill="x", padx=14, pady=(0, 6))
        self.v_filter_steam  = tk.BooleanVar(value=False)
        self.v_filter_rom    = tk.BooleanVar(value=True)
        self.v_filter_extra  = tk.BooleanVar(value=True)
        for var, lbl in [(self.v_filter_steam, "Steam"),
                         (self.v_filter_rom,   "ROM-y"),
                         (self.v_filter_extra, "Extra")]:
            tk.Checkbutton(filter_f, text=lbl, variable=var,
                           bg=C["bg"], fg=C["fg2"],
                           selectcolor=C["bg3"], activebackground=C["bg"],
                           command=self._refresh_list).pack(side="left", padx=8)
        tk.Label(filter_f, text="← wybierz typy gier do eksportu",
                 bg=C["bg"], fg=C["fg2"], font=("Segoe UI", 8)).pack(side="left")

        # v8.2: pobieranie grafik SGDB do folderu grid przy eksporcie
        self.v_art = tk.BooleanVar(value=True)
        art_row = tk.Frame(self, bg=C["bg"])
        art_row.pack(fill="x", padx=14, pady=(0, 4))
        tk.Checkbutton(art_row,
                       text="Pobierz grafiki (SteamGridDB): okladka + poziomy + hero + logo + ikona",
                       variable=self.v_art, bg=C["bg"], fg=C["fg2"],
                       selectcolor=C["bg3"], activebackground=C["bg"]).pack(side="left", padx=8)

        # v8.2: grupowanie w kolekcje Steam per system (PS1/PS2/... / Windows)
        self.v_collections = tk.BooleanVar(value=True)
        coll_row = tk.Frame(self, bg=C["bg"])
        coll_row.pack(fill="x", padx=14, pady=(0, 4))
        tk.Checkbutton(coll_row,
                       text="Grupuj w kolekcje Steam per system (wymaga ZAMKNIETEGO Steam)",
                       variable=self.v_collections, bg=C["bg"], fg=C["fg2"],
                       selectcolor=C["bg3"], activebackground=C["bg"]).pack(side="left", padx=8)

        # Lista gier
        list_wrap = tk.Frame(self, bg=C["bg2"],
                             highlightthickness=1, highlightbackground=C["bg3"])
        list_wrap.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        self._listbox = tk.Listbox(list_wrap, bg=C["bg3"], fg=C["fg"],
                                   selectmode="extended",
                                   font=("Segoe UI", 9), relief="flat",
                                   height=14, activestyle="none",
                                   selectbackground=C["acc"], selectforeground=C["bg"])
        vsb2 = tk.Scrollbar(list_wrap, orient="vertical",
                             command=self._listbox.yview,
                             bg=C["bg3"], width=8, relief="flat")
        self._listbox.config(yscrollcommand=vsb2.set)
        vsb2.pack(side="right", fill="y")
        self._listbox.pack(fill="both", expand=True)
        self._filtered: list[dict] = []
        self._refresh_list()

        # Buttons
        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=14, pady=(0, 12))
        tk.Button(bot, text="Eksportuj zaznaczone",
                  command=self._export,
                  bg=C["grn"], fg=C["bg"],
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=14, pady=6,
                  cursor="hand2").pack(side="right", padx=(4, 0))
        tk.Button(bot, text="Anuluj", command=self.destroy,
                  bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=10, pady=6,
                  cursor="hand2").pack(side="right")
        tk.Button(bot, text="Zaznacz wszystkie",
                  command=lambda: self._listbox.select_set(0, "end"),
                  bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=8, pady=6).pack(side="left")
        tk.Label(bot, text="Grafiki edytuj w głównym oknie (tryb Steam)",
                 bg=C["bg"], fg=C["fg2"], font=("Segoe UI", 8)).pack(side="left", padx=(8, 0))

        self.geometry("820x560")
        self.update_idletasks()
        pw = parent.winfo_x() + (parent.winfo_width()  - 820) // 2
        ph = parent.winfo_y() + (parent.winfo_height() - 560) // 2
        self.geometry(f"+{pw}+{ph}")

    def _refresh_list(self):
        include = set()
        if self.v_filter_steam.get():  include.add("steam")
        if self.v_filter_rom.get():    include.add("rom")
        if self.v_filter_extra.get():  include.add("extra")
        self._filtered = [g for g in self._games if g.get("source") in include]
        self._listbox.delete(0, "end")
        for g in self._filtered:
            src_tag = {"steam": "Steam", "rom": g.get("rom_platform","ROM"),
                       "extra": "Extra"}.get(g.get("source", ""), "?")
            self._listbox.insert("end", f"[{src_tag}]  {g['name']}")

    def _browse_userdata(self):
        p = filedialog.askdirectory(parent=self, title="Wskaż folder Steam userdata")
        if p:
            self.v_profile.set(p)

    @staticmethod
    def _find_steam_userdata(override: str = "") -> list[Path]:
        if override and Path(override).exists():
            return [Path(override)]
        candidates = []
        for base in [
            Path(os.environ.get("LOCALAPPDATA", "C:/")) / "Steam" / "userdata",
            Path("C:/Program Files (x86)/Steam/userdata"),
            Path("C:/Program Files/Steam/userdata"),
        ]:
            if base.is_dir():
                for user_dir in sorted(base.iterdir()):
                    if user_dir.is_dir() and user_dir.name.isdigit():
                        candidates.append(user_dir / "config" / "shortcuts.vdf")
        return candidates

    # ------------------------------------------------------------------
    # Binarny VDF (KeyValues KV1) — poprawny writer/parser shortcuts.vdf
    # ------------------------------------------------------------------
    # Typy pól w binarnym VDF:
    #   0x00 = obiekt / poddrzewo (dzieci aż do 0x08)
    #   0x01 = string (UTF-8, zakończony NUL-em)
    #   0x02 = uint32 (little-endian, 4 bajty)
    #   0x07 = uint64 (little-endian, 8 bajtów) — rzadkie, obsługiwane przy odczycie
    #   0x08 = koniec obiektu
    #
    # Struktura shortcuts.vdf zapisywanego przez Steam:
    #   0x00 "shortcuts" 0x00
    #       0x00 "0" 0x00  <pola wpisu...>  [0x00 "tags" 0x00 <stringi> 0x08]  0x08
    #       0x00 "1" 0x00  ...                                                  0x08
    #   0x08   <- zamyka mapę "shortcuts"
    #   0x08   <- zamyka dokument (root)
    #
    # Uwaga o kluczu root: Steam zapisuje root jako "shortcuts", ale parser
    # poniżej NIE zakłada konkretnej nazwy — czyta obiekt root po TYPIE (0x00),
    # więc akceptuje także pliki z pustym kluczem root (b"\x00\x00...").

    def _export(self):
        sel_idx = self._listbox.curselection()
        if not sel_idx:
            messagebox.showwarning("Steam Export", "Zaznacz gry do eksportu.")
            return
        selected = [self._filtered[i] for i in sel_idx]
        profile_path = Path(self.v_profile.get())
        if not profile_path.parent.is_dir():
            messagebox.showerror("Steam Export",
                f"Nieprawidłowa ścieżka profilu:\n{profile_path}")
            return

        # Ostrzeż, jeśli Steam jest uruchomiony (nie blokuj — tylko potwierdzenie).
        if self._is_steam_running():
            if not messagebox.askyesno("Steam Export",
                    "Steam wygląda na uruchomiony.\n\n"
                    "Steam nadpisuje shortcuts.vdf przy zamknięciu, więc zmiany "
                    "mogą zostać utracone. Zamknij Steam CAŁKOWICIE przed eksportem.\n\n"
                    "Kontynuować mimo to?"):
                return

        # Zbuduj nowe wpisy (surowe dicty pól VDF), zachowując referencje do gier
        # (potrzebne do sgdb_id / steam_art przy pobieraniu grafik).
        pairs = []
        report_rows: list[dict] = []   # po jednym wpisie na WYBRANĄ grę (raport)
        row_by_id: dict = {}           # id(entry) -> wiersz raportu (wynik uzup. niżej)
        for g in selected:
            e = self._build_entry(g)
            if e is not None:
                pairs.append((g, e))
                row = {
                    "name":     g.get("name", ""),
                    "source":   g.get("source", ""),
                    "platform": (g.get("rom_platform") or g.get("romplatform") or ""),
                    "appid":    e.get("appid", ""),
                    "exe":      e.get("Exe", ""),
                    "args":     e.get("LaunchOptions", ""),
                    "tags":     ", ".join((e.get("tags", {}) or {}).values()),
                    "outcome":  "dodane",   # domyślnie; korekta w pętli scalania
                    "reason":   "",
                }
                report_rows.append(row)
                row_by_id[id(e)] = row
            else:
                # Powód pominięcia (jedyna ścieżka None w _build_entry: brak EXE).
                src = g.get("source", "")
                rp = str(g.get("rom_path", "")).lower()
                if src == "rom" and (g.get("rom_is_lnk") or rp.endswith(".lnk")):
                    why = ("nie udało się odczytać docelowego EXE ze skrótu .lnk "
                           "(brak pywin32 lub uszkodzony skrót)")
                elif src == "rom":
                    why = "brak EXE emulatora (launch_exe) dla ROM-a"
                else:
                    why = "brak ścieżki EXE"
                report_rows.append({
                    "name": g.get("name", ""), "source": g.get("source", ""),
                    "platform": (g.get("rom_platform") or g.get("romplatform") or ""),
                    "appid": "", "exe": "", "args": "", "tags": "",
                    "outcome": "pominięte — błąd", "reason": why,
                })
        new_entries = [e for _g, e in pairs]

        # Folder grafik Steam (grid) + klucz SGDB. Ikona wpisu wskazuje na plik,
        # który pojawi się po pobraniu grafik (Steam odczyta go przy restarcie).
        grid_dir = profile_path.parent / "grid"
        sgdb_key = (self._cfg.get("api_keys", {}) or {}).get("sgdb_key", "")
        art_enabled = bool(sgdb_key) and bool(self.v_art.get())
        if art_enabled:
            for e in new_entries:
                e["icon"] = str(grid_dir / f'{e["appid"]}.ico')

        # Wczytaj istniejące shortcuts.vdf (jeśli jest).
        existing_entries: list[dict] = []
        read_failed = False
        if profile_path.exists() and profile_path.stat().st_size > 0:
            try:
                existing_entries = self._read_shortcuts_vdf(profile_path)
            except Exception as ex:
                read_failed = True
                # Uszkodzony plik — NIE nadpisuj bez ostrzeżenia. Zrób kopię.
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                corrupt = profile_path.with_name(
                    profile_path.name + f".corrupt-{ts}.bak")
                try:
                    shutil.copy2(profile_path, corrupt)
                except Exception:
                    corrupt = None
                if not messagebox.askyesno("Steam Export",
                        "Istniejący shortcuts.vdf jest uszkodzony lub w nieznanym "
                        f"formacie:\n{ex}\n\n"
                        + (f"Wykonano kopię:\n{corrupt}\n\n" if corrupt else "")
                        + "Kontynuować, zaczynając od nowej listy skrótów?\n"
                          "(Poprzednie wpisy non-Steam mogą zostać utracone.)"):
                    return
                existing_entries = []

        # ZBIJANIE DUPLIKATÓW PO APPID (patrz _collapse_by_appid).
        def _appid_of(en) -> int:
            try:
                return int(self._field(en, "appid", 0) or 0)
            except Exception:
                return 0

        existing_entries, removed_dupes = self._collapse_by_appid(existing_entries)

        # Połącz: zachowaj WSZYSTKIE istniejące wpisy non-Steam (nawet te, których
        # teraz nie eksportujemy). Dla gry, która JUŻ jest w pliku:
        #   - dopasowanie NAJPIERW po appid (ta sama gra, nawet gdy zmienił się
        #     dysk/argumenty) — wtedy AKTUALIZUJEMY Exe/StartDir/LaunchOptions do
        #     poprawnej wartości (np. Disc 1 → .m3u); dopiero potem po (nazwa,
        #     Exe+LaunchOptions),
        #   - NIE dublujemy wpisu, DOKLEJAMY brakujące tagi (union),
        #   - jeśli wpis nie ma ikony, ustawiamy przewidywaną ścieżkę .ico,
        #   - innych pól (ręcznych ustawień użytkownika) NIE ruszamy.
        existing_by_key: dict = {}
        existing_by_appid: dict = {}
        for e in existing_entries:
            existing_by_key.setdefault(self._dedup_key(e), e)
            ap = _appid_of(e)
            if ap:
                existing_by_appid.setdefault(ap, e)

        added: list[dict] = []
        updated = 0
        skipped = 0
        for e in new_entries:
            k = self._dedup_key(e)
            tgt = existing_by_key.get(k)
            matched_appid = False
            if tgt is None:
                tgt = existing_by_appid.get(_appid_of(e))
                matched_appid = tgt is not None
            row = row_by_id.get(id(e))
            if tgt is not None:
                changed = self._merge_tags(tgt, e.get("tags", {}))
                # Dopasowanie po appid z INNĄ komendą = poprawa launchu
                # (np. pojedynczy dysk → .m3u). Zaktualizuj komendę.
                if matched_appid:
                    for fld in ("Exe", "LaunchOptions", "StartDir"):
                        nv = e.get(fld, "")
                        if str(self._field(tgt, fld, "")) != str(nv):
                            self._set_field(tgt, fld, nv)
                            changed = True
                if art_enabled and not str(self._field(tgt, "icon", "")).strip():
                    self._set_field(tgt, "icon",
                                    str(grid_dir / f'{self._field(tgt, "appid", 0)}.ico'))
                    changed = True
                if changed:
                    updated += 1
                    if row is not None:
                        row["outcome"] = "zaktualizowane"
                else:
                    skipped += 1
                    if row is not None:
                        row["outcome"] = "pominięte — bez zmian"
                continue
            existing_by_key[k] = e
            ap = _appid_of(e)
            if ap:
                existing_by_appid[ap] = e
            added.append(e)

        all_entries = existing_entries + added
        tags_added = any("tags" in e for e in added) or updated > 0
        if removed_dupes:
            try:
                print(f"[Steam Export] usunięto duplikaty (appid): "
                      f"{len(removed_dupes)} — {removed_dupes}")
            except Exception:
                pass

        # Serializuj.
        try:
            vdf_bytes = self._write_shortcuts_vdf(all_entries)
        except Exception as ex:
            messagebox.showerror("Steam Export", f"Błąd serializacji VDF:\n{ex}")
            return

        # Zapis atomowy + kopia zapasowa z datą.
        backup_path = None
        tmp = None
        try:
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            if profile_path.exists() and not read_failed:
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_path = profile_path.with_name(
                    profile_path.name + f".{ts}.bak")
                shutil.copy2(profile_path, backup_path)
            tmp = profile_path.with_name(
                profile_path.name + f".tmp-{uuid.uuid4().hex}")
            tmp.write_bytes(vdf_bytes)
            os.replace(tmp, profile_path)  # atomowa podmiana w tym samym katalogu
            tmp = None
        except Exception as ex:
            try:
                if tmp is not None and tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            messagebox.showerror("Steam Export", f"Błąd zapisu:\n{ex}")
            return

        # Zbierz cele grafik (appid + nazwa + WSPÓLNE sgdb_id + ręczne wybory).
        # Samo pobieranie z paskiem postępu startuje na końcu (po podsumowaniu).
        art_targets = []
        if art_enabled:
            for g, e in pairs:
                art_targets.append({
                    "appid":   self._field(e, "appid", 0),
                    "name":    self._field(e, "AppName", ""),
                    "sgdb_id": g.get("sgdb_id"),
                    "art":     g.get("steam_art"),
                })

        # Kolekcje per system (grupowanie w bibliotece Steam). Zapis do
        # magazynu cloudstorage MUSI odbywać się przy zamkniętym Steam.
        coll_note = ""
        coll_result = None
        if self.v_collections.get():
            tag_appids: dict = {}
            for e in new_entries:
                ap = self._field(e, "appid", 0)
                tags = self._field(e, "tags", {})
                vals = tags.values() if isinstance(tags, dict) else []
                for t in vals:
                    t = (t or "").strip()
                    if not t or t == "Non-Steam":
                        continue  # pomijamy umbrella — grupujemy per system
                    tag_appids.setdefault(t, []).append(ap)
            if not tag_appids:
                pass
            elif self._is_steam_running():
                coll_note = ("\nKolekcje POMINIĘTE: Steam jest uruchomiony. "
                             "Zamknij Steam całkowicie i wyeksportuj ponownie, "
                             "aby utworzyć grupy per system.")
                print("[Collections] pominieto — Steam uruchomiony")
            else:
                coll_result = self._write_collections(profile_path.parent, tag_appids)
                if coll_result.get("ok"):
                    cc = ", ".join(coll_result["created"]) or "-"
                    uu = ", ".join(coll_result["updated"]) or "-"
                    coll_note = ("\nKolekcje zapisane. Nowe: " + cc +
                                 " | zaktualizowane: " + uu)
                    print(f"[Collections] utworzone: {coll_result['created']}")
                    print(f"[Collections] zaktualizowane: {coll_result['updated']}")
                    print(f"[Collections] backup: {coll_result.get('backup')}")
                else:
                    coll_note = ("\nKolekcje NIE zapisane: " +
                                 str(coll_result.get("error")))
                    print(f"[Collections] blad: {coll_result.get('error')}")

        # Diagnostyka (bez kluczy API ani danych prywatnych).
        diag = [
            "[Steam Export] shortcuts.vdf",
            f"  plik            : {profile_path}",
            f"  istniejące wpisy: {len(existing_entries)}",
            f"  nowe wpisy      : {len(new_entries)}",
            f"  dodane          : {len(added)}",
            f"  zaktualizowane  : {updated}",
            f"  pominięte (bez zmian): {skipped}",
            f"  zapisane łącznie: {len(all_entries)}",
            f"  kopia zapasowa  : {backup_path if backup_path else '(brak)'}",
            f"  tagi dodane     : {'tak' if tags_added else 'nie'}",
            f"  grafiki SGDB    : {'w toku (' + str(len(art_targets)) + ')' if art_enabled else 'wyłączone/brak klucza'}",
        ]
        try:
            print("\n".join(diag))
        except Exception:
            pass

        # Raport eksportu (HTML) — po jednym wierszu na wybraną grę.
        report_path = None
        try:
            if coll_result is not None and coll_result.get("ok"):
                coll_sum = ("nowe: " + (", ".join(coll_result.get("created", [])) or "-")
                            + " | zaktualizowane: "
                            + (", ".join(coll_result.get("updated", [])) or "-"))
            elif coll_result is not None:
                coll_sum = "błąd: " + str(coll_result.get("error"))
            elif self.v_collections.get() and self._is_steam_running():
                coll_sum = "pominięte — Steam był uruchomiony"
            elif self.v_collections.get():
                coll_sum = "brak tagów do zgrupowania"
            else:
                coll_sum = "wyłączone"
            art_sum = (f"pobieranie {len(art_targets)} gier" if art_enabled
                       else ("brak klucza SGDB" if not sgdb_key else "wyłączone"))
            meta = {
                "vdf":         str(profile_path),
                "backup":      str(backup_path) if backup_path else "",
                "total":       len(all_entries),
                "collections": coll_sum,
                "art":         art_sum,
                "removed_dupes": removed_dupes,
            }
            # Duplikaty usunięte przy zbijaniu po appid — jako wiersze raportu.
            for nm in removed_dupes:
                report_rows.append({
                    "name": nm, "source": "", "platform": "", "appid": "",
                    "exe": "", "args": "", "tags": "",
                    "outcome": "usunięty duplikat",
                    "reason": "zbity z innym wpisem o tym samym appid (ta sama gra)",
                })
            report_path = write_steam_report(REPORTS_DIR, report_rows, meta, fmt="html")
            print(f"[Steam Export] raport: {report_path}")
        except Exception as ex:
            print(f"[Steam Export] raport — błąd zapisu: {ex}")

        art_note = ""
        if art_enabled:
            art_note = (f"\nGrafiki: pobieranie {len(art_targets)} gier zaraz się rozpocznie "
                        "(osobne okno z paskiem postępu).")
        elif not sgdb_key:
            art_note = "\nGrafiki pominięte: brak klucza SteamGridDB w Ustawieniach."

        parent_app = self._parent_app
        self.destroy()
        messagebox.showinfo("Steam Export",
            f"Dodano {len(added)} nowych, zaktualizowano tagi w {updated} istniejących "
            f"(pominięto {skipped} bez zmian).\n"
            f"Łącznie skrótów w pliku: {len(all_entries)}.\n"
            f"Plik: {profile_path}\n"
            + (f"Kopia: {backup_path}\n" if backup_path else "")
            + (f"Raport: {report_path}\n" if report_path else "")
            + art_note
            + coll_note
            + "\n\nUruchom ponownie Steam, aby zobaczyć zmiany.\n"
              "Gry są otagowane (Non-Steam + platforma) — pojawią się jako kolekcje.")

        # Pasek postępu pobierania grafik (parented do głównego okna — dialog
        # eksportu jest już zniszczony). Niemodalne, można anulować.
        if art_enabled and art_targets:
            try:
                _ArtProgressDialog(parent_app, art_targets, grid_dir, sgdb_key)
            except Exception as ex:
                print(f"[Art] nie udało się otworzyć okna postępu: {ex}")

    @staticmethod
    def _set_field(entry: dict, name: str, value) -> None:
        """Ustawia pole wpisu, respektując istniejącą wielkość liter klucza."""
        low = name.lower()
        for k in list(entry.keys()):
            if k.lower() == low:
                entry[k] = value
                return
        entry[name] = value

    @staticmethod
    def _merge_tags(entry: dict, new_tags_obj: dict) -> bool:
        """Dokleja brakujące tagi do istniejącego wpisu (union, kolejność).

        Zwraca True, jeśli cokolwiek dodano/zmieniono. Zapisuje z powrotem jako
        obiekt {"0": tag0, "1": tag1, ...}."""
        cur = _SteamExportDialog._field(entry, "tags", {})
        if not isinstance(cur, dict):
            cur = {}

        def _order(item):
            k = item[0]
            return (0, int(k)) if k.isdigit() else (1, k)

        merged = [v for _k, v in sorted(cur.items(), key=_order)]
        changed = False
        for v in (new_tags_obj or {}).values():
            v = (v or "").strip()
            if v and v not in merged:
                merged.append(v)
                changed = True
        new_obj = {str(i): t for i, t in enumerate(merged)}
        # Podmień klucz "tags" respektując wielkość liter.
        for k in list(entry.keys()):
            if k.lower() == "tags":
                entry[k] = new_obj
                break
        else:
            entry["tags"] = new_obj
        return changed

    # ------------------------------------------------------------------
    # Kolekcje Steam (grupowanie per system) — magazyn cloudstorage (JSON)
    # ------------------------------------------------------------------
    # Nowy klient Steam trzyma kolekcje NIE w shortcuts.vdf, lecz w:
    #   userdata\<ID>\config\cloudstorage\cloud-storage-namespace-1.json
    # To tablica par [klucz, wrapper]. Kolekcja = wpis o kluczu
    #   "user-collections.<id>" z wrapperem {key,timestamp,value,version},
    # gdzie value to STRING JSON: {"id","name","added":[appid..],"removed":[]}.
    # Gry non-Steam w "added" używają appid = unsigned 32-bit (nasza wartość).
    # Pliki sterujące:
    #   cloud-storage-namespaces.json          -> [[nsId, "<licznik>"], ...]
    #   cloud-storage-namespace-1.modified.json -> lista kluczy do wysłania do chmury
    # Zapis MUSI odbywać się przy ZAMKNIĘTYM Steam (inaczej Steam nadpisze pliki).

    @staticmethod
    def _new_collection_id(name: str) -> str:
        """Deterministyczne, stabilne id kolekcji z nazwy (idempotencja)."""
        import base64
        h = hashlib.md5(("pylinks::" + name).encode("utf-8")).digest()
        s = base64.urlsafe_b64encode(h).decode("ascii").rstrip("=")
        return "uc-" + s[:12]

    @staticmethod
    def _write_collections(config_dir: Path, tag_appids: dict) -> dict:
        """Dopisuje/aktualizuje kolekcje per-system w magazynie cloudstorage.

        tag_appids: {"PS2": [appid, ...], "PS1": [...], "Windows": [...]}.
        Zachowuje WSZYSTKIE istniejące kolekcje; dla istniejącej o tej samej
        nazwie robi union appidów, dla nowej tworzy wpis. Robi backup całego
        folderu cloudstorage, zapisuje atomowo, aktualizuje liczniki zmian i
        listę modified (żeby Steam zsynchronizował zmiany do chmury)."""
        cs_dir = Path(config_dir) / "cloudstorage"
        ns1 = cs_dir / "cloud-storage-namespace-1.json"
        result = {"created": [], "updated": [], "path": str(ns1),
                  "backup": None, "ok": False, "error": None}
        if not ns1.exists():
            result["error"] = ("brak pliku cloud-storage-namespace-1.json — "
                               "ten profil Steam nie ma jeszcze magazynu kolekcji "
                               "(otwórz raz bibliotekę Steam, aby go utworzyć)")
            return result
        try:
            arr = json.loads(ns1.read_text(encoding="utf-8"))
            if not isinstance(arr, list):
                raise ValueError("nieoczekiwany format (nie tablica)")
        except Exception as ex:
            result["error"] = f"nie można odczytać kolekcji: {ex}"
            return result

        # Backup całego folderu cloudstorage (warunek zgody użytkownika).
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        bak = cs_dir.with_name(f"cloudstorage.bak-{ts}")
        try:
            shutil.copytree(cs_dir, bak)
            result["backup"] = str(bak)
        except Exception as ex:
            result["error"] = f"backup nieudany — przerwano bez zapisu: {ex}"
            return result

        # Licznik zmian namespace 1 (z namespaces.json).
        ns_file = cs_dir / "cloud-storage-namespaces.json"
        try:
            ns_list = json.loads(ns_file.read_text(encoding="utf-8"))
            if not isinstance(ns_list, list):
                ns_list = []
        except Exception:
            ns_list = []
        cur = 0
        for pair in ns_list:
            if isinstance(pair, list) and len(pair) == 2 and pair[0] == 1:
                try:
                    cur = int(pair[1])
                except Exception:
                    cur = 0

        # Indeks istniejących kolekcji po nazwie + najwyższa wersja.
        name_to_item = {}
        max_ver = cur
        for item in arr:
            if not (isinstance(item, list) and len(item) == 2):
                continue
            key, wrap = item
            if not (isinstance(key, str) and key.startswith("user-collections.")
                    and isinstance(wrap, dict)):
                continue
            try:
                max_ver = max(max_ver, int(wrap.get("version", 0)))
            except Exception:
                pass
            if wrap.get("is_deleted") or "value" not in wrap:
                continue
            try:
                v = json.loads(wrap["value"])
            except Exception:
                continue
            nm = v.get("name")
            if nm:
                name_to_item.setdefault(nm, [item, v])

        now = int(time.time())
        ver = max(max_ver, cur)
        changed_keys = []

        for tag, appids in tag_appids.items():
            appids = sorted({int(a) for a in appids})
            if not appids:
                continue
            if tag in name_to_item:
                item, v = name_to_item[tag]
                old_added = list(v.get("added", []) or [])
                old_removed = list(v.get("removed", []) or [])
                # union added (zachowaj kolejność), usuń nasze z removed
                merged = list(dict.fromkeys(old_added + appids))
                new_removed = [r for r in old_removed if r not in set(appids)]
                if merged == old_added and new_removed == old_removed:
                    continue  # brak zmian
                v["added"] = merged
                v["removed"] = new_removed
                ver += 1
                item[1]["value"] = json.dumps(v, separators=(",", ":"),
                                              ensure_ascii=False)
                item[1]["timestamp"] = now
                item[1]["version"] = str(ver)
                changed_keys.append(item[0])
                result["updated"].append(f"{tag} (+{len(set(appids) - set(old_added))})")
            else:
                cid = _SteamExportDialog._new_collection_id(tag)
                key = f"user-collections.{cid}"
                v = {"id": cid, "name": tag, "added": appids, "removed": []}
                ver += 1
                wrap = {"key": key, "timestamp": now,
                        "value": json.dumps(v, separators=(",", ":"),
                                            ensure_ascii=False),
                        "version": str(ver)}
                arr.append([key, wrap])
                changed_keys.append(key)
                result["created"].append(f"{tag} ({len(appids)})")

        if not changed_keys:
            result["ok"] = True
            return result

        # modified.json (union kluczy do wysyłki do chmury).
        mod_file = cs_dir / "cloud-storage-namespace-1.modified.json"
        try:
            mod = json.loads(mod_file.read_text(encoding="utf-8"))
            if not isinstance(mod, list):
                mod = []
        except Exception:
            mod = []
        for k in changed_keys:
            if k not in mod:
                mod.append(k)

        # namespaces.json — podbij licznik zmian dla ns 1.
        new_ns = []
        seen1 = False
        for pair in ns_list:
            if isinstance(pair, list) and len(pair) == 2 and pair[0] == 1:
                new_ns.append([1, str(ver)])
                seen1 = True
            else:
                new_ns.append(pair)
        if not seen1:
            new_ns.append([1, str(ver)])

        # Zapisy atomowe (temp + os.replace w tym samym katalogu).
        def _atomic(p: Path, text: str):
            tmp = p.with_name(p.name + f".tmp-{uuid.uuid4().hex}")
            tmp.write_text(text, encoding="utf-8")
            os.replace(tmp, p)

        try:
            _atomic(ns1, json.dumps(arr, separators=(",", ":"), ensure_ascii=False))
            _atomic(mod_file, json.dumps(mod, separators=(",", ":"), ensure_ascii=False))
            _atomic(ns_file, json.dumps(new_ns, separators=(",", ":"), ensure_ascii=False))
        except Exception as ex:
            result["error"] = f"błąd zapisu kolekcji (backup: {bak}): {ex}"
            return result

        result["ok"] = True
        return result

    def _build_entry(self, g: dict):
        """Buduje surowy wpis VDF (dict pól) dla jednej gry wraz z tagami."""
        exe  = g.get("launch_exe") or g.get("rom_path", "")
        args = ""
        start_override = ""
        source = g.get("source", "")
        if source == "rom":
            rp = g.get("rom_path", "")
            if g.get("rom_is_lnk") or str(rp).lower().endswith(".lnk"):
                # ROM uruchamiany przez .lnk (np. PS3/RPCS3) — Steam potrzebuje
                # EXE, więc rozwiń .lnk na docelowy plik + argumenty + katalog.
                tgt, largs, lwd = read_lnk_target(rp)
                exe = tgt
                args = largs
                start_override = lwd
            else:
                # Gra wielopłytowa: dobierz ścieżkę do możliwości emulatora —
                # .m3u dla obsługujących (DuckStation/RetroArch…), pojedynczy
                # dysk dla PCSX2/Dolphin (nie czytają playlist).
                rp = disc_path_for_emulator(rp, g.get("launch_exe", ""))
                la = g.get("launch_args", "")
                if la:
                    args = la.replace("%ROM%", f'"{rp}"') if "%ROM%" in la else f'{la} "{rp}"'
                else:
                    args = f'"{rp}"'
                exe  = g.get("launch_exe", "")
        elif source == "steam":
            exe  = f"steam://rungameid/{g.get('appid','')}"
            args = ""

        if not exe:
            return None
        exe_q = f'"{exe}"' if not exe.startswith('"') else exe

        # AppID stabilny: crc32 z (exe + nazwa) jako bytes — to samo id przy
        # kolejnym eksporcie tej samej gry. Wejście CRC jest już typu bytes.
        appid = (binascii.crc32((exe + g["name"]).encode("utf-8"))
                 | 0x80000000) & 0xFFFFFFFF

        start = start_override or (
            str(Path(exe).parent) if (exe and Path(exe).exists()) else "")

        tags = self._build_tags(g)
        tags_obj = {str(i): t for i, t in enumerate(tags)}  # {"0": tag0, ...}

        # Kolejność pól jak w plikach Steam (dict zachowuje kolejność wstawiania).
        entry = {
            "appid":               appid,
            "AppName":             g["name"],
            "Exe":                 exe_q,
            "StartDir":            start,
            "icon":                "",
            "ShortcutPath":        "",
            "LaunchOptions":       args,
            "IsHidden":            0,
            "AllowDesktopConfig":  1,
            "AllowOverlay":        1,
            "OpenVR":              0,
            "Devkit":              0,
            "DevkitGameID":        "",
            "DevkitOverrideAppID": 0,
            "LastPlayTime":        0,
            "FlatpakAppID":        "",
            "tags":                tags_obj,
        }
        return entry

    @staticmethod
    def _build_tags(g: dict):
        """Buduje listę tagów: Non-Steam + platforma/źródło.

        Usuwa puste oraz zduplikowane tagi, zachowując kolejność."""
        tags = ["Non-Steam"]
        source = g.get("source", "")
        if source == "rom":
            plat = (g.get("rom_platform") or g.get("romplatform") or "").strip()
            tags.append(plat if plat else "ROM")
        elif source == "extra":
            tags.append("Windows")
        elif source == "steam":
            tags.append("Steam")
        elif source:
            tags.append(source.capitalize())
        seen = set()
        out = []
        for t in tags:
            t = (t or "").strip()
            if not t or t in seen:
                continue
            seen.add(t)
            out.append(t)
        return out

    @staticmethod
    def _is_steam_running() -> bool:
        """Wykrywa działający proces Steam przez rejestr (Windows).

        Czyta HKCU\\Software\\Valve\\Steam\\ActiveProcess\\pid — Steam ustawia je
        na != 0, gdy działa. Szybkie, bez subprocess i bez fałszywych alarmów;
        przy błędzie zwraca False (nie blokuje eksportu)."""
        if not WINREG_OK:
            return False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Valve\Steam\ActiveProcess") as k:
                pid, _ = winreg.QueryValueEx(k, "pid")
                return int(pid) != 0
        except Exception:
            return False

    @staticmethod
    def _bvdf_parse_object(data: bytes, pos: int):
        """Parsuje dzieci obiektu binarnego VDF aż do 0x08. Zwraca (dict, pos).

        Zachowuje kolejność pól (dict insertion order) oraz obiekty zagnieżdżone
        (np. tags). Nie gubi nieznanych pól."""
        import struct
        result: dict = {}
        n = len(data)
        while pos < n:
            typ = data[pos]; pos += 1
            if typ == 0x08:  # koniec obiektu
                return result, pos
            key_end = data.index(b'\x00', pos)
            key = data[pos:key_end].decode("utf-8", errors="replace")
            pos = key_end + 1
            if typ == 0x00:  # zagnieżdżony obiekt (np. tags)
                child, pos = _SteamExportDialog._bvdf_parse_object(data, pos)
                result[key] = child
            elif typ == 0x01:  # string
                val_end = data.index(b'\x00', pos)
                result[key] = data[pos:val_end].decode("utf-8", errors="replace")
                pos = val_end + 1
            elif typ == 0x02:  # uint32
                result[key] = struct.unpack_from('<I', data, pos)[0]
                pos += 4
            elif typ == 0x07:  # uint64
                result[key] = struct.unpack_from('<Q', data, pos)[0]
                pos += 8
            else:
                raise ValueError(
                    f"Nieznany typ binarnego VDF 0x{typ:02x} @ offset {pos}")
        raise ValueError("Nieoczekiwany koniec danych — brak 0x08")

    @staticmethod
    def _bvdf_dump_value(key: str, val) -> bytes:
        """Serializuje pojedyncze pole (key->val) do binarnego VDF.

        Typ wyprowadzany jest z typu Pythona: dict->obiekt(0x00),
        int/bool->uint32(0x02), reszta->string(0x01). Dzięki temu round-trip
        odczyt->zapis zachowuje wszystkie pola (w tym nieznane) i tagi."""
        import struct
        kb = key.encode("utf-8") + b'\x00'
        if isinstance(val, dict):
            out = bytearray()
            out += b'\x00' + kb
            for k, v in val.items():
                out += _SteamExportDialog._bvdf_dump_value(str(k), v)
            out += b'\x08'
            return bytes(out)
        if isinstance(val, bool):
            return b'\x02' + kb + struct.pack('<I', 1 if val else 0)
        if isinstance(val, int):
            return b'\x02' + kb + struct.pack('<I', val & 0xFFFFFFFF)
        return b'\x01' + kb + str(val).encode("utf-8") + b'\x00'

    @staticmethod
    def _field(entry: dict, name: str, default=""):
        """Pobiera pole wpisu niezależnie od wielkości liter klucza."""
        if name in entry:
            return entry[name]
        low = name.lower()
        for k, v in entry.items():
            if k.lower() == low:
                return v
        return default

    @classmethod
    def _collapse_by_appid(cls, entries: list[dict]) -> "tuple[list[dict], list[str]]":
        """Zbija wpisy o TYM SAMYM appid do jednego (ta sama gra).

        appid = crc32(Exe+nazwa), więc identyczny appid = definicyjnie ta sama
        gra (np. Disc 1 i Disc 2 tego samego tytułu bez .m3u, albo stary + nowy
        eksport). Zostawia JEDEN wpis (preferuje uruchamiany przez .m3u — pełny
        zestaw dysków), scala do niego tagi i ikonę, resztę usuwa. Zachowuje
        kolejność. Wpisy bez appid (0) zostają nietknięte. Różny appid = różna
        gra (np. PaRappa PS1 vs PSP, albo bonusowy „Making of") — NIE łączone.

        Zwraca (lista_bez_duplikatów, nazwy_usuniętych).
        """
        f = cls._field
        def _ap(en) -> int:
            try:
                return int(f(en, "appid", 0) or 0)
            except Exception:
                return 0
        def _is_m3u(en) -> bool:
            return ".m3u" in str(f(en, "LaunchOptions", "")).lower()
        def _is_disc1(en) -> bool:
            o = str(f(en, "LaunchOptions", "")).lower()
            return "(disc 1)" in o or "(disk 1)" in o or " disc 1" in o

        groups: dict = {}
        order: list = []
        for e in entries:
            ap = _ap(e)
            if ap == 0:
                order.append(("keep", e)); continue
            if ap not in groups:
                groups[ap] = []; order.append(("group", ap))
            groups[ap].append(e)

        removed: list[str] = []
        out: list[dict] = []
        for kind, val in order:
            if kind == "keep":
                out.append(val); continue
            grp = groups[val]
            if len(grp) == 1:
                out.append(grp[0]); continue
            # Preferencja wpisu do zachowania: .m3u (pełny zestaw) > Disc 1
            # (dla emulatorów bez .m3u, np. PCSX2) > pierwszy w kolejności.
            keep = (next((x for x in grp if _is_m3u(x)), None)
                    or next((x for x in grp if _is_disc1(x)), None)
                    or grp[0])
            for other in grp:
                if other is keep:
                    continue
                cls._merge_tags(keep, other.get("tags", {}))
                if not str(f(keep, "icon", "")).strip():
                    oi = str(f(other, "icon", "")).strip()
                    if oi:
                        cls._set_field(keep, "icon", oi)
                removed.append(str(f(other, "AppName", "")))
            out.append(keep)
        return out, removed

    @staticmethod
    def _dedup_key(entry: dict):
        """Znormalizowany klucz deduplikacji: (AppName, Exe+LaunchOptions)."""
        f = _SteamExportDialog._field
        name = str(f(entry, "AppName", "")).strip().lower()
        exe  = str(f(entry, "Exe", "")).strip().lower()
        opts = str(f(entry, "LaunchOptions", "")).strip().lower()
        return (name, exe + "\x00" + opts)

    @staticmethod
    def _write_shortcuts_vdf(entries: list[dict]) -> bytes:
        """Serializuje listę wpisów do POPRAWNEGO binarnego shortcuts.vdf.

        Struktura: 0x00 'shortcuts' 0x00 <numerowane wpisy> 0x08 0x08.
        Każdy wpis i pod-obiekt (tags) ma prawidłowe znaczniki typów oraz
        domknięcie 0x08. Podwójne 0x08 na końcu zamyka mapę 'shortcuts'
        i cały dokument (root)."""
        shortcuts = {str(i): e for i, e in enumerate(entries)}
        out = bytearray()
        out += _SteamExportDialog._bvdf_dump_value("shortcuts", shortcuts)
        out += b'\x08'  # domknięcie dokumentu (root)
        return bytes(out)

    @staticmethod
    def _read_shortcuts_vdf(path: Path) -> list[dict]:
        """Parsuje binarny shortcuts.vdf i zwraca listę wpisów (dict pól).

        Poprawnie przechodzi przez obiekty zagnieżdżone (w tym tags), nie gubi
        istniejących tagów, pól ani wpisów. Nazwa klucza root nie jest zakładana
        — obiekt root czytany jest po typie (0x00)."""
        data = path.read_bytes()
        if len(data) < 2 or data[0] != 0x00:
            raise ValueError("Nieprawidłowy nagłówek binarnego VDF")
        pos = 1
        key_end = data.index(b'\x00', pos)  # nazwa root ('shortcuts' lub pusta)
        pos = key_end + 1
        root, _pos = _SteamExportDialog._bvdf_parse_object(data, pos)

        def _order(item):
            k = item[0]
            return (0, int(k)) if k.isdigit() else (1, k)

        entries: list[dict] = []
        for _k, v in sorted(root.items(), key=_order):
            if isinstance(v, dict):
                entries.append(v)
        return entries

    @staticmethod
    def _self_test() -> None:
        """Wewnętrzny self-test round-trip writer<->parser.

        Buduje dwa wpisy (gra Windows + ROM PS2), serializuje, odczytuje i
        weryfikuje AppName, appid, Exe, LaunchOptions oraz tags. Zgłasza czytelny
        wyjątek przy niezgodności. NIE jest uruchamiany automatycznie przy
        starcie GUI — można go wywołać ręcznie przed właściwym zapisem."""
        f = _SteamExportDialog._field
        e_win = {
            "appid": 0x80ABCDEF, "AppName": "Testowa Gra Windows",
            "Exe": '"C:\\Games\\game.exe"', "StartDir": '"C:\\Games"',
            "icon": "", "ShortcutPath": "", "LaunchOptions": "-fullscreen",
            "IsHidden": 0, "AllowDesktopConfig": 1, "AllowOverlay": 1,
            "OpenVR": 0, "Devkit": 0, "DevkitGameID": "",
            "DevkitOverrideAppID": 0, "LastPlayTime": 0,
            "tags": {"0": "Non-Steam", "1": "Windows"},
        }
        e_ps2 = {
            "appid": 0x80123456, "AppName": "Testowy ROM PS2",
            "Exe": '"C:\\Emu\\pcsx2.exe"', "StartDir": '"C:\\Emu"',
            "icon": "", "ShortcutPath": "", "LaunchOptions": '"C:\\ROM\\game.iso"',
            "IsHidden": 0, "AllowDesktopConfig": 1, "AllowOverlay": 1,
            "OpenVR": 0, "Devkit": 0, "DevkitGameID": "",
            "DevkitOverrideAppID": 0, "LastPlayTime": 0,
            "tags": {"0": "Non-Steam", "1": "PS2"},
        }
        blob = _SteamExportDialog._write_shortcuts_vdf([e_win, e_ps2])
        import tempfile
        tmp = Path(tempfile.gettempdir()) / f"_pylinks_selftest_{uuid.uuid4().hex}.vdf"
        try:
            tmp.write_bytes(blob)
            got = _SteamExportDialog._read_shortcuts_vdf(tmp)
        finally:
            try:
                tmp.unlink()
            except Exception:
                pass
        if len(got) != 2:
            raise AssertionError(f"Round-trip: oczekiwano 2 wpisow, jest {len(got)}")
        for want in (e_win, e_ps2):
            match = next((x for x in got
                          if f(x, "AppName") == want["AppName"]), None)
            if match is None:
                raise AssertionError(f"Round-trip: brak wpisu {want['AppName']!r}")
            for fld in ("appid", "Exe", "LaunchOptions"):
                if f(match, fld) != want[fld]:
                    raise AssertionError(
                        f"Round-trip: pole {fld} nie zgadza sie dla "
                        f"{want['AppName']!r}: {f(match, fld)!r} != {want[fld]!r}")
            wt = list(want["tags"].values())
            gt = list(f(match, "tags", {}).values())
            if wt != gt:
                raise AssertionError(
                    f"Round-trip: tags nie zgadzaja sie dla {want['AppName']!r}: "
                    f"{gt!r} != {wt!r}")


def _dat_detect_system(dat_path: Path) -> str:
    """Auto-wykryj system ROM na podstawie nagłówka DAT lub nazwy pliku.

    Zwraca klucz systemu (np. "PS1", "N64") lub "" jeśli nieznany.
    """
    # 1. Parsuj <header><name> z XML
    dat_name_raw = ""
    try:
        for _, elem in ET.iterparse(str(dat_path), events=("end",)):
            if elem.tag == "name":
                dat_name_raw = (elem.text or "").strip()
                break
    except Exception:
        dat_name_raw = dat_path.stem

    if not dat_name_raw:
        dat_name_raw = dat_path.stem

    def _norm(s: str) -> str:
        return re.sub(r'[^a-z0-9 ]', ' ', s.lower()).strip()

    target = _norm(dat_name_raw)

    # 2. Dopasuj do LIBRETRO_SYSTEM_MAP (np. "Sony_-_PlayStation" → "sony playstation")
    best_sys   = ""
    best_score = 0
    for sys_key, lib_name in LIBRETRO_SYSTEM_MAP.items():
        lib_norm = _norm(lib_name.replace("_", " "))
        if lib_norm in target or target.startswith(lib_norm[:12]):
            score = len(lib_norm)
            if score > best_score:
                best_score, best_sys = score, sys_key

    if best_sys:
        return best_sys

    # 3. Dopasuj do ROM_SYSTEM_PRESETS (display names + dir_names)
    for preset in ROM_SYSTEM_PRESETS:
        for candidate in [preset["display"]] + preset.get("dir_names", []):
            if _norm(candidate) in target:
                return preset["name"]

    # 4. Słowa kluczowe (ostateczny fallback)
    kw_map = [
        ("playstation 4",  ""),  # nie obsługujemy
        ("playstation 3",  "PS3"),
        ("playstation 2",  "PS2"),
        ("playstation portable", "PSP"),
        ("playstation",    "PS1"),
        ("nintendo 64",    "N64"),
        ("super nintendo", "SNES"),
        ("super famicom",  "SNES"),
        ("game boy advance", "GBA"),
        ("game boy color", "GBC"),
        ("game boy",       "GB"),
        ("nintendo ds",    "NDS"),
        ("gamecube",       "GCN"),
        ("nintendo wii",   "WII"),
        (" wii ",          "WII"),
        ("mega drive",     "MD"),
        ("genesis",        "MD"),
        ("master system",  "SMS"),
        ("game gear",      "GG"),
        ("dreamcast",      "DC"),
        ("saturn",         "SATURN"),
        ("sega cd",        "SEGACD"),
        ("mega cd",        "SEGACD"),
        ("mame",           "MAME"),
        ("neo geo",        "NEOGEO"),
        ("pc engine",      "PCENGINE"),
        ("turbografx",     "PCENGINE"),
        ("atari jaguar",   "JAGUAR"),
        ("jaguar",         "JAGUAR"),
        ("atari 2600",     "ATARI2600"),
        ("amiga",          "AMIGA"),
        ("pc-98",          "PC98"),
        ("pc98",           "PC98"),
        ("msx",            "MSX2"),
        ("naomi 2",        "NAOMI2"),
        ("naomi",          "NAOMI"),
        ("3do",            "3DO"),
        ("nes ",           "NES"),
        ("famicom",        "NES"),
        ("gb ",            "GB"),
        ("gba",            "GBA"),
        ("gbc",            "GBC"),
        ("n64",            "N64"),
        ("psx",            "PS1"),
        ("ps1",            "PS1"),
        ("ps2",            "PS2"),
    ]
    for kw, sys in kw_map:
        if sys and kw in target:
            return sys

    return ""


# Globalny log weryfikacji (drukuje do stdout i trzyma ostatnie 500 linii)
_verify_log_lines: list[str] = []
_verify_log_cb = None   # opcjonalny callback do odświeżania UI

def _log(msg: str):
    """Loguj do stdout i bufora (widoczne w CMD i w oknie logu)."""
    line = f"[VERIFY] {msg}"
    print(line, flush=True)
    _verify_log_lines.append(line)
    if len(_verify_log_lines) > 500:
        _verify_log_lines.pop(0)
    if _verify_log_cb:
        try:
            _verify_log_cb(line)
        except Exception:
            pass


def _scan_all_dats(dat_dir: Path, assignments: dict[str, str]) -> list[dict]:
    """Skanuj wszystkie pliki DAT w dat_dir rekurencyjnie.

    Zwraca listę słowników:
      {path, filename, system (auto lub przypisany), auto_system, label}
    """
    results = []
    for p in sorted(dat_dir.rglob("*.dat")):
        fname       = p.name
        # Przypisanie ręczne ma priorytet
        manual_sys  = assignments.get(fname, "")
        auto_sys    = _dat_detect_system(p)
        sys_final   = manual_sys or auto_sys
        src_tag     = "ręcznie" if manual_sys else ("auto" if auto_sys else "?")
        label       = f"[{sys_final or '?'}]  {fname}  ({src_tag})" if sys_final \
                      else f"[?]  {fname}  (nieznany — przypisz system)"
        results.append({
            "path":        p,
            "filename":    fname,
            "system":      sys_final,
            "auto_system": auto_sys,
            "manual":      bool(manual_sys),
            "label":       label,
        })
    return results


class _StatsDialog(tk.Toplevel):
    """Statystyki biblioteki: liczby, rozmiary, weryfikacja."""

    def __init__(self, parent, games: list, cfg: dict):
        super().__init__(parent)
        self.title("📊 Statystyki biblioteki")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.geometry("860x560")
        self.grab_set()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        t1 = tk.Frame(nb, bg=C["bg"]); nb.add(t1, text="Biblioteka")
        t2 = tk.Frame(nb, bg=C["bg"]); nb.add(t2, text="Dysk & formaty")

        pc_sources = {"steam", "gog", "epic", "extra"}
        src_map: dict[str, int] = {}
        rom_sys:  dict[str, int] = {}
        for g in games:
            s = g.get("source", "steam")
            if s in pc_sources:
                src_map[s] = src_map.get(s, 0) + 1
            elif s == "rom":
                p = g.get("rom_platform", "?")
                rom_sys[p] = rom_sys.get(p, 0) + 1

        # ── Tab 1: Biblioteka ─────────────────────────────────────────────────
        self._draw_bar_section(t1, "Gry PC", src_map,
                               {"steam": C["grn"], "gog": C["yel"],
                                "epic": C["orn"], "extra": C["ext"]})
        self._draw_bar_section(t1, "ROM-y wg systemu", rom_sys)

        total = len(games)
        pc_tot = sum(src_map.values())
        rom_tot = sum(rom_sys.values())
        tk.Label(t1,
                 text=f"Łącznie: {total}  |  PC: {pc_tot}  |  ROM-y: {rom_tot}",
                 bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 10, "bold")).pack(pady=8)

        # ── Tab 2: Dysk & formaty ─────────────────────────────────────────────
        systems = cfg.get("rom_support", {}).get("systems", [])
        size_data: dict[str, int] = {}
        fmt_data:  dict[str, int] = {}
        for sys in systems:
            rom_dir = sys.get("rom_dir", "")
            sname   = sys.get("name", "?")
            if not rom_dir or not Path(rom_dir).is_dir():
                continue
            total_bytes = 0
            for f in Path(rom_dir).rglob("*"):
                if f.is_file():
                    try:
                        sz = f.stat().st_size
                        total_bytes += sz
                        ext = f.suffix.lower().lstrip(".")
                        fmt_data[ext] = fmt_data.get(ext, 0) + 1
                    except Exception:
                        pass
            if total_bytes:
                size_data[sname] = total_bytes

        size_gb = {k: v / (1024**3) for k, v in size_data.items()}
        self._draw_bar_section(t2, "Rozmiar wg systemu (GB)",
                               {k: round(v, 1) for k, v in size_gb.items()},
                               label_suffix=" GB")
        top_fmts = dict(sorted(fmt_data.items(),
                                key=lambda x: x[1], reverse=True)[:12])
        self._draw_bar_section(t2, "Pliki wg formatu", top_fmts)

        tk.Button(self, text="Zamknij", command=self.destroy,
                  bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=16, pady=6).pack(pady=8)

        self.update_idletasks()
        pw = parent.winfo_x() + (parent.winfo_width()  - 860) // 2
        ph = parent.winfo_y() + (parent.winfo_height() - 560) // 2
        self.geometry(f"+{pw}+{ph}")

    def _draw_bar_section(self, parent, title: str, data: dict,
                          colors: dict | None = None,
                          label_suffix: str = ""):
        if not data:
            return
        frame = tk.LabelFrame(parent, text=title,
                              bg=C["bg"], fg=C["fg2"],
                              font=("Segoe UI", 8))
        frame.pack(fill="x", padx=14, pady=6)

        max_val = max(data.values()) or 1
        BAR_MAX = 320

        for key, val in sorted(data.items(), key=lambda x: x[1], reverse=True):
            row = tk.Frame(frame, bg=C["bg"])
            row.pack(fill="x", padx=8, pady=1)
            color = (colors or {}).get(key, C["acc"])
            bar_w = max(4, int(val / max_val * BAR_MAX))
            tk.Label(row, text=f"{key:<14}", bg=C["bg"], fg=C["fg2"],
                     font=("Consolas", 8), width=16, anchor="w").pack(side="left")
            tk.Frame(row, bg=color, width=bar_w, height=14).pack(side="left")
            tk.Label(row, text=f" {val}{label_suffix}",
                     bg=C["bg"], fg=C["fg"],
                     font=("Segoe UI", 8)).pack(side="left")


class _PlayniteExportDialog(tk.Toplevel):
    """Eksport gier do Playnite (JSON) i LaunchBox (XML)."""

    def __init__(self, parent, games: list):
        super().__init__(parent)
        self.title("🎮 Eksport → Playnite / LaunchBox")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.geometry("720x480")
        self.grab_set()
        self._games = games

        tk.Label(self,
                 text="Eksport gier do zewnętrznych menedżerów",
                 bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(12, 4))

        # Filtry
        fil_f = tk.Frame(self, bg=C["bg"])
        fil_f.pack(fill="x", padx=14, pady=4)
        tk.Label(fil_f, text="Eksportuj:", bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 9)).pack(side="left")
        self.v_exp_steam = tk.BooleanVar(value=False)
        self.v_exp_extra = tk.BooleanVar(value=True)
        self.v_exp_rom   = tk.BooleanVar(value=True)
        for var, lbl in [(self.v_exp_steam,"Steam"),
                         (self.v_exp_extra,"Extra/GOG/Epic"),
                         (self.v_exp_rom,  "ROM-y")]:
            tk.Checkbutton(fil_f, text=lbl, variable=var,
                           bg=C["bg"], fg=C["fg2"], selectcolor=C["bg3"],
                           activebackground=C["bg"]).pack(side="left", padx=6)

        # Folder docelowy
        dst_row = tk.Frame(self, bg=C["bg"])
        dst_row.pack(fill="x", padx=14, pady=6)
        tk.Label(dst_row, text="Folder docelowy:", bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 9)).pack(side="left")
        self.v_dst = tk.StringVar(value=str(SCRIPT_DIR / "export"))
        tk.Entry(dst_row, textvariable=self.v_dst,
                 bg=C["bg3"], fg=C["fg"], insertbackground="white",
                 relief="flat", font=("Segoe UI", 9)).pack(side="left", fill="x",
                                                            expand=True, padx=4)
        tk.Button(dst_row, text="…",
                  command=lambda: self.v_dst.set(
                      filedialog.askdirectory(parent=self) or self.v_dst.get()),
                  bg=C["bg3"], fg=C["acc"], relief="flat", padx=6).pack(side="left")

        # Przyciski eksportu
        btn_f = tk.Frame(self, bg=C["bg"])
        btn_f.pack(fill="x", padx=14, pady=8)
        tk.Button(btn_f, text="📄 Eksportuj Playnite JSON",
                  command=self._export_playnite,
                  bg=C["acc"], fg=C["bg"],
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=14, pady=6,
                  cursor="hand2").pack(side="left")
        tk.Button(btn_f, text="📋 Eksportuj LaunchBox XML",
                  command=self._export_launchbox,
                  bg=C["bg3"], fg=C["fg"],
                  font=("Segoe UI", 9),
                  relief="flat", padx=14, pady=6,
                  cursor="hand2").pack(side="left", padx=8)

        self.v_status = tk.StringVar(value="")
        tk.Label(self, textvariable=self.v_status,
                 bg=C["bg"], fg=C["grn"],
                 font=("Segoe UI", 9)).pack(padx=14, pady=4)

        tk.Button(self, text="Zamknij", command=self.destroy,
                  bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=12, pady=4).pack(pady=8)

        self.update_idletasks()
        pw = parent.winfo_x() + (parent.winfo_width()  - 720) // 2
        ph = parent.winfo_y() + (parent.winfo_height() - 480) // 2
        self.geometry(f"+{pw}+{ph}")

    def _filtered_games(self) -> list:
        out = []
        for g in self._games:
            s = g.get("source", "")
            if s == "steam" and not self.v_exp_steam.get(): continue
            if s in ("gog", "epic", "extra") and not self.v_exp_extra.get(): continue
            if s == "rom" and not self.v_exp_rom.get(): continue
            out.append(g)
        return out

    def _export_playnite(self):
        import json as _json, uuid as _uuid
        games = self._filtered_games()
        dst = Path(self.v_dst.get().strip())
        dst.mkdir(parents=True, exist_ok=True)
        pla_dir = dst / "playnite_games"
        pla_dir.mkdir(exist_ok=True)

        # Playnite platform map
        plat_map = {
            "steam": "PC",
            "gog":   "PC", "epic": "PC", "extra": "PC",
            "rom":   None,   # per-system
        }
        written = 0
        for g in games:
            exe  = g.get("launch_exe", "")
            args = g.get("launch_args", "")
            if g.get("source") == "rom":
                plat = g.get("rom_platform", "PC")
                exe  = g.get("launch_exe", "")
                args = g.get("launch_args", "") or g.get("rom_path", "")
            else:
                plat = "PC"

            entry = {
                "Id":          str(_uuid.uuid4()),
                "Name":        g["name"],
                "IsInstalled": True,
                "Platform":    {"Name": plat},
                "GameActions": [{
                    "Name":       "Play",
                    "Type":       0,
                    "Path":       exe,
                    "Arguments":  args,
                    "IsPlayAction": True,
                }],
                "Source": {"Name": "PyLinks"},
            }
            fname = re.sub(r'[\\/:*?"<>|]', '_', g["name"])[:80] + ".json"
            (pla_dir / fname).write_text(
                _json.dumps(entry, ensure_ascii=False, indent=2),
                encoding="utf-8")
            written += 1

        self.v_status.set(
            f"✓ Playnite: {written} plików JSON → {pla_dir}")

    def _export_launchbox(self):
        games = self._filtered_games()
        dst = Path(self.v_dst.get().strip())
        dst.mkdir(parents=True, exist_ok=True)

        # Grupuj wg platformy
        by_plat: dict[str, list] = {}
        for g in games:
            s = g.get("source", "")
            if s == "rom":
                plat = g.get("rom_platform", "PC")
            else:
                plat = "PC"
            by_plat.setdefault(plat, []).append(g)

        written = 0
        for plat, plat_games in by_plat.items():
            root = ET.Element("LaunchBox")
            for g in plat_games:
                gel = ET.SubElement(root, "Game")
                ET.SubElement(gel, "Title").text    = g["name"]
                ET.SubElement(gel, "Platform").text = plat
                exe = (g.get("launch_exe") or g.get("rom_path") or "")
                ET.SubElement(gel, "ApplicationPath").text = exe
                ET.SubElement(gel, "CommandLine").text = g.get("launch_args","")
                ET.SubElement(gel, "Installed").text   = "true"
                written += 1
            ET.indent(root, space="  ")
            safe = re.sub(r'[\\/:*?"<>|]', '_', plat)
            xml_str = ET.tostring(root, encoding="unicode", xml_declaration=True)
            (dst / f"LaunchBox_{safe}.xml").write_text(
                xml_str, encoding="utf-8")

        self.v_status.set(
            f"✓ LaunchBox: {written} gier w {len(by_plat)} plikach XML → {dst}")


class RomExtPickDialog(tk.Toplevel):
    """Dialog wyboru głównego rozszerzenia dla systemu ROM w trybie podkatalogów.

    Wywoływany RAZ gdy żaden plik w podkatalogach nie pasuje do listy primary_ext.
    Użytkownik wybiera, które rozszerzenie emulator ma dostawać jako argument.
    Wybór jest zapamiętywany w configu systemu (nie pytamy ponownie).

    Atrybuty wynikowe:
      result_ext  (str | None)  – wybrane rozszerzenie (bez kropki), None = anuluj
      save_choice (bool)        – czy zapisać do konfigu
    """

    def __init__(self, parent, plat: str, ext_counts: dict[str, int]):
        """
        plat       – nazwa systemu (np. "PS3")
        ext_counts – {ext: count} wszystkich plików znalezionych
        """
        super().__init__(parent)
        self.title(f"Wybierz główny plik — {plat}")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.grab_set()
        self.result_ext:  str | None = None
        self.save_choice: bool       = True

        # Nagłówek
        tk.Label(self,
                 text=f"System {plat}: nie znaleziono pliku\nz listy priorytetów.",
                 bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 10, "bold"),
                 justify="left").pack(anchor="w", padx=14, pady=(12, 4))
        tk.Label(self,
                 text="Wybierz rozszerzenie które emulator otrzyma\n"
                      "jako argument (plik główny każdej gry).",
                 bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 8), justify="left").pack(anchor="w", padx=14, pady=(0, 8))

        # Lista rozszerzeń z licznikami plików (posortowana od najliczniejszego)
        list_f = tk.Frame(self, bg=C["bg2"],
                          highlightthickness=1, highlightbackground=C["bg3"])
        list_f.pack(fill="both", padx=14, pady=(0, 8), expand=True)

        self._var = tk.StringVar()
        sorted_exts = sorted(ext_counts.items(), key=lambda x: -x[1])
        if sorted_exts:
            self._var.set(sorted_exts[0][0])   # domyślnie: najczęstsze

        for ext, count in sorted_exts:
            row = tk.Frame(list_f, bg=C["bg2"])
            row.pack(fill="x", padx=8, pady=2)
            tk.Radiobutton(row,
                           text=f".{ext}",
                           variable=self._var, value=ext,
                           bg=C["bg2"], fg=C["fg"],
                           activebackground=C["bg2"],
                           selectcolor=C["bg3"],
                           font=("Segoe UI", 10, "bold"),
                           width=8, anchor="w").pack(side="left")
            tk.Label(row,
                     text=f"{count} {'plik' if count == 1 else 'pliki' if count < 5 else 'plików'}",
                     bg=C["bg2"], fg=C["fg2"],
                     font=("Segoe UI", 9)).pack(side="left", padx=(4, 0))

        # Checkbox: zapamiętaj wybór
        v_save = tk.BooleanVar(value=True)
        tk.Checkbutton(self,
                       text=f"Zapamiętaj dla systemu {plat} (dodaj do listy ext)",
                       variable=v_save,
                       bg=C["bg"], fg=C["fg2"],
                       activebackground=C["bg"],
                       selectcolor=C["bg3"],
                       font=("Segoe UI", 8)).pack(anchor="w", padx=14, pady=(0, 6))

        # Przyciski
        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=14, pady=(0, 12))
        tk.Button(bot, text="OK — użyj wybranego ext",
                  command=lambda: self._ok(v_save),
                  bg=C["grn"], fg=C["bg"],
                  relief="flat", padx=14, pady=6,
                  font=("Segoe UI", 9, "bold"),
                  cursor="hand2").pack(side="right", padx=(4, 0))
        tk.Button(bot, text="Anuluj (pomijaj te katalogi)",
                  command=self.destroy,
                  bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=10, pady=6,
                  cursor="hand2").pack(side="right")

        self.update_idletasks()
        pw = parent.winfo_x() + (parent.winfo_width()  - self.winfo_width())  // 2
        ph = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{pw}+{ph}")
        self.wait_window(self)

    def _ok(self, v_save: tk.BooleanVar):
        self.result_ext  = self._var.get()
        self.save_choice = bool(v_save.get())
        self.destroy()


class EmuPickDialog(tk.Toplevel):
    """Dialog wyboru emulatora: RetroArch (z wyborem core) lub standalone exe.

    Skanuje base_emu_dir w poszukiwaniu RetroArch oraz znanych exe.
    result_exe  (str) – ścieżka do emulatora (retroarch.exe lub standalone)
    result_args (str) – launch_args (np. -L "core.dll" %ROM% lub "")
    result_name (str) – przyjazna nazwa wyboru
    """

    def __init__(self, parent, plat: str, base_emu_dir: str):
        super().__init__(parent)
        self.title(f"Wybierz emulator — {plat}")
        self.configure(bg=C["bg"])
        self.resizable(True, False)
        self.grab_set()
        self.result_exe:  str = ""
        self.result_args: str = ""
        self.result_name: str = ""
        self._entries: list[dict] = []

        tk.Label(self,
                 text=f"Dostępne emulatory dla {plat}:",
                 bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(12, 6))

        # Lista z radio buttonami
        wrap = tk.Frame(self, bg=C["bg2"],
                        highlightthickness=1, highlightbackground=C["bg3"])
        wrap.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        canvas = tk.Canvas(wrap, bg=C["bg2"], highlightthickness=0,
                           height=320)
        vsb = tk.Scrollbar(wrap, orient="vertical", command=canvas.yview,
                           bg=C["bg3"], width=8, relief="flat")
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=C["bg2"])
        cw = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._var = tk.StringVar(value="manual")
        self._inner = inner

        # FIX v7.1: skan katalogu emulatorów był wykonywany synchronicznie
        # w wątku UI (3x glob po całym base_emu_dir) — przy dużym katalogu
        # GUI wisiało kilka-kilkanaście sekund. Teraz: skan w tle + status.
        self._lbl_scan = tk.Label(inner,
                                  text="⏳ Skanowanie katalogu emulatorów…",
                                  bg=C["bg2"], fg=C["yel"],
                                  font=("Segoe UI", 9, "italic"))
        self._lbl_scan.pack(padx=10, pady=14)

        # Opcja: wskaż ręcznie (dostępna od razu, bez czekania na skan)
        manual_row = tk.Frame(inner, bg=C["bg2"])
        manual_row.pack(fill="x", padx=6, pady=4)
        tk.Radiobutton(manual_row, variable=self._var, value="manual",
                       bg=C["bg2"], activebackground=C["bg2"],
                       selectcolor=C["bg3"]).pack(side="left")
        tk.Label(manual_row, text="Wskaż ręcznie…",
                 bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 9, "italic")).pack(side="left")

        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(fill="x", padx=14, pady=(0, 12))
        tk.Button(bot, text="OK", command=lambda: self._ok(self._entries),
                  bg=C["grn"], fg=C["bg"],
                  relief="flat", padx=14, pady=6,
                  font=("Segoe UI", 9, "bold"),
                  cursor="hand2").pack(side="right", padx=(4, 0))
        tk.Button(bot, text="Anuluj", command=self.destroy,
                  bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=10, pady=6,
                  cursor="hand2").pack(side="right")

        def _scan_bg():
            try:
                found = self._scan_emulators(plat, base_emu_dir)
            except Exception as e:
                print(f"[EmuPick] Błąd skanowania: {e}")
                found = []
            try:
                self.after(0, lambda: self._populate(found))
            except Exception:
                pass  # okno zamknięte w trakcie skanowania

        threading.Thread(target=_scan_bg, daemon=True).start()

        self.geometry("620x480")
        self.update_idletasks()
        pw = parent.winfo_x() + (parent.winfo_width()  - 620) // 2
        ph = parent.winfo_y() + (parent.winfo_height() - 480) // 2
        self.geometry(f"+{pw}+{ph}")
        self.wait_window(self)

    def _populate(self, entries: list[dict]):
        """FIX v7.1: wstaw wyniki skanu (wywoływane z wątku UI przez after)."""
        if not self.winfo_exists():
            return
        self._entries = entries
        try:
            self._lbl_scan.destroy()
        except Exception:
            pass
        if not entries:
            tk.Label(self._inner,
                     text="Nie znaleziono emulatorów w katalogu bazowym.\n"
                          "Ustaw 'Katalog emulatorów' w sekcji powyżej.",
                     bg=C["bg2"], fg=C["orn"],
                     font=("Segoe UI", 8)).pack(padx=10, pady=(0, 8))
            self._var.set("manual")
            return
        for i, entry in enumerate(entries):
            bg = C["bg"] if i % 2 == 0 else C["bg2"]
            row = tk.Frame(self._inner, bg=bg)
            row.pack(fill="x", padx=6, pady=4)
            tk.Radiobutton(row, variable=self._var, value=str(i),
                           bg=bg, activebackground=bg, selectcolor=C["bg3"]
                           ).pack(side="left", anchor="n", pady=2)
            info = tk.Frame(row, bg=bg)
            info.pack(side="left", fill="x", expand=True)
            lbl_col = C["grn"] if entry["type"] == "retroarch" else C["acc"]
            tk.Label(info, text=entry["label"],
                     bg=bg, fg=lbl_col,
                     font=("Segoe UI", 9, "bold"),
                     anchor="w").pack(fill="x")
            tk.Label(info, text=entry["exe"],
                     bg=bg, fg=C["fg2"],
                     font=("Segoe UI", 7),
                     anchor="w").pack(fill="x")
            if entry.get("args"):
                tk.Label(info, text=entry["args"],
                         bg=bg, fg=C["yel"],
                         font=("Segoe UI", 7, "italic"),
                         anchor="w").pack(fill="x")
        self._var.set("0")

    def _ok(self, entries: list[dict]):
        sel = self._var.get()
        if sel == "manual":
            # Otwórz file dialog
            pth = filedialog.askopenfilename(
                title="Wybierz emulator",
                filetypes=[("EXE", "*.exe"), ("Wszystkie", "*")]
            )
            if pth:
                self.result_exe  = pth
                self.result_args = ""
                self.result_name = _exe_friendly_name(pth)
        else:
            idx = int(sel)
            e = entries[idx]
            self.result_exe  = e["exe"]
            self.result_args = e["args"]
            self.result_name = e["label"]
        self.destroy()

    @staticmethod
    def _scan_emulators(plat: str, base_emu_dir: str) -> list[dict]:
        """Skanuj base_emu_dir w poszukiwaniu RetroArch i standalone emulatorów.

        Zwraca listę wpisów posortowaną: RetroArch pierwsze, potem standalone.
        """
        if not base_emu_dir or not Path(base_emu_dir).is_dir():
            return []

        results: list[dict] = []
        plat_upper = plat.upper()
        seen_exes: set[str] = set()

        # Skanuj wszystkie .exe rekurencyjnie (max 3 poziomy głębokości)
        # FIX v7.1: twardy limit liczby plików — gdy ktoś wskaże ogromny
        # katalog (np. cały dysk), skan kończy się zamiast mielić minutami.
        _MAX_EXES = 2000
        exe_files: list[Path] = []
        base = Path(base_emu_dir)
        for depth, glob_pat in [(1, "*.exe"), (2, "*/*.exe"), (3, "*/*/*.exe")]:
            try:
                for p in base.glob(glob_pat):
                    exe_files.append(p)
                    if len(exe_files) >= _MAX_EXES:
                        break
            except Exception:
                pass
            if len(exe_files) >= _MAX_EXES:
                print(f"[EmuPick] Przerwano skan po {_MAX_EXES} plikach EXE — "
                      f"katalog emulatorów jest podejrzanie duży: {base}")
                break

        for exe in sorted(exe_files):
            exe_str = str(exe)
            if exe_str in seen_exes:
                continue
            seen_exes.add(exe_str)

            if exe.stem.lower() == "retroarch":
                # RetroArch — szukaj corów pasujących do platformy
                cores_dir = exe.parent / "cores"
                if not cores_dir.is_dir():
                    continue
                for core_f in sorted(cores_dir.iterdir()):
                    if not core_f.suffix.lower() in (".dll", ".so"):
                        continue
                    # Strip _libretro.dll / _libretro.so
                    core_stem = core_f.stem
                    if core_stem.endswith("_libretro"):
                        core_stem = core_stem[:-len("_libretro")]

                    systems = RETROARCH_CORE_SYSTEMS.get(core_stem)
                    if not systems:
                        continue
                    if isinstance(systems, str):
                        systems = [systems]
                    if plat_upper not in [s.upper() for s in systems]:
                        continue

                    core_path = str(core_f)
                    results.append({
                        "label": f"RetroArch — {_core_display(core_stem)}",
                        "exe":   exe_str,
                        "args":  f'-L "{core_path}" %ROM%',
                        "type":  "retroarch",
                    })
            else:
                # Standalone — dopasuj po nazwie pliku do platformy
                friendly = _exe_friendly_name(exe_str)
                if friendly == exe.stem:
                    # Nierozpoznany exe — wciąż pokaż (użytkownik może wybrać)
                    pass
                results.append({
                    "label": f"{friendly} (standalone)",
                    "exe":   exe_str,
                    "args":  "",
                    "type":  "standalone",
                })

        # RetroArch pierwsze, potem standalone posortowane alfabetycznie
        ra    = [e for e in results if e["type"] == "retroarch"]
        stand = [e for e in results if e["type"] == "standalone"]
        # Filtruj standalone: pokaż tylko te których nazwa pasuje do systemu
        # (nie zaśmiecamy listy niezwiązanymi exe)
        _PLAT_EXE_HINTS: dict[str, list[str]] = {
            "PS1":     ["epsxe","duckstation","pcsx","mednafen","retroarch"],
            "PS2":     ["pcsx2","retroarch"],
            "PS3":     ["rpcs3","retroarch"],
            "PSP":     ["ppsspp","retroarch"],
            "NES":     ["fceux","mesen","nestopia","retroarch"],
            "SNES":    ["snes9x","bsnes","retroarch"],
            "N64":     ["project64","mupen","retroarch"],
            "GB":      ["mgba","vba","retroarch"],
            "GBC":     ["mgba","vba","retroarch"],
            "GBA":     ["mgba","vba","visualboy","retroarch"],
            "NDS":     ["desmume","melon","retroarch"],
            "GCN":     ["dolphin","retroarch"],
            "WII":     ["dolphin","retroarch"],
            "MD":      ["fusion","retroarch","gens","blast"],
            "SATURN":  ["mednafen","ssf","retroarch"],
            "DC":      ["redream","flycast","demul","retroarch"],
            "MAME":    ["mame","retroarch"],
        }
        hints = _PLAT_EXE_HINTS.get(plat_upper, [])
        if hints:
            stand = [e for e in stand
                     if any(h in e["exe"].lower() for h in hints)]
        return ra + stand


class OrphanDialog(tk.Toplevel):
    """Prosty dialog TAK/NIE — brakujące gry po skanie.

    Pokazuje listę osieroconych wpisów (LNK bez gry lub ROM bez pliku)
    i pyta jednym przyciskiem czy usunąć wszystkie naraz.
    Dla każdego usuwanego wpisu: LNK usunięty, grafiki z cache wyczyszczone,
    stub zachowany (ID + URL-e do ponownego pobrania ikon gdy gra wróci).
    """
    def __init__(self, parent, orphans: list[dict]):
        super().__init__(parent)
        self.title("Brakujące gry")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.grab_set()
        self.result: list[dict] = []   # wypełniane przez _yes(); puste = Nie
        self._orphans = orphans

        # ── Nagłówek ─────────────────────────────────────────────────────
        n = len(orphans)
        hdr = tk.Frame(self, bg=C["bg"])
        hdr.pack(fill="x", padx=14, pady=(14, 4))
        tk.Label(hdr,
                 text=f"Znaleziono {n} {'wpis' if n == 1 else 'wpisy' if n < 5 else 'wpisów'}"
                      " bez pliku lub gry",
                 bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(hdr,
                 text="Usunąć skróty (.lnk) i grafiki z cache?\n""Stub z ID gry zostanie zachowany \u2014 przy ponownym dodaniu\n""ikona zostanie przywrócona automatycznie.",
                 bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 8), justify="left").pack(anchor="w", pady=(4, 0))

        # ── Przyciski ─────────────────────────────────────────────────────
        # FIX v7.4: przyciski pakowane PRZED listą, side="bottom" — przy
        # sztywnej geometrii pack() wypychał ostatnio spakowane widgety
        # (czyli przyciski) poza dolną krawędź okna i dialog wyglądał jak
        # "sama lista bez pytania".
        bot = tk.Frame(self, bg=C["bg"])
        bot.pack(side="bottom", fill="x", padx=14, pady=(2, 12))
        tk.Button(bot,
                  text=f"Tak, usuń {n} {'wpis' if n==1 else 'wpisy' if n<5 else 'wpisów'}",
                  command=self._yes,
                  bg=C["red"], fg="white",
                  relief="flat", padx=14, pady=6,
                  font=("Segoe UI", 9, "bold"),
                  cursor="hand2").pack(side="right", padx=(4, 0))
        tk.Button(bot, text="Nie, zostaw",
                  command=self.destroy,
                  bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=10, pady=6,
                  cursor="hand2").pack(side="right")

        # ── Lista (tylko do wglądu, bez checkboxów) ───────────────────────
        wrap = tk.Frame(self, bg=C["bg2"],
                        highlightthickness=1, highlightbackground=C["bg3"])
        wrap.pack(fill="both", expand=True, padx=14, pady=(8, 6))
        canvas = tk.Canvas(wrap, bg=C["bg2"], highlightthickness=0,
                           height=min(300, n * 28 + 16))
        vsb = tk.Scrollbar(wrap, orient="vertical", command=canvas.yview,
                           bg=C["bg3"], width=8, relief="flat")
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=C["bg2"])
        cw = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(cw, width=e.width))
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        SRC_COL = {"steam": C["grn"], "rom": C["orn"],
                   "gog": C["acc"], "epic": C["yel"]}
        for i, g in enumerate(orphans):
            bg = C["bg2"] if i % 2 == 0 else C["bg"]
            row = tk.Frame(inner, bg=bg)
            row.pack(fill="x", padx=4, pady=1)
            s = g.get("source", "extra")
            tk.Label(row, text=f"[{s[:5].upper()}]",
                     bg=bg, fg=SRC_COL.get(s, C["fg2"]),
                     font=("Segoe UI", 8, "bold"), width=8).pack(side="left")
            tk.Label(row, text=g.get("name", "?"),
                     bg=bg, fg=C["fg"],
                     font=("Segoe UI", 9), anchor="w",
                     width=30).pack(side="left")
            # powód — ścieżka której brak lub osierocony LNK
            stale = g.get("_stale_lnk")
            reason = (f"skrót bez gry: …{stale[-55:]}"
                      if stale else
                      (g.get("rom_path") or g.get("launch_exe")
                       or g.get("game_dir") or ""))
            if reason:
                tk.Label(row, text=str(reason)[:70],
                         bg=bg, fg=C["red"],
                         font=("Segoe UI", 7, "italic")).pack(side="left", padx=4)

        # ── Geometria ─────────────────────────────────────────────────────
        # FIX v7.4: wyższe okno + minsize, żeby przyciski nigdy nie znikały
        self.geometry("680x480")
        self.minsize(560, 300)
        self.update_idletasks()
        pw = parent.winfo_x() + (parent.winfo_width() - 680) // 2
        ph = parent.winfo_y() + (parent.winfo_height() - 480) // 2
        self.geometry(f"+{pw}+{ph}")
        self.wait_window(self)

    def _yes(self):
        self.result = list(self._orphans)   # usuń wszystkie
        self.destroy()


# ---------------------------------------------------------------------------
# v8.0 (wariant 2): dymki podpowiedzi — tkinter nie ma wbudowanych
# ---------------------------------------------------------------------------
class Tooltip:
    """Prosty tooltip: pojawia się po 500 ms nad widgetem, znika przy
    opuszczeniu. Tekst pisany prostym językiem — dla osób nietechnicznych."""

    def __init__(self, widget, text: str, delay: int = 500):
        self.widget, self.text, self.delay = widget, text, delay
        self._tip = None
        self._after = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _e=None):
        self._cancel()
        self._after = self.widget.after(self.delay, self._show)

    def _cancel(self):
        if self._after:
            try:
                self.widget.after_cancel(self._after)
            except Exception:
                pass
            self._after = None

    def _show(self):
        if self._tip or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 10
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
            self._tip = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            tk.Label(tw, text=self.text, justify="left", wraplength=340,
                     bg=C["bg3"], fg=C["fg"], font=("Segoe UI", 9),
                     relief="solid", borderwidth=1, padx=8, pady=5).pack()
        except Exception:
            self._tip = None

    def _hide(self, _e=None):
        self._cancel()
        if self._tip:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config_data = load_config()
        # Inicjalizacja zstd (dla stubów) — auto-install lub gzip fallback
        if not _init_zstd():
            pip_cmd = f"{sys.executable} -m pip install zstandard"
            print(f"[zstd] niedostępny — użyto gzip. Lepszy: {pip_cmd}")
        self.title("Steam Icon Shortcut Creator v3")
        self.geometry(self.config_data.get("window_geometry", "1400x900"))
        self.minsize(1100, 700)
        self.configure(bg=C["bg"])

        # Auto-detect Steam jeśli domyślna ścieżka nie istnieje
        steam_exe = self.config_data.get("steam_exe", DEFAULT_STEAM_EXE)
        if not Path(steam_exe).exists():
            detected = detect_steam_exe()
            if detected:
                steam_exe = detected
                self.config_data["steam_exe"] = detected

        self.v_exe    = tk.StringVar(value=steam_exe)
        self.v_extra  = tk.StringVar(value=self.config_data.get("extra_dir", DEFAULT_EXTRA_DIR))
        self.v_search        = tk.StringVar(value="")
        self.v_status        = tk.StringVar(value="Gotowy.")
        self.v_prog          = tk.DoubleVar(value=0)
        self.v_filter        = tk.StringVar(value="all")
        self.v_source_filter = tk.StringVar(value="all")  # "all"|"pc"|rom sys name
        # ROM: wybrany system z combobox
        self.v_rom_system = tk.StringVar(value=self._rom_default_system())

        self.steam_lib_dirs  = list(self.config_data.get("steam_lib_dirs", []))
        self.extra_dirs_list = list(self.config_data.get("extra_dirs_list", []))
        self.games: list[dict] = []
        self._check_vars: list[tk.BooleanVar] = []   # (legacy, nieużywane – stan trzyma g["enabled"])
        # v8.1 – wirtualizacja listy: pula wierszy odtwarzana przy przewijaniu
        self._row_pool: list[dict] = []   # {frame,cb,var,badge,name,bound_gi}
        self._vis: list[int] = []         # indeksy gier widocznych wg filtra (posortowane)
        self._row_h: int = 22             # stała wysokość wiersza (px) – potrzebna do obliczeń
        self._relayout_job = None
        self.cur_idx: int | None = None
        self._q: queue.Queue = queue.Queue()
        self._refs: list = []
        self._scanning = False
        self._rebuild_job = None
        self._save_job    = None
        self._stop = threading.Event()

        # Cache i LINKS zawsze obok skryptu
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        LINKS_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        self._asset_store   = AssetStore(CACHE_DIR)
        # v8.2: jednorazowa naprawa cache — odbuduj wpisy `assets` z plików na
        # dysku (desync plik↔baza po resecie). W tle, żeby nie blokować startu.
        if not self.config_data.get("assets_reconciled_v82"):
            def _reconcile_once():
                try:
                    n, g = self._asset_store.reconcile_from_disk()
                    print(f"[Cache] odzyskano {n} grafik dla {g} gier z dysku")
                except Exception as _ex:
                    print(f"[Cache] reconcile nieudany: {_ex}")
                self.config_data["assets_reconciled_v82"] = True
                try:
                    save_config(self.config_data)
                except Exception:
                    pass
            threading.Thread(target=_reconcile_once, daemon=True).start()
        self._extra_sources = ExtraArtSources(self.config_data)
        self._sync_mgr = None
        self._syncing = False
        self._art_pool = None        # FIX v7.2: pula wątków auto-pobierania grafik
        self._steam_thumb_pool = None  # pula wątków miniatur Steam (poza UI)
        # Stan paginacji plakatów (square grids)
        self._poster_page: int = 0          # aktualna strona (0-indexed)
        self._poster_game_key: str = ""     # klucz gry dla której ładujemy plakaty
        self._poster_loading: bool = False  # blokada przed podwójnym kliknięciem

        self._ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        for var in (self.v_exe, self.v_extra):
            var.trace_add("write", self._save_settings_debounced)
        self.v_search.trace_add("write",        lambda *_: self._rebuild_list())
        self.v_filter.trace_add("write",        lambda *_: self._rebuild_list())
        self.v_source_filter.trace_add("write", lambda *_: self._rebuild_list())
        self._tick()

    # -------- Config helpers (bez profili) --------
    @staticmethod
    def _candidate_stable_key(c: dict) -> str:
        """Zwróć stabilny klucz dla kandydata ikony — przeżywa rescan i restart.

        FIX v7: priorytet remote_asset_id (jest zapisywany w SQLite i obecny
        zarówno w kandydatach 'na żywo' jak i odtworzonych z cache).
        Wcześniej priorytet miał URL, którego kandydaci z cache nie mają —
        przez co wybór ikony nie przeżywał restartu.
        """
        return (str(c.get("remote_asset_id") or "")
                or c.get("url")
                or c.get("path", "")
                or c.get("local_path", "")
                or f"{c.get('type','')}/{c.get('label','')}").strip()

    @staticmethod
    def _candidate_matches_key(c: dict, sk: str) -> bool:
        """FIX v7: tolerancyjne dopasowanie zapisanego klucza ikony.

        Porównuje ze wszystkimi identyfikatorami kandydata (remote_asset_id,
        url, path, local_path) — dzięki temu stare configi z kluczami-URL
        nadal działają po zmianie priorytetu w _candidate_stable_key.
        """
        if not sk:
            return False
        return sk in (
            str(c.get("remote_asset_id") or ""),
            c.get("url") or "",
            c.get("path") or "",
            c.get("local_path") or "",
        )

    def _game_key(self, g: dict) -> str:
        """Unikalny klucz identyfikujący grę — STABILNY między sesjami.

        FIX: dla ROM-ów NIE używamy `uid` (=`{plat}_{idx}`, pozycja w skanie!)
        ani `rom_path` (zmienia się: iso→lnk, Disc 1↔Disc 2, .m3u). To gubiło
        powiązania ikon/grafik przy każdej zmianie kolejności czy pliku. Klucz
        ROM = platforma + znormalizowana nazwa gry (bez regionu/dysku) — ta sama
        gra ma ten sam klucz niezależnie od pozycji i konkretnego pliku."""
        if g.get("source") == "rom":
            plat = (g.get("rom_platform") or "").strip().lower()
            nm = self._norm_rom_stem(
                g.get("name") or Path(g.get("rom_path", "")).stem)
            return f"rom::{plat}::{nm}"
        return str(
            g.get("appid")
            or g.get("epic_app_name")
            or g.get("gog_id")
            or g.get("game_dir")
            or g.get("uid")
            or g.get("name", "")
        )

    def _async_key(self, g: dict) -> str:
        """Klucz do dopasowania wyników WĄTKÓW (plakaty/art) do gry w TEJ sesji.

        MUSI być spójny między producentem (wątek) a konsumentem (_tick). Używa
        tożsamości żywego obiektu (`_poster_key`/`uid`), a dla nie-ROM spada na
        `_game_key`. UWAGA: to NIE jest `_game_key` — ten jest trwały (po nazwie)
        i służy do ZAPISU; async_key jest sesyjny (po pozycji) i służy do
        DOPASOWANIA w locie. Mieszanie ich gubiło wyniki plakatów/IGDB/TGDB."""
        return str(g.get("_poster_key") or g.get("uid") or self._game_key(g))

    def _legacy_game_keys(self, g: dict) -> list:
        """Stare (niestabilne) klucze gry — do JEDNORAZOWEJ migracji zapisów.

        Dawniej ROM-y kluczowano po `uid` = `{plat}_{idx}` (pozycja w skanie).
        Gdy kolejność się nie zmieniła (np. PS2), pozwala odzyskać wybór ikony."""
        out = []
        if g.get("source") == "rom" and g.get("uid"):
            out.append(str(g["uid"]))
        return out

    def _cfg_map_migrate(self, mapping: dict, g: dict):
        """Pobierz wartość dla gry, migrując ze starego klucza pozycyjnego na
        nowy stabilny (przenosi wpis pod nowy klucz). None gdy brak."""
        nk = self._game_key(g)
        if nk in mapping:
            return mapping[nk]
        for lk in self._legacy_game_keys(g):
            if lk != nk and lk in mapping:
                mapping[nk] = mapping.pop(lk)
                return mapping[nk]
        return None

    def _rom_default_system(self) -> str:
        """Nazwa pierwszego skonfigurowanego systemu ROM lub ''."""
        systems = (self.config_data
                   .get("rom_support", {})
                   .get("systems", []))
        return systems[0]["name"] if systems else ""

    def _rom_systems(self) -> list[dict]:
        """Lista systemów ROM z konfiguracji."""
        return (self.config_data
                .get("rom_support", {})
                .get("systems", []))

    def _save_settings_debounced(self, *_):
        """Debounce 500 ms — nie zapisuje JSON przy każdym znaku."""
        if hasattr(self, "_save_job") and self._save_job:
            try:
                self.after_cancel(self._save_job)
            except Exception:
                pass
        self._save_job = self.after(500, self._save_settings)

    def _save_settings(self):
        if self.games:
            self.config_data["enabled_keys"] = [
                self._game_key(g) for g in self.games if g.get("enabled")
            ]
            self.config_data["selected_indices"] = {
                self._game_key(g): g.get("selected_idx")
                for g in self.games if g.get("selected_idx") is not None
            }
            # Aktualizuj selected_icon_keys dla gier z załadowanymi kandydatami
            icon_keys = self.config_data.setdefault("selected_icon_keys", {})
            for g in self.games:
                sel = g.get("selected_idx")
                cands = g.get("candidates", [])
                if sel is not None and 0 <= sel < len(cands):
                    sk = self._candidate_stable_key(cands[sel])
                    if sk:
                        icon_keys[self._game_key(g)] = sk
            # Grafiki Steam (steam_art = {typ: url}) — trwałe, po game_key, tak
            # jak wybór ikon .lnk. Bez tego wybór znika po skanie/restarcie.
            art_map = self.config_data.setdefault("steam_art_by_key", {})
            for g in self.games:
                gk = self._game_key(g)
                sa = g.get("steam_art")
                if sa:
                    art_map[gk] = sa
                elif gk in art_map:
                    art_map.pop(gk, None)   # wyczyszczone w tej sesji
        self.config_data.update({
            "window_geometry":  self.geometry(),
            "steam_exe":        self.v_exe.get(),
            "extra_dir":        self.v_extra.get(),
            "steam_lib_dirs":   list(self.steam_lib_dirs),
            "extra_dirs_list":  list(self.extra_dirs_list),
            "selected_game_key": self._current_game_key(),
        })
        save_config(self.config_data)

    def _persist_now(self, game: dict) -> None:
        """Zapis NATYCHMIAST po kliknięciu w grafikę (bez 500 ms debounce).

        Aktualizuje tylko wybór TEJ gry (ikona .lnk + grafiki Steam) i od razu
        zapisuje config — dzięki temu po zamknięciu programu można dokończyć
        wybór, a nie zaczynać od nowa. Lekkie: nie przebudowuje map dla całej
        kolekcji (to robi _save_settings przy innych zdarzeniach i na zamknięciu).
        """
        if not game:
            return
        gk = self._game_key(game)
        # grafiki Steam (steam_art = {typ: url})
        art_map = self.config_data.setdefault("steam_art_by_key", {})
        sa = game.get("steam_art")
        if sa:
            art_map[gk] = sa
        elif gk in art_map:
            art_map.pop(gk, None)
        # wybór ikony .lnk (stabilny klucz)
        sel = game.get("selected_idx")
        cands = game.get("candidates", [])
        if sel is not None and 0 <= sel < len(cands):
            sk = self._candidate_stable_key(cands[sel])
            if sk:
                self.config_data.setdefault("selected_icon_keys", {})[gk] = sk
        try:
            save_config(self.config_data)
        except Exception as ex:
            print(f"[persist] błąd zapisu: {ex}")

    def _current_game_key(self):
        if self.cur_idx is None or self.cur_idx >= len(self.games):
            return None
        return self._game_key(self.games[self.cur_idx])

    def _on_close(self):
        self._save_settings()
        self._stop.set()
        if self._art_pool is not None:  # FIX v7.2
            try:
                self._art_pool.shutdown(wait=False, cancel_futures=True)
            except Exception:
                pass
        if self._steam_thumb_pool is not None:
            try:
                self._steam_thumb_pool.shutdown(wait=False, cancel_futures=True)
            except Exception:
                pass
        if self._sync_mgr is not None: self._sync_mgr.stop()
        try: self._asset_store.close()
        except Exception: pass
        self.destroy()

    def _restore_steam_art(self, g: dict) -> None:
        """Przywróć zapisane grafiki Steam (steam_art) dla gry z configu.

        Symetrycznie do wyboru ikon .lnk — trzymane po game_key w
        steam_art_by_key, przeżywa skan i restart. Nie nadpisuje, jeśli w tej
        sesji już coś ustawiono."""
        if g.get("steam_art"):
            return
        sa = self._cfg_map_migrate(
            self.config_data.setdefault("steam_art_by_key", {}), g)
        if sa:
            g["steam_art"] = dict(sa)

    def _restore_selected_icon(self, g: dict) -> bool:
        """FIX v7: przywróć zapisany wybór ikony dla gry z załadowanymi
        kandydatami. Zwraca True jeśli się udało.

        Używane przez _scan_thread PO załadowaniu kandydatów — wcześniej
        skan bezwarunkowo ustawiał best_idx(), a pierwszy _save_settings()
        nadpisywał zapisany wybór użytkownika.
        """
        self._restore_steam_art(g)   # grafiki Steam — przy każdej ścieżce skanu
        key_map = self.config_data.setdefault("selected_icon_keys", {})
        saved_sk = self._cfg_map_migrate(key_map, g)  # nowy klucz + migracja starego
        if not saved_sk:
            return False
        for i, c in enumerate(g.get("candidates", [])):
            if self._candidate_matches_key(c, saved_sk):
                g["selected_idx"] = i
                return True
        return False

    def _apply_saved_state_to_games(self):
        """Przywróć zaznaczenia gier i wybrane ikony z configu.

        Używa selected_icon_keys (stabilne klucze) jako primary,
        selected_indices (pozycja) tylko jako fallback gdy brak stable key.
        """
        enabled   = set(self.config_data.get("enabled_keys", []))
        sel_map   = self.config_data.setdefault("selected_indices", {})
        key_map   = self.config_data.setdefault("selected_icon_keys", {})
        has_snap  = bool(enabled) or bool(sel_map) or bool(key_map)
        for g in self.games:
            k     = self._game_key(g)
            cands = g.get("candidates", [])
            self._restore_steam_art(g)   # grafiki Steam (trwałe, po game_key)
            if has_snap:
                # nowy klucz LUB stary pozycyjny (migracja stanu enabled)
                g["enabled"] = (k in enabled
                                or any(lk in enabled
                                       for lk in self._legacy_game_keys(g)))
            # 1. Stable key — preferowane (FIX v7: tolerancyjne dopasowanie) +
            #    migracja starego klucza pozycyjnego na nowy stabilny
            saved_sk = self._cfg_map_migrate(key_map, g)
            sel_idx = self._cfg_map_migrate(sel_map, g)
            if saved_sk and cands:
                for i, c in enumerate(cands):
                    if self._candidate_matches_key(c, saved_sk):
                        g["selected_idx"] = i
                        break
            # 2. Fallback: stary indeks
            elif sel_idx is not None and cands and sel_idx < len(cands):
                g["selected_idx"] = sel_idx

    # -------- Scanner/IconManager/Creator factory --------
    def _scanner(self) -> SteamScanner:
        api = self.config_data.get("api_keys", {})
        return SteamScanner(
            steam_exe=self.v_exe.get(),
            extra_lib_dirs=self.steam_lib_dirs,
            use_libraryfolders_vdf=self.config_data.get("use_libraryfolders_vdf", True),
            api_key=api.get("steam_api_key"),
            steam_id64=api.get("steam_id64"),
            use_web_api=self.config_data.get("use_steam_web_api", True),
        )

    def _icons(self) -> IconManager:
        api = self.config_data.get("api_keys", {})
        flt = self.config_data.get("filters", {})
        return IconManager(
            sgdb_key=api.get("sgdb_key", ""),
            min_size=flt.get("min_icon_size", DEFAULT_MIN_SIZE),
            preferred_type=flt.get("preferred_icon_type", "any"),
            exe_skip_regex=flt.get("exe_skip_regex", DEFAULT_EXE_SKIP_REGEX),
            shape_filter=flt.get("icon_shape", "any"),
            max_icons=flt.get("max_icons_per_game", DEFAULT_MAX_ICONS),
        )

    def _sync_manager(self):
        key = self.config_data.get("api_keys", {}).get("sgdb_key", "").strip()
        if self._sync_mgr is None or self._sync_mgr.sgdb_key != key:
            self._sync_mgr = SyncManager(self._asset_store, key,
                max_workers=int(self.config_data.get("sync_workers", 6)))
        return self._sync_mgr

    def _creator(self) -> ShortcutCreator:
        return ShortcutCreator(self.v_exe.get())

    # -------- UI builder --------
    def _ui(self):
        # ── PASEK GÓRNY ──────────────────────────────────────────────────────
        top = tk.Frame(self, bg=C["bg2"], pady=8, padx=10)
        top.pack(fill="x")
        self._entry(top, "Steam.exe:", self.v_exe)
        tk.Button(top, text="⚙ Ustawienia", command=self._open_settings,
                  bg=C["bg3"], fg=C["acc"], font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, pady=4, cursor="hand2").pack(side="right", padx=(6, 0))
        tk.Button(top, text="🔍 Auto-wykryj Steam", command=self._auto_detect_steam,
                  bg=C["bg3"], fg=C["grn"], font=("Segoe UI", 9),
                  relief="flat", padx=10, pady=4, cursor="hand2").pack(side="right", padx=(6, 0))

        # Info: ścieżki katalogów (readonly)
        top_paths = tk.Frame(self, bg=C["bg2"], pady=2, padx=10)
        top_paths.pack(fill="x")
        def _open_dir(path):
            try:
                import subprocess; subprocess.Popen(["explorer", str(path)])
            except Exception: pass
        for lbl_text, path in [("📁 Cache:", CACHE_DIR), ("📁 Linki:", LINKS_DIR),
                                ("📊 Raporty:", REPORTS_DIR)]:
            tk.Label(top_paths, text=lbl_text, bg=C["bg2"], fg=C["fg2"],
                     font=("Segoe UI", 8)).pack(side="left")
            # Bindujemy do konkretnej etykiety — NIE bind_all (bind_all odpala się
            # na każdym kliknięciu i wywołuje TclError na widgetach bez opcji -text)
            path_lbl = tk.Label(top_paths, text=str(path), bg=C["bg2"], fg=C["acc"],
                                font=("Segoe UI", 8), cursor="hand2")
            path_lbl.pack(side="left", padx=(2, 12))
            path_lbl.bind("<Button-1>", lambda e, p=path: _open_dir(p))

        top2 = tk.Frame(self, bg=C["bg2"], pady=4, padx=10)
        top2.pack(fill="x")
        self._entry(top2, "Extra Dir (non-Steam):", self.v_extra, True, width=40)
        tk.Label(top2, text="Każdy podkatalog = jedna gra  →  LINKS/PC/",
                 bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 8, "italic")).pack(side="left", padx=6)

        # ── PASEK NARZĘDZI ────────────────────────────────────────────────────
        top3 = tk.Frame(self, bg=C["bg2"], pady=4, padx=10)
        top3.pack(fill="x")
        tk.Button(top3, text="Steam biblioteki…", command=self._edit_steam_libs,
                  bg=C["bg3"], fg=C["grn"], relief="flat", padx=10, pady=3,
                  cursor="hand2").pack(side="left", padx=(0, 4))
        tk.Button(top3, text="Extra katalogi…", command=self._edit_extra_dirs,
                  bg=C["bg3"], fg=C["ext"], relief="flat", padx=10, pady=3,
                  cursor="hand2").pack(side="left", padx=4)

        # ROM: ustawienia + dropdown systemu + przycisk
        tk.Frame(top3, bg=C["fg2"], width=1).pack(side="left", fill="y", padx=(10, 6))
        tk.Button(top3, text="⚙ ROMy", command=self._open_rom_settings,
                  bg=C["bg3"], fg=C["orn"], relief="flat", padx=10, pady=3,
                  cursor="hand2").pack(side="left", padx=(0, 4))
        self._rom_cb = ttk.Combobox(top3, textvariable=self.v_rom_system,
                                    width=14, state="readonly")
        self._refresh_rom_combobox()
        # FIX v7.6: migracja starych skrótów PC do LINKS/PC (raz, w tle)
        self.after(600, self._migrate_legacy_pc_links)
        # Diff-skan przy starcie jeśli włączony
        if self.config_data.get("scan_on_startup"):
            self.after(1200, self._startup_diff_scan)
        # v8.0: przywróć tryb prosty jeśli był aktywny przy zamknięciu
        if self.config_data.get("ui_mode") == "simple":
            self.after(300, self._enter_simple_mode)
        self._rom_cb.pack(side="left", padx=(0, 4))
        tk.Button(top3, text="SKANUJ ROM", command=self._rom_scan_click,
                  bg=C["ext"], fg=C["bg"], font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, pady=3, cursor="hand2").pack(side="left")
        tk.Frame(top3, bg=C["bg2"], width=6).pack(side="left")
        tk.Button(top3, text="🎵 M3U", command=self._open_m3u_generator,
                  bg=C["bg3"], fg=C["yel"], font=("Segoe UI", 9),
                  relief="flat", padx=8, pady=3, cursor="hand2").pack(side="left")
        tk.Frame(top3, bg=C["bg2"], width=6).pack(side="left")
        tk.Button(top3, text="📤 → Steam", command=self._open_steam_export,
                  bg=C["bg3"], fg=C["grn"], font=("Segoe UI", 9),
                  relief="flat", padx=8, pady=3, cursor="hand2").pack(side="left")
        tk.Frame(top3, bg=C["bg2"], width=6).pack(side="left")
        tk.Button(top3, text="📥 Import LNK", command=self._import_lnk,
                  bg=C["bg3"], fg=C["fg2"], font=("Segoe UI", 9),
                  relief="flat", padx=8, pady=3, cursor="hand2").pack(side="left")
        tk.Frame(top3, bg=C["bg2"], width=6).pack(side="left")
        tk.Button(top3, text="📊 Statystyki", command=self._open_stats,
                  bg=C["bg3"], fg=C["acc"], font=("Segoe UI", 9),
                  relief="flat", padx=8, pady=3, cursor="hand2").pack(side="left")
        tk.Frame(top3, bg=C["bg2"], width=6).pack(side="left")
        tk.Button(top3, text="🎮 Playnite", command=self._open_playnite_export,
                  bg=C["bg3"], fg=C["yel"], font=("Segoe UI", 9),
                  relief="flat", padx=8, pady=3, cursor="hand2").pack(side="left")

        # Przyciski akcji
        btn_row = tk.Frame(self, bg=C["bg2"], pady=6, padx=10)
        btn_row.pack(fill="x")

        # v8.0 (wariant 2): toolbar pogrupowany w nazwane sekcje + dymki
        # podpowiedzi prostym językiem; "DRY RUN" → "PODGLĄD ZMIAN".
        def _sec(label: str):
            tk.Label(btn_row, text=label, bg=C["bg2"], fg=C["fg2"],
                     font=("Segoe UI", 7)).pack(side="left", padx=(2, 3))

        def _sep():
            tk.Frame(btn_row, bg=C["bg3"], width=1).pack(
                side="left", fill="y", padx=8, pady=2)

        _sec("BIBLIOTEKA")
        self._btn_scan = self._btn(btn_row, "SKANUJ", self._scan_click, C["acc"])
        self._btn_scan.pack(side="left", padx=4)
        Tooltip(self._btn_scan,
                "Wyszukuje zainstalowane gry (Steam, GOG, Epic, katalogi "
                "Extra) i pobiera dla nich obrazki ikon.")

        _sep()
        _sec("TWORZENIE")
        _b_dry = self._btn(btn_row, "PODGLĄD ZMIAN", self._dry_run_click, C["yel"])
        _b_dry.pack(side="left", padx=4)
        Tooltip(_b_dry,
                "Pokazuje listę skrótów, które POWSTANĄ po kliknięciu "
                "STWÓRZ SKRÓTY — nic jeszcze nie zapisuje na dysku.")
        _b_create = self._btn(btn_row, "STWÓRZ SKRÓTY", self._create_click, C["grn"])
        _b_create.pack(side="left", padx=4)
        Tooltip(_b_create,
                "Tworzy skróty z ikonami w folderze LINKS dla wszystkich "
                "zaznaczonych gier.")

        _sep()
        _sec("NARZĘDZIA")
        _b_exp = self._btn(btn_row, "EKSPORT…", self._export_click, C["ext"])
        _b_exp.pack(side="left", padx=4)
        Tooltip(_b_exp, "Zapisuje listę gier do pliku (CSV/JSON).")
        _b_sync = tk.Button(btn_row, text="⬇ SYNC CACHE",
            command=self._sync_cache_click, bg=C["bg3"], fg=C["ext"],
            font=("Segoe UI",9), relief="flat", padx=8, pady=5, cursor="hand2")
        _b_sync.pack(side="left", padx=2)
        Tooltip(_b_sync,
                "Dociąga z internetu brakujące obrazki dla całej "
                "biblioteki (do przeglądania bez sieci).")

        # v7.9 (cache-diet): jednorazowe odchudzenie istniejącego cache —
        # nie-wybrane assety → miniatury 256px WEBP, wybrane → pełny WEBP.
        _b_compact = tk.Button(btn_row, text="🧹 KOMPAKTUJ",
            command=self._compact_cache_click, bg=C["bg3"], fg=C["yel"],
            font=("Segoe UI",9), relief="flat", padx=8, pady=5, cursor="hand2")
        _b_compact.pack(side="left", padx=2)
        Tooltip(_b_compact,
                "Zmniejsza miejsce zajmowane przez zapisane obrazki "
                "(pomniejsza nieużywane do miniatur).")

        # v8.0 (wariant 1): przełącznik trybu prostego — z prawej strony
        _b_simple = tk.Button(btn_row, text="🙂 TRYB PROSTY",
            command=self._enter_simple_mode, bg=C["bg3"], fg=C["grn"],
            font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=5,
            cursor="hand2")
        _b_simple.pack(side="right", padx=2)
        Tooltip(_b_simple,
                "Uproszczony widok w 3 krokach — dla osób, które chcą "
                "tylko zrobić skróty bez wnikania w szczegóły.")

        # Pasek postępu + status
        pb = tk.Frame(self, bg=C["bg2"], pady=3, padx=10)
        pb.pack(fill="x")
        tk.Label(pb, textvariable=self.v_status, bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 8), anchor="w").pack(side="left", fill="x", expand=True)
        self._lbl_prog = tk.Label(pb, text="", bg=C["bg2"], fg=C["fg2"],
                                  font=("Segoe UI", 8))
        self._lbl_prog.pack(side="right")
        sty = ttk.Style(self)
        sty.theme_use("default")
        sty.configure("A.Horizontal.TProgressbar", troughcolor=C["bg3"], background=C["acc"],
                      bordercolor=C["bg2"], lightcolor=C["acc"], darkcolor=C["acc"], thickness=6)

        # ── Treeview (tabele w całej aplikacji) ───────────────────────────────
        sty.configure("Treeview",
                      background=C["bg2"],
                      foreground=C["fg"],
                      fieldbackground=C["bg2"],
                      bordercolor=C["bg3"],
                      rowheight=22,
                      font=("Segoe UI", 9))
        sty.configure("Treeview.Heading",
                      background=C["bg3"],
                      foreground=C["acc"],
                      relief="flat",
                      font=("Segoe UI", 8, "bold"))
        # Zaznaczenie wiersza — jasny tekst na wyraźnym tle
        sty.map("Treeview",
                background=[("selected", C["acc"])],
                foreground=[("selected", C["bg"])])
        sty.map("Treeview.Heading",
                background=[("active", C["bg2"])])

        # ── Combobox ──────────────────────────────────────────────────────────
        sty.configure("TCombobox",
                      selectbackground=C["acc"],
                      selectforeground=C["bg"],
                      fieldbackground=C["bg3"],
                      background=C["bg3"],
                      foreground=C["fg"],
                      arrowcolor=C["acc"],
                      bordercolor=C["bg3"],
                      insertcolor=C["fg"])
        sty.map("TCombobox",
                fieldbackground=[("readonly", C["bg3"]),
                                 ("disabled", C["bg2"])],
                foreground=[("readonly",  C["fg"]),
                            ("disabled",  C["fg2"])],
                selectbackground=[("readonly", C["acc"])],
                selectforeground=[("readonly", C["bg"])])

        # ── Notebook (zakładki w Verify dialog) ───────────────────────────────
        sty.configure("TNotebook",
                      background=C["bg"],
                      bordercolor=C["bg3"])
        sty.configure("TNotebook.Tab",
                      background=C["bg3"],
                      foreground=C["fg2"],
                      padding=[10, 4],
                      font=("Segoe UI", 9))
        sty.map("TNotebook.Tab",
                background=[("selected", C["bg"]),
                             ("active",  C["bg2"])],
                foreground=[("selected", C["acc"]),
                             ("active",  C["fg"])])

        # ── Scrollbar ─────────────────────────────────────────────────────────
        sty.configure("TScrollbar",
                      background=C["bg3"],
                      troughcolor=C["bg2"],
                      arrowcolor=C["fg2"],
                      bordercolor=C["bg2"])
        ttk.Progressbar(pb, variable=self.v_prog, length=380, mode="determinate",
                        style="A.Horizontal.TProgressbar").pack(side="right", padx=6)

        # GŁÓWNE - lewy panel z listą, prawy z detalami
        main = tk.Frame(self, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=8, pady=6)

        lf = tk.Frame(main, bg=C["bg2"], width=330)
        lf.pack(side="left", fill="y", padx=(0, 6))
        lf.pack_propagate(False)
        # ── Nagłówek lewego panelu ────────────────────────────────────────────
        lf_head = tk.Frame(lf, bg=C["bg2"])
        lf_head.pack(fill="x", padx=6, pady=(6, 2))
        tk.Label(lf_head, text="BIBLIOTEKA", bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=2)
        self._lbl_game_count = tk.Label(lf_head, text="", bg=C["bg2"], fg=C["fg2"],
                                        font=("Segoe UI", 7))
        self._lbl_game_count.pack(side="right", padx=4)

        # ── Wyszukiwarka ──────────────────────────────────────────────────────
        search_bar = tk.Frame(lf, bg=C["bg2"])
        search_bar.pack(fill="x", padx=6, pady=(2, 3))
        tk.Label(search_bar, text="🔎", bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 2))
        tk.Entry(search_bar, textvariable=self.v_search,
                 bg=C["bg3"], fg=C["fg"], insertbackground="white",
                 relief="flat", font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True)
        tk.Button(search_bar, text="✕",
                  command=lambda: self.v_search.set(""),
                  bg=C["bg2"], fg=C["fg2"], relief="flat",
                  font=("Segoe UI", 8), padx=2, cursor="hand2").pack(side="left")

        # ── Pasek platform: PC | ROM-y ────────────────────────────────────────
        plat_outer = tk.Frame(lf, bg=C["bg"])
        plat_outer.pack(fill="x", padx=0, pady=(0, 0))

        # Wiersz 1: PC / ROM-y / wszystkie
        plat_row1 = tk.Frame(plat_outer, bg=C["bg3"])
        plat_row1.pack(fill="x")

        self._src_btns: dict[str, tk.Label] = {}

        def _src_btn(parent, key: str, label: str, color: str):
            lbl = tk.Label(parent, text=label,
                           bg=C["bg3"], fg=C["fg2"],
                           font=("Segoe UI", 8, "bold"),
                           padx=10, pady=5, cursor="hand2")
            lbl.pack(side="left")
            lbl.bind("<Button-1>", lambda e, k=key: self._set_source_filter(k))
            self._src_btns[key] = lbl
            return lbl

        _src_btn(plat_row1, "all", "Wszystkie", C["fg"])
        _src_btn(plat_row1, "pc",  "🖥 PC",     C["grn"])

        # ROM-y: dynamiczny wiersz z systemami
        self._plat_row2 = tk.Frame(plat_outer, bg=C["bg"])
        self._plat_row2.pack(fill="x")
        self._rom_src_btns: dict[str, tk.Label] = {}
        self._rebuild_platform_bar()

        # ── Filtr jakości ─────────────────────────────────────────────────────
        filter_bar = tk.Frame(lf, bg=C["bg2"])
        filter_bar.pack(fill="x", padx=6, pady=(3, 1))
        for val, label, color in [
            ("all",           "Wszystkie",       C["fg2"]),
            ("no_icon",       "Bez ikony",        C["red"]),
            ("extra_no_exe",  "Extra/GOG bez EXE", C["orn"]),
            ("errors",        "Błędy",            C["yel"]),
        ]:
            tk.Radiobutton(filter_bar, text=label, variable=self.v_filter, value=val,
                           bg=C["bg2"], fg=color, activebackground=C["bg2"],
                           selectcolor=C["bg3"], font=("Segoe UI", 7),
                           highlightthickness=0).pack(side="left", padx=1)

        # ── FIX v7.5: wiersz zaznaczania gier — nad listą, zawsze widoczny.
        # (Wcześniej przyciski były na końcu dolnego paska akcji i przy
        # typowej szerokości okna wypadały poza prawą krawędź.)
        sel_bar = tk.Frame(lf, bg=C["bg2"])
        sel_bar.pack(fill="x", padx=6, pady=(1, 2))
        for txt, cmd, fg in [
            ("☑ Wszystkie",  self._check_all,     C["grn"]),
            ("☐ Żadna",      self._uncheck_all,   C["fg2"]),
            ("☑ Brakujące",  self._check_missing, C["yel"]),
        ]:
            tk.Button(sel_bar, text=txt, command=cmd,
                      bg=C["bg3"], fg=fg, font=("Segoe UI", 8),
                      relief="flat", padx=6, pady=2,
                      cursor="hand2").pack(side="left", padx=(0, 3))
        self._lbl_sel = tk.Label(sel_bar, text="", bg=C["bg2"], fg=C["fg2"],
                                 font=("Segoe UI", 8))
        self._lbl_sel.pack(side="left", padx=6)

        lf2 = tk.Frame(lf, bg=C["bg2"])
        lf2.pack(fill="both", expand=True, padx=2, pady=(0, 4))
        self._list_canvas = tk.Canvas(lf2, bg=C["bg2"], highlightthickness=0)
        lsb = tk.Scrollbar(lf2, orient="vertical", command=self._list_canvas.yview,
                           bg=C["bg3"], troughcolor=C["bg"], width=8, relief="flat")
        self._list_sb = lsb
        # v8.1: każda zmiana widoku (przewinięcie / przeciągnięcie / resize)
        # przechodzi przez nasz hook, który dokleja przeliczenie widocznych
        # wierszy (wirtualizacja). Scrollbar aktualizujemy sami.
        self._list_canvas.configure(yscrollcommand=self._on_list_yview)
        lsb.pack(side="right", fill="y")
        self._list_canvas.pack(side="left", fill="both", expand=True)
        self._list_inner = tk.Frame(self._list_canvas, bg=C["bg2"])
        self._list_cw = self._list_canvas.create_window((0, 0), window=self._list_inner, anchor="nw")
        # UWAGA: wiersze są teraz układane przez place() na wysokim, pustym
        # _list_inner (wysokość = liczba_widocznych * _row_h). Nie polegamy już
        # na bbox("all") — scrollregion ustawiamy jawnie w _do_rebuild_list.
        def _list_configure(e):
            self._list_canvas.itemconfig(self._list_cw, width=e.width)
            self._schedule_relayout()
        self._list_canvas.bind("<Configure>", _list_configure)
        def _list_scroll(e):
            self._list_canvas.yview_scroll(-1 * (e.delta // 120), "units")
        def _list_scroll_linux_up(e):
            self._list_canvas.yview_scroll(-1, "units")
        def _list_scroll_linux_dn(e):
            self._list_canvas.yview_scroll(1, "units")

        # Bezpośrednie kółko na canvas
        self._list_canvas.bind("<MouseWheel>", _list_scroll)
        self._list_canvas.bind("<Button-4>", _list_scroll_linux_up)   # Linux
        self._list_canvas.bind("<Button-5>", _list_scroll_linux_dn)   # Linux

        # Gdy kursor wchodzi w obszar listy → bind_all żeby kółko działało
        # na wierszach, etykietach i checkboxach wewnątrz listy
        def _on_list_enter(e):
            self._list_canvas.bind_all("<MouseWheel>", _list_scroll)
            self._list_canvas.bind_all("<Button-4>", _list_scroll_linux_up)
            self._list_canvas.bind_all("<Button-5>", _list_scroll_linux_dn)
        def _on_list_leave(e):
            self._list_canvas.unbind_all("<MouseWheel>")
            self._list_canvas.unbind_all("<Button-4>")
            self._list_canvas.unbind_all("<Button-5>")
        self._list_canvas.bind("<Enter>", _on_list_enter)
        self._list_canvas.bind("<Leave>", _on_list_leave)
        self._list_inner.bind("<Enter>", _on_list_enter)
        self._list_inner.bind("<Leave>", _on_list_leave)

        # Prawy panel
        rf = tk.Frame(main, bg=C["bg"])
        rf.pack(side="left", fill="both", expand=True)
        self._title = tk.Label(rf, text="← Wybierz grę z listy", bg=C["bg"], fg=C["acc"],
                               font=("Segoe UI", 13, "bold"), anchor="w")
        self._title.pack(fill="x", padx=10, pady=(6, 1))
        self._info = tk.Label(rf, text="", bg=C["bg"], fg=C["fg2"],
                              font=("Segoe UI", 8), anchor="w")
        self._info.pack(fill="x", padx=10)
        self._action_bar = tk.Frame(rf, bg=C["bg"])
        self._action_bar.pack(fill="x", padx=10, pady=(4, 2))

        # v8.2: przełącznik trybu edycji grafik — Desktop (.lnk) / Steam.
        # Wspólna lista gier i korekta tytułu; zmienia się tylko panel grafik.
        self.v_appmode = tk.StringVar(value="lnk")
        self._steam_art_type = tk.StringVar(value="cover")
        self._steam_art_token = 0
        mode_f = tk.Frame(self._action_bar, bg=C["bg3"])
        mode_f.pack(side="left", padx=(0, 10))
        tk.Label(mode_f, text="Tryb:", bg=C["bg3"], fg=C["fg2"],
                 font=("Segoe UI", 8)).pack(side="left", padx=(6, 2))
        for _val, _lbl in (("lnk", "Desktop (.lnk)"), ("steam", "Steam")):
            tk.Radiobutton(mode_f, text=_lbl, variable=self.v_appmode, value=_val,
                           command=self._on_appmode_change, bg=C["bg3"], fg=C["fg"],
                           selectcolor=C["bg2"], activebackground=C["bg3"],
                           font=("Segoe UI", 8, "bold"), indicatoron=False,
                           padx=8, pady=3, cursor="hand2").pack(side="left")

        # v8.2: czyszczenie błędnych grafik z cache dla bieżącej gry.
        self._btn_clear_art = tk.Button(
            self._action_bar, text="🗑 Wyczyść grafiki",
            command=self._clear_art_cache_for_current, bg=C["bg3"], fg=C["red"],
            font=("Segoe UI", 9), relief="flat", padx=10, pady=4, cursor="hand2")
        self._btn_clear_art.pack(side="left", padx=(0, 8))

        self._btn_pick_exe = tk.Button(
            self._action_bar, text="Wybierz plik uruchamiający (EXE)…",
            command=self._pick_exe_for_current, bg=C["bg3"], fg=C["orn"],
            font=("Segoe UI", 9), relief="flat", padx=10, pady=4, cursor="hand2")
        self._btn_manual_search = tk.Button(
            self._action_bar, text="Ręczne wyszukiwanie tytułu / ikon…",
            command=self._manual_search_for_current, bg=C["bg3"], fg=C["acc"],
            font=("Segoe UI", 9), relief="flat", padx=10, pady=4, cursor="hand2")
        self._btn_load_posters = tk.Button(
            self._action_bar, text="🖼 Pobierz plakaty (20)",
            command=self._load_posters_for_current, bg=C["bg3"], fg=C["ext"],
            font=("Segoe UI", 9), relief="flat", padx=10, pady=4, cursor="hand2")
        self._btn_fetch_extra = tk.Button(
            self._action_bar, text="🎨 Pobierz z IGDB/TGDB",
            command=self._fetch_extra_art_for_current, bg=C["bg3"], fg=C["yel"],
            font=("Segoe UI", 9), relief="flat", padx=10, pady=4, cursor="hand2")
        self._lbl_launch = tk.Label(self._action_bar, text="", bg=C["bg"],
                                    fg=C["fg2"], font=("Segoe UI", 8))

        # FIX v7.4: suwak wielkości podglądów ikon/plakatów
        self._thumb_var = tk.IntVar(
            value=int(self.config_data.get("thumb_size", 100)))
        _sl = tk.Frame(self._action_bar, bg=C["bg"])
        _sl.pack(side="right", padx=(8, 0))
        tk.Label(_sl, text="Podgląd:", bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 8)).pack(side="left", padx=(0, 4))
        self._thumb_scale = tk.Scale(
            _sl, from_=64, to=256, resolution=16, orient="horizontal",
            variable=self._thumb_var, showvalue=True, length=140,
            bg=C["bg"], fg=C["fg2"], troughcolor=C["bg3"],
            highlightthickness=0, bd=0, font=("Segoe UI", 7),
            command=self._on_thumb_size_change)
        self._thumb_scale.pack(side="left")

        cf = tk.Frame(rf, bg=C["bg"])
        cf.pack(fill="both", expand=True)
        self._cv = tk.Canvas(cf, bg=C["bg"], highlightthickness=0)
        vsb = tk.Scrollbar(cf, orient="vertical", command=self._cv.yview, bg=C["bg3"],
                           troughcolor=C["bg"], width=8, relief="flat")
        self._cv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._cv.pack(side="left", fill="both", expand=True)
        self._grid = tk.Frame(self._cv, bg=C["bg"])
        self._gcw = self._cv.create_window((0, 0), window=self._grid, anchor="nw")
        self._grid.bind("<Configure>", lambda e: self._cv.configure(scrollregion=self._cv.bbox("all")))
        self._cv.bind("<Configure>", lambda e: self._cv.itemconfig(self._gcw, width=e.width))

        # FIX v7.4: przewijanie kółkiem myszy nad siatką ikon (przy
        # większych miniaturach często wychodzą poza okno)
        def _grid_scroll(e):
            self._cv.yview_scroll(-1 * (e.delta // 120), "units")
        def _grid_scroll_lin_up(e):
            self._cv.yview_scroll(-1, "units")
        def _grid_scroll_lin_dn(e):
            self._cv.yview_scroll(1, "units")
        self._cv.bind("<MouseWheel>", _grid_scroll)
        self._cv.bind("<Button-4>", _grid_scroll_lin_up)
        self._cv.bind("<Button-5>", _grid_scroll_lin_dn)
        def _on_grid_enter(_e):
            self._cv.bind_all("<MouseWheel>", _grid_scroll)
            self._cv.bind_all("<Button-4>", _grid_scroll_lin_up)
            self._cv.bind_all("<Button-5>", _grid_scroll_lin_dn)
        def _on_grid_leave(e):
            # <Leave> z detalem NotifyInferior = wjazd kursora w dziecko (kartę/
            # miniaturę), a nie opuszczenie siatki — NIE odpinaj przewijania.
            # Bez tego w trybie Steam (thumbs zakrywa cały _grid) kółko nie działa.
            if getattr(e, "detail", "") == "NotifyInferior":
                return
            self._cv.unbind_all("<MouseWheel>")
            self._cv.unbind_all("<Button-4>")
            self._cv.unbind_all("<Button-5>")
        self._cv.bind("<Enter>", _on_grid_enter)
        self._cv.bind("<Leave>", _on_grid_leave)
        self._grid.bind("<Enter>", _on_grid_enter)
        self._grid.bind("<Leave>", _on_grid_leave)
        # Zapamiętaj handlery, by podpiąć je też do dynamicznych podramek
        # (np. „thumbs" w trybie Steam), które w całości zakrywają _grid.
        self._grid_scroll_enter = _on_grid_enter
        self._grid_scroll_leave = _on_grid_leave

    def _entry(self, par, label, var, pick_dir=False, width=34):
        tk.Label(par, text=label, bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 9)).pack(side="left")
        tk.Entry(par, textvariable=var, width=width, bg=C["bg3"], fg=C["fg"],
                 insertbackground="white", relief="flat",
                 font=("Segoe UI", 9)).pack(side="left", padx=(3, 2))
        cmd = ((lambda v=var: v.set(filedialog.askdirectory() or v.get())) if pick_dir
               else (lambda v=var: v.set(filedialog.askopenfilename(filetypes=[("EXE", "*.exe")]) or v.get())))
        tk.Button(par, text="...", command=cmd, bg="#45475a", fg=C["fg"],
                  relief="flat", padx=5, pady=3, cursor="hand2").pack(side="left", padx=(0, 10))

    def _btn(self, par, text, cmd, bg, fg=None):
        return tk.Button(par, text=text, command=cmd, bg=bg, fg=fg or C["bg"],
                         font=("Segoe UI", 10, "bold"), relief="flat", padx=14, pady=6,
                         activebackground=bg, cursor="hand2")

    # -------- Dialogi konfiguracyjne --------
    def _auto_detect_steam(self):
        d = detect_steam_exe()
        if d:
            self.v_exe.set(d)
            messagebox.showinfo("Steam wykryty", f"Ustawiono: {d}")
        else:
            messagebox.showwarning(
                "Nie znaleziono",
                "Nie udało się znaleźć Steam.exe w rejestrze.\nUstaw ścieżkę ręcznie.",
            )

    def _open_settings(self):
        dlg = SettingsDialog(self, self.config_data)
        if dlg.result:
            for k, v in dlg.result.items():
                self.config_data[k] = v
            self._extra_sources = ExtraArtSources(self.config_data)
            self._save_settings()
            messagebox.showinfo("Ustawienia", "Zmiany zapisane. Skanuj ponownie, aby je zastosować.")

    # _open_profiles removed (profiles feature removed in v5)

    def _edit_steam_libs(self):
        dlg = PathListDialog(
            self, "Dodatkowe biblioteki Steam (steamapps)",
            "Lista dodatkowych katalogów steamapps.\nGłówne steamapps + libraryfolders.vdf dodawane automatycznie.",
            self.steam_lib_dirs,
        )
        if dlg.result is not None:
            self.steam_lib_dirs = dlg.result
            self._save_settings()

    def _edit_extra_dirs(self):
        dlg = PathListDialog(
            self, "Dodatkowe katalogi Extra",
            "Lista dodatkowych katalogów z grami non-Steam.\nKażdy podkatalog = jedna gra.",
            self.extra_dirs_list,
        )
        if dlg.result is not None:
            self.extra_dirs_list = dlg.result
            self._save_settings()

    # -------- Lista gier + filtry --------
    # ── Pasek platform ────────────────────────────────────────────────────────

    def _set_source_filter(self, key: str):
        """Ustaw filtr źródła i odśwież podświetlenie przycisków."""
        self.v_source_filter.set(key)
        self._update_platform_bar_highlight()

    def _update_platform_bar_highlight(self):
        """Podświetl aktywny przycisk platformy."""
        cur = self.v_source_filter.get()
        # FIX v7.2: synchronizuj dropdown ROM z aktualnym filtrem
        dd = getattr(self, "_rom_dd", None)
        if dd is not None and dd.winfo_exists():
            if cur == "rom_all":
                dd.set(self._ROM_DD_ALL)
            elif cur in ("all", "pc"):
                dd.set("— wybierz system —")
            else:
                dd.set(cur)
        for k, btn in {**self._src_btns, **self._rom_src_btns}.items():
            active = (k == cur)
            btn.configure(
                bg=C["acc"] if active else (C["bg3"] if k in self._src_btns else C["bg"]),
                fg=C["bg"] if active else (C["fg"] if k in self._rom_src_btns else C["fg2"]),
                font=("Segoe UI", 8, "bold") if active else ("Segoe UI", 8),
            )

    _ROM_DD_ALL = "🎮 ROM: wszystkie"

    def _rebuild_platform_bar(self):
        """FIX v7.2: dynamiczny DROPDOWN systemów ROM (zamiast wiersza
        przycisków) — lista zawsze zgodna ze skonfigurowanymi systemami."""
        for w in self._plat_row2.winfo_children():
            w.destroy()
        self._rom_src_btns.clear()

        systems = self._rom_systems()
        if not systems:
            tk.Label(self._plat_row2, text="  (brak systemów ROM)",
                     bg=C["bg"], fg=C["fg2"],
                     font=("Segoe UI", 7), pady=3).pack(side="left")
            return

        tk.Label(self._plat_row2, text="ROM:", bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 8), padx=6, pady=4).pack(side="left")

        names = [s["name"] for s in systems]
        self._v_rom_dd = tk.StringVar(value="")
        self._rom_dd = ttk.Combobox(
            self._plat_row2, textvariable=self._v_rom_dd,
            values=[self._ROM_DD_ALL] + names,
            state="readonly", width=22, font=("Segoe UI", 9))
        self._rom_dd.pack(side="left", padx=(0, 6), pady=2)
        self._rom_dd.set("— wybierz system —")

        def _on_dd(_e=None):
            val = self._v_rom_dd.get()
            if val == self._ROM_DD_ALL:
                self._set_source_filter("rom_all")
            elif val and val != "— wybierz system —":
                self._set_source_filter(val)
        self._rom_dd.bind("<<ComboboxSelected>>", _on_dd)

        self._update_platform_bar_highlight()

    def _visible_games_idx(self) -> list[int]:
        q      = (self.v_search.get() or "").lower().strip()
        flt    = self.v_filter.get()
        src_f  = self.v_source_filter.get()   # "all" | "pc" | rom_sys_name
        errs   = self.config_data.get("last_run_errors", {}) or {}
        min_size = 0
        idxs: list[int] = []

        # Które źródła są widoczne
        pc_sources = {"steam", "gog", "epic", "extra"}

        for i, g in enumerate(self.games):
            src = g.get("source", "steam")

            # ── Filtr platformy ───────────────────────────────────────────────
            if src_f == "pc":
                if src not in pc_sources:
                    continue
            elif src_f == "rom_all":          # FIX v7.2: wszystkie ROM-y
                if src != "rom":
                    continue
            elif src_f != "all":
                # ROM system name
                if src != "rom" or g.get("rom_platform") != src_f:
                    continue

            # ── Filtr wyszukiwania ────────────────────────────────────────────
            if q and q not in g["name"].lower():
                continue

            # ── Filtr jakości ─────────────────────────────────────────────────
            if flt == "no_icon":
                good = any(
                    c["type"] == "sgdb" and min(c["w"], c["h"]) >= min_size
                    for c in g.get("candidates", [])
                )
                if good:
                    continue
            elif flt == "extra_no_exe":
                if src not in ("extra", "gog"):
                    continue
                has_exe = any(c["type"] == "exe" for c in g.get("candidates", []))
                if has_exe or g.get("launch_exe"):
                    continue
            elif flt == "errors":
                if self._game_key(g) not in errs:
                    continue

            idxs.append(i)
        return idxs

    # ══════════════════════════════════════════════════════════════════════
    # v8.0 (wariant 1): TRYB PROSTY — nakładka 3-krokowa dla osób
    # nietechnicznych. Nie zmienia istniejącego UI: przy wejściu chowamy
    # (pack_forget) wszystkie widgety główne zapamiętując ich pack_info,
    # przy wyjściu przywracamy je 1:1. Kroki wywołują istniejące funkcje.
    # ══════════════════════════════════════════════════════════════════════
    def _enter_simple_mode(self):
        if getattr(self, "_simple_active", False):
            return
        if getattr(self, "_simple_frame", None) is None:
            self._build_simple_frame()
        # Snapshot rozmieszczenia zaawansowanego UI (kolejność = kolejność pack)
        self._adv_pack_state = []
        for w in self.pack_slaves():
            if w is self._simple_frame:
                continue
            try:
                self._adv_pack_state.append((w, dict(w.pack_info())))
            except Exception:
                pass
        for w, _ in self._adv_pack_state:
            w.pack_forget()
        self._simple_frame.pack(fill="both", expand=True)
        self._simple_active = True
        self.config_data["ui_mode"] = "simple"
        self._save_settings()
        self._refresh_simple_list()

    def _exit_simple_mode(self):
        if not getattr(self, "_simple_active", False):
            return
        self._simple_frame.pack_forget()
        for w, info in self._adv_pack_state:
            try:
                w.pack(**info)
            except Exception:
                pass
        self._simple_active = False
        self.config_data["ui_mode"] = "advanced"
        self._save_settings()
        self._rebuild_list()

    # ── budowa panelu ──────────────────────────────────────────────────────
    def _build_simple_frame(self):
        f = tk.Frame(self, bg=C["bg"])
        self._simple_frame = f

        hdr = tk.Frame(f, bg=C["bg2"], padx=14, pady=8)
        hdr.pack(fill="x")
        tk.Label(hdr, text="PyLinks — skróty do twoich gier",
                 bg=C["bg2"], fg=C["fg"], font=("Segoe UI", 13, "bold")
                 ).pack(side="left")
        tk.Button(hdr, text="Tryb zaawansowany ▸",
                  command=self._exit_simple_mode, bg=C["bg3"], fg=C["fg2"],
                  font=("Segoe UI", 9), relief="flat", padx=10, pady=4,
                  cursor="hand2").pack(side="right")

        steps = tk.Frame(f, bg=C["bg"], padx=14, pady=10)
        steps.pack(fill="x")
        steps.columnconfigure(0, weight=1, uniform="s")
        steps.columnconfigure(1, weight=1, uniform="s")
        steps.columnconfigure(2, weight=1, uniform="s")
        self._simple_step_btns = []
        defs = [
            ("1.  Znajdź gry",
             "Przeszukaj Steam, GOG, Epic\ni katalogi z grami",
             self._simple_scan,
             "Wyszukuje zainstalowane gry i pobiera dla nich obrazki. "
             "Możesz klikać wielokrotnie — nic nie zepsujesz."),
            ("2.  Sprawdź obrazki",
             "Popraw tylko gry oznaczone\nna żółto lub czerwono",
             self._simple_goto_review,
             "Pokazuje gry, które wymagają Twojej decyzji. Zielonych nie "
             "musisz ruszać."),
            ("3.  Utwórz skróty",
             "Gotowe skróty z ikonami\ntrafią do folderu LINKS",
             self._simple_create,
             "Zapisuje skróty na dysku. Przed zapisem pokaże podsumowanie "
             "do potwierdzenia."),
        ]
        for col, (title, sub, cmd, tip) in enumerate(defs):
            b = tk.Button(steps,
                          text=f"{title}\n{sub}",
                          command=cmd, justify="center",
                          bg=C["bg2"], fg=C["fg"], activebackground=C["bg3"],
                          activeforeground=C["fg"],
                          font=("Segoe UI", 11, "bold"),
                          relief="flat", bd=0, padx=8, pady=14,
                          cursor="hand2", wraplength=280)
            b.grid(row=0, column=col, sticky="nsew",
                   padx=(0 if col == 0 else 8, 0))
            Tooltip(b, tip)
            self._simple_step_btns.append(b)

        self._simple_banner = tk.Label(
            f, text="Zacznij od kroku 1 — kliknij „Znajdź gry”.",
            bg=C["bg3"], fg=C["fg"], font=("Segoe UI", 10),
            anchor="w", padx=12, pady=8)
        self._simple_banner.pack(fill="x", padx=14, pady=(8, 8))

        romrow = tk.Frame(f, bg=C["bg"], padx=14)
        self._simple_romrow = romrow
        tk.Label(romrow, text="Konsole:", bg=C["bg"], fg=C["fg2"],
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 6))
        self._simple_rom_var = tk.StringVar()
        self._simple_rom_cb = ttk.Combobox(
            romrow, textvariable=self._simple_rom_var,
            state="readonly", width=18, font=("Segoe UI", 9))
        self._simple_rom_cb.pack(side="left", padx=(0, 6))
        _rb = tk.Button(romrow, text="Znajdź gry z konsoli",
                        command=self._simple_rom_scan, bg=C["bg3"],
                        fg=C["ext"], font=("Segoe UI", 9), relief="flat",
                        padx=10, pady=3, cursor="hand2")
        _rb.pack(side="left")
        Tooltip(_rb, "Wyszukuje gry dla wybranej konsoli (np. PS3) "
                     "w skonfigurowanym folderze z grami.")

        body = tk.Frame(f, bg=C["bg"], padx=14, pady=8)
        body.pack(fill="both", expand=True)
        srow = tk.Frame(body, bg=C["bg"])
        srow.pack(fill="x", pady=(0, 6))
        tk.Label(srow, text="🔎", bg=C["bg"], fg=C["fg2"]).pack(side="left")
        self._simple_search = tk.StringVar()
        e = tk.Entry(srow, textvariable=self._simple_search, bg=C["bg3"],
                     fg=C["fg"], insertbackground=C["fg"], relief="flat",
                     font=("Segoe UI", 10))
        e.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self._simple_search.trace_add(
            "write", lambda *_: self._refresh_simple_list())
        self._simple_flt_attn = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(srow, text="pokaż tylko do sprawdzenia",
                            variable=self._simple_flt_attn,
                            command=self._refresh_simple_list,
                            bg=C["bg"], fg=C["fg2"], selectcolor=C["bg3"],
                            activebackground=C["bg"], font=("Segoe UI", 9))
        cb.pack(side="left", padx=(8, 0))

        cols = ("gra", "status")
        tv = ttk.Treeview(body, columns=cols, show="headings",
                          selectmode="browse")
        tv.heading("gra", text="Gra")
        tv.heading("status", text="Status")
        tv.column("gra", width=380, anchor="w")
        tv.column("status", width=240, anchor="w")
        tv.tag_configure("ok",   foreground=C["grn"])
        tv.tag_configure("attn", foreground=C["yel"])
        tv.tag_configure("bad",  foreground=C["red"])
        tv.tag_configure("off",  foreground=C["fg2"])
        sb = ttk.Scrollbar(body, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        tv.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        tv.bind("<Double-1>", lambda _e: self._simple_fix_selected())
        self._simple_tv = tv

        foot = tk.Frame(f, bg=C["bg2"], padx=14, pady=8)
        foot.pack(fill="x", side="bottom")
        tk.Label(foot, textvariable=self.v_status, bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 8), anchor="w"
                 ).pack(side="left", fill="x", expand=True)
        _bf = tk.Button(foot, text="🖼 Popraw obrazek zaznaczonej gry",
                        command=self._simple_fix_selected, bg=C["bg3"],
                        fg=C["yel"], font=("Segoe UI", 9), relief="flat",
                        padx=10, pady=5, cursor="hand2")
        _bf.pack(side="right", padx=(6, 0))
        Tooltip(_bf, "Otwiera wyszukiwanie obrazka po nazwie gry — możesz "
                     "wpisać inną nazwę, jeśli ta nie daje wyników. "
                     "Działa też podwójne kliknięcie na grze.")
        self._simple_create_btn = tk.Button(
            foot, text="✔ Utwórz skróty", command=self._simple_create,
            bg=C["grn"], fg=C["bg"], font=("Segoe UI", 10, "bold"),
            relief="flat", padx=16, pady=5, cursor="hand2")
        self._simple_create_btn.pack(side="right")

    # ── logika ─────────────────────────────────────────────────────────────
    @staticmethod
    def _simple_game_status(g: dict) -> tuple[str, str]:
        """Status gry prostym językiem → (tekst, tag koloru)."""
        if not g.get("enabled", True):
            return "pominięta", "off"
        if g.get("ambiguous"):
            return "wybierz właściwy tytuł (kliknij 2×)", "attn"
        if not g.get("icons_loaded"):
            return "pobieram obrazki…", "attn"
        if g.get("candidates"):
            return "✓ gotowa", "ok"
        return "brak obrazka — kliknij 2× aby poprawić", "bad"

    def _refresh_simple_list(self):
        if not getattr(self, "_simple_active", False):
            return
        tv = self._simple_tv
        tv.delete(*tv.get_children())
        q = (self._simple_search.get() or "").lower().strip()
        only_attn = self._simple_flt_attn.get()
        n_ok = n_attn = 0
        for i, g in enumerate(self.games):
            txt, tag = self._simple_game_status(g)
            if tag == "ok":
                n_ok += 1
            elif tag in ("attn", "bad"):
                n_attn += 1
            if q and q not in g["name"].lower():
                continue
            if only_attn and tag not in ("attn", "bad"):
                continue
            tv.insert("", "end", iid=str(i),
                      values=(g["name"], txt), tags=(tag,))
        total = len(self.games)

        if total == 0:
            self._simple_banner.config(
                text="Zacznij od kroku 1 — kliknij „Znajdź gry”.",
                fg=C["fg"])
            step = 0
        elif n_attn:
            self._simple_banner.config(
                text=f"Znaleziono {total} gier. {n_ok} gotowych, "
                     f"{n_attn} do sprawdzenia (żółte/czerwone na liście).",
                fg=C["yel"])
            step = 1
        else:
            self._simple_banner.config(
                text=f"Wszystkie {total} gier ma obrazki — możesz "
                     f"utworzyć skróty (krok 3).",
                fg=C["grn"])
            step = 2
        for j, b in enumerate(self._simple_step_btns):
            if j == step:
                b.config(bg=C["acc"], fg=C["bg"], activebackground=C["acc"],
                         activeforeground=C["bg"])
            else:
                b.config(bg=C["bg2"], fg=C["fg"], activebackground=C["bg3"],
                         activeforeground=C["fg"])
        n_en = sum(1 for g in self.games if g.get("enabled", True))
        self._simple_create_btn.config(text=f"✔ Utwórz skróty ({n_en})")

        names = [s["name"] for s in self._rom_systems()]
        if names:
            self._simple_rom_cb["values"] = names
            if self._simple_rom_var.get() not in names:
                self._simple_rom_var.set(names[0])
            if not self._simple_romrow.winfo_ismapped():
                self._simple_romrow.pack(fill="x", padx=14,
                                         before=self._simple_banner)
        else:
            self._simple_romrow.pack_forget()

    def _simple_refresh_debounced(self):
        """Odśwież listę trybu prostego najwyżej co ~700 ms (skan potrafi
        sypać zdarzeniami per gra)."""
        if not getattr(self, "_simple_active", False):
            return
        if getattr(self, "_simple_refresh_pending", False):
            return
        self._simple_refresh_pending = True

        def _do():
            self._simple_refresh_pending = False
            self._refresh_simple_list()
        self.after(700, _do)

    # ── akcje kroków ───────────────────────────────────────────────────────
    def _simple_scan(self):
        self._scan_click()

    def _simple_rom_scan(self):
        name = self._simple_rom_var.get().strip()
        if not name:
            messagebox.showinfo(
                "Konsole", "Najpierw dodaj konsolę w trybie zaawansowanym "
                "(przycisk ⚙ ROMy).")
            return
        self._rom_run_platform(name)

    def _simple_goto_review(self):
        """Krok 2: pokaż tylko gry wymagające uwagi."""
        self._simple_flt_attn.set(True)
        self._refresh_simple_list()
        kids = self._simple_tv.get_children()
        if not kids:
            messagebox.showinfo(
                "Sprawdź obrazki",
                "Wszystkie gry mają już obrazki — nic do poprawienia!\n"
                "Możesz przejść do kroku 3.")
            self._simple_flt_attn.set(False)
            self._refresh_simple_list()
        else:
            self._simple_tv.selection_set(kids[0])
            self._simple_tv.see(kids[0])

    def _simple_fix_selected(self):
        sel = self._simple_tv.selection()
        if not sel:
            messagebox.showinfo(
                "Popraw obrazek",
                "Najpierw kliknij grę na liście, potem ten przycisk.")
            return
        try:
            idx = int(sel[0])
        except ValueError:
            return
        if not (0 <= idx < len(self.games)):
            return
        self.cur_idx = idx
        # Istniejąca ścieżka naprawy: ręczne wyszukiwanie tytułu (v7.8 —
        # działa w tle, nie blokuje okna). Po zakończeniu hook w
        # _rebuild_list odświeży też listę prostą.
        self._manual_search_for_current()

    def _simple_create(self):
        if not self.games:
            messagebox.showinfo(
                "Utwórz skróty", "Najpierw kliknij krok 1 — „Znajdź gry”.")
            return
        enabled = [g for g in self.games if g.get("enabled", True)]
        if not enabled:
            messagebox.showinfo("Utwórz skróty",
                                "Wszystkie gry są oznaczone jako pominięte.")
            return
        pending = [g["name"] for g in enabled if g.get("ambiguous")]
        if pending:
            messagebox.showinfo(
                "Najpierw krok 2",
                f"{len(pending)} gier czeka na wybór właściwego tytułu "
                "(żółte na liście).\nKliknij każdą z nich dwa razy i wybierz "
                "grę z listy, potem wróć tutaj.")
            return
        no_icon = sum(1 for g in enabled if not g.get("candidates"))
        msg = (f"Zostanie utworzonych {len(enabled)} skrótów "
               f"w folderze:\n{LINKS_DIR}\n")
        if no_icon:
            msg += (f"\nUwaga: {no_icon} gier nie ma obrazka — ich skróty "
                    "dostaną domyślną ikonę.")
        msg += "\n\nKontynuować?"
        if not messagebox.askyesno("Utwórz skróty", msg):
            return
        threading.Thread(target=self._create_thread, daemon=True).start()

    def _rebuild_list(self):
        """Debounce 150 ms — grupuje szybkie wywołania."""
        if hasattr(self, "_rebuild_job") and self._rebuild_job:
            try:
                self.after_cancel(self._rebuild_job)
            except Exception:
                pass
        self._rebuild_job = self.after(150, self._do_rebuild_list)

    def _update_game_count_label(self):
        """Aktualizuj licznik gier w nagłówku lewego panelu."""
        try:
            visible = len(self._visible_games_idx())
            total   = len(self.games)
            if visible == total:
                self._lbl_game_count.configure(text=f"{total} gier")
            else:
                self._lbl_game_count.configure(text=f"{visible}/{total}")
        except Exception:
            pass

    def _ico_exists_in_output(self, g: dict) -> bool:
        """Sprawdź czy .ico dla tej gry istnieje w Cache/.

        Ikony w CACHE_DIR jako <uid>_<hash>.ico (hash treści — patrz cache_ico),
        dla ROM-ów z ewentualnym sufiksem platformy. Dopasowujemy przez glob.
        """
        try:
            uid = g.get("appid") or re.sub(r"[^a-zA-Z0-9_]", "_", g["name"])
            return (any(CACHE_DIR.glob(f"{uid}_*.ico"))
                    or (CACHE_DIR / f"{uid}.ico").exists())  # zgodność wstecz
        except Exception:
            return False

    # ── Wirtualizacja listy (v8.1) ─────────────────────────────────────────
    # Zamiast tworzyć 4 widgety × N gier (przy dużych kolekcjach = dziesiątki
    # tysięcy obiektów Tcl → zawieszenie), utrzymujemy małą PULĘ wierszy
    # wielkości widocznego okna i przypinamy ją do aktualnie widocznych gier
    # przy każdym przewinięciu. Liczba widgetów jest stała (~20), niezależnie
    # od rozmiaru kolekcji.

    def _output_ico_stems(self) -> set:
        """Jedno listowanie katalogu zamiast N wywołań .exists() w kluczu sortowania.

        Wcześniej sortowanie listy robiło po jednym stat()/exists() na KAŻDĄ
        widoczną grę przy każdym rebuildzie (na NTFS bardzo drogie).
        """
        try:
            return {p.stem for p in CACHE_DIR.glob("*.ico")}
        except Exception:
            return set()

    def _schedule_relayout(self):
        if self._relayout_job is None:
            self._relayout_job = self.after_idle(self._relayout_rows)

    def _on_list_yview(self, first, last):
        """yscrollcommand — aktualizuje scrollbar i przelicza widoczne wiersze."""
        try:
            self._list_sb.set(first, last)
        except Exception:
            pass
        self._schedule_relayout()

    def _make_row(self) -> dict:
        """Tworzy JEDEN wielokrotnego użytku wiersz puli (widgety powstają raz)."""
        row = tk.Frame(self._list_inner, bg=C["bg2"], cursor="hand2", height=self._row_h)
        var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(row, variable=var, bg=C["bg2"], fg=C["fg"],
                            activebackground=C["bg3"], selectcolor=C["bg3"],
                            highlightthickness=0, relief="flat")
        cb.pack(side="left", padx=(4, 0))
        badge = tk.Label(row, text="", bg=C["bg2"], font=("Segoe UI", 7, "bold"),
                         width=4, anchor="w")
        badge.pack(side="left", padx=(0, 2))
        name = tk.Label(row, text="", bg=C["bg2"], fg=C["fg"],
                        font=("Segoe UI", 9), anchor="w", cursor="hand2")
        name.pack(side="left", fill="x", expand=True, padx=(0, 4))
        slot = {"frame": row, "cb": cb, "var": var, "badge": badge,
                "name": name, "bound_gi": None}

        def _click(e, s=slot):
            gi = s["bound_gi"]
            if gi is not None:
                self._select_game(gi)
        row.bind("<Button-1>", _click)
        name.bind("<Button-1>", _click)

        def _toggle(s=slot):
            gi = s["bound_gi"]
            if gi is not None:
                self._on_check(gi, s["var"])
        cb.configure(command=_toggle)
        return slot

    def _unbind_slot_keys(self, gi):
        if gi is None or not (0 <= gi < len(self.games)):
            return
        g = self.games[gi]
        g.pop("_list_row", None)
        g.pop("_list_name_lbl", None)
        g.pop("_check_var", None)

    def _bind_row(self, slot: dict, gi: int, y: int):
        g = self.games[gi]
        src = g.get("source", "steam")
        if src == "rom":
            badge_text  = (g.get("rom_platform", "ROM"))[:4]
            badge_color = C["ext"]
        else:
            badge_text  = {"steam": "ST", "extra": "EX",
                           "epic": "EP",  "gog":   "GG"}.get(src, "?")
            badge_color = {"steam": C["grn"], "extra": C["ext"],
                           "epic": C["orn"],  "gog":   C["yel"]}.get(src, C["fg"])
        bg = C["bg3"] if gi == self.cur_idx else C["bg2"]
        slot["frame"].configure(bg=bg)
        slot["cb"].configure(bg=bg, selectcolor=C["bg3"])
        slot["badge"].configure(text=badge_text, fg=badge_color, bg=bg)
        slot["name"].configure(text=g["name"], bg=bg)
        slot["var"].set(bool(g.get("enabled", True)))
        slot["bound_gi"] = gi
        g["_list_row"]      = slot["frame"]
        g["_list_name_lbl"] = slot["name"]
        g["_check_var"]     = slot["var"]
        slot["frame"].place(x=0, y=y, relwidth=1.0, height=self._row_h)
        self._color_from_state(gi)   # koloruje nazwę wg stanu modelu

    def _relayout_rows(self):
        """Przypina pulę do wierszy widocznych w aktualnym oknie przewijania."""
        self._relayout_job = None
        vis = self._vis
        n = len(vis)
        view_h = self._list_canvas.winfo_height() or 320
        top_px = self._list_canvas.canvasy(0)
        if top_px < 0:
            top_px = 0
        first = int(top_px // self._row_h)
        if first < 0:
            first = 0
        count = int(view_h // self._row_h) + 2   # +bufor
        last  = min(n, first + count)
        need  = max(0, last - first)

        while len(self._row_pool) < need:
            self._row_pool.append(self._make_row())

        targets = [vis[first + k] for k in range(need)]
        tgt_set = set(targets)

        # pass 1: zwolnij klucze gier, które wypadły z okna
        for slot in self._row_pool:
            gi = slot["bound_gi"]
            if gi is not None and gi not in tgt_set:
                self._unbind_slot_keys(gi)
                slot["bound_gi"] = None
        # ukryj nadmiarowe sloty
        for slot in self._row_pool[need:]:
            if slot["bound_gi"] is not None:
                self._unbind_slot_keys(slot["bound_gi"])
                slot["bound_gi"] = None
            slot["frame"].place_forget()
        # pass 2: przypnij widoczne
        for k in range(need):
            gi = targets[k]
            self._bind_row(self._row_pool[k], gi, (first + k) * self._row_h)

    def _reset_list_view(self):
        """Zwolnij pulę i referencje (np. przed skanem czyszczącym gry PC)."""
        for g in self.games:
            g.pop("_list_row", None)
            g.pop("_list_name_lbl", None)
            g.pop("_check_var", None)
        for slot in getattr(self, "_row_pool", []):
            slot["bound_gi"] = None
            try:
                slot["frame"].place_forget()
            except Exception:
                pass
        self._vis = []

    def _do_rebuild_list(self):
        """Przebudowa listy (wirtualna) – wywoływana przez debounce."""
        self._rebuild_job = None
        self._update_game_count_label()
        # referencje wierszy trzyma teraz pula; zwolnij martwe klucze
        for g in self.games:
            g.pop("_list_row", None)
            g.pop("_list_name_lbl", None)
            g.pop("_check_var", None)
        for slot in self._row_pool:
            slot["bound_gi"] = None
            slot["frame"].place_forget()

        visible = self._visible_games_idx()
        # FIX v4-3: gry bez ikony w Cache/ idą na szczyt.
        # PERF v8.1: jedno listowanie katalogu zamiast N wywołań exists().
        have_ico = self._output_ico_stems()

        def _has_ico(i: int) -> bool:
            g = self.games[i]
            uid = g.get("appid") or re.sub(r"[^a-zA-Z0-9_]", "_", g["name"])
            return uid in have_ico

        visible.sort(key=lambda i: (
            1 if _has_ico(i) else 0,
            self.games[i]["name"].lower()
        ))
        self._vis = visible

        total_h = max(1, len(visible) * self._row_h)
        self._list_inner.configure(height=total_h)
        cw = self._list_canvas.winfo_width() or 1
        self._list_canvas.configure(scrollregion=(0, 0, cw, total_h))
        # przy zmianie filtra wracamy na górę (inaczej po zawężeniu listy
        # okno mogłoby wylądować poza treścią → pusto)
        self._list_canvas.yview_moveto(0.0)
        self._relayout_rows()
        self._update_sel_label()
        self._restore_selected_game()

    def _restore_selected_game(self):
        key = self.config_data.get("selected_game_key")
        if not key:
            return
        for i, g in enumerate(self.games):
            if self._game_key(g) == key:
                # bez scrolla — po zmianie filtra lista zostaje na górze,
                # ale stan zaznaczenia i panel szczegółów są odtworzone
                self._select_game(i, scroll=False)
                break

    def _on_check(self, idx, var):
        self.games[idx]["enabled"] = var.get()
        self._update_sel_label()
        self._save_settings()

    @staticmethod
    def _shortcut_exists(g: dict) -> bool:
        """FIX v7.2: czy gra ma już utworzony skrót (.lnk/.url) w LINKS/…

        FIX v7.6: dla gier PC sprawdza też stare podkatalogi
        (LINKS/Steam, GOG, Epic, Extra), żeby "Zaznacz brakujące" nie
        oznaczało gier, które mają skrót sprzed zmiany struktury.
        """
        try:
            safe = safe_name(g.get("name", ""))
            dirs = [_links_dir_for(g)]
            if g.get("source", "extra") != "rom":
                dirs += [LINKS_DIR / d for d in _LEGACY_PC_DIRS]
            for d in dirs:
                if (d / f"{safe}.lnk").exists() or (d / f"{safe}.url").exists():
                    return True
            return False
        except Exception:
            return False

    def _set_enabled_visible(self, predicate) -> int:
        """FIX v7.3: wspólna, niezawodna implementacja zaznaczania.

        Ustawia g["enabled"] wg predykatu dla widocznych gier, aktualizuje
        zmienne checkboxów, a na koniec PRZEBUDOWUJE listę bezpośrednio
        (_do_rebuild_list, bez debounce) — widok jest wtedy zawsze zgodny
        ze stanem modelu, nawet gdyby referencje _check_var były nieaktualne
        (to powodowało, że "Zaznacz wszystkie" nie zaznaczało).
        """
        n_on = 0
        for i in self._visible_games_idx():
            g = self.games[i]
            val = bool(predicate(g))
            g["enabled"] = val
            if val:
                n_on += 1
            var = g.get("_check_var")
            if var is not None:
                try:
                    var.set(val)
                except Exception:
                    pass
        # Twarda przebudowa — checkboxy odtwarzane z g["enabled"]
        try:
            self._do_rebuild_list()
        except Exception:
            self._update_sel_label()
        self._save_settings()
        return n_on

    def _check_missing(self):
        """FIX v7.2: zaznacz tylko gry BEZ skrótu w katalogu LINKS
        (widoczne wg aktualnego filtra), resztę widocznych odznacz."""
        n = self._set_enabled_visible(lambda g: not self._shortcut_exists(g))
        self.v_status.set(f"Zaznaczono {n} gier bez skrótu w LINKS.")

    def _check_all(self):
        n = self._set_enabled_visible(lambda g: True)
        self.v_status.set(f"Zaznaczono {n} widocznych gier.")

    def _uncheck_all(self):
        self._set_enabled_visible(lambda g: False)
        self.v_status.set("Odznaczono widoczne gry.")

    def _update_sel_label(self):
        total = len(self.games)
        checked = sum(1 for g in self.games if g.get("enabled", True))
        visible = len(self._visible_games_idx())
        self._lbl_sel.config(text=f"Zaznaczone: {checked}/{total}  (widoczne: {visible})")
        # v8.0: tryb prosty ma własną listę — odśwież (debounced)
        self._simple_refresh_debounced()

    def _color_from_state(self, idx: int):
        g = self.games[idx]
        min_size = int(self.config_data.get("filters", {}).get("min_icon_size", DEFAULT_MIN_SIZE))
        if g.get("ambiguous"):
            col = C["orn"]
        elif not g.get("icons_loaded"):
            col = C["yel"]
        else:
            has_good = any(
                min(c["w"], c["h"]) >= min_size for c in g.get("candidates", [])
            )
            n = len(g.get("candidates", []))
            if g.get("source") == "steam":
                col = C["grn"] if has_good else C["red"] if n > 0 else C["fg2"]
            else:
                col = C["ext"] if has_good else C["red"] if n > 0 else C["fg2"]
        if "_list_name_lbl" in g:
            lbl_w = g["_list_name_lbl"]
            if lbl_w.winfo_exists():
                lbl_w.config(fg=col)

    def _color_list_item(self, idx, color):
        g = self.games[idx]
        if "_list_name_lbl" in g:
            lbl_w = g["_list_name_lbl"]
            if lbl_w.winfo_exists():
                lbl_w.config(fg=color)

    def _paint_list_row(self, j: int, selected: bool):
        """FIX v7: pomaluj pojedynczy wiersz listy (zamiast pętli po wszystkich)."""
        if not (0 <= j < len(self.games)):
            return
        gj = self.games[j]
        bg = C["bg3"] if selected else C["bg2"]
        row_w = gj.get("_list_row")
        if row_w is not None and row_w.winfo_exists():
            row_w.config(bg=bg)
            for child in row_w.winfo_children():
                try:
                    child.config(bg=bg)
                except Exception:
                    pass
        lbl_w = gj.get("_list_name_lbl")
        if lbl_w is not None and lbl_w.winfo_exists():
            lbl_w.config(bg=bg)

    def _ensure_gi_visible(self, gi: int):
        """Przewiń listę tak, by gra o indeksie gi była w oknie (wirtualizacja)."""
        try:
            pos = self._vis.index(gi)
        except (ValueError, AttributeError):
            return
        total_h = max(1, len(self._vis) * self._row_h)
        row_top = pos * self._row_h
        row_bot = row_top + self._row_h
        top_px  = self._list_canvas.canvasy(0)
        view_h  = self._list_canvas.winfo_height() or 320
        if row_top < top_px:
            self._list_canvas.yview_moveto(row_top / total_h)
        elif row_bot > top_px + view_h:
            self._list_canvas.yview_moveto(max(0.0, (row_bot - view_h) / total_h))
        self._relayout_rows()

    def _select_game(self, idx, scroll: bool = True):
        prev = getattr(self, "_prev_sel_idx", None)
        self.cur_idx = idx
        if scroll:
            self._ensure_gi_visible(idx)   # przewinięcie + relayout pomaluje zaznaczenie
        g = self.games[idx]
        # Resetuj licznik stron plakatów przy zmianie gry
        cur_key = self._game_key(g)
        if self._poster_game_key != cur_key:
            self._poster_page = 0
            self._poster_game_key = cur_key
        tag = {"steam": "", "extra": " [Extra]", "epic": " [Epic]", "gog": " [GOG]"}.get(
            g.get("source", "steam"), "")
        if g.get("ambiguous"):
            tag += " ⚠ oczekuje na wybór..."
        self._title.config(text=g["name"] + tag)
        # FIX v7: PERF — wcześniej pętla rekonfigurowała tła WSZYSTKICH
        # wierszy i ich dzieci przy każdym kliknięciu (tysiące .config()).
        # Teraz malujemy tylko poprzednio zaznaczony i nowy wiersz.
        if prev is not None and prev != idx:
            self._paint_list_row(prev, False)
        self._paint_list_row(idx, True)
        self._prev_sel_idx = idx
        self._draw_detail(g)
        # FIX v7: PERF — debounce zamiast pełnego zapisu JSON przy każdym kliku
        self._save_settings_debounced()

    # -------- Akcje na wybranej grze --------
    def _pick_exe_for_current(self):
        if self.cur_idx is None:
            return
        g = self.games[self.cur_idx]
        if g.get("source") not in ("extra", "gog"):
            return
        game_dir = g.get("game_dir", "")
        exe_list = [c["exe"] for c in g.get("candidates", []) if c["type"] == "exe" and c["exe"]]
        if not exe_list and game_dir:
            exe_list = [str(e) for e in self._icons().find_exes(game_dir)]
        if not exe_list:
            messagebox.showinfo("Brak EXE", f"Nie znaleziono plików EXE w:\n{game_dir}")
            return
        dlg = ExePickDialog(self, g["name"], exe_list)
        if dlg.result_exe:
            g["launch_exe"] = dlg.result_exe
            self._update_launch_label(g)
            self._save_settings()

    def _update_launch_label(self, g):
        self._btn_manual_search.pack(side="left", padx=(0, 8))
        # Przycisk IGDB/TGDB – widoczny gdy skonfigurowane co najmniej jedno źródło
        _has_extra = any([
            self._extra_sources.use_igdb and self._extra_sources.igdb_client_id,
            self._extra_sources.use_tgdb  and self._extra_sources.tgdb_key,
        ])
        if _has_extra:
            self._btn_fetch_extra.pack(side="left", padx=(0, 8))
        else:
            self._btn_fetch_extra.pack_forget()
        # Przycisk plakatów – widoczny tylko gdy jest klucz SGDB API
        if self.config_data.get("api_keys", {}).get("sgdb_key"):
            key = g.get("_poster_key") or g.get("uid") or self._game_key(g)
            poster_count = sum(1 for c in g.get("candidates", []) if c.get("type") == "grid")
            if self._poster_game_key == key and poster_count > 0:
                lbl = f"🖼 Więcej plakatów (str. {self._poster_page + 1})"
            else:
                lbl = "🖼 Pobierz plakaty (20)"
            self._btn_load_posters.config(text=lbl, state="normal")
            self._btn_load_posters.pack(side="left", padx=(0, 8))
        else:
            self._btn_load_posters.pack_forget()
        if g.get("source") in ("extra", "gog"):
            self._btn_pick_exe.pack(side="left", padx=(0, 8))
            exe = g.get("launch_exe")
            self._lbl_launch.config(
                text=f"▶ {Path(exe).name}" if exe else "▶ (auto — największy EXE)",
                fg=C["grn"] if exe else C["fg2"],
            )
            self._lbl_launch.pack(side="left")
        else:
            self._btn_pick_exe.pack_forget()
            self._lbl_launch.pack_forget()

    # ── FIX v7.2: auto-pobieranie plakatów + IGDB/TGDB po skanie ──────────
    def _submit_auto_art(self, g: dict):
        """Zleć w tle pobranie plakatów SGDB oraz grafik IGDB/TGDB/Steam CDN
        dla gry — wywoływane po załadowaniu ikon (handler "ready" w _tick).
        Działa jak pobieranie ikon: asynchronicznie, od razu po SKANUJ.
        Wyłączane kluczem configu "auto_fetch_art": false.
        """
        if not self.config_data.get("auto_fetch_art", True):
            return
        if g.get("_art_submitted"):
            return
        g["_art_submitted"] = True
        if self._art_pool is None:
            from concurrent.futures import ThreadPoolExecutor
            # 3 równoległe gry — kompromis między tempem a limitami API SGDB
            self._art_pool = ThreadPoolExecutor(
                max_workers=3, thread_name_prefix="autoart")
        self._art_pool.submit(self._auto_art_worker, g, self._async_key(g))

    def _auto_art_worker(self, g: dict, key: str):
        """Wątek: plakaty (SGDB grids, str. 0) + IGDB/TGDB → cache → UI."""
        new_cands: list[dict] = []
        try:
            if self._stop.is_set():
                return
            gid = g.get("_game_id")
            _st = self._asset_store
            # Cache-hit: gridy już na dysku → tylko dograj do kandydatów
            if gid and _st.get_assets(gid, "grids"):
                new_cands = _st.candidates_from_cache(gid, "grids")
            else:
                # 1) Plakaty SGDB (pierwsza strona, jak przycisk "Pobierz plakaty")
                if self.config_data.get("api_keys", {}).get("sgdb_key"):
                    try:
                        icons = self._icons()
                        appid   = g.get("appid")
                        sgdb_id = g.get("sgdb_id")
                        raw = []
                        if appid:
                            raw = icons.sgdb_grids_for_appid(appid, page=0, per_page=20)
                        elif sgdb_id:
                            raw = icons.sgdb_grids_for_id(sgdb_id, page=0, per_page=20)
                        new_cands += icons.grids_to_cands(raw)
                    except Exception as e:
                        print(f"[AutoArt] SGDB grids błąd ({g.get('name')}): {e}")
                # 2) IGDB / TGDB / Steam CDN — wg włączonych źródeł
                try:
                    # FIX v7.3: ROM-y → tylko IGDB/TGDB (bez zawodnych
                    # Libretro/ScreenScraper, które mają osobny pipeline)
                    new_cands += self._extra_sources.candidates_for_game(
                        g, include_rom_scrapers=False)
                except Exception as e:
                    print(f"[AutoArt] extra sources błąd ({g.get('name')}): {e}")
                # 3) Zapis do cache (przeżywa restart)
                if gid and new_cands:
                    saved = 0
                    for cv in new_cands:
                        if not cv.get("bytes"):
                            continue
                        rid = (str(cv.get("remote_asset_id") or "")
                               or (cv.get("url") or "")[-40:].replace("/", "_"))
                        if not rid:
                            continue
                        try:
                            p = _st.save_asset(gid, "grids", rid,
                                               cv["bytes"], cv.get("w", 0),
                                               cv.get("h", 0), commit=False,
                                               url=cv.get("url", ""),
                                               tier="thumb")
                            if p is not None:
                                cv["local_path"] = str(p)
                            saved += 1
                        except Exception as se:
                            print(f"[AutoArt] Błąd zapisu: {se}")
                    if saved:
                        try:
                            _st.commit()
                        except Exception:
                            pass
        except Exception:
            import traceback; traceback.print_exc()
            new_cands = []
        if new_cands and not self._stop.is_set():
            self._q.put(("art_ready", key, new_cands))

    def _load_posters_for_current(self):
        """Pobierz kolejne 20 kwadratowych plakatów dla aktualnej gry."""
        if self.cur_idx is None or self._poster_loading:
            return
        g = self.games[self.cur_idx]
        if not self.config_data.get("api_keys", {}).get("sgdb_key"):
            messagebox.showinfo("Brak klucza SGDB",
                                "Ustaw klucz SteamGridDB API w Ustawieniach.")
            return
        key = g.get("_poster_key") or g.get("uid") or self._game_key(g)
        # Resetuj stronę jeśli zmieniliśmy grę
        if self._poster_game_key != key:
            self._poster_page = 0
            self._poster_game_key = key
        page = self._poster_page
        print(f"[Plakaty] Kliknięto – gra: {g['name']}, strona: {page}, "
              f"appid: {g.get('appid')}, sgdb_id: {g.get('sgdb_id')}")
        self._poster_loading = True
        self._btn_load_posters.config(text="⏳ Pobieranie...", state="disabled")
        threading.Thread(
            target=self._poster_thread,
            args=(g, key, page),
            daemon=True,
        ).start()

    def _poster_thread(self, g: dict, key: str, page: int):
        """Wątek pobierający plakaty — wyniki odsyła przez queue do _tick()."""
        PER_PAGE = 20
        new_cands = []
        try:
            icons = self._icons()
            appid = g.get("appid")
            sgdb_id = g.get("sgdb_id")
            print(f"[Plakaty] Thread start – appid={appid}, sgdb_id={sgdb_id}, page={page}")
            if appid:
                raw_grids = icons.sgdb_grids_for_appid(appid, page=page, per_page=PER_PAGE)
            elif sgdb_id:
                raw_grids = icons.sgdb_grids_for_id(sgdb_id, page=page, per_page=PER_PAGE)
            else:
                print(f"[Plakaty] Brak appid i sgdb_id dla gry: {g.get('name')}")
                raw_grids = []
            print(f"[Plakaty] Surowych rekordów z API: {len(raw_grids)}")
            new_cands = icons.grids_to_cands(raw_grids)
            print(f"[Plakaty] Pobrano miniaturek: {len(new_cands)}")
        except Exception as e:
            print(f"[Plakaty] WYJĄTEK w wątku: {e}")
            import traceback; traceback.print_exc()
        # FIX v7: zapis plakatów do SQLite/dysku — wcześniej trafiały tylko
        # do RAM (g["candidates"]) i znikały po restarcie programu.
        if new_cands:
            gid = g.get("_game_id")
            if gid:
                saved = 0
                for cv in new_cands:
                    if not cv.get("bytes"):
                        continue
                    rid = (str(cv.get("remote_asset_id") or "")
                           or (cv.get("url") or "")[-40:].replace("/", "_"))
                    if not rid:
                        continue
                    try:
                        p = self._asset_store.save_asset(
                            gid, "grids", rid,
                            cv["bytes"], cv.get("w", 0), cv.get("h", 0),
                            commit=False, url=cv.get("url", ""),
                            tier="thumb")
                        if p is not None:
                            cv["local_path"] = str(p)
                        saved += 1
                    except Exception as se:
                        print(f"[Plakaty] Błąd zapisu do cache: {se}")
                if saved:
                    try:
                        self._asset_store.commit()
                    except Exception:
                        pass
                    print(f"[Plakaty] Zapisano {saved} plakatów do cache")
        if new_cands:
            _target = next((x for x in self.games if (x.get("uid") or self._game_key(x)) == key), None)
            if _target is not None:
                _target.setdefault("candidates", [])
                grids = [c for c in new_cands if c.get("type") == "grid"]
                if grids:
                    _target["candidates"].extend(grids)
                    if _target.get("selected_idx") is None:
                        _target["selected_idx"] = 0
                    _target["icons_loaded"] = True
        self._q.put(("posters_ready", key, page, new_cands))

    def _clear_art_cache_for_current(self):
        """Usuwa z cache pobrane grafiki (SGDB/IGDB/TGDB + wybór Steam) dla
        bieżącej gry — sposób na pozbycie się błędnych dopasowań. Zachowuje
        dopasowanie SGDB (g["sgdb_id"]); następne wyszukiwanie pobierze grafiki
        od nowa (IGDB/TGDB mają teraz próg podobieństwa, więc nie wrócą złe)."""
        if self.cur_idx is None or not (0 <= self.cur_idx < len(self.games)):
            return
        g = self.games[self.cur_idx]
        if not messagebox.askyesno(
                "Wyczyść grafiki",
                f"Usunąć z cache wszystkie pobrane grafiki dla:\n{g.get('name','')}\n\n"
                "Dotyczy SGDB / IGDB / TheGamesDB oraz wyboru grafik Steam.\n"
                "Zostaną pobrane od nowa przy następnym wyszukiwaniu."):
            return
        # 1. SQLite + pliki assetów (tu trafiają też błędne IGDB/TGDB)
        gid = g.get("_game_id")
        if gid:
            try:
                self._asset_store.delete_assets_for_game(gid)
            except Exception as ex:
                print(f"[ClearCache] store: {ex}")
        # 2. Cache list SGDB (steam_art) dla dopasowanego sgdb_id
        sid = g.get("sgdb_id")
        if sid:
            try:
                for p in _STEAM_ART_LIST_DIR.glob(f"{sid}_*.json"):
                    p.unlink()
            except Exception as ex:
                print(f"[ClearCache] steam_art: {ex}")
        # 3. Stan w pamięci (zachowaj sgdb_id — to dobre dopasowanie)
        g["candidates"] = []
        g["selected_idx"] = None
        g["icons_loaded"] = True
        g.pop("steam_art", None)
        try:
            gk = self._game_key(g)
            self.config_data.get("selected_icon_keys", {}).pop(gk, None)
            self.config_data.get("steam_art_by_key", {}).pop(gk, None)
        except Exception:
            pass
        self._save_settings()
        self._color_from_state(self.cur_idx)
        self._draw_detail(g)
        self.v_status.set(f"Wyczyszczono grafiki z cache: {g.get('name','')}")

    def _manual_search_for_current(self):
        """FIX v4-3: naprawione ręczne wyszukiwanie.

        Obsługuje trzy tryby wejścia:

        1. Tytuł gry (np. "Legaia 2", "castlevania")
           → sgdb_search_with_fallback: autocomplete + automatyczne skracanie
             zapytania gdy pełny tytuł nie daje wyników (Legaia 2 - Duel Saga
             → próbuje "Legaia 2", "Legaia" itd.)

        2. URL SGDB (np. https://www.steamgriddb.com/game/5254926)
           → sgdb_get_by_id: bezpośrednie pobranie gry po ID, omija autocomplete.
           Przydatne dla gier których autocomplete w ogóle nie indeksuje.

        3. Samo ID (np. "5254926")
           → jak wyżej, bez potrzeby pełnego URL.
        """
        if self.cur_idx is None:
            return
        # FIX v7.8: blokada re-entry — drugie kliknięcie w trakcie
        # trwającego wyszukiwania jest ignorowane.
        if getattr(self, "_manual_search_busy", False):
            return
        g = self.games[self.cur_idx]
        dlg = ManualSearchDialog(self, g.get("name", ""))

        if dlg.result is None:
            return                          # Anuluj / X — nie rób nic
        query = dlg.result.strip()
        if not query:
            return

        # FIX v7.8 (zawieszanie GUI): sgdb_get_by_id / sgdb_search_with_fallback
        # / candidates_for_* to żądania HTTP — wykonywane dotąd w wątku
        # głównym tkintera, więc okno "zamierało" na czas sieci. Cała praca
        # sieciowa idzie teraz do wątku roboczego; do wątku UI wracają tylko
        # dialogi i finalne odświeżenie (przez self.after).
        self._manual_search_busy = True
        try:
            self._btn_manual_search.config(state="disabled")
        except Exception:
            pass
        self.v_status.set(f"Szukam: {query}…")
        threading.Thread(
            target=self._manual_search_worker,
            args=(self.cur_idx, g, query),
            daemon=True,
        ).start()

    def _manual_search_end(self, msg: str | None = None):
        """Odblokuj przycisk / status po zakończeniu ręcznego wyszukiwania."""
        self._manual_search_busy = False
        try:
            self._btn_manual_search.config(state="normal")
        except Exception:
            pass
        if msg:
            self.v_status.set(msg)

    def _manual_search_worker(self, idx: int, g: dict, query: str):
        """Wątek roboczy ręcznego wyszukiwania — cała sieć poza GUI."""
        icons = self._icons()
        scanner = self._scanner()

        def _info_and_end(title: str, text: str):
            def _do():
                self._manual_search_end("Gotowy.")
                messagebox.showinfo(title, text)
            self.after(0, _do)

        try:
            # --- Tryb 2 / 3: URL lub samo ID SGDB ---
            # Np. https://www.steamgriddb.com/game/5254926 lub "5254926"
            _url_m = re.search(r'steamgriddb\.com/(?:game|games)/(\d+)', query, re.I)
            _id_only = re.fullmatch(r'\d{5,}', query)   # ≥5 cyfr = SGDB ID

            if _url_m or _id_only:
                sgdb_id_direct = int((_url_m.group(1) if _url_m else query))
                self.after(0, lambda: self.v_status.set(
                    f"Pobieranie gry SGDB #{sgdb_id_direct}…"))
                game_info = icons.sgdb_get_by_id(sgdb_id_direct)
                if not game_info:
                    _info_and_end(
                        "Brak wyników",
                        f"Nie znaleziono gry SGDB o ID {sgdb_id_direct}.\n"
                        "Sprawdź czy klucz API jest poprawny i czy gra istnieje.",
                    )
                    return
                # Ustaw bezpośrednio — pomijamy SgdbPickDialog gdy ID jest pewne
                g["sgdb_id"] = sgdb_id_direct
                g["sgdb_results"] = [game_info]
                matched_name = game_info.get("name", str(sgdb_id_direct))
                self.after(0, lambda: self.v_status.set(
                    f"Pobieranie ikon dla: {matched_name}…"))

            else:
                # --- Tryb 1: wyszukiwanie po tytule z fallbackiem ---
                results = icons.sgdb_search_with_fallback(query)
                if not results:
                    _info_and_end(
                        "Brak wyników",
                        f"Nie znaleziono wyników SGDB dla: '{query}'.\n\n"
                        "Wskazówka: otwórz steamgriddb.com w przeglądarce,\n"
                        "wyszukaj grę i wklej URL strony do tego pola.",
                    )
                    return
                # Dialog wyboru MUSI iść w wątku UI → Event jak w
                # _ask_ext_for_system.
                holder: list = [None]
                evt = threading.Event()

                def _show_pick():
                    try:
                        pick = SgdbPickDialog(self, query, results, icons.sgdb_key)
                        holder[0] = pick.result_id
                    finally:
                        evt.set()

                self.after(0, _show_pick)
                evt.wait(timeout=300)
                if holder[0] is None:
                    self.after(0, lambda: self._manual_search_end("Gotowy."))
                    return
                g["sgdb_id"] = holder[0]
                matched = next((r for r in results
                                if r.get("id") == holder[0]), None)
                if matched:
                    g["sgdb_results"] = [matched]
                self.after(0, lambda: self.v_status.set("Pobieranie ikon…"))

            # --- wspólna część: pobierz kandydatów (sieć, nadal w wątku) ---
            if g["source"] == "steam":
                cands = icons.candidates_for_steam(g, scanner)
                cands += self._extra_sources.steam_cdn_candidates(g.get("appid",""))
            else:
                cands = icons.candidates_for_extra(g, g["sgdb_id"])
            # Dodaj IGDB / TGDB / Libretro gdy skonfigurowane
            cands += self._extra_sources.candidates_for_game(g)
            g["candidates"] = cands
            if not self._restore_selected_icon(g):  # FIX v7
                g["selected_idx"] = icons.best_idx(cands)
            g["icons_loaded"] = True
            g["ambiguous"] = False

            # Zapis do SQLite (bez GUI — może zostać w wątku roboczym)
            self._manual_search_save_cache(g, cands)
        except Exception as e:
            print(f"[Manual search] błąd: {e}")
            import traceback; traceback.print_exc()
            self.after(0, lambda: self._manual_search_end(f"Błąd wyszukiwania: {e}"))
            return

        # Finalne odświeżenie UI — tylko w wątku głównym
        def _finish():
            self._manual_search_end("Gotowy.")
            # Indeks mógł się zmienić (rescan) — odśwież tylko gdy gra
            # nadal istnieje na liście.
            try:
                cur = self.games.index(g)
            except ValueError:
                return
            self._color_from_state(cur)
            if cur == self.cur_idx:
                self._draw_detail(g)
                self._set_info(g)
            self._rebuild_list()
            self._save_settings()
        self.after(0, _finish)

    def _manual_search_save_cache(self, g: dict, cands: list[dict]):
        """Zapis wyników ręcznego wyszukiwania do SQLite (wydzielone z
        _manual_search_for_current przy przenoszeniu do wątku — FIX v7.8)."""
        gid = g.get("_game_id")
        _st = self._asset_store
        if gid and g.get("sgdb_id"):
            # 1. sgdb_id → tabela games (żeby candidates_from_cache działał)
            with _st._lock:  # FIX v7
                _st._db.execute(
                    "UPDATE games SET sgdb_id=? WHERE id=?",
                    (str(g["sgdb_id"]), gid),
                )
            # 2. Ikony SGDB/grid → assets (asset_type="icons")
            for cv in cands:
                if cv.get("type") in ("sgdb", "grid") and cv.get("bytes"):
                    _st.save_asset(
                        gid, "icons",
                        str(cv.get("remote_asset_id") or cv.get("label", "")),
                        cv["bytes"], cv["w"], cv["h"],
                        sgdb_key=str(g["sgdb_id"]),
                        commit=False,
                        url=cv.get("url", ""), tier="thumb",
                    )
            # 3. Grafiki zewnętrzne IGDB/TGDB/CDN → assets (asset_type="grids")
            ext_styles = {"igdb", "tgdb", "steam_cdn", "libretro", "screenscraper"}
            for cv in cands:
                if (cv.get("bytes") and cv.get("url")
                        and cv.get("style", "") in ext_styles):
                    rid = (cv.get("remote_asset_id")
                           or cv["url"][-40:].replace("/", "_"))
                    _st.save_asset(gid, "grids", rid,
                                   cv["bytes"], cv["w"], cv["h"],
                                   commit=False,
                                   url=cv.get("url", ""), tier="thumb")
            _st.commit()
            # 4. Pełny stub — zawiera sgdb_id + URL-e ext. źródeł + wybrany kandydat
            _st.save_stub(gid, self._build_stub(g))
            print(f"[Manual search] zapisano do cache: {g['name']!r} "
                  f"sgdb_id={g['sgdb_id']} cands={len(cands)}")
        elif gid and g.get("source") == "rom":
            # ROM bez sgdb_id (np. EXE-only) — zapisz przynajmniej stub z phash
            if g.get("rom_path") and Path(g["rom_path"]).exists():
                phash = _rom_pseudo_hash(Path(g["rom_path"]))
                _st.save_stub(gid, self._build_stub(g), phash)
        # FIX v7.8: odświeżenie UI przeniesione do _finish w
        # _manual_search_worker (ta funkcja działa w wątku roboczym).

    # ── Orphan check / stub management ──────────────────────────────────────

    def _build_stub_minimal(self, g: dict) -> dict:
        """Lekki stub tylko z sgdb_id — tworzony podczas skanu gdy gra istnieje.
        Pełny stub (_build_stub) tworzony jest dopiero przy usuwaniu gry (orphan).
        Cel: przyszłe _restore_from_stub nie musi szukać na SGDB od nowa.
        """
        return {
            "name":    g.get("name", ""),
            "source":  g.get("source", ""),
            "appid":   g.get("appid"),
            "sgdb_id": g.get("sgdb_id"),
            "ext_art_urls": [],
        }

    def _build_stub(self, g: dict) -> dict:
        """Zbuduj słownik metadanych do zapisania w stub.

        FIX: teraz zawiera też URL-e z zewnętrznych źródeł (IGDB/TGDB/Steam CDN)
        żeby _restore_from_stub mógł je ponownie pobrać bez przeszukiwania.
        """
        cands = g.get("candidates", [])
        sel   = g.get("selected_idx")

        # SGDB: identyfikacja po remote_asset_id (stabilny ID z API)
        sgdb_rids = [
            c.get("remote_asset_id", "")
            for c in cands
            if c.get("remote_asset_id") and c.get("type") == "sgdb"
        ]

        # Zewnętrzne źródła: identyfikacja po URL (IGDB/TGDB/Steam CDN/Libretro)
        ext_styles = {"igdb", "tgdb", "steam_cdn", "libretro", "screenscraper"}
        ext_urls = [
            {"url": c.get("url",""), "style": c.get("style",""),
             "w": c.get("w",0), "h": c.get("h",0)}
            for c in cands
            if c.get("url") and c.get("style","") in ext_styles
        ]

        stub = {
            "name":                  g.get("name", ""),
            "source":                g.get("source", ""),
            "appid":                 g.get("appid"),
            "sgdb_id":               g.get("sgdb_id"),
            "sgdb_icon_remote_ids":  sgdb_rids,
            "ext_art_urls":          ext_urls,   # IGDB/TGDB/CDN/Libretro
            "selected_remote_id":    None,
            "selected_asset_type":   None,
            "selected_url":          None,       # wybrany URL (ext sources)
            "selected_style":        None,
        }

        if sel is not None and 0 <= sel < len(cands):
            c = cands[sel]
            stub["selected_remote_id"]  = c.get("remote_asset_id")
            stub["selected_asset_type"] = c.get("type")
            stub["selected_url"]        = c.get("url")
            stub["selected_style"]      = c.get("style")

        return stub

    def _migrate_legacy_pc_links(self):
        """FIX v7.6: jednorazowo przenieś skróty ze starych podkatalogów
        (LINKS/Steam, GOG, Epic, Extra) do wspólnego LINKS/PC.

        Kolizje nazw: istniejący plik w PC wygrywa, stary zostaje (log).
        Puste stare katalogi są usuwane.
        """
        try:
            dst = LINKS_DIR / "PC"
            moved = 0
            for name in _LEGACY_PC_DIRS:
                d = LINKS_DIR / name
                if not d.is_dir():
                    continue
                dst.mkdir(parents=True, exist_ok=True)
                for f in list(d.iterdir()):
                    if not f.is_file() or f.suffix.lower() not in (".lnk", ".url"):
                        continue
                    target = dst / f.name
                    if target.exists():
                        print(f"[Migracja LINKS] kolizja, zostawiam: {f}")
                        continue
                    try:
                        f.rename(target)
                        moved += 1
                    except Exception as e:
                        print(f"[Migracja LINKS] nie można przenieść {f}: {e}")
                try:
                    if not any(d.iterdir()):
                        d.rmdir()
                except Exception:
                    pass
            if moved:
                print(f"[Migracja LINKS] przeniesiono {moved} skrótów do LINKS/PC")
                self.v_status.set(
                    f"Przeniesiono {moved} skrótów PC do LINKS/PC.")
        except Exception as e:
            print(f"[Migracja LINKS] błąd: {e}")

    def _check_orphans_after_scan(self, check_dirs: set[str] | None = None):
        """Sprawdź osierocone LNK-i po zakończeniu skanu.

        check_dirs: JAWNA lista katalogów LINKS/ do sprawdzenia.
          • Po skanie Steam: {LINKS/Steam, LINKS/GOG, LINKS/Epic, LINKS/Extra}
          • Po skanie PS1:   {LINKS/PS1}
          • None (domyślnie): wyprowadzone z aktualnych źródeł w self.games

        Zasada: każdy skan sprawdza TYLKO SWOJE katalogi — skan Steam nie
        wchodzi w LINKS/PS1/ i odwrotnie.
        """
        # Wyznacz katalogi do sprawdzenia
        if check_dirs is None:
            check_dirs = {str(_links_dir_for(g)) for g in self.games}

        if not check_dirs or not LINKS_DIR.exists():
            return

        orphans: list[dict] = []

        # Mapa (safe_name, folder) → aktywna gra
        current_map: dict[tuple[str, str], dict] = {}
        for g in self.games:
            ldir = str(_links_dir_for(g))
            current_map[(safe_name(g.get("name", "")), ldir)] = g

        # Mapa safe_name → wiersz SQLite (dla gier które już nie są w self.games)
        db_by_name: dict[str, dict] = {}
        try:
            with self._asset_store._lock:  # FIX v7.4: odczyt pod lockiem
                rows = self._asset_store._db.execute(
                    "SELECT id, name, source, sgdb_id, appid FROM games"
                ).fetchall()
            for row in rows:
                db_by_name[safe_name(row["name"])] = dict(row)
        except Exception:
            pass

        for subdir in sorted(LINKS_DIR.iterdir()):
            if not subdir.is_dir():
                continue
            # Sprawdzamy TYLKO katalogi tego konkretnego skanu
            if str(subdir) not in check_dirs:
                continue
            for lnk in sorted(subdir.iterdir()):
                if lnk.suffix.lower() not in (".lnk", ".url"):
                    continue
                key = (lnk.stem, str(subdir))
                if key in current_map:
                    continue   # gra aktywna — OK
                # LNK bez aktywnej gry
                db_row = db_by_name.get(lnk.stem, {})
                orphans.append({
                    "_game_id":   db_row.get("id"),
                    "name":       lnk.stem,
                    "source":     subdir.name.lower(),
                    "sgdb_id":    db_row.get("sgdb_id"),
                    "appid":      db_row.get("appid"),
                    "_stale_lnk": str(lnk),
                    "candidates": [],
                    "game_dir":   "", "launch_exe": "", "rom_path": "",
                })

        if not orphans:
            return
        self.after(600, lambda: self._show_orphan_dialog(orphans))

    def _show_orphan_dialog(self, missing: list[dict]):
        dlg = OrphanDialog(self, missing)
        if dlg.result:
            threading.Thread(
                target=self._delete_orphans,
                args=(dlg.result,),
                daemon=True,
            ).start()

    def _delete_orphans(self, orphans: list[dict]):
        """Wątek: usuń brakujące gry — stub → obrazy → LNK → games list."""
        _st = self._asset_store
        deleted_names = []

        for g in orphans:
            gid = g.get("_game_id")
            name = g.get("name", "?")

            # 1. Zapisz stub (zachowujemy metadane + sgdb_id + URL-e)
            if gid:
                stub = self._build_stub(g)
                phash = None
                if g.get("source") == "rom" and g.get("rom_path"):
                    try:
                        phash = _rom_pseudo_hash(Path(g["rom_path"]))
                    except Exception:
                        pass
                try:
                    _st.save_stub(gid, stub, phash)
                except Exception as e:
                    print(f"[Stub] błąd zapisu dla {name!r}: {e}")

            # 2. Usuń pliki obrazów + rekordy assets (zachowuje games + stub)
            if gid:
                try:
                    _st.delete_assets_for_game(gid)
                except Exception as e:
                    print(f"[Assets] błąd usuwania dla {name!r}: {e}")

            # 3. Usuń .lnk / .url ze LINKS/
            # _stale_lnk: konkretny plik wykryty przez scanner (typ B)
            # Jeśli brak — oblicz ścieżkę z nazwy gry (typ A: ROM z brakującym plikiem)
            stale_lnk = g.get("_stale_lnk")
            if stale_lnk:
                try:
                    Path(stale_lnk).unlink(missing_ok=True)
                except Exception:
                    pass
            else:
                lnk_dir = _links_dir_for(g)
                safe = safe_name(name)
                for ext in (".lnk", ".url"):
                    f = lnk_dir / (safe + ext)
                    try:
                        if f.exists():
                            f.unlink()
                    except Exception:
                        pass

            deleted_names.append(name)

        # 4. Usuń z self.games (na wątku głównym)
        # Stale LNK games (typ B) nie są w self.games, więc nie filtrujemy po id()
        orphan_ids = {id(g) for g in orphans if not g.get("_stale_lnk")}
        def _finish():
            self.games = [g for g in self.games if id(g) not in orphan_ids]
            self._rebuild_list()
            names_str = "\n".join(f"  \u2022 {n}" for n in deleted_names[:25])
            if len(deleted_names) > 25:
                names_str += f"\n  ...i {len(deleted_names)-25} więcej"
            report = "\n".join(f"  \u2022 {n}" for n in deleted_names)
            messagebox.showinfo(
                "Brakujące gry usunięte",
                f"Usunięto {len(deleted_names)} brakujących gier:\n\n"
                f"{report}\n\n"
                "Stuby z ID i URL-ami zachowane w bazie.\n"
                "Gry zostaną rozpoznane bez ponownego wyszukiwania gdy wrócą.",
            )
        self.after(0, _finish)

    def _restore_from_stub(self, g: dict):
        """Wątek: re-pobierz obrazy dla gry odnalezionej przez stub.

        Przywraca zarówno SGDB ikony (po sgdb_id) jak i zewnętrzne grafiki
        (IGDB/TGDB/CDN) po URL-ach zapamiętanych w stub.ext_art_urls.
        Preferuje wcześniej wybrany kandydat (stub.selected_url lub selected_remote_id).
        """
        gid = g.get("_game_id")
        if not gid:
            return
        icons_mgr = self._icons()
        _st = self._asset_store

        stub = _st.load_stub(gid)
        if not stub:
            return

        all_cands: list[dict] = []

        # ── 1. SGDB ikony ─────────────────────────────────────────────────
        if stub.get("sgdb_id"):
            g["sgdb_id"] = stub["sgdb_id"]
            sgdb_cands = icons_mgr.candidates_for_extra(g, stub["sgdb_id"])
            all_cands += sgdb_cands
            for cv in sgdb_cands:
                if cv.get("type") in ("sgdb","grid") and cv.get("bytes"):
                    _st.save_asset(gid, "icons",
                                   str(cv.get("remote_asset_id") or ""),
                                   cv["bytes"], cv["w"], cv["h"],
                                   sgdb_key=str(stub["sgdb_id"]),
                                   commit=False,
                                   url=cv.get("url", ""), tier="thumb")

        # ── 2. Zewnętrzne grafiki z URL-i (IGDB/TGDB/CDN) ────────────────
        for entry in (stub.get("ext_art_urls") or []):
            url = entry.get("url","") if isinstance(entry, dict) else str(entry)
            if not url:
                continue
            b = fetch(url, timeout=10)
            if not b:
                continue
            w, h = entry.get("w",0), entry.get("h",0)
            if PIL_OK and not (w and h):
                try:
                    w, h = Image.open(BytesIO(b)).size
                except Exception:
                    pass
            rid = url[-40:].replace("/", "_")
            cand = {
                "type":  "grid",
                "bytes": b, "w": w, "h": h,
                "style": entry.get("style","ext") if isinstance(entry, dict) else "ext",
                "shape": "unknown",
                "label": f"Restored {entry.get('style','ext') if isinstance(entry,dict) else 'ext'} {w}x{h}",
                "exe":   None, "url": url,
                "remote_asset_id": rid,
            }
            all_cands.append(cand)
            _st.save_asset(gid, "grids", rid, b, w, h, commit=False,
                           url=url, tier="thumb")

        if not all_cands:
            return

        _st.commit()

        g["candidates"]   = all_cands
        if not self._restore_selected_icon(g):  # FIX v7
            g["selected_idx"] = icons_mgr.best_idx(all_cands)
        g["icons_loaded"] = True

        # Przywróć wcześniej wybrany kandydat (stable key > stub > indeks)
        gk         = self._game_key(g)
        key_map    = self.config_data.get("selected_icon_keys", {})
        saved_sk   = key_map.get(gk, "")
        sel_url    = stub.get("selected_url")
        sel_rid    = stub.get("selected_remote_id")
        sel_idx_cf = self.config_data.get("selected_indices", {}).get(gk)

        restored = False
        for i, c in enumerate(all_cands):
            ck = self._candidate_stable_key(c)
            # 1. Dokładne dopasowanie do stable key z config.json
            if saved_sk and ck == saved_sk:
                g["selected_idx"] = i
                restored = True
                break
            # 2. URL ze stuba (legacy: SGDB/CDN)
            if sel_url and c.get("url") == sel_url:
                g["selected_idx"] = i
                restored = True
                break
            # 3. Remote asset ID ze stuba
            if sel_rid and c.get("remote_asset_id") == sel_rid:
                g["selected_idx"] = i
                restored = True
                break
        # 4. Fallback: stary indeks z config — tylko jeśli nic innego nie zadziałało
        if not restored and sel_idx_cf is not None and 0 <= sel_idx_cf < len(all_cands):
            g["selected_idx"] = sel_idx_cf
            # Zapamiętaj stable key żeby następnym razem było lepiej
            sk = self._candidate_stable_key(all_cands[sel_idx_cf])
            if sk:
                self.config_data.setdefault("selected_icon_keys", {})[gk] = sk

        self.after(0, lambda: self._draw_detail(g)
                   if self.cur_idx is not None
                   and self.games[self.cur_idx] is g
                   else None)

    # -------- Pobierz z zewnętrznych baz (IGDB/TGDB/ScreenScraper) --------
    def _fetch_extra_art_for_current(self):
        """Pobierz grafiki z IGDB, TGDB, ScreenScraper dla aktualnie wybranej gry.

        Uruchamia się przyciskiem — nie blokuje GUI.
        Wyniki dołączane są do istniejących kandydatów.
        """
        if self.cur_idx is None:
            return
        g = self.games[self.cur_idx]
        if not any([
            self._extra_sources.use_igdb and self._extra_sources.igdb_client_id,
            self._extra_sources.use_tgdb  and self._extra_sources.tgdb_key,
            self._extra_sources.use_screenscraper and self._extra_sources.ss_user,
        ]):
            messagebox.showinfo(
                "Brak aktywnych źródeł",
                "Żadne zewnętrzne źródło nie jest skonfigurowane.\n\n"
                "Włącz IGDB lub TheGamesDB w:\n"
                "⚙ Ustawienia → Dodatkowe źródła grafik",
            )
            return
        self._btn_fetch_extra.config(text="⏳ Pobieranie…", state="disabled")
        self.v_status.set(f"Pobieram z zewnętrznych baz: {g['name']}…")
        threading.Thread(
            target=self._fetch_extra_art_thread,
            args=(g,),
            daemon=True,
        ).start()

    def _fetch_extra_art_thread(self, g: dict):
        """Wątek pobierający dodatkowe grafiki (IGDB/TGDB/ScreenScraper).

        FIX: kandydaci są teraz zapisywani do SQLite (asset_type="grids")
        tak że przy kolejnym skanie są wczytywane z cache — bez HTTP.
        """
        extra = self._extra_sources.candidates_for_game(g)
        _st   = self._asset_store
        gid   = g.get("_game_id")

        # Zapisz do cache zanim trafi do UI (wątek, bez locka — tylko jeden wątek tu)
        saved_count = 0
        if gid and extra:
            for cv in extra:
                if cv.get("bytes") and (cv.get("url") or cv.get("remote_asset_id")):
                    rid = (cv.get("remote_asset_id")
                           or (cv.get("url") or "")[-40:].replace("/", "_"))
                    try:
                        p = _st.save_asset(gid, "grids", rid,
                                           cv["bytes"], cv["w"], cv["h"],
                                           commit=False,
                                           url=cv.get("url", ""),
                                           tier="thumb")
                        if p is not None:
                            cv["local_path"] = str(p)
                        saved_count += 1
                    except Exception as se:
                        # FIX v7: błąd zapisu był połykany po cichu — logujemy
                        print(f"[Extra art] Błąd zapisu assetu: {se}")
            if saved_count:
                _st.commit()
                print(f"[Extra art] zapisano {saved_count} grafik do cache "
                      f"dla {g['name']!r}")

        def _finish():
            self._btn_fetch_extra.config(
                text="🎨 Pobierz z IGDB/TGDB", state="normal")
            if not extra:
                self.v_status.set(
                    f"Brak wyników z zewnętrznych baz dla: {g['name']}")
                return
            g.setdefault("candidates", [])
            existing_urls = {c.get("url", "") for c in g["candidates"]}
            new_cands = [c for c in extra
                         if c.get("url", "") not in existing_urls]
            g["candidates"] += new_cands
            if g.get("selected_idx") is None and g["candidates"]:
                g["selected_idx"] = 0
            self.v_status.set(
                f"+{len(new_cands)} grafik z zewnętrznych baz "
                f"({saved_count} w cache) dla: {g['name']}")
            if self.cur_idx is not None and self.games[self.cur_idx] is g:
                self._draw_detail(g)
        self.after(0, _finish)

    # -------- Skan (wątek) --------
    def _scan_click(self):
        if self._scanning:
            self._stop.set()
            self._btn_scan.config(text="SKANUJ")
            return
        self._stop.clear()
        self._scanning = True
        self._btn_scan.config(text="STOP")
        # Wyczyść tylko gry PC — ROM-y mają własny przycisk skanowania
        # i są addytywne (nie kasujemy PS1 gdy skanujemy PS2)
        src_filter = getattr(self, "v_source_filter", None)
        current_filter = src_filter.get() if src_filter else "all"
        if current_filter in ("all", "pc", "steam", "gog", "epic", "extra"):
            self.games = [g for g in self.games if g.get("source") == "rom"]
        self._reset_list_view()   # v8.1: zwolnij pulę zamiast niszczyć widgety
        self._clear_grid()
        self.v_prog.set(0)
        threading.Thread(target=self._scan_thread, daemon=True).start()

    @staticmethod
    def _norm_title(name: str) -> str:
        """Znormalizowany tytuł do porównań duplikatów.

        FIX v7.7: interpunkcja jest zamieniana na SPACJE i sklejana,
        a nie usuwana — usuwanie sklejało tokeny i np.
        "DRAGON QUEST I & II HD-2D Remake" stawało się identyczne z
        "DRAGON QUEST III HD-2D Remake" (I+II → III), przez co druga
        gra z serii znikała jako rzekomy duplikat.
        Dodatkowo "&" ≡ "and", żeby "I & II" = "I and II".
        """
        s = (name or "").lower()
        s = re.sub(r"[\u2122\u00ae]", "", s)          # ™ ®
        s = s.replace("&", " and ")
        s = re.sub(r"[^a-z0-9ąćęłńóśźż]+", " ", s)     # interpunkcja → spacja
        s = re.sub(r"\s+", " ", s).strip()
        s = re.sub(r"^(the|a) ", "", s)
        return s

    def _dedupe_pc_games(self, games: list[dict]) -> list[dict]:
        """FIX v7.6: usuń duplikaty gier PC między źródłami.

        Duplikat = ten sam znormalizowany tytuł LUB ten sam katalog gry.
        Wygrywa źródło o wyższym priorytecie: steam > gog > epic > extra
        (skanery sklepów znają appid/buildy — Extra to tylko folder).
        """
        prio = {"steam": 0, "gog": 1, "epic": 2, "extra": 3}
        # sortowanie stabilne wg priorytetu — pierwszy wygrywa
        ordered = sorted(games,
                         key=lambda g: prio.get(g.get("source", "extra"), 9))
        seen_titles: dict[str, dict] = {}
        seen_dirs:   dict[str, dict] = {}
        out: list[dict] = []
        dropped: list[str] = []
        for g in ordered:
            if g.get("source") == "rom":
                out.append(g); continue
            t = self._norm_title(g.get("name", ""))
            d = ""
            try:
                gd = g.get("game_dir") or ""
                d = str(Path(gd).resolve()).lower() if gd else ""
            except Exception:
                pass
            dup_of = (seen_titles.get(t) if t else None) or \
                     (seen_dirs.get(d) if d else None)
            # FIX v7.7: deduplikacja działa tylko MIĘDZY źródłami.
            # Skanery sklepów nie zwracają duplikatów w obrębie siebie —
            # dwie różne gry Steam (różne appid / katalogi) zostają obie.
            if dup_of is not None and dup_of.get("source") == g.get("source"):
                dup_of = None
            # Różne appid = na pewno różne gry, niezależnie od tytułu
            if (dup_of is not None and g.get("appid") and dup_of.get("appid")
                    and str(g["appid"]) != str(dup_of["appid"])):
                dup_of = None
            if dup_of is not None:
                dropped.append(f"{g.get('name')} [{g.get('source')}] "
                               f"→ duplikat [{dup_of.get('source')}]")
                continue
            if t:
                seen_titles[t] = g
            if d:
                seen_dirs[d] = g
            out.append(g)
        if dropped:
            print(f"[Dedupe] Pominięto {len(dropped)} duplikatów PC:")
            for line in dropped[:20]:
                print("   ", line)
        # przywróć pierwotną kolejność źródeł (steam, extra, epic, gog
        # tak jak przyszły ze skanerów) — sort stabilny po starym indeksie
        idx = {id(g): i for i, g in enumerate(games)}
        out.sort(key=lambda g: idx.get(id(g), 1 << 30))
        return out

    def _scan_thread(self):
        scanner = self._scanner()
        icons = self._icons()
        # Steam Web API (opcjonalnie)
        if scanner.use_web_api:
            owned = scanner.fetch_owned_games()
            self._q.put(("st", f"API Steam: {len(owned)} gier"))
        steam_games = scanner.scan_installed()
        extra_games: list[dict] = []
        if self.v_extra.get().strip():
            extra_games.extend(scan_extra_dir(self.v_extra.get().strip()))
        for part in self.extra_dirs_list:
            extra_games.extend(scan_extra_dir(part))
        self._q.put(("st", f"Extra Dir (łącznie): {len(extra_games)} folderów"))
        epic_games = scan_epic_games() if self.config_data.get("scan_epic", True) else []
        if epic_games:
            self._q.put(("st", f"Epic Games: {len(epic_games)} gier"))
        gog_games = scan_gog_games() if self.config_data.get("scan_gog", True) else []
        if gog_games:
            self._q.put(("st", f"GOG.com: {len(gog_games)} gier"))
        all_games = steam_games + extra_games + epic_games + gog_games
        # FIX v7.6: deduplikacja — ta sama gra znaleziona przez skaner
        # GOG/Epic/Steam ORAZ jako folder Extra (np. Wiedźmin 3 z GOG
        # zainstalowany w katalogu objętym Extra Dir) ma zostać RAZ,
        # ze źródłem bardziej wiarygodnym (steam > gog > epic > extra).
        all_games = self._dedupe_pc_games(all_games)
        self._q.put(("games", all_games))
        total = len(all_games)
        _st = self._asset_store
        # PERF v7.8: cała biblioteka upsertowana w JEDNEJ transakcji
        # (wcześniej commit + print per gra = fsync × N i spam konsoli,
        # zauważalny narzut na Windows).
        for _gg in all_games:
            _gg["_game_id"] = _st.upsert_game(
                _gg.get("source","extra"), _gg.get("appid"),
                _gg.get("sgdb_id"), _gg.get("name",""), commit=False)
        _st.commit()
        print(f"[DB] upsert {total} gier (batch)")

        # PERF v7.8: prefetch WSZYSTKICH assetów z cache jednym zapytaniem
        # + współdzielony cache listingów katalogów (jeden os.listdir na
        # katalog zamiast stat() per plik). To główny fix wolnego odczytu
        # cache przy starcie.
        _bulk = _st.assets_bulk([g.get("_game_id") for g in all_games],
                                ("icons", "grids"))
        _sgdb_bulk = _st.sgdb_ids_bulk([g.get("_game_id") for g in all_games])
        _dir_cache: dict = {}

        for i, g in enumerate(all_games):
            if self._stop.is_set():
                break
            self._q.put(("prog", i, total, g["name"]))
            _gid = g.get("_game_id")
            _cached = []
            if _gid:
                # FIX v7: scalamy OBA typy assetów. Wcześniej "albo-albo" —
                # jeśli gra miała ikony SGDB, zapisane gridy (IGDB/TGDB/
                # plakaty) nigdy nie były wczytywane z cache.
                _cached = (
                    _st.candidates_from_cache(
                        _gid, "icons", dir_cache=_dir_cache,
                        rows=_bulk.get((_gid, "icons"), []))
                    + _st.candidates_from_cache(
                        _gid, "grids", dir_cache=_dir_cache,
                        rows=_bulk.get((_gid, "grids"), []))
                )
            if _cached:
                g["candidates"] = _cached
                # FIX v7: najpierw spróbuj przywrócić zapisany wybór ikony;
                # best_idx() tylko jako fallback (wcześniej nadpisywał wybór)
                if not self._restore_selected_icon(g):
                    g["selected_idx"] = icons.best_idx(_cached)
                g["icons_loaded"] = True
                g["_from_cache"] = True
                # FIX: odczytaj sgdb_id z DB – bez tego pobieranie plakatów
                # nie działa, bo _poster_thread sprawdza g["sgdb_id"]
                if _gid and not g.get("sgdb_id"):
                    saved = _sgdb_bulk.get(_gid)  # PERF v7.8: bulk zamiast per gra
                    if saved:
                        g["sgdb_id"] = saved
                self._q.put(("ready", i))
            elif g["source"] == "steam":
                cands = icons.candidates_for_steam(g, scanner)
                # Dodaj grafiki Steam CDN (bez dodatkowego klucza API)
                cands += self._extra_sources.steam_cdn_candidates(g.get("appid",""))
                if _gid:
                    _sk = str(g.get("sgdb_id") or _gid)
                    for _cv in cands:
                        if _cv.get("type") in ("sgdb","grid") and _cv.get("bytes"):
                            _st.save_asset(_gid,"icons",
                                str(_cv.get("remote_asset_id") or _cv.get("label","")),
                                _cv["bytes"],_cv["w"],_cv["h"],sgdb_key=_sk,
                                commit=False,
                                url=_cv.get("url",""), tier="thumb")
                    _st.commit()
                    # Stub: zachowaj sgdb_id żeby przyszłe _restore_from_stub
                    # mogło re-pobrać ikony bez wyszukiwania (Fix 3)
                    if g.get("sgdb_id"):
                        _st.save_stub(_gid, self._build_stub_minimal(g))
                g["candidates"] = cands
                if not self._restore_selected_icon(g):  # FIX v7
                    g["selected_idx"] = icons.best_idx(cands)
                g["icons_loaded"] = True
                self._q.put(("ready", i))
            else:
                results = icons.sgdb_search(g["name"]) if icons.sgdb_key else []
                g["sgdb_results"] = results
                if not results:
                    cands = icons.candidates_for_extra(g, None)
                    g["candidates"] = cands
                    if not self._restore_selected_icon(g):  # FIX v7
                        g["selected_idx"] = icons.best_idx(cands)
                    g["icons_loaded"] = True
                    self._q.put(("ready", i))
                elif needs_disambiguation(g["name"], results):
                    g["ambiguous"] = True
                    g["icons_loaded"] = False
                    self._q.put(("ask_disambig", i, g["name"], results))
                    g["_disambig_event"] = threading.Event()
                    g["_disambig_event"].wait(timeout=300)
                    cands = icons.candidates_for_extra(g, g.get("sgdb_id"))
                    if _gid:
                        _sk = str(g.get("sgdb_id") or _gid)
                        for _cv in cands:
                            if _cv.get("type") in ("sgdb", "grid") and _cv.get("bytes"):  # FIX v7: też grid
                                _st.save_asset(_gid,"icons",
                                    str(_cv.get("remote_asset_id") or _cv.get("label","")),
                                    _cv["bytes"],_cv["w"],_cv["h"],sgdb_key=_sk,
                                    commit=False,  # FIX: batch
                                    url=_cv.get("url",""), tier="thumb")
                        _st.commit()  # FIX: jeden commit na grę
                    g["candidates"] = cands
                    if not self._restore_selected_icon(g):  # FIX v7
                        g["selected_idx"] = icons.best_idx(cands)
                    g["icons_loaded"] = True
                    g["ambiguous"] = False
                    self._q.put(("ready", i))
                else:
                    g["sgdb_id"] = results[0]["id"]
                    cands = icons.candidates_for_extra(g, g["sgdb_id"])
                    if _gid:
                        _sk = str(g["sgdb_id"])
                        with _st._lock:  # FIX v7
                            _st._db.execute("UPDATE games SET sgdb_id=? WHERE id=?",(_sk,_gid))
                        for _cv in cands:
                            if _cv.get("type") in ("sgdb", "grid") and _cv.get("bytes"):  # FIX v7: też grid
                                _st.save_asset(_gid,"icons",
                                    str(_cv.get("remote_asset_id") or _cv.get("label","")),
                                    _cv["bytes"],_cv["w"],_cv["h"],sgdb_key=_sk,
                                    commit=False,
                                    url=_cv.get("url",""), tier="thumb")
                        _st.commit()
                        # Stub z sgdb_id dla Extra/GOG/Epic (Fix 3)
                        _st.save_stub(_gid, self._build_stub_minimal(g))
                    g["candidates"] = cands
                    if not self._restore_selected_icon(g):  # FIX v7
                        g["selected_idx"] = icons.best_idx(cands)
                    g["icons_loaded"] = True
                    self._q.put(("ready", i))
        self._q.put(("done_scan", total))

    def _clear_grid(self):
        for w in self._grid.winfo_children():
            w.destroy()
        self._refs = []

    # FIX v7.4: zmiana wielkości podglądów suwakiem
    def _on_thumb_size_change(self, _val=None):
        self.config_data["thumb_size"] = int(self._thumb_var.get())
        self._save_settings_debounced()
        # debounce — przerysuj dopiero 250 ms po puszczeniu suwaka
        job = getattr(self, "_thumb_redraw_job", None)
        if job:
            try:
                self.after_cancel(job)
            except Exception:
                pass
        self._thumb_redraw_job = self.after(250, self._redraw_current_detail)

    def _redraw_current_detail(self):
        self._thumb_redraw_job = None
        if self.cur_idx is not None and 0 <= self.cur_idx < len(self.games):
            self._draw_detail(self.games[self.cur_idx])

    # FIX v7.4: scal assety z cache (SQLite/dysk) do kandydatów gry w UI.
    # Używane po SYNC CACHE — wcześniej pobrane grafiki były niewidoczne
    # do następnego skanu. Zwraca liczbę dodanych kandydatów.
    def _merge_cached_candidates(self, g: dict) -> int:
        gid = g.get("_game_id")
        if not gid:
            return 0
        try:
            cached = (self._asset_store.candidates_from_cache(gid, "icons")
                      + self._asset_store.candidates_from_cache(gid, "grids"))
        except Exception as e:
            print(f"[Sync merge] {g.get('name','?')}: {e}")
            return 0
        if not cached:
            return 0
        existing: set[str] = set()
        for c in g.get("candidates", []):
            for f in ("url", "remote_asset_id", "local_path"):
                v = c.get(f)
                if v:
                    existing.add(str(v))
        added = 0
        for c in cached:
            ids = {str(c.get(f)) for f in
                   ("url", "remote_asset_id", "local_path") if c.get(f)}
            if ids & existing:
                continue
            existing |= ids
            g.setdefault("candidates", []).append(c)
            added += 1
        if added:
            g["icons_loaded"] = True
            if g.get("selected_idx") is None:
                g["selected_idx"] = 0
        return added

    def _on_appmode_change(self):
        """Przełączenie trybu Desktop/.lnk ↔ Steam — przerysuj panel grafik."""
        if self.cur_idx is not None and 0 <= self.cur_idx < len(self.games):
            self._draw_detail(self.games[self.cur_idx])

    def _draw_detail(self, game):
        self._clear_grid()
        self._update_launch_label(game)
        # v8.2: tryb Steam — inny panel grafik (typy + wybór per typ).
        if getattr(self, "v_appmode", None) is not None and self.v_appmode.get() == "steam":
            self._draw_detail_steam(game)
            return
        if game.get("ambiguous") or not game["icons_loaded"]:
            tk.Label(self._grid,
                     text=("⚠ Oczekuje na wybór gry w oknie dialogowym..." if game.get("ambiguous")
                           else "Pobieranie ikon..."),
                     bg=C["bg"], fg=C["yel"], font=("Segoe UI", 11)).pack(pady=40)
            self._info.config(text="")
            return
        if not game["candidates"]:
            tk.Label(self._grid, text="Brak ikon dla tej gry.", bg=C["bg"], fg=C["fg2"],
                     font=("Segoe UI", 10)).pack(pady=40)
            self._info.config(text="")
            return
        THUMB = max(48, min(256, int(self.config_data.get("thumb_size", 100))))
        cols = max(1, (self._cv.winfo_width() or 900) // (THUMB + 36))
        sel = game["selected_idx"]
        uid = game.get("uid") or self._game_key(game)
        min_size = int(self.config_data.get("filters", {}).get("min_icon_size", DEFAULT_MIN_SIZE))

        # FIX v7: PERF — siatka budowana porcjami przez after(), żeby UI nie
        # zamarzał przy kilkudziesięciu kandydatach. Licznik generacji anuluje
        # stare przebiegi przy szybkim przełączaniu gier.
        self._draw_gen = getattr(self, "_draw_gen", 0) + 1
        gen = self._draw_gen
        cands = list(game["candidates"])
        BATCH = 12

        def _make_card(i, c):
            chosen = (i == sel)
            card = tk.Frame(self._grid, bg="#24273a" if chosen else C["bg2"],
                            highlightthickness=2,
                            highlightbackground=C["acc"] if chosen else C["bg3"])
            card.grid(row=i // cols, column=i % cols, padx=5, pady=5, sticky="n")
            thumb = None
            if c["type"] in ("sgdb", "grid"):
                # FIX v7: PERF — kolejność: mała miniatura WEBP z cache >
                # pełny plik > bajty (z cache po kluczu, nie dekodujemy
                # za każdym przerysowaniem)
                # FIX v7.4: miniatura WEBP ma 128 px — przy większym suwaku
                # czytamy pełny plik, żeby podgląd nie był rozmyty
                if c.get("thumb_path") and THUMB <= 128:
                    thumb = thumb_cached(c["thumb_path"], THUMB)
                if thumb is None and c.get("local_path"):
                    thumb = thumb_cached(c["local_path"], THUMB)
                if thumb is None and c.get("bytes"):
                    thumb = thumb_from_bytes_cached(
                        c["bytes"],
                        str(c.get("remote_asset_id") or c.get("url") or ""),
                        THUMB)
            elif c["type"] == "exe" and c.get("exe"):
                thumb = thumb_from_exe_cached(c["exe"], THUMB)  # FIX v7: cache
            if thumb:
                self._refs.append(thumb)
                tk.Label(card, image=thumb, bg=card["bg"], cursor="hand2").pack(padx=4, pady=(8, 2))
            else:
                tk.Label(card, text="[exe]", bg=card["bg"],
                         font=("Segoe UI", 28)).pack(padx=4, pady=(12, 2))
            ok = min(c["w"], c["h"]) >= min_size
            tk.Label(card, text=f"{c['w']}x{c['h']}", bg=card["bg"],
                     fg=C["grn"] if ok else C["red"],
                     font=("Segoe UI", 8, "bold")).pack()
            src = c["label"] if len(c["label"]) <= 22 else c["label"][:20] + "..."
            tk.Label(card, text=src, bg=card["bg"], fg=C["fg2"],
                     font=("Segoe UI", 7)).pack(pady=(0, 6))

            def on_click(event, _idx=i, _uid=uid):
                target = next((g for g in self.games if (g.get("uid") or self._game_key(g)) == _uid), None)
                if target is None:
                    return
                target["selected_idx"] = _idx
                # Zapis NATYCHMIAST po kliknięciu (stabilny klucz + steam_art) —
                # przeżywa rescan/restart i nagłe zamknięcie (dokończysz wybór).
                self._persist_now(target)
                if self.cur_idx is not None:
                    cur = self.games[self.cur_idx]
                    if (cur.get("uid") or self._game_key(cur)) == _uid:
                        self._draw_detail(target)
                        self._set_info(target)

            card.bind("<Button-1>", on_click)
            for ch in card.winfo_children():
                ch.bind("<Button-1>", on_click)

        def _build_batch(start):
            if gen != self._draw_gen or not self._grid.winfo_exists():
                return  # anulowane — użytkownik kliknął inną grę
            end = min(start + BATCH, len(cands))
            for i in range(start, end):
                _make_card(i, cands[i])
            if end < len(cands):
                self.after(1, lambda: _build_batch(end))

        _build_batch(0)
        self._set_info(game)

    def _draw_detail_steam(self, game):
        """Panel grafik w trybie Steam: zakładki typów + miniatury (wybór per typ).

        Wybory zapisywane do game["steam_art"] = {typ: url}. Dopasowanie SGDB
        (game["sgdb_id"]) jest WSPÓLNE z trybem .lnk — ustawiane przyciskiem
        „Ręczne wyszukiwanie tytułu…”. Renderuje w self._grid (pack)."""
        sgdb_key = self.config_data.get("api_keys", {}).get("sgdb_key", "")
        # Panel Steam bywa krótszy niż widok .lnk — przewiń na górę, żeby nie
        # zostać na starej pozycji (inaczej góra panelu jest poza ekranem).
        try:
            self._cv.yview_moveto(0)
        except Exception:
            pass

        bar = tk.Frame(self._grid, bg=C["bg"])
        bar.pack(fill="x", padx=6, pady=(6, 2))
        tk.Label(bar, text="Grafiki Steam:", bg=C["bg"], fg=C["acc"],
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        self._steam_tab_btns = {}   # ref do zakładek (aktualizacja znacznika ●/○)
        self._steam_cards = {}      # url -> karta (aktualizacja ramki bez reloadu)
        for key, label, _a, _b, _c in STEAM_ART_TYPES:
            mark = "●" if (game.get("steam_art") or {}).get(key) else "○"
            rb = tk.Radiobutton(bar, text=f"{mark} {label}",
                                variable=self._steam_art_type, value=key,
                                command=lambda g=game: self._draw_detail(g),
                                bg=C["bg"], fg=C["fg2"], selectcolor=C["bg3"],
                                activebackground=C["bg"], font=("Segoe UI", 8),
                                indicatoron=False, padx=6, pady=2)
            rb.pack(side="left", padx=2)
            self._steam_tab_btns[key] = rb

        if not sgdb_key:
            tk.Label(self._grid, text="Brak klucza SteamGridDB w Ustawieniach.",
                     bg=C["bg"], fg=C["red"], font=("Segoe UI", 10)).pack(pady=30)
            self._info.config(text="")
            return
        if not game.get("sgdb_id"):
            tk.Label(self._grid,
                     text=("Brak dopasowania SGDB dla tej gry.\n"
                           "Użyj „Ręczne wyszukiwanie tytułu…”, aby ustawić "
                           "(wspólne z trybem .lnk)."),
                     bg=C["bg"], fg=C["yel"], font=("Segoe UI", 10),
                     justify="left").pack(pady=30)
            self._info.config(text="")
            return

        tkey = self._steam_art_type.get()
        chosen = (game.get("steam_art") or {}).get(tkey)
        self._info.config(
            text=f"Typ „{tkey}”: {'wybrano grafikę' if chosen else 'brak wyboru'} "
                 "— kliknij miniaturę, aby wybrać.",
            fg=C["grn"] if chosen else C["fg2"])

        thumbs = tk.Frame(self._grid, bg=C["bg"])
        thumbs.pack(fill="both", expand=True, padx=6, pady=4)
        # thumbs zakrywa cały _grid — podepnij pod nią włączanie przewijania
        # kółkiem, żeby najechanie na obszar miniatur działało jak w trybie .lnk.
        if getattr(self, "_grid_scroll_enter", None):
            thumbs.bind("<Enter>", self._grid_scroll_enter)
            thumbs.bind("<Leave>", self._grid_scroll_leave)
        status = tk.Label(self._grid, text="Ładowanie miniatur…", bg=C["bg"],
                          fg=C["fg2"], font=("Segoe UI", 8))
        status.pack(anchor="w", padx=6)

        self._steam_art_token += 1
        token = self._steam_art_token
        gid = game["sgdb_id"]
        uid = game.get("uid") or self._game_key(game)
        # Rozmiar miniatur z suwaka „Podgląd" (wspólny z trybem .lnk).
        thumb_px = max(48, min(256, int(self.config_data.get("thumb_size", 100))))
        threading.Thread(target=self._steam_thumbs_worker,
                         args=(gid, tkey, token, thumbs, status, uid, thumb_px),
                         daemon=True).start()

    def _steam_thumbs_worker(self, gid, tkey, token, thumbs, status, uid, thumb_px=120):
        key = self.config_data.get("api_keys", {}).get("sgdb_key", "")
        items = steam_sgdb_list(gid, tkey, key, limit=30)

        def _build():
            if token != self._steam_art_token or not thumbs.winfo_exists():
                return
            if not items:
                if status.winfo_exists():
                    status.config(text="Brak grafik tego typu dla wybranej gry.")
                return
            if status.winfo_exists():
                status.config(text=f"{len(items)} grafik — kliknij, aby wybrać "
                                   "(ramka = wybrana).")
            game = next((g for g in self.games
                         if (g.get("uid") or self._game_key(g)) == uid), None)
            if game is None:
                return
            chosen = (game.get("steam_art") or {}).get(tkey)
            cols = max(1, (self._cv.winfo_width() or 700) // (thumb_px + 30))
            for idx, it in enumerate(items):
                url = it.get("url")
                thumb = it.get("thumb") or url
                card = tk.Frame(thumbs, bg=C["bg2"], highlightthickness=2,
                                highlightbackground=C["acc"] if chosen == url else C["bg3"])
                card.grid(row=idx // cols, column=idx % cols, padx=5, pady=5, sticky="n")
                if url:
                    self._steam_cards[url] = card   # do aktualizacji ramki bez reloadu
                # Placeholder w jednostkach tekstu (rezerwuje ~120 px). Po
                # załadowaniu obrazu przełączamy width/height na PIKSELE, bo
                # Label z obrazem interpretuje je w pikselach (inaczej obraz jest
                # przycięty do kilku pikseli).
                ph_w = max(6, thumb_px // 8)
                ph_h = max(3, thumb_px // 16)
                lbl = tk.Label(card, text="…", bg=C["bg3"], fg=C["fg2"],
                               width=ph_w, height=ph_h, cursor="hand2")
                lbl.pack(padx=4, pady=4)
                cb = lambda e, u=url, _uid=uid, _tk=tkey: self._steam_choose(_uid, _tk, u)
                lbl.bind("<Button-1>", cb)
                card.bind("<Button-1>", cb)
                self.after(30 * idx,
                           lambda l=lbl, t=thumb, tok=token: self._steam_load_thumb(l, t, tok, thumb_px))

        self.after(0, _build)

    def _steam_load_thumb(self, label, url, token, thumb_px=120):
        # FIX: pobieranie z sieci NIE może iść na wątku UI — steam_fetch_cached
        # przy zimnym cache robi fetch_api (timeout do 25 s), a 30 miniatur ×
        # synchronicznie = zamrożony program. Pobieramy w puli wątków, a
        # dekodowanie do PhotoImage (obiekt Tk) wykonujemy z powrotem na UI.
        if token != self._steam_art_token or not url:
            return
        pool = self._steam_thumb_executor()

        def _fetch():
            if token != self._steam_art_token:
                return
            try:
                b = steam_fetch_cached(url)             # sieć/dysk — POZA UI
            except Exception:
                b = None
            if not b:
                return

            def _apply():
                if token != self._steam_art_token:
                    return
                try:
                    if not label.winfo_exists():
                        return
                    ph = thumb_from_bytes_cached(b, url, thumb_px)
                    if ph:
                        self._refs.append(ph)
                        # width/height w PIKSELACH (obraz obecny) — inaczej Label
                        # użyłby jednostek tekstu i przyciął obraz.
                        label.config(image=ph, text="",
                                     width=ph.width(), height=ph.height(),
                                     bg=C["bg3"])
                except Exception:
                    pass
            try:
                self.after(0, _apply)
            except Exception:
                pass

        try:
            pool.submit(_fetch)
        except Exception:
            pass

    def _steam_thumb_executor(self):
        """Leniwa, ograniczona pula wątków do pobierania miniatur Steam."""
        pool = getattr(self, "_steam_thumb_pool", None)
        if pool is None:
            pool = ThreadPoolExecutor(max_workers=6,
                                      thread_name_prefix="steamthumb")
            self._steam_thumb_pool = pool
        return pool

    def _steam_choose(self, uid, tkey, url):
        game = next((g for g in self.games
                     if (g.get("uid") or self._game_key(g)) == uid), None)
        if game is None:
            return
        art = dict(game.get("steam_art") or {})
        art[tkey] = url
        game["steam_art"] = art
        self._persist_now(game)   # zapis natychmiast po kliknięciu w grafikę
        # Aktualizacja W MIEJSCU (bez przeładowania panelu / bez sieci):
        # przenieś ramkę zaznaczenia, zaktualizuj znacznik zakładki i info.
        for u, card in getattr(self, "_steam_cards", {}).items():
            try:
                if card.winfo_exists():
                    card.config(highlightbackground=C["acc"] if u == url else C["bg3"])
            except Exception:
                pass
        btn = getattr(self, "_steam_tab_btns", {}).get(tkey)
        if btn is not None:
            try:
                lab = next((l for k, l, *_ in STEAM_ART_TYPES if k == tkey), tkey)
                if btn.winfo_exists():
                    btn.config(text=f"● {lab}")
            except Exception:
                pass
        try:
            self._info.config(
                text=f"Typ „{tkey}”: wybrano grafikę — kliknij inną, aby zmienić.",
                fg=C["grn"])
        except Exception:
            pass

    def _set_info(self, game):
        min_size = 0
        if game["candidates"] and game["selected_idx"] is not None:
            c = game["candidates"][game["selected_idx"]]
            ok = True
            tag = {"extra": " [Extra]", "epic": " [Epic]", "gog": " [GOG]"}.get(game.get("source", ""), "")
            type_tag = " [plakat]" if c.get("type") == "grid" else ""
            self._info.config(
                text=f"Ikona #{game['selected_idx']+1}: {c['label']} {'OK' if ok else 'za mała'}{tag}{type_tag}",
                fg=C["grn"] if ok else C["red"],
            )
        else:
            self._info.config(text="Brak wybranej ikony", fg=C["fg2"])

    # -------- Dry run i tworzenie skrótów --------

    # ── ROM settings helpers ────────────────────────────────────────────────────

    def _refresh_rom_combobox(self):
        """Odśwież listę systemów w comboboxie ROM."""
        names = [s["name"] for s in self._rom_systems()]
        self._rom_cb["values"] = names
        if names:
            if self.v_rom_system.get() not in names:
                self.v_rom_system.set(names[0])
        else:
            self.v_rom_system.set("")

    def _rom_scan_click(self):
        """Przycisk SKANUJ ROM — wczytuje wybrany system z combobox."""
        name = self.v_rom_system.get().strip()
        if not name:
            messagebox.showwarning("ROMy", "Wybierz system ROM z listy lub dodaj go w ⚙ ROMy.")
            return
        self._rom_run_platform(name)

    def _open_rom_settings(self):
        """Dialog CRUD systemów ROM."""
        rs = self.config_data.setdefault("rom_support", {"enabled": False, "systems": []})
        rs.setdefault("systems", [])

        win = tk.Toplevel(self)
        win.title("Konfiguracja systemów ROM")
        win.configure(bg=C["bg"])
        win.resizable(True, False)
        win.grab_set()

        # Kopia robocza
        systems: list[dict] = [dict(s) for s in rs["systems"]]

        v_enabled     = tk.BooleanVar(value=bool(rs.get("enabled", False)))
        v_base_rom    = tk.StringVar(value=rs.get("base_rom_dir", ""))
        v_base_emu    = tk.StringVar(value=rs.get("base_emu_dir", ""))

        tk.Checkbutton(win, text="Włącz obsługę ROM-ów",
                       variable=v_enabled, bg=C["bg"], fg=C["fg"],
                       selectcolor=C["bg3"], activebackground=C["bg"],
                       font=("Segoe UI", 9)).pack(anchor="w", padx=14, pady=(12, 4))

        # Katalogi bazowe (wspólne dla wszystkich systemów)
        base_f = tk.LabelFrame(win, text="Katalogi bazowe",
                               bg=C["bg"], fg=C["fg2"],
                               font=("Segoe UI", 8))
        base_f.pack(fill="x", padx=14, pady=(0, 6))
        def _on_base_emu(*_):
            emu = v_base_emu.get().strip()
            if emu and not v_base_rom.get().strip():
                roms_sub = Path(emu) / "roms"
                if roms_sub.is_dir():
                    v_base_rom.set(str(roms_sub))
        v_base_emu.trace_add("write", _on_base_emu)

        for lbl_txt, var in [("ROM-y:", v_base_rom), ("Emulatory:", v_base_emu)]:
            br = tk.Frame(base_f, bg=C["bg"])
            br.pack(fill="x", padx=8, pady=3)
            tk.Label(br, text=lbl_txt, bg=C["bg"], fg=C["fg2"],
                     font=("Segoe UI", 9), width=10, anchor="w").pack(side="left")
            tk.Entry(br, textvariable=var, bg=C["bg3"], fg=C["fg"],
                     insertbackground="white", relief="flat",
                     font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True, padx=(0, 4))
            def _bdir(v=var):
                p = filedialog.askdirectory(parent=win)
                if p: v.set(p)
            tk.Button(br, text="…", command=_bdir,
                      bg=C["bg3"], fg=C["acc"], relief="flat", padx=6
                      ).pack(side="left")
        tk.Label(base_f,
                 text="  Używane do automatycznego uzupełniania ścieżek przy dodawaniu systemu z szablonu.",
                 bg=C["bg"], fg=C["fg2"], font=("Segoe UI", 7, "italic")
                 ).pack(anchor="w", padx=8, pady=(0, 4))

        # Tabela systemów
        tbl_frame = tk.Frame(win, bg=C["bg2"],
                             highlightthickness=1, highlightbackground=C["bg3"])
        tbl_frame.pack(fill="both", padx=14, pady=4, expand=True)

        HDR_BG = C["bg3"]
        for col, (text, w) in enumerate([
            ("Nazwa", 8), ("Folder ROM", 22), ("Emulator EXE", 22),
            ("Podkat.", 7), ("Parametry / Ext prio", 20),
        ]):
            tk.Label(tbl_frame, text=text, bg=HDR_BG, fg=C["acc"],
                     font=("Segoe UI", 8, "bold"), width=w, anchor="w",
                     padx=6, pady=4).grid(row=0, column=col, sticky="ew", padx=1, pady=1)
        tk.Label(tbl_frame, text="", bg=HDR_BG, width=5).grid(row=0, column=5)

        row_widgets: list[dict] = []

        def _refresh_table():
            for w in tbl_frame.grid_slaves():
                if int(w.grid_info()["row"]) > 0:
                    w.destroy()
            row_widgets.clear()
            for r, sys in enumerate(systems, start=1):
                bg = C["bg"] if r % 2 == 0 else C["bg2"]
                v_name    = tk.StringVar(value=sys.get("name", ""))
                v_rom     = tk.StringVar(value=sys.get("rom_dir", ""))
                v_exe     = tk.StringVar(value=sys.get("emulator", ""))
                v_subdirs = tk.BooleanVar(value=bool(sys.get("roms_in_subdirs", False)))
                v_args    = tk.StringVar(value=sys.get("launch_args", ""))
                v_ext     = tk.StringVar(value=sys.get("primary_ext", "m3u,cue,iso,chd,bin"))

                # Kol 0: Nazwa
                tk.Entry(tbl_frame, textvariable=v_name, width=9,
                         bg=C["bg3"], fg=C["fg"], insertbackground="white",
                         relief="flat", font=("Segoe UI", 9)
                         ).grid(row=r, column=0, padx=2, pady=1)

                # Kol 1+2: Folder ROM / Emulator z browse
                for col, (var, is_dir) in enumerate([(v_rom, True), (v_exe, False)], start=1):
                    cell = tk.Frame(tbl_frame, bg=bg)
                    cell.grid(row=r, column=col, sticky="ew", padx=2, pady=1)
                    tk.Entry(cell, textvariable=var, bg=C["bg3"], fg=C["fg"],
                             insertbackground="white", relief="flat",
                             font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True)
                    _is = is_dir
                    def _browse(v=var, d=_is):
                        pth = (filedialog.askdirectory(parent=win)
                               if d
                               else filedialog.askopenfilename(
                                   parent=win,
                                   filetypes=[("EXE", "*.exe"), ("Wszystkie", "*")]))
                        if pth: v.set(pth)
                    tk.Button(cell, text="…", command=_browse,
                              bg=C["bg3"], fg=C["acc"],
                              relief="flat", padx=4).pack(side="left")
                    # Dla kolumny Emulator (nie ROM folder): przycisk 🎮
                    if not is_dir:
                        def _pick(ve=v_exe, va=v_args, vn=v_name):
                            dlg = EmuPickDialog(win, vn.get().strip() or "?",
                                               v_base_emu.get().strip())
                            if dlg.result_exe:
                                ve.set(dlg.result_exe)
                                if dlg.result_args:
                                    va.set(dlg.result_args)
                        tk.Button(cell, text="🎮", command=_pick,
                                  bg=C["bg3"], fg=C["orn"],
                                  relief="flat", padx=4,
                                  font=("Segoe UI", 9)).pack(side="left")

                # Kol 3: ☐ Podkat. (roms_in_subdirs)
                chk_cell = tk.Frame(tbl_frame, bg=bg)
                chk_cell.grid(row=r, column=3, padx=4, pady=1)
                tk.Checkbutton(chk_cell, variable=v_subdirs, bg=bg,
                               activebackground=bg, selectcolor=C["bg3"],
                               ).pack()

                # Kol 4: Parametry + Ext priority (2-liniowy)
                args_cell = tk.Frame(tbl_frame, bg=bg)
                args_cell.grid(row=r, column=4, sticky="ew", padx=2, pady=1)
                tk.Entry(args_cell, textvariable=v_args, bg=C["bg3"], fg=C["fg"],
                         insertbackground="white", relief="flat",
                         font=("Segoe UI", 9),
                         ).pack(fill="x", expand=True)
                ext_row = tk.Frame(args_cell, bg=bg)
                ext_row.pack(fill="x")
                tk.Label(ext_row, text="ext:", bg=bg, fg=C["fg2"],
                         font=("Segoe UI", 7)).pack(side="left")
                tk.Entry(ext_row, textvariable=v_ext, bg=C["bg3"], fg=C["fg2"],
                         insertbackground="white", relief="flat",
                         font=("Segoe UI", 7), width=24).pack(side="left",
                                                               fill="x", expand=True)

                # Kol 5: ✕
                btn_f = tk.Frame(tbl_frame, bg=bg)
                btn_f.grid(row=r, column=5, padx=4, pady=1)
                idx = r - 1
                tk.Button(btn_f, text="✕", fg=C["red"], bg=C["bg3"],
                          relief="flat", padx=4,
                          command=lambda i=idx: _del(i)).pack()
                row_widgets.append({
                    "name": v_name, "rom_dir": v_rom, "emulator": v_exe,
                    "roms_in_subdirs": v_subdirs,
                    "launch_args": v_args,
                    "primary_ext": v_ext,
                })

        def _del(idx):
            systems.pop(idx)
            _refresh_table()

        def _add():
            systems.append({"name": "Nowy", "rom_dir": "", "emulator": "",
                             "roms_in_subdirs": False, "launch_args": "",
                             "primary_ext": "m3u,cue,iso,chd,bin"})
            _refresh_table()

        _refresh_table()

        # ── Dolny pasek: Dodaj własny + Dodaj z szablonu ─────────────────
        add_row = tk.Frame(win, bg=C["bg"])
        add_row.pack(fill="x", padx=14, pady=(4, 2))

        # "Dodaj z szablonu" — dropdown z ROM_SYSTEM_PRESETS
        preset_names = [f"{p['display']}  ({p['name']})" for p in ROM_SYSTEM_PRESETS]
        v_preset = tk.StringVar(value=preset_names[0] if preset_names else "")
        preset_cb = ttk.Combobox(add_row, textvariable=v_preset,
                                 values=preset_names, state="readonly", width=30)
        preset_cb.pack(side="left", padx=(0, 4))

        def _add_from_template():
            sel = v_preset.get()
            # Znajdź preset po display string
            preset = next(
                (p for p in ROM_SYSTEM_PRESETS
                 if f"{p['display']}  ({p['name']})" == sel),
                None
            )
            if not preset:
                return
            base_rom = v_base_rom.get().strip()
            base_emu = v_base_emu.get().strip()
            # Auto-uzupełnij rom_dir: szukaj pierwszego istniejącego folderu
            # (obsługa obu konwencji: EmulationStation i No-Intro/Libretro)
            auto_rom = _rom_find_dir(base_rom, preset.get("dir_names", [preset["name"]]))
            systems.append({
                "name":            preset["name"],
                "rom_dir":         auto_rom,
                "emulator":        base_emu,
                "roms_in_subdirs": preset.get("roms_in_subdirs", False),
                "launch_args":     preset.get("launch_args", ""),
                "primary_ext":     preset.get("primary_ext", "m3u,cue,iso,chd,bin"),
                "all_exts":        preset.get("all_exts",
                                              preset.get("primary_ext", "m3u,cue,iso,chd,bin")),
            })
            _refresh_table()
            # Pokaż hint o emulatorze
            note = preset.get("note", "")
            if note:
                _pn = preset['name']; _pd = preset['display']
                win.after(200, lambda pn=_pn, pd=_pd, no=note:
                          messagebox.showinfo(
                    f"Szablon {pn}",
                    f"Dodano {pd}.\n\n"
                    f"Wskazówka emulatora: {no}\n\n"
                    "Uzupełnij ścieżkę emulatora w tabeli.",
                    parent=win,
                ))

        tk.Button(add_row, text="+ Dodaj z szablonu",
                  command=_add_from_template,
                  bg=C["grn"], fg=C["bg"],
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, pady=3,
                  cursor="hand2").pack(side="left", padx=(0, 16))

        tk.Button(add_row, text="+ Dodaj własny",
                  command=_add,
                  bg=C["bg3"], fg=C["grn"],
                  relief="flat", padx=10, pady=3,
                  cursor="hand2").pack(side="left")

        # Info o katalogach
        info_f = tk.Frame(win, bg=C["bg2"],
                          highlightthickness=1, highlightbackground=C["bg3"])
        info_f.pack(fill="x", padx=14, pady=(4, 8))
        tk.Label(info_f, text="Katalogi (automatyczne):",
                 bg=C["bg2"], fg=C["fg2"],
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=8, pady=(6,2))
        tk.Label(info_f, text=f"  Ikony (Cache):  {CACHE_DIR}",
                 bg=C["bg2"], fg=C["acc"], font=("Segoe UI", 8)).pack(anchor="w", padx=8)
        tk.Label(info_f, text=f"  Skróty (LINKS): {LINKS_DIR}/<nazwa_systemu>/",
                 bg=C["bg2"], fg=C["acc"], font=("Segoe UI", 8)).pack(anchor="w", padx=8, pady=(0,6))

        def _save():
            # Zbierz dane z widgetów
            new_systems = []
            for rw in row_widgets:
                name = rw["name"].get().strip()
                if not name:
                    continue
                new_systems.append({
                    "name":            name,
                    "rom_dir":         rw["rom_dir"].get().strip(),
                    "emulator":        rw["emulator"].get().strip(),
                    "roms_in_subdirs": bool(rw["roms_in_subdirs"].get()),
                    "launch_args":     rw["launch_args"].get().strip(),
                    "primary_ext":     rw["primary_ext"].get().strip()
                                       or "m3u,cue,iso,chd,bin",
                })
            rs["enabled"]      = bool(v_enabled.get())
            rs["base_rom_dir"] = v_base_rom.get().strip()
            rs["base_emu_dir"] = v_base_emu.get().strip()
            rs["systems"]      = new_systems
            self._save_settings()
            self._refresh_rom_combobox()
            # FIX v7.9.1: nowo dodany/usunięty system musi od razu pojawić
            # się też w dropdownie filtra widoku biblioteki ("ROM: ...") —
            # wcześniej pasek platform był budowany tylko przy starcie,
            # więc świeży system był widoczny dopiero po restarcie.
            self._rebuild_platform_bar()
            # Jeśli aktywny filtr wskazywał usunięty system → wróć do "all"
            _valid = {"all", "pc", "rom_all"} | {s["name"]
                                                 for s in self._rom_systems()}
            if self.v_source_filter.get() not in _valid:
                self._set_source_filter("all")
                self._rebuild_list()
            win.destroy()

        bot = tk.Frame(win, bg=C["bg"])
        bot.pack(fill="x", padx=14, pady=(0, 12))
        tk.Button(bot, text="Zapisz", command=_save, bg=C["grn"], fg=C["bg"],
                  relief="flat", padx=14, pady=5, cursor="hand2").pack(side="right", padx=(4,0))
        tk.Button(bot, text="Anuluj", command=win.destroy, bg=C["bg3"], fg=C["fg2"],
                  relief="flat", padx=10, pady=5, cursor="hand2").pack(side="right")

    def _flat_scan_with_ext_fallback(self, folder: str, known_exts: set[str],
                                     plat: str, primary_ext: list[str],
                                     system_cfg: dict | None) -> list[Path]:
        """Tryb płaski: gdy skan zwrócił 0 wyników mimo że folder ma pliki.

        Zbiera wszystkie rozszerzenia plików w folderze,
        sprawdza czy są pliki poza known_exts,
        i jeśli tak — pyta użytkownika RAZ o właściwe rozszerzenie.
        """
        base = Path(folder)
        if not base.is_dir():
            return []

        # Zbierz rozszerzenia wszystkich plików w folderze (bez podkatalogów)
        all_files = [p for p in base.rglob("*") if p.is_file()]
        unknown_ext_counts: dict[str, int] = {}
        for p in all_files:
            ext = p.suffix.lower().lstrip(".")
            if ext and ext not in known_exts and ext not in ("txt","nfo","png","jpg","xml","dat"):
                unknown_ext_counts[ext] = unknown_ext_counts.get(ext, 0) + 1

        if not unknown_ext_counts:
            return []   # folder naprawdę pusty lub tylko znane ext bez wyników

        # Zapytaj użytkownika — ta sama logika co w _ask_ext_for_system
        chosen = self._ask_ext_for_system(plat, unknown_ext_counts)
        if not chosen:
            return []

        # Zapisz wybrany ext do system_cfg i configa (nie pytamy ponownie)
        if system_cfg is not None:
            existing = system_cfg.get("primary_ext", "")
            exts_list = [e.strip().lstrip(".").lower()
                         for e in existing.split(",") if e.strip()]
            if chosen not in exts_list:
                exts_list.insert(0, chosen)
                system_cfg["primary_ext"] = ",".join(exts_list)
                # Dopisz też do all_exts
                all_e = system_cfg.get("all_exts", "")
                all_list = [e.strip().lstrip(".").lower()
                            for e in all_e.split(",") if e.strip()]
                if chosen not in all_list:
                    all_list.insert(0, chosen)
                    system_cfg["all_exts"] = ",".join(all_list)
                # Zapisz do configu
                rs = self.config_data.get("rom_support", {})
                for s in rs.get("systems", []):
                    if s.get("name") == plat:
                        s["primary_ext"] = system_cfg["primary_ext"]
                        s["all_exts"]    = system_cfg["all_exts"]
                        break
                self.after(0, self._save_settings)
                print(f"[ROM flat] zapamiętano ext '{chosen}' dla {plat!r}")

        # Reskanuj z nowym rozszerzeniem
        new_extra = known_exts | {chosen}
        return self._rom_m3u_bundle(self._rom_scan(folder, new_extra),
                                    primary_ext=primary_ext)

    def _rom_scan_subdirs(self, folder: str, primary_ext: list[str],
                          plat: str = "", system_cfg: dict | None = None
                          ) -> list[Path]:
        """Tryb podkatalogów: każdy podkatalog = jedna gra.

        Gdy żaden plik nie pasuje do primary_ext, zbiera wszystkie rozszerzenia
        i pyta użytkownika RAZ (jedno pytanie na system).
        Wybór jest zapamiętywany w system_cfg["primary_ext"] i configu.
        """
        base = Path(folder)
        if not base.is_dir():
            return []

        # Zbierz WSZYSTKIE podkatalogi z ich plikami
        subdirs: list[tuple[Path, list[Path]]] = []
        all_found_exts: dict[str, int] = {}   # ext → liczba plików
        # NOWE v7.8 (PS3/RPCS3): pliki .lnk leżące BEZPOŚREDNIO w katalogu
        # ROM-ów to skróty utworzone przez emulator — każdy .lnk = jedna gra.
        toplevel_lnk: list[Path] = []

        for d in sorted(base.iterdir()):
            if not d.is_dir():
                if d.is_file() and d.suffix.lower() == ".lnk":
                    toplevel_lnk.append(d)
                continue
            files = [p for p in sorted(d.iterdir()) if p.is_file()]
            if not files:
                continue
            for p in files:
                ext = p.suffix.lower().lstrip(".")
                if ext:
                    all_found_exts[ext] = all_found_exts.get(ext, 0) + 1
            subdirs.append((d, files))

        if not subdirs:
            return toplevel_lnk    # v7.8: same .lnk (np. czysty setup RPCS3)

        # Sprawdź czy primary_ext pasuje do czegokolwiek
        pri = list(primary_ext)
        matched = any(
            any(p.suffix.lower().lstrip(".") in pri for p in files)
            for _, files in subdirs
        )

        if not matched and all_found_exts:
            # Żaden plik nie pasuje do listy priorytetów →
            # zapytaj użytkownika RAZ o main ext dla tego systemu
            chosen = self._ask_ext_for_system(plat, all_found_exts)
            if chosen:
                pri = [chosen] + pri   # wybrane ext na pierwszym miejscu
                # Zapisz do system_cfg i do configa żeby nie pytać ponownie
                if system_cfg is not None:
                    existing = system_cfg.get("primary_ext", "")
                    exts_list = [e.strip().lstrip(".").lower()
                                 for e in existing.split(",") if e.strip()]
                    if chosen not in exts_list:
                        exts_list.insert(0, chosen)
                        system_cfg["primary_ext"] = ",".join(exts_list)
                        # Persist to config immediately
                        rs = self.config_data.get("rom_support", {})
                        for s in rs.get("systems", []):
                            if s.get("name") == plat:
                                s["primary_ext"] = system_cfg["primary_ext"]
                                break
                        self.after(0, self._save_settings)
                        print(f"[ROM] zapamiętano ext '{chosen}' dla {plat!r}")

        # Wybierz main plik z każdego podkatalogu wg zaktualizowanego pri
        result: list[Path] = list(toplevel_lnk)   # v7.8: .lnk zawsze jako gry
        for d, files in subdirs:
            ext_files = [p for p in files if p.suffix.lower().lstrip(".") in
                         (frozenset(pri) | self._DISC_EXTS)]
            if not ext_files:
                continue   # brak pasujących plików — pomiń katalog
            main = self._rom_pick_main_file(ext_files, pri)
            result.append(main)
        return result

    def _ask_ext_for_system(self, plat: str,
                            ext_counts: dict[str, int]) -> str | None:
        """Pokaż dialog wyboru ext w głównym wątku i poczekaj na odpowiedź.

        Wywoływane z wątku skanowania → synchronizacja przez threading.Event.
        """
        result_holder: list[str | None] = [None]
        evt = threading.Event()

        def _show_in_main():
            dlg = RomExtPickDialog(self, plat, ext_counts)
            result_holder[0] = dlg.result_ext
            evt.set()

        self.after(0, _show_in_main)
        evt.wait(timeout=180)    # czekaj max 3 minuty na odpowiedź
        return result_holder[0]

    def _rom_pick_main_file(self, files: list[Path], priority: list[str]) -> Path:
        """Wybierz główny plik dla emulatora z listy plików w folderze gry.

        Pierwszeństwo: .m3u (playlist multi-disc) > .cue > .iso > .chd > reszta.
        """
        # FIX v7.4: gdy w folderze jest arkusz (.cue/.gdi/.m3u), surowe
        # pliki danych nie mogą być plikiem uruchamiającym — nawet jeśli
        # "bin" stoi wyżej w skonfigurowanym priorytecie
        has_sheet = any(f.suffix.lower() in (".cue", ".gdi", ".m3u")
                        for f in files)
        cand_files = ([f for f in files
                       if f.suffix.lower() not in (".bin", ".img",
                                                   ".raw", ".sub")]
                      if has_sheet else files) or files
        for ext in priority:
            for f in cand_files:
                if f.suffix.lower().lstrip(".") == ext:
                    return f
        # Fallback wg rankingu rozszerzeń (cue/gdi przed bin)
        return min(cand_files, key=lambda p: self._main_file_sort_key(p))

    def _rom_scan(self, folder: str,
                  extra_exts: set[str] | None = None) -> list[Path]:
        """Skanuje folder ROM-ów, zwraca listę plików posortowaną .m3u-pierwsze.

        extra_exts: dodatkowe rozszerzenia specyficzne dla platformy
                    (np. nes, z64, gba) nie zawarte w domyślnym zestawie.
        """
        exts = {"m3u","chd","cue","iso","bin","img","ccd","sub","mdf","nrg","zip","7z",
                "lnk"}  # .lnk zawsze (gotowy skrót emulatora — jak PS3/X360)
        if extra_exts:
            exts |= extra_exts
        base = Path(folder)
        if not base.is_dir():
            return []
        files = [p for p in base.rglob("*")
                 if p.is_file() and p.suffix.lower().lstrip(".") in exts]
        files.sort(key=lambda p: (0 if p.suffix.lower() == ".m3u" else 1, p.name.lower()))
        return files

    # Pliki obrazów dysków obsługiwane przez emulatory
    _DISC_EXTS = frozenset(
        {"chd", "cue", "iso", "bin", "img", "ccd", "mdf", "nrg", "zip", "7z",
         # Kartridże i ROM-y
         "n64", "z64", "v64", "nes", "fds", "sfc", "smc", "gba", "gb", "gbc",
         "nds", "gdi", "rvz", "gcm", "wbfs", "jag", "lha", "pce", "md",
         "sms", "gg", "a26", "pbi"}
    )

    def _m3u_referenced_files(self, m3u_path: Path) -> set[Path]:
        """Czyta plik .m3u i zwraca zbiór absolutnych ścieżek referencowanych dysków.

        Format M3U: jedna ścieżka per linia, linie zaczynające się od # to komentarze.
        Ścieżki mogą być relatywne do katalogu .m3u lub absolutne.
        """
        refs: set[Path] = set()
        try:
            for line in m3u_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                ref = Path(line)
                if not ref.is_absolute():
                    ref = m3u_path.parent / ref
                try:
                    refs.add(ref.resolve())
                except Exception:
                    refs.add(ref)
        except Exception:
            pass
        return refs

    @staticmethod
    def _cue_gdi_referenced_files(path: Path) -> set[Path]:
        """FIX v7.4: zwróć pliki danych referencowane przez .cue lub .gdi.

        .cue:  linie  FILE "nazwa.bin" BINARY
        .gdi:  pierwsza linia = liczba ścieżek, kolejne:
               <nr> <lba> <typ> <sectorsize> <plik> <offset>
        Dzięki temu .bin/.raw/.img będące ścieżkami płyty są traktowane
        jako "pokryte" przez plik główny (jak dyski przez M3U) i nie
        stają się osobnymi grami ani plikiem uruchamiającym.
        """
        refs: set[Path] = set()
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return refs
        base = path.parent
        ext = path.suffix.lower()
        if ext == ".cue":
            for m in re.finditer(r'FILE\s+"([^"]+)"', text, flags=re.I):
                refs.add((base / m.group(1)).resolve())
            # wariant bez cudzysłowów: FILE nazwa.bin BINARY
            for m in re.finditer(r'FILE\s+([^"\s]+)\s+\w+', text, flags=re.I):
                refs.add((base / m.group(1)).resolve())
        elif ext == ".gdi":
            for line in text.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 5:
                    # plik może być w cudzysłowach (spacje w nazwie)
                    m = re.search(r'"([^"]+)"', line)
                    fname = m.group(1) if m else parts[4]
                    refs.add((base / fname).resolve())
        return refs

    _LNK_ROM_EXTS = frozenset({
        ".iso", ".chd", ".cue", ".gdi", ".bin", ".img", ".pkg", ".rvz",
        ".wbfs", ".gcm", ".nrg", ".mdf", ".ccd", ".xex", ".god"})

    def _lnk_referenced_files(self, lnk_path: Path) -> set[Path]:
        """Pliki ROM, do których odnosi się skrót .lnk (z target/args).

        Dzięki temu surowy .iso/.chd uruchamiany przez ten .lnk NIE staje się
        osobną (zwykle niedziałającą — bez emulatora) grą; .lnk go „pokrywa",
        jak .m3u pokrywa dyski. Xenia/RPCS3 trzymają ścieżkę gry w argumentach."""
        refs: set[Path] = set()
        try:
            tgt, args, _wd = read_lnk_target(str(lnk_path))
        except Exception:
            return refs
        parent = lnk_path.parent
        cands: list[str] = list(re.findall(r'"([^"]+)"', f"{tgt} {args}"))
        cands += [t for t in re.split(r"\s+", args or "") if (":" in t or "\\" in t or "/" in t)]
        for cs in cands:
            cs = cs.strip().strip('"')
            if not cs:
                continue
            try:
                p = Path(cs)
                if not p.is_absolute():
                    p = parent / p
                if p.suffix.lower() in self._LNK_ROM_EXTS:
                    try:
                        refs.add(p.resolve())
                    except Exception:
                        refs.add(p)
            except Exception:
                continue
        return refs

    @staticmethod
    def _norm_rom_stem(stem: str) -> str:
        """Znormalizowany rdzeń nazwy: bez (region)/[tag] i „Disc N"."""
        s = str(stem).lower()
        s = re.sub(r"[ _.-]*(disc|disk)\s*\d+", "", s, flags=re.I)
        changed = True
        while changed:
            s2 = re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()
            s2 = re.sub(r"\s*\[[^\]]*\]\s*$", "", s2).strip()
            changed = (s2 != s); s = s2
        return s

    # Ranking rozszerzeń przy wyborze pliku głównego gry:
    # playlisty/arkusze (m3u, cue, gdi, ccd) PRZED obrazami,
    # surowe dane (.bin/.img/.raw/.sub) ZAWSZE na końcu.
    # FIX v7.4: wcześniej wygrywał porządek alfabetyczny — .bin < .cue,
    # więc np. gry Dreamcast startowały z .bin (emulator wykrywał NAOMI
    # zamiast Dreamcasta i gra się nie uruchamiała).
    # .lnk = gotowy skrót emulatora → najwyższy priorytet (wygrywa z surowym .iso).
    _MAIN_FILE_EXT_RANK = {
        "lnk": 0, "m3u": 0, "cue": 1, "gdi": 2, "ccd": 3, "mds": 4, "mdf": 40,
        "cdi": 10, "chd": 11, "iso": 12, "rvz": 13, "cso": 14, "pbp": 15,
        "nrg": 30,
        "bin": 90, "img": 91, "raw": 92, "sub": 93,
    }

    @classmethod
    def _main_file_sort_key(cls, p: Path, priority: list[str] | None = None):
        ext = p.suffix.lower().lstrip(".")
        if priority and ext in priority:
            rank = priority.index(ext)          # konfiguracja systemu wygrywa
        else:
            rank = cls._MAIN_FILE_EXT_RANK.get(ext, 50)
            if priority:
                rank += len(priority)           # za skonfigurowanymi ext
        return (rank, p.name.lower())

    def _rom_m3u_bundle(self, roms: list,
                        primary_ext: list[str] | None = None) -> list:
        """Filtruje listę ROM-ów tak by M3U zastępowały referencowane dyski.

        Algorytm (robust, oparty na treści M3U, nie na podobieństwie nazw):

        1. Wczytaj wszystkie pliki .m3u i zbierz dokładne ścieżki dysków
           które każde M3U referuje.
        2. Usuń z listy dowolny plik dysku który jest referencowany przez
           jakiekolwiek M3U — jest on już objęty playlistą.
        3. Zwróć: M3U + pozostałe pliki które NIE są referencowane.

        Dlaczego nie grupowanie po nazwie:
          'Legend of Dragoon (USA).m3u' vs 'Legend of Dragoon, The (USA) (Disc 1).chd'
          mają różne znormalizowane stemmy → stara metoda zwracała OBE.
          Nowa metoda czyta zawartość M3U i wie dokładnie co zakrywa.

        Pliki multi-disc bez M3U: zwracamy tylko pierwszy dysk
        (emulatory zazwyczaj same wykrywają kolejne dyski lub użytkownik może
        ręcznie zamienić w emulatorze).
        """
        m3u_files  = [p for p in roms if p.suffix.lower() == ".m3u"]
        # Traktujemy WSZYSTKIE nie-M3U pliki jako pliki gier.
        # _rom_scan() już przefiltrował po rozszerzeniach dla tej platformy
        # (extra_exts), więc nie filtrujemy ponownie przez _DISC_EXTS —
        # to wykluczałoby formaty kartridżowe (.n64, .z64, .nes, .sfc, .gba itp.)
        game_files = [p for p in roms if p.suffix.lower() != ".m3u"]

        # Zbiór absolutnych ścieżek plików pokrytych przez M3U
        covered: set[Path] = set()
        for m3u in m3u_files:
            covered |= self._m3u_referenced_files(m3u)

        # FIX v7.4: pliki danych referencowane przez .cue/.gdi też są
        # "pokryte" — gra ma być uruchamiana plikiem .cue/.gdi, a nie .bin
        for sheet in game_files:
            if sheet.suffix.lower() in (".cue", ".gdi"):
                covered |= self._cue_gdi_referenced_files(sheet)

        # X360/PS3 itp.: skróty .lnk (gotowe komendy emulatora) POKRYWAJĄ surowe
        # pliki, które uruchamiają — inaczej ten sam .iso stałby się drugą,
        # niedziałającą grą (bez emulatora). Pokrycie: 1) po ścieżce z args .lnk,
        # 2) fallback po znormalizowanej nazwie (region/tag pominięte).
        lnk_files = [p for p in game_files if p.suffix.lower() == ".lnk"]
        if lnk_files:
            lnk_norms = {self._norm_rom_stem(p.stem) for p in lnk_files}
            for lk in lnk_files:
                covered |= self._lnk_referenced_files(lk)
            for p in game_files:
                if p.suffix.lower() == ".lnk":
                    continue
                if self._norm_rom_stem(p.stem) in lnk_norms:
                    try:
                        covered.add(p.resolve())
                    except Exception:
                        covered.add(p)

        # Pliki które NIE są referencowane przez żadne M3U
        uncovered = [p for p in game_files if p.resolve() not in covered]

        if covered:
            print(f"[ROM] {len(m3u_files)} M3U, {len(lnk_files)} .lnk, "
                  f"{len(game_files) - len(uncovered)} pokrytych, "
                  f"{len(uncovered)} samodzielnych")

        # Pogrupuj uncovered multi-disc po znorm. stemie → weź tylko pierwszą grę
        # (wielodyskowe / wieloplikowe bez M3U — obsługiwane)
        by_stem: dict[str, list[Path]] = {}
        for p in uncovered:
            by_stem.setdefault(self._norm_rom_stem(p.stem), []).append(p)

        standalone: list[Path] = []
        for items in by_stem.values():
            # FIX v7.4: jeśli grupa zawiera arkusz (.cue/.gdi/.m3u), surowe
            # dane (.bin/.img/.raw/.sub) odpadają — NIGDY nie są plikiem
            # uruchamiającym obok arkusza (Dreamcast .bin = emulacja NAOMI!)
            has_sheet = any(p.suffix.lower() in (".cue", ".gdi", ".m3u")
                            for p in items)
            if has_sheet:
                items = [p for p in items
                         if p.suffix.lower() not in (".bin", ".img",
                                                     ".raw", ".sub")] or items
            # Wybór pliku głównego wg rankingu rozszerzeń, nie alfabetycznie
            items.sort(key=lambda p: self._main_file_sort_key(p, primary_ext))
            standalone.append(items[0])   # tylko Dysk 1 (lub jedyny plik)

        # Wynik: M3U jako pierwsze (zachowany porządek skanowania), potem standalone
        return m3u_files + standalone


    def _strip_region(self, name: str) -> str:
        """Usuwa WSZYSTKIE końcowe tagi regionalne i numer dysku.

        Obsługuje wiele nawiasów:
          'Legend of Dragoon, The (USA) (Disc 1)' → 'Legend of Dragoon, The'
          'Castlevania [USA] [Disc 1]'            → 'Castlevania'
          'Gran Turismo (NTSC-U)'                 → 'Gran Turismo'
        """
        result = name.strip()
        changed = True
        while changed:
            prev = result
            # Nawiasy okrągłe: (USA), (Disc 1), (Rev 1), (En,Fr,De), ...
            result = re.sub(r"\s*\([^)]*\)\s*$", "", result).strip()
            # Nawiasy kwadratowe: [USA], [!], [T-Pol], ...
            result = re.sub(r"\s*\[[^\]]*\]\s*$", "", result).strip()
            changed = (result != prev)
        return result

    def _rom_uid(self, plat: str, idx: int) -> str:
        return f"{plat.lower()}_{idx + 1}"


    def _rom_run_platform(self, plat: str):
        romcfg = self.config_data.get("rom_support", {}) or {}
        if not romcfg.get("enabled"):
            messagebox.showwarning("ROMy", "Najpierw włącz obsługę ROM-ów w ⚙ ROMy.")
            return
        # Znajdź system po nazwie
        system = next(
            (s for s in romcfg.get("systems", []) if s.get("name") == plat),
            None
        )
        if not system:
            messagebox.showerror("ROMy", f"Nieznany system: {plat!r}")
            return
        romdir   = system.get("rom_dir",  "").strip()
        emulator = system.get("emulator", "").strip()
        if not romdir or not Path(romdir).is_dir():
            messagebox.showerror("ROMy", f"Błędny folder ROM dla {plat}")
            return
        if not emulator or not Path(emulator).is_file():
            # v7.8: gry .lnk (np. skróty RPCS3 w roms/PS3) nie potrzebują
            # ścieżki do emulatora — skrót już zawiera komendę uruchamiania.
            has_lnk = any(p.suffix.lower() == ".lnk"
                          for p in Path(romdir).glob("*.lnk"))
            if not has_lnk:
                messagebox.showerror("ROMy", f"Błędny emulator dla {plat}")
                return
            emulator = ""   # skanuj dalej — tylko .lnk będą uruchamialne
        self.v_status.set(f"{plat}: skanowanie ROM-ów...")
        threading.Thread(
            target=self._rom_run_platform_thread,
            args=(plat, romdir, emulator, system),
            daemon=True,
        ).start()

    def _rom_run_platform_thread(self, plat: str, romdir: str, emulator: str,
                                  system_cfg: dict | None = None):
        """Wątek skanowania ROM-ów.

        system_cfg zawiera konfigurację systemu (roms_in_subdirs, launch_args, primary_ext).
        """
        system_cfg = system_cfg or {}
        roms_in_subdirs  = system_cfg.get("roms_in_subdirs", False)
        launch_args_tpl  = system_cfg.get("launch_args", "").strip()
        primary_ext_str  = system_cfg.get("primary_ext", "m3u,cue,iso,chd,bin")
        primary_ext      = [e.strip().lower().lstrip(".")
                            for e in primary_ext_str.split(",") if e.strip()]

        # Dodatkowe rozszerzenia z all_exts (np. nes, z64, gba dla kartridżów)
        all_exts_str = system_cfg.get("all_exts", primary_ext_str)
        extra_exts   = {e.strip().lower().lstrip(".")
                        for e in all_exts_str.split(",") if e.strip()}

        if roms_in_subdirs:
            roms = self._rom_scan_subdirs(romdir, primary_ext,
                                          plat=plat, system_cfg=system_cfg)
        else:
            roms = self._rom_m3u_bundle(self._rom_scan(romdir, extra_exts),
                                        primary_ext=primary_ext)
            # Tryb płaski: jeśli brak wyników ale folder ma pliki →
            # sprawdź czy są pliki z nieznanymi rozszerzeniami i zapytaj użytkownika
            if not roms:
                roms = self._flat_scan_with_ext_fallback(
                    romdir, extra_exts, plat, primary_ext, system_cfg
                )

        if not roms:
            self.after(0, lambda: messagebox.showinfo("ROMy", f"Brak ROM-ów w {plat}"))
            return
        links_out = _links_dir_for({"source": "rom", "rom_platform": plat})
        links_out.mkdir(parents=True, exist_ok=True)
        new_games = []
        for i, rom in enumerate(roms):
            # Tytuł: dla podkatalogów używamy nazwy katalogu nadrzędnego
            rom_p = Path(rom)
            if roms_in_subdirs and rom_p.parent != Path(romdir):
                raw_title = rom_p.parent.name   # nazwa folderu gry
            else:
                raw_title = rom_p.stem
            title = self._strip_region(raw_title)
            uid = self._rom_uid(plat, i)
            # v7.8: skrót .lnk (RPCS3/PS3) — gra jest gotowym linkiem
            # emulatora; PyLinks tylko go kopiuje i podmienia ikonę.
            is_lnk = rom_p.suffix.lower() == ".lnk"
            new_games.append({
                "uid": uid,
                "appid": None, "name": title, "content": "",
                "game_dir": str(rom_p.parent if roms_in_subdirs else Path(romdir)),
                "source": "rom", "rom_platform": plat,
                "rom_path": str(rom), "launch_exe": emulator,
                "launch_args": launch_args_tpl,   # parametry dla emulatora
                "rom_is_lnk": is_lnk,
                "_poster_key": uid, "_rom_id": uid,
                "enabled": True, "sgdb_results": [], "sgdb_id": None,
                "ambiguous": False, "candidates": [], "selected_idx": None,
                "icons_loaded": False,
            })
        def finish():
            # Usuń TYLKO gry tej platformy — inne platformy zostają z ikonami
            self.games = [g for g in self.games
                          if not (g.get("source") == "rom"
                                  and g.get("rom_platform") == plat)] + new_games
            self._apply_saved_state_to_games()
            self._rebuild_list()
            if new_games:
                self.cur_idx = len(self.games) - len(new_games)
                self._draw_detail(self.games[self.cur_idx])
                self._update_launch_label(self.games[self.cur_idx])
            self.v_status.set(f"{plat}: wykryto {len(new_games)} ROM-ów")
            threading.Thread(target=self._rom_resolve_sgdb_thread, args=(plat, new_games), daemon=True).start()
        self.after(0, finish)

    def _rom_resolve_sgdb_thread(self, plat: str, games: list[dict]):
        """v5: przyspieszony resolve — parallel I/O + brak sieci dla cache-hit.

        Problemy v4 (naprawione):
        1. Libretro wywoływany na KAŻDEJ grze nawet przy cache-hit
           → 50 ROM × 3 HTTP = 150 żądań sieciowych mimo pełnego cache
        2. Przetwarzanie kolejne (1 wątek) → N gier × czas sieciowy

        Rozwiązania:
        A) Cache-hit: ZERO sieci — tylko odczyt SQLite (natychmiastowe)
        B) Libretro wyniki zapisywane w SQLite (asset_type="grids") — cache miss
           tylko raz, potem też z cache
        C) ThreadPoolExecutor(4) — 4 cache-miss równolegle (I/O-bound)
        D) Status bar co gotową grę (feedback podczas długich skanów)
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        icons_mgr = self._icons()
        _st       = self._asset_store
        _db_lock  = threading.Lock()   # SQLite: jeden zapis naraz
        total     = len(games)
        done_ctr  = [0]                # mutable counter dla lambdy

        # PERF v7.8: upsert + odczyt cache dla WSZYSTKICH ROM-ów przed
        # startem workerów — jedna transakcja i 2 zapytania SQL zamiast
        # (1 commit + 2 zapytania + burza stat()) per gra pod lockiem.
        with _db_lock:
            for g in games:
                g["_game_id"] = _st.upsert_game(
                    "rom", None, g.get("sgdb_id"), g.get("name", ""),
                    commit=False)
            _st.commit()
        _bulk      = _st.assets_bulk([g["_game_id"] for g in games],
                                     ("icons", "grids"))
        _sgdb_bulk = _st.sgdb_ids_bulk([g["_game_id"] for g in games])
        _dir_cache: dict = {}

        def _process_one(g: dict):
            # ── 1. Cache sprawdzony z prefetchu (bez SQL per gra) ──────────
            _gid = g["_game_id"]
            _cached = (
                _st.candidates_from_cache(
                    _gid, "icons", dir_cache=_dir_cache,
                    rows=_bulk.get((_gid, "icons"), []))
                + _st.candidates_from_cache(
                    _gid, "grids", dir_cache=_dir_cache,
                    rows=_bulk.get((_gid, "grids"), []))  # tu: Libretro
            )

            if _cached:
                # ── CACHE HIT: zero sieci ────────────────────────────────
                g["candidates"] = _cached
                if not self._restore_selected_icon(g):  # FIX v7
                    g["selected_idx"] = icons_mgr.best_idx(_cached)
                g["icons_loaded"] = True
                if not g.get("sgdb_id"):
                    saved_sid = _sgdb_bulk.get(_gid)
                    if saved_sid:
                        g["sgdb_id"] = saved_sid
                # Libretro NIE jest wywoływany dla cache-hit → brak HTTP!
                return

            # ── CACHE MISS: sieć (bez locka — I/O równoległe) ────────────
            _rom_stem    = Path(g.get("rom_path", "") or g.get("name", "")).stem
            _clean_title = self._strip_region(_rom_stem)
            _plt         = (g.get("rom_platform") or "").upper()
            q            = self._strip_region(_rom_stem)

            # Stub lookup przez pseudo-hash (skip SGDB search jeśli znany ID)
            _phash, _stub = None, None
            if g.get("rom_path") and Path(g["rom_path"]).exists():
                _phash = _rom_pseudo_hash(Path(g["rom_path"]))
                with _db_lock:
                    _stub = _st.lookup_stub_by_phash(_phash)
                if _stub and _stub.get("sgdb_id"):
                    g["sgdb_id"] = _stub["sgdb_id"]
                    print(f"[Stub HIT] {g['name']!r} → sgdb_id={_stub['sgdb_id']}")

            sgdb_cands: list[dict] = []
            pick_id = None

            if _stub and _stub.get("sgdb_id"):
                # Znany ID ze stuba → bezpośrednie pobieranie (bez search)
                pick_id    = _stub["sgdb_id"]
                g["sgdb_id"] = pick_id
                sgdb_cands = icons_mgr.candidates_for_extra(g, pick_id)
            else:
                results = icons_mgr.sgdb_search(q)
                if results:
                    pick_id = results[0].get("id")
                    if pick_id:
                        g["sgdb_results"] = results
                        g["sgdb_id"]      = pick_id
                        sgdb_cands        = icons_mgr.candidates_for_extra(g, pick_id)

            # Libretro — pobierz (I/O, bez locka)
            libretro_cands: list[dict] = []
            if self._extra_sources.use_libretro and _plt:
                libretro_cands = self._extra_sources.libretro_candidates(
                    _plt, _clean_title)

            all_cands = sgdb_cands + libretro_cands
            if not all_cands:
                return

            g["candidates"]   = all_cands
            if not self._restore_selected_icon(g):  # FIX v7
                g["selected_idx"] = icons_mgr.best_idx(all_cands)
            g["icons_loaded"] = True

            # ── Zapis do cache (pod lockiem, batch) ───────────────────────
            with _db_lock:
                if pick_id:
                    _st._db.execute(
                        "UPDATE games SET sgdb_id=? WHERE id=?",
                        (str(pick_id), _gid),
                    )
                # SGDB ikony → asset_type="icons"
                for _cv in sgdb_cands:
                    if _cv.get("type") in ("sgdb","grid") and _cv.get("bytes"):
                        _st.save_asset(
                            _gid, "icons",
                            str(_cv.get("remote_asset_id") or _cv.get("label", "")),
                            _cv["bytes"], _cv["w"], _cv["h"],
                            sgdb_key=str(pick_id) if pick_id else "",
                            commit=False,
                            url=_cv.get("url", ""), tier="thumb",
                        )
                # Libretro → asset_type="grids" (znajdowane przez candidates_from_cache)
                for i, _lv in enumerate(libretro_cands):
                    if _lv.get("bytes"):
                        _st.save_asset(
                            _gid, "grids",
                            f"libretro_{i}_{_lv.get('style','')[:20]}",
                            _lv["bytes"], _lv["w"], _lv["h"],
                            commit=False,
                            url=_lv.get("url", ""), tier="thumb",
                        )
                # Zapisz pseudo-hash w stub (dla przyszłej re-identyfikacji)
                if _phash and pick_id and not _stub:
                    _st.save_stub(_gid, {
                        "name":    g.get("name", ""),
                        "sgdb_id": str(pick_id),
                        "source":  "rom",
                    }, _phash)
                _st.commit()

        # ── Przetwarzaj równolegle (4 wątki = 4× szybszy dla cache-miss) ──
        with ThreadPoolExecutor(max_workers=4) as executor:
            fmap = {executor.submit(_process_one, g): g for g in games}
            for future in as_completed(fmap):
                g = fmap[future]
                try:
                    future.result()
                except Exception as exc:
                    print(f"[ROM] błąd {g.get('name','?')!r}: {exc}")
                done_ctr[0] += 1
                d = done_ctr[0]
                self.after(0, lambda d=d: self.v_status.set(
                    f"{plat}: {d}/{total} gier..."))
                # FIX v7.3: plakaty SGDB + IGDB/TGDB także dla ROM-ów —
                # zlecane z wątku UI po zakończeniu resolve danej gry
                self.after(0, lambda gg=g: self._submit_auto_art(gg))

        self.after(0, self._rebuild_list)
        # Sprawdź sieroty tylko w LINKS/<plat>/ tego konkretnego skanu
        _plat_dir = str(LINKS_DIR / safe_name(plat))
        self.after(1200, lambda d=frozenset([_plat_dir]):
                   self._check_orphans_after_scan(d))


    def _build_plan(self) -> list[dict]:
        steam_exe = self.v_exe.get()
        plan: list[dict] = []
        for g in self.games:
            if not g.get("enabled", True):
                continue
            safe = safe_name(g["name"])
            sel_idx = g.get("selected_idx")
            icon_src = "(domyślna)"
            if g.get("candidates") and sel_idx is not None and sel_idx < len(g["candidates"]):
                c = g["candidates"][sel_idx]
                icon_src = c.get("label", "?")
            src = g.get("source", "extra")
            game_out = _links_dir_for(g)
            game_out.mkdir(parents=True, exist_ok=True)
            if src == "steam":
                target = f"{steam_exe} -applaunch {g.get('appid','?')}"
                file_path = str(game_out / f"{safe}.lnk")
            elif src == "epic":
                target = f"com.epicgames.launcher://apps/{g.get('epic_app_name','?')}"
                file_path = str(game_out / f"{safe}.url")
            elif src == "gog":
                target = g.get("launch_exe") or "(auto EXE)"
                file_path = str(game_out / f"{safe}.lnk")
            elif src == "rom":
                rom_path = g.get("rom_path") or ""
                if g.get("rom_is_lnk") or rom_path.lower().endswith(".lnk"):
                    # v7.8: kopiowanie gotowego .lnk (RPCS3) + podmiana ikony
                    target    = f"[kopiuj .lnk] {rom_path}"
                    file_path = str(game_out / f"{safe}.lnk")
                else:
                    launch_exe   = g.get("launch_exe") or "(auto EXE)"
                    _launch_args = g.get("launch_args", "")
                    _rp          = disc_path_for_emulator(rom_path, g.get("launch_exe", ""))
                    args_str     = _rom_build_args(_launch_args, _rp)
                    target       = f"{launch_exe} {args_str}"
                    file_path    = str(game_out / f"{safe}.lnk")
            else:  # extra
                target = g.get("launch_exe") or "(auto największy EXE)"
                file_path = str(game_out / f"{safe}.lnk")
            plan.append({
                "name": g["name"],
                "source": src,
                "action": "utwórz/nadpisz",
                "target": target,
                "icon": icon_src,
                "file": file_path,
            })
        return plan

    def _dry_run_click(self):
        if not self.games:
            messagebox.showwarning("Brak gier", "Najpierw kliknij SKANUJ.")
            return
        plan = self._build_plan()
        if not plan:
            messagebox.showwarning("Brak zaznaczonych", "Zaznacz co najmniej jedną grę.")
            return
        DryRunDialog(self, plan)

    @staticmethod
    def _lnk_name_norm(name: str) -> str:
        """v7.9.2: nazwa .lnk sprowadzona do formy porównywalnej —
        NFC (formy unicode), casefold, bez kropek/spacji na końcu
        (Win32 sam je obcina przy zapisie, stąd 'bliźniacze' pliki)."""
        stem = name[:-4] if name.lower().endswith(".lnk") else name
        return unicodedata.normalize("NFC", stem).casefold().rstrip(" .")

    def _sweep_lnk_duplicates(self, out_dir: Path, target: Path) -> None:
        """v7.9.2: usuń w out_dir pliki .lnk, które po normalizacji nazwy
        są tym samym skrótem co target, ale leżą pod inną ścieżką —
        pozostałości po zapisie COM pod nazwą znormalizowaną przez Win32
        inaczej niż nazwa kopii Pythona (duplikaty z v7.8-v7.9.1)."""
        want = self._lnk_name_norm(target.name)
        try:
            entries = list(out_dir.iterdir())
        except OSError:
            return
        for p in entries:
            if (p.suffix.lower() == ".lnk" and p != target
                    and self._lnk_name_norm(p.name) == want):
                try:
                    p.unlink()
                    print(f"[LNK-SWEEP] usunięto duplikat: {p.name!r} "
                          f"(docelowy: {target.name!r})")
                except OSError as e:
                    print(f"[LNK-SWEEP] nie mogę usunąć {p}: {e}")

    def _create_click(self):
        if not self.games:
            messagebox.showwarning("Brak gier", "Najpierw kliknij SKANUJ.")
            return
        pending = [g["name"] for g in self.games if g.get("ambiguous")]
        if pending:
            messagebox.showwarning(
                "Oczekujące wybory",
                "Następujące gry czekają na wybór tytułu SGDB:\n\n"
                + "\n".join(f"• {n}" for n in pending[:10])
                + ("\n..." if len(pending) > 10 else ""),
            )
            return
        enabled = [g for g in self.games if g.get("enabled", True)]
        if not enabled:
            messagebox.showwarning("Brak zaznaczonych", "Zaznacz co najmniej jedną grę.")
            return
        plan = self._build_plan()
        dlg = DryRunDialog(self, plan)
        if not dlg.confirm:
            return
        threading.Thread(target=self._create_thread, daemon=True).start()

    def _create_thread(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        scanner = self._scanner()
        icons = self._icons()
        creator = self._creator()
        # v8.2: grzbiet platformy — jeśli włączony, upewnij się, że są logotypy
        # (auto-pobranie raz do platform_logo_dir; fallback na tekst gdy brak).
        _spine_logo_dir = ""
        if self.config_data.get("icon_platform_spine", False):
            _spine_logo_dir = (self.config_data.get("platform_logo_dir")
                               or str(SCRIPT_DIR / "platform_logos"))
            try:
                _ld = Path(_spine_logo_dir)
                # pobierz tylko BRAKUJĄCE logotypy platform z bieżącego zestawu
                _needed = {
                    _spine_canon_key(g.get("rom_platform"))  # rozwiń aliasy (SNESMSU1→SNES)
                    for g in self.games
                    if g.get("enabled", True) and g.get("source") == "rom"
                    and g.get("rom_platform")
                }
                _missing = {p for p in _needed
                            if p and not (_ld / f"{p}.png").exists()}
                if _missing:
                    self._q.put(("st", "Pobieram brakujące logotypy platform…"))
                    n = download_platform_logos(
                        _spine_logo_dir, only=_missing,
                        style=self.config_data.get("spine_logo_style",
                                                   "Light - Just White"))
                    print(f"[Spine] pobrano {n} logotypów platform → {_spine_logo_dir}")
            except Exception as _ex:
                print(f"[Spine] pobieranie logotypów nieudane: {_ex}")
        to_process = [(i, g) for i, g in enumerate(self.games) if g.get("enabled", True)]
        total = len(to_process)
        n_ok = 0
        n_err = 0
        report: list[dict] = []
        errors_map: dict[str, str] = {}
        for step, (i, g) in enumerate(to_process):
            self._q.put(("st", f"Tworzę [{step+1}/{total}]: {g['name']}"))
            game_out = _links_dir_for(g)
            game_out.mkdir(parents=True, exist_ok=True)
            self._q.put(("cprog", int(step / total * 100)))
            if not g["icons_loaded"]:
                cands = icons.candidates_for_steam(g, scanner) if g["source"] == "steam" \
                    else icons.candidates_for_extra(g, g.get("sgdb_id"))
                g["candidates"] = cands
                if not self._restore_selected_icon(g):  # FIX v7
                    g["selected_idx"] = icons.best_idx(cands)
                g["icons_loaded"] = True
            sel_idx = g["selected_idx"]
            icon_path = f"{self.v_exe.get()},0"
            if g["candidates"] and sel_idx is not None:
                sel = g["candidates"][sel_idx]
                if sel["type"] == "exe" and sel["exe"]:
                    icon_path = f"{sel['exe']},0"
                elif sel["type"] in ("sgdb", "grid", "grids", "icons") and (sel.get("bytes") or sel.get("local_path")):
                    uid = g["appid"] or re.sub(r"[^a-zA-Z0-9_]", "_", g["name"])
                    # v8.2: grzbiet platformy — dla ROM-ów osobny plik .ico per
                    # platforma, żeby ten sam tytuł na PS1/PS2/… się nie nadpisał.
                    _spine_on = bool(self.config_data.get("icon_platform_spine", False))
                    _spine_side = self.config_data.get("icon_spine_side", "left")
                    _spine_plat = (g.get("rom_platform") or "").upper() if g.get("source") == "rom" else ""
                    if _spine_on and _spine_plat:
                        uid = f"{uid}_{re.sub(r'[^A-Za-z0-9]', '', _spine_plat)}"
                    ico_data = sel.get("bytes")
                    if not ico_data and sel.get("local_path"):
                        _lp = sel["local_path"]
                        # v7.9 (tier): kandydat z cache może być miniaturą
                        # 256px — przed generowaniem .ico dociągnij pełną
                        # wersję z zapisanego url (promocja thumb→full).
                        _gid2 = g.get("_game_id")
                        if (sel.get("tier") == "thumb" and _gid2
                                and sel.get("remote_asset_id")):
                            _full = self._asset_store.ensure_full_asset(
                                _gid2,
                                sel.get("asset_type", "icons"),
                                str(sel["remote_asset_id"]),
                                fetch_fn=fetch,
                            )
                            if _full:
                                _lp = _full
                                sel["local_path"] = _full
                                sel["tier"] = "full"
                        try:
                            ico_data = Path(_lp).read_bytes()
                        except Exception:
                            ico_data = None
                    if ico_data:
                        # Ikona zawsze w Cache/ (nie obok skrótu)
                        ico = icons.cache_ico(CACHE_DIR, str(uid), ico_data,
                                              platform=_spine_plat,
                                              spine=_spine_on, side=_spine_side,
                                              logo_dir=_spine_logo_dir)
                        if ico:
                            icon_path = str(ico)
            ok = False
            err_msg = ""
            try:
                print(f"[CREATE] source={g.get('source')} name={g.get('name')} out={game_out}")
                if g["source"] == "steam":
                    ok = creator.make_steam_shortcut(game_out, g, icon_path)
                    target = f"{self.v_exe.get()} -applaunch {g['appid']}"
                    file_p = str(game_out / f"{safe_name(g['name'])}.lnk")
                elif g["source"] == "epic":
                    ok = creator.make_epic_shortcut(game_out, g, icon_path)
                    target = f"com.epicgames.launcher://apps/{g.get('epic_app_name','')}"
                    file_p = str(game_out / f"{safe_name(g['name'])}.url")
                elif g["source"] == "gog":
                    ok = creator.make_gog_shortcut(game_out, g, icon_path)
                    _pt = gog_playtask(g.get("game_dir", "") or "")
                    target = (_pt[0] if _pt else g.get("launch_exe")) or ""
                    file_p = str(game_out / f"{safe_name(g['name'])}.lnk")
                elif g["source"] == "rom":
                    rom_path = g.get("rom_path") or ""
                    file_p   = str(game_out / f"{safe_name(g['name'])}.lnk")
                    if g.get("rom_is_lnk") or rom_path.lower().endswith(".lnk"):
                        # v7.9.2: sprzątnij duplikaty po poprzednich runach —
                        # pliki .lnk których nazwa po normalizacji Win32/NFC
                        # (wielkość liter, kropki/spacje na końcu, formy
                        # unicode) jest tą samą nazwą, ale ścieżka inna.
                        self._sweep_lnk_duplicates(game_out, Path(file_p))
                        # v7.9.2 (PS3/RPCS3): gotowy skrót emulatora — kopiuj
                        # przez plik tymczasowy + atomic replace (naprawa
                        # duplikatów i losowo niepodmienionych ikon).
                        ok     = creator.copy_lnk_with_icon(rom_path, file_p,
                                                            icon_path)
                        target = rom_path
                    else:
                        launch_exe   = g.get("launch_exe") or ""
                        _launch_args = g.get("launch_args", "")
                        if not launch_exe:
                            # Surowy ROM (.iso/.chd…) bez emulatora — NIE twórz
                            # skrótu z pustym targetem. Zwykle: brak .exe emulatora
                            # w ⚙ ROMy, albo gra ma osobny .lnk (Xenia/RPCS3),
                            # którego użyj zamiast surowego pliku.
                            ok = False
                            target = ""
                            _plt = g.get("rom_platform", "?")
                            err_msg = (f"Brak emulatora dla systemu „{_plt}” — "
                                       "ustaw plik .exe w ⚙ ROMy, albo dodaj skrót "
                                       ".lnk gry do folderu ROM-ów (jak PS3/Xbox 360).")
                        else:
                            # PS2/PCSX2 (bez obsługi .m3u): skrót celuje w istniejący
                            # dysk (Disc 1); emulatory z .m3u dostają playlistę.
                            _rp          = disc_path_for_emulator(rom_path, launch_exe)
                            args         = _rom_build_args(_launch_args, _rp)
                            ok           = creator.make_lnk(file_p, launch_exe,
                                                            args, icon_path)
                            target       = launch_exe
                else:  # extra
                    launch_exe = g.get("launch_exe")   # ręczny wybór ma priorytet
                    x_args = ""
                    x_workdir = ""
                    # v8.2: gry GOG — launcher z goggame-*.info (path+args+workingDir),
                    # obsługuje DOSBox/ScummVM (find_exes wziąłby goły dosbox.exe bez -conf).
                    if not launch_exe:
                        pt = gog_playtask(g.get("game_dir", ""))
                        if pt:
                            launch_exe, x_args, x_workdir = pt
                            print(f"[CREATE] GOG playTask → exe={launch_exe} "
                                  f"args={x_args!r} workdir={x_workdir}")
                    if not launch_exe and g["candidates"] and sel_idx is not None:
                        s2 = g["candidates"][sel_idx]
                        if s2["type"] == "exe" and s2["exe"]:
                            launch_exe = s2["exe"]
                    if not launch_exe:
                        exes = icons.find_exes(g.get("game_dir", ""))
                        if exes:
                            launch_exe = str(exes[0])
                    file_p = str(game_out / f"{safe_name(g['name'])}.lnk")
                    if not launch_exe:
                        # Najczęstsza przyczyna pustego skrótu extra: nie udało
                        # się ustalić pliku uruchamiającego (EXE). Podaj powód.
                        ok = False
                        target = ""
                        gdir = g.get("game_dir", "") or ""
                        if gdir and not Path(gdir).is_dir():
                            err_msg = f"Katalog gry nie istnieje: {gdir}"
                        elif gdir:
                            err_msg = (f"Nie znaleziono pliku uruchamiającego (EXE) w: "
                                       f"{gdir}. Jeśli to gra GOG — pobranie mogło być "
                                       "niekompletne (brak wypakowanych plików). Możesz też "
                                       "wskazać EXE ręcznie („Wybierz plik uruchamiający (EXE)…”).")
                        else:
                            err_msg = ("Brak katalogu gry i pliku uruchamiającego (EXE). "
                                       "Wskaż EXE ręcznie („Wybierz plik uruchamiający (EXE)…”).")
                    else:
                        ok = creator.make_extra_shortcut(game_out, g, launch_exe,
                                                         icon_path, args=x_args,
                                                         work_dir=x_workdir)
                        target = launch_exe
                        if not ok and not err_msg:
                            err_msg = (f"WScript.Shell nie zapisał .lnk (target: {launch_exe}). "
                                       "Sprawdź czy plik EXE istnieje i czy dostępny jest pywin32.")
            except Exception as e:
                ok = False
                err_msg = f"{type(e).__name__}: {e}"
                target = ""
                file_p = ""
            # Każde niepowodzenie MUSI mieć powód w raporcie (koniec pustej kolumny „Błąd").
            if not ok and not err_msg:
                if not WIN32COM:
                    err_msg = ("Brak modułu pywin32 (WScript.Shell) — nie można tworzyć "
                               ".lnk. Zainstaluj: pip install pywin32.")
                elif not str(target or "").strip():
                    err_msg = ("Nie ustalono celu skrótu (target). Dla gier extra/GOG wskaż "
                               "plik uruchamiający (EXE); dla ROM-ów sprawdź ścieżkę ROM/emulatora.")
                else:
                    err_msg = (f"Tworzenie skrótu nie powiodło się (target: {target}). "
                               "Sprawdź czy plik istnieje i czy dostępny jest pywin32.")
            if ok:
                n_ok += 1
            else:
                n_err += 1
                errors_map[self._game_key(g)] = err_msg or "Tworzenie skrótu nie powiodło się"
                print(f"[CREATE][ERR] {g.get('name')} ({g.get('source')}): {err_msg}")
            report.append({
                "name": g["name"], "source": g.get("source", ""),
                "file": file_p, "icon": icon_path, "target": target,
                "ok": ok, "error": err_msg,
            })
        # zapisz raport
        try:
            report_path = write_report(REPORTS_DIR, report, fmt="html")
        except Exception:
            report_path = None
        self.config_data["last_run_errors"] = errors_map
        save_config(self.config_data)
        self._q.put(("cprog", 100))
        # FIX v7: 'out' nie istniało (NameError przy końcu tworzenia skrótów)
        msg = f"Gotowe!\nUtworzone: {n_ok} Błędy: {n_err}\nZ {len(self.games)} gier zaznaczono: {total}\nFolder: {LINKS_DIR}"
        if report_path:
            msg += f"\nRaport: {report_path}"
        self._q.put(("done_create", msg))

    # -------- Eksport --------

    # ══════════════════════════════════════════════════════════════════════════
    # M3U Generator
    # ══════════════════════════════════════════════════════════════════════════

    def _open_m3u_generator(self):
        """Otwórz dialog generatora M3U dla multi-disc gier."""
        romcfg = self.config_data.get("rom_support", {})
        if not romcfg.get("enabled") or not romcfg.get("systems"):
            messagebox.showinfo("M3U", "Najpierw włącz i skonfiguruj systemy ROM.")
            return

        self.v_status.set("Szukam multi-disc grup…")
        self.update_idletasks()

        all_groups: list[dict] = []
        for sys in romcfg.get("systems", []):
            rom_dir = sys.get("rom_dir", "").strip()
            if not rom_dir or not Path(rom_dir).is_dir():
                continue
            plat = sys.get("name", "")
            roms_in_subdirs = sys.get("roms_in_subdirs", False)
            primary_ext = [e.strip().lower().lstrip(".")
                           for e in sys.get("primary_ext", "cue,iso,chd,bin").split(",")
                           if e.strip()]
            groups = self._find_multidisc_groups(rom_dir, primary_ext, roms_in_subdirs)
            for title, discs in groups.items():
                m3u_path = Path(rom_dir) / f"{title}.m3u"
                all_groups.append({
                    "plat":    plat,
                    "rom_dir": rom_dir,
                    "title":   title,
                    "discs":   discs,
                    "m3u_path": m3u_path,
                    "exists":  m3u_path.exists(),
                })

        self.v_status.set("Gotowy.")
        if not all_groups:
            messagebox.showinfo("M3U", "Nie znaleziono grup multi-disc.")
            return
        _M3uDialog(self, all_groups)

    @staticmethod
    def _find_multidisc_groups(rom_dir: str, primary_ext: list[str],
                               roms_in_subdirs: bool) -> dict[str, list[str]]:
        """Znajdź grupy multi-disc w katalogu ROM-ów.

        Zwraca {tytuł_bez_dysku: [ścieżki_dysków]}.
        Obsługuje tryb płaski (*.cue / *.chd) i tryb podkatalogów.
        """
        base = Path(rom_dir)
        disc_re = re.compile(
            r'\s*[\(\[](Disc|Disk|CD|Side)\s*\d+[\)\]]',
            re.IGNORECASE
        )

        groups: dict[str, list[str]] = {}

        if roms_in_subdirs:
            # Tryb podkatalogów: szukaj par katalogów z "(Disc N)" w nazwie
            for d in sorted(base.iterdir()):
                if not d.is_dir():
                    continue
                if not disc_re.search(d.name):
                    continue
                # Znajdź główny plik w tym katalogu
                for ext in primary_ext:
                    candidates = list(d.glob(f"*.{ext}"))
                    if candidates:
                        key = disc_re.sub("", d.name).strip()
                        groups.setdefault(key, []).append(
                            str(candidates[0].relative_to(base))
                        )
                        break
        else:
            # Tryb płaski: szukaj plików z "(Disc N)" w nazwie
            for ext in primary_ext:
                for f in sorted(base.glob(f"*.{ext}")):
                    if not disc_re.search(f.name):
                        continue
                    key = disc_re.sub("", f.stem).strip()
                    groups.setdefault(key, []).append(f.name)

        return {k: sorted(v) for k, v in groups.items() if len(v) >= 2}

    # ══════════════════════════════════════════════════════════════════════════
    # Startup diff scan
    # ══════════════════════════════════════════════════════════════════════════

    def _canonical_rom_files(self, system_cfg: dict) -> list[Path]:
        """Zwraca kanoniczną listę plików ROM dla systemu — IDENTYCZNĄ z tą,
        którą tworzy SKANUJ ROM (po filtrowaniu M3U/CUE/GDI i multi-disc).

        Wersja bez efektów ubocznych: w trybie podkatalogów NIE pokazuje
        dialogu wyboru rozszerzenia (diff przy starcie musi być cichy).
        Dzięki temu diff porównuje to samo, co faktycznie staje się grami,
        a nie surowe pliki .bin/.sub czy dyski pokryte przez .cue/.m3u.
        """
        rom_dir = (system_cfg.get("rom_dir") or "").strip()
        if not rom_dir or not Path(rom_dir).is_dir():
            return []

        primary_ext_str = system_cfg.get("primary_ext", "m3u,cue,iso,chd,bin")
        primary_ext = [e.strip().lower().lstrip(".")
                       for e in primary_ext_str.split(",") if e.strip()]
        all_exts_str = system_cfg.get("all_exts", primary_ext_str)
        extra_exts = {e.strip().lower().lstrip(".")
                      for e in all_exts_str.split(",") if e.strip()}

        if system_cfg.get("roms_in_subdirs"):
            # Mirror nieinteraktywnej części _rom_scan_subdirs (bez dialogu)
            base = Path(rom_dir)
            pri = list(primary_ext)
            result: list[Path] = []
            try:
                subiter = sorted(base.iterdir())
            except Exception:
                return []
            for d in subiter:
                if not d.is_dir():
                    # v7.8: top-level .lnk (RPCS3/PS3) — jak w _rom_scan_subdirs
                    if d.is_file() and d.suffix.lower() == ".lnk":
                        result.append(d)
                    continue
                try:
                    files = [p for p in sorted(d.iterdir()) if p.is_file()]
                except Exception:
                    continue
                ext_files = [p for p in files
                             if p.suffix.lower().lstrip(".") in
                             (frozenset(pri) | self._DISC_EXTS)]
                if not ext_files:
                    continue
                result.append(self._rom_pick_main_file(ext_files, pri))
            return result

        # Tryb płaski: dokładnie jak _rom_run_platform_thread
        return self._rom_m3u_bundle(
            self._rom_scan(rom_dir, extra_exts),
            primary_ext=primary_ext,
        )

    def _startup_diff_scan(self):
        """Diff ROM-ów przy starcie — trzy jednoznaczne reguły:

          1. plik ROM istnieje + skrót istnieje  → brak działania (nie nowy)
          2. plik ROM istnieje + brak skrótu      → NOWY
          3. skrót istnieje + brak pliku ROM       → USUNIĘTY → skasuj .lnk/.url

        Porównanie opiera się na TRWAŁYM artefakcie (skrót .lnk/.url w
        LINKS/<system>/), bo self.games jest przy starcie puste (biblioteka nie
        jest ładowana do pamięci przy boot). Dzięki temu monit nie wraca dla
        gier, które mają już utworzone ikony, nawet po restarcie.

        Lista plików ROM liczona jest TĄ SAMĄ kanoniczną metodą co SKANUJ ROM
        (_canonical_rom_files → filtrowanie M3U/CUE/GDI + multi-disc), a nazwa
        skrótu jest deterministyczna: safe_name(_strip_region(tytuł)) —
        identycznie jak przy tworzeniu skrótów.

        Osierocone skróty (reguła 3) trafiają do istniejącego OrphanDialog,
        który po potwierdzeniu kasuje pliki .lnk/.url (zachowując stub w bazie).
        """
        def _norm(s: str) -> str:
            try:
                return os.path.normcase(os.path.normpath(s))
            except Exception:
                return s

        def _rom_title_for(rom: Path, rom_dir: str, subdirs: bool) -> str:
            if subdirs and rom.parent != Path(rom_dir):
                raw_title = rom.parent.name
            else:
                raw_title = rom.stem
            return safe_name(self._strip_region(raw_title))

        def _run():
            romcfg = self.config_data.get("rom_support", {})
            if not romcfg.get("enabled"):
                return

            # Mapa safe_name → wiersz SQLite (by zachować stub przy kasowaniu)
            db_by_name: dict[str, dict] = {}
            try:
                with self._asset_store._lock:
                    rows = self._asset_store._db.execute(
                        "SELECT id, name, source, sgdb_id, appid FROM games"
                    ).fetchall()
                for row in rows:
                    db_by_name[safe_name(row["name"])] = dict(row)
            except Exception:
                pass

            new_roms: list[tuple[str, str]] = []   # (plat, rom_path)  reguła 2
            orphans:  list[dict] = []              # do skasowania      reguła 3

            for syscfg in romcfg.get("systems", []):
                plat    = syscfg.get("name", "")
                rom_dir = syscfg.get("rom_dir", "").strip()
                if not rom_dir or not Path(rom_dir).is_dir():
                    continue
                subdirs = bool(syscfg.get("roms_in_subdirs"))

                # Wszystkie pliki ROM na dysku — DOKŁADNIE jak SKANUJ ROM
                canonical = self._canonical_rom_files(syscfg)

                links_dir = _links_dir_for({"source": "rom",
                                            "rom_platform": plat})

                # Tytuł skrótu → ścieżka ROM (na dysku)
                rom_by_title: dict[str, str] = {}
                for rom in canonical:
                    rom_by_title[_rom_title_for(Path(rom), rom_dir, subdirs)] = \
                        str(rom)

                # Nazwy skrótów istniejących na dysku (.lnk/.url)
                shortcut_files: dict[str, Path] = {}
                if links_dir.is_dir():
                    try:
                        for f in links_dir.iterdir():
                            if (f.is_file()
                                    and f.suffix.lower() in (".lnk", ".url")):
                                shortcut_files[f.stem] = f
                    except Exception:
                        pass

                # Reguła 1+2: plik jest, skrótu nie ma → nowy
                for title, rom_path in rom_by_title.items():
                    if title not in shortcut_files:
                        new_roms.append((plat, rom_path))

                # Reguła 3: skrót jest, pliku ROM nie ma → osierocony skrót
                for title, lnk in shortcut_files.items():
                    if title in rom_by_title:
                        continue
                    db_row = db_by_name.get(title, {})
                    orphans.append({
                        "_game_id":    db_row.get("id"),
                        "name":        title,
                        "source":      "rom",
                        "rom_platform": plat,
                        "sgdb_id":     db_row.get("sgdb_id"),
                        "appid":       db_row.get("appid"),
                        "_stale_lnk":  str(lnk),
                        "candidates":  [],
                        "game_dir":    "", "launch_exe": "", "rom_path": "",
                    })

            if not new_roms and not orphans:
                return  # brak zmian — cicho

            def _show():
                # Reguła 2: nowe pliki bez skrótu — wymagają skanu/ikon
                if new_roms:
                    msg = [f"Nowe gry ({len(new_roms)}):"]
                    for plat, p in new_roms[:12]:
                        msg.append(f"  [{plat}] {Path(p).stem}")
                    if len(new_roms) > 12:
                        msg.append(f"  … i {len(new_roms) - 12} więcej")
                    msg.append("\nKliknij SKANUJ ROM dla danego systemu, "
                               "aby utworzyć dla nich ikony.")
                    messagebox.showinfo("Nowe ROM-y", "\n".join(msg))

                # Reguła 3: osierocone skróty → dialog kasowania .lnk
                if orphans:
                    self._show_orphan_dialog(orphans)

            self.after(0, _show)

        threading.Thread(target=_run, daemon=True).start()

    # ══════════════════════════════════════════════════════════════════════════
    # Steam non-Steam export
    # ══════════════════════════════════════════════════════════════════════════

    def _import_lnk(self):
        """Importuj skróty .lnk jako gry Extra."""
        folder = filedialog.askdirectory(
            parent=self,
            title="Wskaż folder ze skrótami .lnk")
        if not folder:
            return
        lnk_files = list(Path(folder).glob("*.lnk"))
        if not lnk_files:
            messagebox.showinfo("Import LNK", "Brak plików .lnk w tym folderze.")
            return

        added = 0
        skipped = 0
        existing_names = {g["name"].lower() for g in self.games}

        for lnk in lnk_files:
            name = lnk.stem
            if name.lower() in existing_names:
                skipped += 1
                continue
            # Rozwiąż cel skrótu przez PowerShell
            target = ""
            try:
                r = subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     f'(New-Object -ComObject WScript.Shell)'
                     f'.CreateShortcut("{lnk}").TargetPath'],
                    capture_output=True, text=True, timeout=8)
                target = r.stdout.strip()
            except Exception:
                target = str(lnk)   # fallback: .lnk jako launcher

            game: dict = {
                "name":       name,
                "source":     "extra",
                "launch_exe": target or str(lnk),
                "enabled":    False,
                "candidates": [],
                "selected_idx": None,
                "uid":        str(lnk),
            }
            self.games.append(game)
            existing_names.add(name.lower())
            added += 1

        if added:
            self._rebuild_platform_bar()
            self._rebuild_list()
        messagebox.showinfo("Import LNK",
            f"Dodano {added} gier, pominięto {skipped} duplikatów.")

    def _open_steam_export(self):
        """Otwórz dialog eksportu gier do Steam jako non-Steam shortcuts."""
        games_ok = [g for g in self.games
                    if g.get("enabled") and (g.get("launch_exe") or g.get("rom_path"))]
        if not games_ok:
            messagebox.showinfo("Steam Export",
                "Brak gier do eksportu. Najpierw kliknij SKANUJ.")
            return
        _SteamExportDialog(self, games_ok, self.config_data)

    def _open_stats(self):
        """Otwórz okno statystyk biblioteki."""
        _StatsDialog(self, self.games, self.config_data)

    def _open_playnite_export(self):
        """Eksport do Playnite JSON / LaunchBox XML."""
        if not self.games:
            messagebox.showinfo("Eksport", "Brak gier — najpierw kliknij SKANUJ.")
            return
        _PlayniteExportDialog(self, self.games)

    def _export_click(self):
        if not self.games:
            messagebox.showwarning("Brak gier", "Najpierw kliknij SKANUJ.")
            return
        enabled = [g for g in self.games if g.get("enabled", True)]
        if not enabled:
            messagebox.showwarning("Brak zaznaczonych", "Zaznacz co najmniej jedną grę.")
            return
        dlg = tk.Toplevel(self)
        dlg.title("Eksport do front-endów")
        dlg.configure(bg=C["bg"])
        dlg.grab_set()
        dlg.resizable(False, False)
        tk.Label(dlg, text="Wybierz format eksportu:", bg=C["bg"], fg=C["fg"],
                 font=("Segoe UI", 10, "bold")).pack(padx=20, pady=(16, 8))

        def _do_launchbox():
            dlg.destroy()
            path = self._creator().export_launchbox(enabled, LINKS_DIR)
            messagebox.showinfo("Eksport", f"Zapisano:\n{path}")

        def _do_pegasus():
            dlg.destroy()
            path = self._creator().export_pegasus(enabled, LINKS_DIR)
            messagebox.showinfo("Eksport", f"Zapisano:\n{path}")

        def _do_report_txt():
            dlg.destroy()
            entries = [{"name": g["name"], "source": g.get("source", ""),
                        "file": "", "icon": "", "target": g.get("launch_exe", ""),
                        "ok": True, "error": ""} for g in enabled]
            p = write_report(REPORTS_DIR, entries, fmt="txt")
            messagebox.showinfo("Raport", f"Zapisano:\n{p}")

        tk.Button(dlg, text="LaunchBox (XML)", command=_do_launchbox, bg=C["acc"],
                  fg=C["bg"], font=("Segoe UI", 9, "bold"), relief="flat",
                  padx=14, pady=6, cursor="hand2").pack(fill="x", padx=20, pady=4)
        tk.Button(dlg, text="Pegasus (metadata.txt)", command=_do_pegasus,
                  bg=C["ext"], fg=C["bg"], font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=14, pady=6, cursor="hand2").pack(fill="x", padx=20, pady=4)
        tk.Button(dlg, text="Raport TXT z listą gier", command=_do_report_txt,
                  bg=C["bg3"], fg=C["fg"], font=("Segoe UI", 9),
                  relief="flat", padx=14, pady=6, cursor="hand2").pack(fill="x", padx=20, pady=4)
        tk.Button(dlg, text="Anuluj", command=dlg.destroy, bg=C["bg3"], fg=C["fg2"],
                  font=("Segoe UI", 9), relief="flat", padx=14, pady=6,
                  cursor="hand2").pack(fill="x", padx=20, pady=(4, 16))

    # -------- Kolejka zdarzeń z wątków --------
    def _selected_asset_keys(self) -> "set[tuple[int, str]]":
        """v7.9: zbiór (game_id, remote_asset_id) WYBRANYCH ikon —
        chronione przed eksmisją LRU i degradacją przy kompaktowaniu
        (skróty .lnk wskazują ich .ico)."""
        keep: set[tuple[int, str]] = set()
        key_map = self.config_data.get("selected_icon_keys", {})
        for g in self.games:
            gid = g.get("_game_id")
            if not gid:
                continue
            # 1) z załadowanych kandydatów (dokładny remote_asset_id)
            sel = g.get("selected_idx")
            cands = g.get("candidates") or []
            if sel is not None and 0 <= sel < len(cands):
                rid = cands[sel].get("remote_asset_id")
                if rid:
                    keep.add((gid, str(rid)))
            # 2) FIX v8.2: z ZAPISANEGO wyboru (config) — chroni ikonę nawet gdy
            #    kandydaci nie są załadowani w pamięci (inaczej eksmisja LRU
            #    kasowała wybraną grafikę gier, których się nie kliknęło).
            saved = key_map.get(self._game_key(g))
            if saved:
                keep.add((gid, str(saved)))
        return keep

    def _run_cache_eviction(self):
        """v7.9 (D): pilnuj limitu cache po skanie — w tle, bez blokowania UI."""
        limit_mb = int(self.config_data.get("cache_limit_mb", 2048) or 0)
        if limit_mb <= 0:
            return
        keep = self._selected_asset_keys()

        def _work():
            try:
                freed = self._asset_store.evict_lru(limit_mb * 1024 * 1024, keep)
                if freed:
                    self._q.put(("st",
                        f"Cache: zwolniono {freed/1024/1024:.0f} MB "
                        f"(limit {limit_mb} MB, LRU)"))
            except Exception as e:
                print(f"[LRU] błąd eksmisji: {e}")
        threading.Thread(target=_work, daemon=True).start()

    def _compact_cache_click(self):
        """v7.9: jednorazowe odchudzenie cache (migracja do tierów).

        Nie-wybrane assety → miniatury 256px WEBP (pełna wersja wróci
        lazy z zapisanego url przy wyborze ikony); wybrane → pełny WEBP.
        """
        if getattr(self, "_compacting", False):
            return
        size_mb = self._asset_store.cache_size_bytes() / 1024 / 1024
        if not messagebox.askyesno(
                "Kompaktuj cache",
                f"Obecny rozmiar cache: {size_mb:.0f} MB.\n\n"
                "Nie-wybrane grafiki zostaną zmniejszone do miniatur 256 px\n"
                "(WEBP); wybrane ikony pozostaną w pełnym rozmiarze (WEBP).\n"
                "Pełne wersje można później dociągnąć z internetu.\n\n"
                "Kontynuować?"):
            return
        self._compacting = True
        keep = self._selected_asset_keys()

        def _work():
            def _prog(done, total, freed):
                self._q.put(("st",
                    f"[Kompaktuj {done}/{total}] "
                    f"zwolnione: {freed/1024/1024:.0f} MB"))
            try:
                freed, done = self._asset_store.compact(keep, _prog)
                new_mb = self._asset_store.cache_size_bytes() / 1024 / 1024
                self._q.put(("st",
                    f"Kompaktowanie zakończone: -{freed/1024/1024:.0f} MB, "
                    f"cache: {new_mb:.0f} MB ({done} assetów)"))
                # Odśwież ścieżki kandydatów w UI (pliki zmieniły rozszerzenie)
                self.after(0, self._reload_candidates_after_compact)
            except Exception as e:
                self._q.put(("st", f"Kompaktowanie: błąd — {e}"))
                import traceback; traceback.print_exc()
            finally:
                self._compacting = False
        threading.Thread(target=_work, daemon=True).start()

    def _reload_candidates_after_compact(self):
        """Po kompaktowaniu local_path/tier w DB są nowe — przeładuj
        kandydatów gier ładowanych z cache, żeby UI nie trzymało ścieżek
        do usuniętych plików .png."""
        _st = self._asset_store
        ids = [g.get("_game_id") for g in self.games if g.get("_game_id")]
        bulk = _st.assets_bulk(ids, ("icons", "grids"))
        dc: dict = {}
        for g in self.games:
            gid = g.get("_game_id")
            if not gid or not g.get("_from_cache"):
                continue
            cached = (_st.candidates_from_cache(gid, "icons", dir_cache=dc,
                                                rows=bulk.get((gid, "icons"), []))
                      + _st.candidates_from_cache(gid, "grids", dir_cache=dc,
                                                  rows=bulk.get((gid, "grids"), [])))
            if cached:
                g["candidates"] = cached
                if not self._restore_selected_icon(g):
                    g["selected_idx"] = 0 if cached else None
        if self.cur_idx is not None and 0 <= self.cur_idx < len(self.games):
            self._draw_detail(self.games[self.cur_idx])

    def _sync_cache_click(self):
        if self._syncing:
            if self._sync_mgr: self._sync_mgr.stop()
            self._syncing = False
            self.v_status.set("Synchronizacja anulowana.")
            return
        if not self.games:
            messagebox.showwarning("Brak gier","Najpierw kliknij SKANUJ."); return
        if not self.config_data.get("api_keys",{}).get("sgdb_key","").strip():
            messagebox.showwarning("Brak klucza SGDB",
                "Ustaw klucz SGDB API w Ustawieniach."); return
        self._syncing = True
        self.v_status.set("Synchronizacja cache – start…")
        to_sync = [g for g in self.games if g.get("enabled", True)]
        threading.Thread(target=self._sync_cache_thread,
                         args=(to_sync,), daemon=True).start()

    def _sync_cache_thread(self, games: list[dict]):
        mgr = self._sync_manager()
        mgr.reset_stop()
        total = len(games)
        new_total = 0
        for idx, g in enumerate(games):
            if mgr._stop.is_set(): break
            self._q.put(("st", f"[SYNC {idx+1}/{total}] {g['name']}…"))
            try:
                gid, n_new = mgr.sync_game(g, asset_types=("icons","grids"))
                g["_game_id"] = gid
                new_total += n_new
                # FIX v7.4: SYNC odpytuje też pozostałe poprawnie
                # skonfigurowane źródła (Steam CDN / IGDB / TGDB /
                # Libretro / ScreenScraper), nie tylko SGDB
                if gid and not mgr._stop.is_set():
                    n_extra = self._sync_extra_sources_for_game(g, gid, mgr._stop)
                    if n_extra:
                        print(f"[SYNC extra] {g['name']!r}: +{n_extra} z dodatkowych źródeł")
                    new_total += n_extra
                    n_new += n_extra
                self._q.put(("sync_game_done",g["name"],gid,n_new,idx+1,total))
            except Exception as e:
                import traceback
                print(f"[SYNC ERR] {g.get('name','?')} – {e}")
                traceback.print_exc()
                self._q.put(("sync_game_err",g.get("name","?"),str(e),idx+1,total))
        self._syncing = False
        self._q.put(("sync_done", new_total))

    # FIX v7.4: delta-sync źródeł spoza SGDB. Każde źródło jest odpytywane
    # tylko gdy jest włączone i poprawnie skonfigurowane w Ustawieniach,
    # ORAZ gdy cache nie ma jeszcze jego grafik dla tej gry (oszczędza
    # limity API IGDB/TGDB/ScreenScraper przy kolejnych SYNC-ach).
    def _sync_extra_sources_for_game(self, g: dict, gid: int,
                                     stop_evt: threading.Event) -> int:
        ex  = self._extra_sources
        _st = self._asset_store
        src   = g.get("source", "")
        appid = g.get("appid", "")
        name  = g.get("name", "")
        plat  = (g.get("rom_platform") or "").upper()
        rom_p = g.get("rom_path", "")
        rom_title = (re.sub(r"\s*\([^)]*\)$", "", Path(rom_p).stem).strip()
                     if rom_p else name)
        cands: list[dict] = []

        # Steam CDN — deterministyczne ID, więc pełny skip gdy komplet w cache
        if src == "steam" and appid and ex.use_steam_cdn and not stop_evt.is_set():
            _cdn = ("library_600x900_2x.jpg", "header.jpg",
                    "library_hero.jpg", "capsule_616x353.jpg")
            if not all(_st.asset_exists(gid, "grids", f"steamcdn_{appid}_{f}")
                       for f in _cdn):
                cands += ex.steam_cdn_candidates(appid)

        # IGDB — pomijamy zapytanie, jeśli cache ma już grafiki igdb_ tej gry
        if (ex.use_igdb and ex.igdb_client_id and name
                and not stop_evt.is_set()
                and not _st.has_asset_prefix(gid, "grids", "igdb_")):
            try:
                cands += ex.igdb_candidates(name)
            except Exception as e:
                print(f"[SYNC extra] IGDB {name!r}: {e}")

        # TGDB
        if (ex.use_tgdb and ex.tgdb_key and name
                and not stop_evt.is_set()
                and not _st.has_asset_prefix(gid, "grids", "tgdb_")):
            try:
                cands += ex.tgdb_candidates(name, platform=plat or "")
            except Exception as e:
                print(f"[SYNC extra] TGDB {name!r}: {e}")

        # Libretro / ScreenScraper — tylko ROM-y z rozpoznaną platformą
        if src == "rom" and plat and not stop_evt.is_set():
            if (ex.use_libretro
                    and not _st.has_asset_prefix(gid, "grids", "libretro_")):
                try:
                    cands += ex.libretro_candidates(plat, rom_title)
                except Exception as e:
                    print(f"[SYNC extra] Libretro {name!r}: {e}")
            if (ex.use_screenscraper and ex.ss_user and ex.ss_pass
                    and not stop_evt.is_set()
                    and not _st.has_asset_prefix(gid, "grids", "ss_")):
                try:
                    cands += ex.screenscraper_candidates(plat, rom_title, rom_p)
                except Exception as e:
                    print(f"[SYNC extra] ScreenScraper {name!r}: {e}")

        # Zapis do cache — pomijamy duplikaty, jeden commit na grę
        new = 0
        for cv in cands:
            if stop_evt.is_set():
                break
            if not cv.get("bytes"):
                continue
            rid = (str(cv.get("remote_asset_id") or "")
                   or (cv.get("url") or "")[-40:].replace("/", "_"))
            if not rid or _st.asset_exists(gid, "grids", rid):
                continue
            try:
                _st.save_asset(gid, "grids", rid, cv["bytes"],
                               cv.get("w", 0), cv.get("h", 0), commit=False,
                               url=cv.get("url", ""), tier="thumb")
                new += 1
            except Exception as se:
                print(f"[SYNC extra] błąd zapisu {name!r}/{rid}: {se}")
        if new:
            try:
                _st.commit()
            except Exception:
                pass
        return new

    def _tick(self):
        try:
            while True:
                msg = self._q.get_nowait()
                k = msg[0]
                if k == "st":
                    self.v_status.set(msg[1])
                elif k == "games":
                    self.games = msg[1]
                    self._apply_saved_state_to_games()
                    self._rebuild_list()
                    self._title.config(text=f"Znaleziono {len(self.games)} gier — pobieram ikony...")
                elif k == "prog":
                    i, total, name = msg[1], msg[2], msg[3]
                    self.v_prog.set(int(i / total * 100) if total else 0)
                    self.v_status.set(f"Ikony [{i+1}/{total}]: {name}")
                    self._lbl_prog.config(text=f"{i+1}/{total}")
                    self._color_list_item(i, C["yel"])
                elif k == "ask_disambig":
                    _, game_idx, game_name, results = msg
                    self._color_list_item(game_idx, C["orn"])
                    dlg = SgdbPickDialog(self, game_name, results, self._icons().sgdb_key)
                    g = self.games[game_idx]
                    if dlg.result_id is not None:
                        g["sgdb_id"] = dlg.result_id
                        matched = next((r for r in results if r.get("id") == dlg.result_id), None)
                        if matched:
                            g["sgdb_results"] = [matched]
                    else:
                        g["sgdb_id"] = None
                    ev = g.get("_disambig_event")
                    if ev:
                        ev.set()
                elif k == "ready":
                    self._simple_refresh_debounced()
                    i = msg[1]
                    self._color_from_state(i)
                    if i == self.cur_idx:
                        self._draw_detail(self.games[i])
                    # FIX v7.2: od razu zleć pobranie plakatów + IGDB/TGDB w tle
                    self._submit_auto_art(self.games[i])
                elif k == "done_scan":
                    self.v_prog.set(100)
                    self._scanning = False
                    self._btn_scan.config(text="SKANUJ")
                    self._title.config(text=f"Gotowe — {msg[1]} gier")
                    self.v_status.set("Skanowanie zakończone.")
                    self._lbl_prog.config(text=f"{msg[1]}/{msg[1]}")
                    self._update_sel_label()
                    self._save_settings()
                    # Sprawdź sieroty tylko w katalogach PC (Steam/GOG/Epic/Extra)
                    # ROM-y (LINKS/PS1/ itp.) sprawdzane są osobno po skanie ROM
                    # FIX v7.6: wszystkie gry PC żyją w LINKS/PC
                    _pc_dirs = {str(LINKS_DIR / "PC")}
                    self.after(1200, lambda d=_pc_dirs:
                               self._check_orphans_after_scan(d))
                    # v7.9 (D): po skanie pilnuj limitu cache (LRU, w tle)
                    self.after(4000, self._run_cache_eviction)
                elif k == "sync_progress":
                    self.v_status.set(f"[SYNC] {msg[1]} | {msg[2]}: +{msg[3]}")
                elif k == "sync_game_done":
                    self.v_prog.set(int(msg[4]/msg[5]*100) if msg[5] else 0)
                    self._lbl_prog.config(text=f"{msg[4]}/{msg[5]}")
                    self.v_status.set(
                        f"[SYNC {msg[4]}/{msg[5]}] {msg[1]} — +{msg[3]} assetów")
                elif k == "sync_game_err":
                    self.v_status.set(
                        f"[SYNC ERR {msg[3]}/{msg[4]}] {msg[1]}: {msg[2][:55]}")
                elif k == "sync_done":
                    self._syncing = False
                    self.v_prog.set(100)
                    self._lbl_prog.config(text="")
                    self.v_status.set(
                        f"Sync zakończony — pobranych assetów: {msg[1]}")
                    # FIX v7.4: SYNC wrzucał grafiki tylko do cache na dysku
                    # — UI ich nie widziało aż do rescanu/restartu. Teraz
                    # scalamy świeże assety z cache do kandydatów i od razu
                    # przerysowujemy aktualną grę.
                    if msg[1]:
                        merged = 0
                        for _g in self.games:
                            merged += self._merge_cached_candidates(_g)
                        if merged:
                            self.v_status.set(
                                f"Sync zakończony — pobranych: {msg[1]}, "
                                f"dodanych do podglądu: {merged}")
                        if self.cur_idx is not None and 0 <= self.cur_idx < len(self.games):
                            self._draw_detail(self.games[self.cur_idx])
                elif k == "posters_ready":
                    _, p_key, p_page, new_cands = msg
                    self._poster_loading = False
                    target = next(
                        (g for g in self.games if self._async_key(g) == p_key), None
                    )
                    if target is not None:
                        if new_cands:
                            existing_urls = {
                                c.get("url", "") for c in target.get("candidates", [])
                            }
                            added = [
                                c for c in new_cands
                                if c.get("url", "") not in existing_urls
                            ]
                            target["candidates"] = target.get("candidates", []) + added
                            self._poster_page = p_page + 1
                            count = sum(
                                1 for c in target["candidates"] if c.get("type") == "grid"
                            )
                            self.v_status.set(
                                f"Pobrano {len(added)} plakatów (łącznie {count}) "
                                f"dla: {target['name']}"
                            )
                            # Przywróć saved icon po załadowaniu nowych kandydatów
                            if target.get("selected_idx") is None:
                                self._restore_selected_icon(target)  # FIX v7
                        else:
                            self.v_status.set(
                                f"Brak kolejnych plakatów dla: {target['name']}"
                            )
                        # Odśwież widok jeśli to aktualnie wybrana gra
                        if (self.cur_idx is not None
                                and self._async_key(self.games[self.cur_idx]) == p_key):
                            self._draw_detail(target)
                            self._update_launch_label(target)
                    else:
                        self._btn_load_posters.config(
                            text="🖼 Pobierz plakaty (20)", state="normal"
                        )
                elif k == "art_ready":
                    _, a_key, a_cands = msg
                    target = next((x for x in self.games
                                   if self._async_key(x) == a_key), None)
                    if target is not None and a_cands:
                        # Dedupe po url / remote_asset_id / local_path
                        existing: set[str] = set()
                        for c in target.get("candidates", []):
                            for f in ("url", "remote_asset_id", "local_path"):
                                v = c.get(f)
                                if v:
                                    existing.add(str(v))
                        added = []
                        for c in a_cands:
                            ids = {str(c.get(f)) for f in
                                   ("url", "remote_asset_id", "local_path")
                                   if c.get(f)}
                            if ids & existing:
                                continue
                            existing |= ids
                            added.append(c)
                        if added:
                            target.setdefault("candidates", []).extend(added)
                            if target.get("selected_idx") is None:
                                target["selected_idx"] = 0
                            target["icons_loaded"] = True
                            # przywróć zapisany wybór (mógł być plakatem)
                            self._restore_selected_icon(target)
                            if (self.cur_idx is not None
                                    and self._async_key(self.games[self.cur_idx]) == a_key):
                                self._draw_detail(target)
                                self._update_launch_label(target)
                elif k == "cprog":
                    self.v_prog.set(msg[1])
                elif k == "done_create":
                    self.v_prog.set(0)
                    messagebox.showinfo("Gotowe", msg[1])
        except queue.Empty:
            pass
        except Exception:
            # FIX v7.4: dowolny wyjątek w handlerze (np. przy rysowaniu
            # miniatur) zabijał całą pętlę kolejki — self.after(60) nigdy
            # nie był planowany, UI przestawał odbierać "ready"/"art_ready"
            # i podglądy pobranych obrazów nigdy się nie pojawiały.
            import traceback
            print("[Tick] błąd obsługi komunikatu z kolejki:")
            traceback.print_exc()
        finally:
            self.after(60, self._tick)


# ---------------------------------------------------------------------------
# FIX v7.4: sprawdzanie zależności przed startem
# ---------------------------------------------------------------------------
def check_dependencies() -> None:
    """Sprawdza zależności i proponuje doinstalowanie przez pip.

    Krytyczne (bez nich kluczowe funkcje nie działają):
      • Pillow  — WSZYSTKIE podglądy/miniatury ikon i plakatów
      • pywin32 — tworzenie skrótów .lnk + ikony z plików EXE (Windows)
    Opcjonalne:
      • zstandard — lepsza kompresja stubów (fallback: gzip)
    """
    missing: list[tuple[str, str, str]] = []   # (pip_name, import_name, opis)

    if not PIL_OK:
        missing.append(("Pillow", "PIL",
                        "podglądy ikon i plakatów (bez tego miniatury "
                        "się NIE wyświetlają)"))
    if IS_WIN and not WIN32COM:
        missing.append(("pywin32", "win32com",
                        "tworzenie skrótów .lnk i ikony z plików EXE"))
    try:
        import zstandard  # noqa: F401
    except Exception:
        missing.append(("zstandard", "zstandard",
                        "(opcjonalne) szybsza kompresja stubów — "
                        "bez tego użyty będzie gzip"))

    if not missing:
        return

    crit = [m for m in missing if m[0] != "zstandard"]
    lines = "\n".join(f"  • {pip} — {desc}" for pip, _imp, desc in missing)
    print("[Zależności] Brakujące moduły Pythona:\n" + lines)

    pip_names = [m[0] for m in missing]
    pip_cmd = f"{sys.executable} -m pip install " + " ".join(pip_names)

    # GUI pytanie (ukryty root, bo App jeszcze nie istnieje)
    try:
        _r = tk.Tk()
        _r.withdraw()
        ans = messagebox.askyesno(
            "Brakujące zależności",
            "Brakuje następujących modułów Pythona:\n\n"
            f"{lines}\n\n"
            "Zainstalować je teraz automatycznie przez pip?\n"
            f"({pip_cmd})",
            parent=_r,
        )
        if ans:
            try:
                res = subprocess.run(
                    [sys.executable, "-m", "pip", "install", *pip_names],
                    capture_output=True, text=True, timeout=600,
                )
                if res.returncode == 0:
                    messagebox.showinfo(
                        "Zainstalowano",
                        "Moduły zostały zainstalowane.\n\n"
                        "Uruchom program ponownie, aby zmiany zadziałały.",
                        parent=_r,
                    )
                    _r.destroy()
                    sys.exit(0)
                else:
                    messagebox.showerror(
                        "Błąd instalacji",
                        "pip zakończył się błędem:\n\n"
                        f"{(res.stderr or res.stdout)[-800:]}\n\n"
                        f"Zainstaluj ręcznie:\n{pip_cmd}",
                        parent=_r,
                    )
            except Exception as e:
                messagebox.showerror(
                    "Błąd instalacji",
                    f"Nie udało się uruchomić pip: {e}\n\n"
                    f"Zainstaluj ręcznie:\n{pip_cmd}",
                    parent=_r,
                )
        elif crit:
            messagebox.showwarning(
                "Ograniczona funkcjonalność",
                "Program uruchomi się, ale bez brakujących modułów:\n\n"
                + "\n".join(f"  • {p} — {d}" for p, _i, d in crit)
                + f"\n\nAby doinstalować później:\n{pip_cmd}",
                parent=_r,
            )
        _r.destroy()
    except SystemExit:
        raise
    except Exception:
        # Brak GUI (np. środowisko bez wyświetlacza) — zostaje log w konsoli
        print(f"[Zależności] Zainstaluj ręcznie: {pip_cmd}")


# ---------------------------------------------------------------------------
# Build: v7.7 (2026-06-11) — bugfix/perf + ROM verify removed
if __name__ == "__main__":  # pragma: no cover - uruchomienie GUI
    check_dependencies()  # FIX v7.4
    app = App()
    app.mainloop()
