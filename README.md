# PyLinks

Narzędzie (Windows, GUI tkinter) do tworzenia i utrzymywania skrótów do gier:
skanuje biblioteki **Steam / GOG / Epic** oraz katalogi „Extra", pobiera grafiki/ikony
(SteamGridDB, Steam CDN, Libretro, IGDB, TheGamesDB, ScreenScraper) i generuje
skróty `.lnk`/`.url` pogrupowane per platforma — z podmienionymi ikonami.
Obsługuje też **ROM-y/emulatory** (presety systemów, playlisty `.m3u` multi-disc,
grzbiet platformy na ikonie, eksport do biblioteki Steam).

## Wymagania

- **Python 3.10+** (Windows)
- **Pillow** — obróbka grafik/ikon (wymagane)
- *(opcjonalnie)* **zstandard** — kompresja stubów; przy braku instaluje się
  automatycznie, a jako fallback używany jest `gzip`
- Reszta na bibliotece standardowej (`tkinter`, `sqlite3`, `urllib`, `ctypes`…)

```bash
pip install -r requirements.txt
```

## Uruchomienie

```bash
python PyLinks_v8_4.py
```

Przy pierwszym starcie obok skryptu powstają katalogi robocze `Cache/`, `LINKS/`,
`Reports/` oraz `config.json`. Klucze API (Steam, SteamGridDB, IGDB…) wpisuje się
w **Ustawieniach** — nie są trzymane w kodzie.

## Struktura

Aplikacja przechodzi fazowy refaktor z jednego pliku do pakietu. **Faza 1**
wydzieliła czyste, niskiego ryzyka moduły; logika GUI/skanowania nadal żyje
w pliku głównym i importuje te symbole zwrotnie (compatibility bridge), więc
zachowanie i formaty pozostają bez zmian.

```
PyLinks_v8_4.py          # plik główny (GUI, skanowanie, sieć) + mostek importów
pylinks/
  app_paths.py           # ścieżki aplikacji (Cache/LINKS/Reports/config)
  constants.py           # stałe: progi dopasowania, słowniki UI, paleta
  config/
    defaults.py          # fabryka domyślnej konfiguracji (schemat v3)
    migrate.py           # migracja starych configów v1/v2 → v3
  core/
    naming.py            # safe_name — bezpieczne nazwy plików
    matching.py          # podobieństwo tytułów (bigramy) + disambiguacja
    rom_args.py          # budowanie argumentów emulatora (%ROM%)
    compression.py       # kompresja stubów (zstd → fallback gzip)
  roms/
    presets.py           # presety systemów ROM (dane)
platform_logos/          # logotypy platform (grzbiet ikony)
CHANGELOG.md
```

Historia zmian: [CHANGELOG.md](CHANGELOG.md).
