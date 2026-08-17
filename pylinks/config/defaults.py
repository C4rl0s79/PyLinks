"""config.defaults — fabryka domyślnej konfiguracji (schemat v3).

Ownership: pełny domyślny słownik configu. Nie zmienia schematu ani kluczy.
v8.2: klucze grzbietu platformy (icon_platform_spine, platform_logo_dir…) —
platform_logo_dir zależy od SCRIPT_DIR, więc importujemy go z app_paths.

Behavior preserved from legacy single-file module.
"""

from __future__ import annotations

from pylinks.app_paths import SCRIPT_DIR
from pylinks.constants import (
    DEFAULT_STEAM_API_KEY,
    DEFAULT_SGDB_KEY,
    DEFAULT_STEAM_ID64,
    DEFAULT_EXE_SKIP_REGEX,
    DEFAULT_MIN_SIZE,
    DEFAULT_MAX_ICONS,
    DEFAULT_STEAM_EXE,
    DEFAULT_EXTRA_DIR,
)


def _default_config() -> dict:
    return {
        "version": 3,
        "api_keys": {
            "steam_api_key": DEFAULT_STEAM_API_KEY,
            "sgdb_key": DEFAULT_SGDB_KEY,
            "steam_id64": DEFAULT_STEAM_ID64,
        },
        "use_steam_web_api": True,
        "thumb_size": 100,  # FIX v7.4: wielkość podglądów (suwak 64-256)
        # v8.2: „grzbiet" platformy na ikonie ROM-a (jak grzbiet pudełka płyty)
        # — pozwala odróżnić gry o tym samym tytule na różnych platformach.
        "icon_platform_spine": False,
        "icon_spine_side": "left",   # "left" | "right"
        # folder z logotypami platform (auto-pobierane, gdy pusty i grzbiet ON)
        "platform_logo_dir": str(SCRIPT_DIR / "platform_logos"),
        "spine_logo_style": "Light - Just White",  # kolorystyka logotypów grzbietu
        "filters": {
            "exe_skip_regex": DEFAULT_EXE_SKIP_REGEX,
            "min_icon_size": DEFAULT_MIN_SIZE,
            "preferred_icon_type": "any",
            "icon_shape": "any",
            "max_icons_per_game": DEFAULT_MAX_ICONS,
        },
        "steam_exe": DEFAULT_STEAM_EXE,
        "extra_dir": DEFAULT_EXTRA_DIR,
        "extra_dirs_list": [],
        "steam_lib_dirs": [],
        "use_libraryfolders_vdf": True,
        "scan_epic": True,
        "scan_gog": True,
        "scan_on_startup": False,    # diff-skan ROM-ów przy starcie
        "ui_mode": "advanced",      # v8.0: "simple" | "advanced"
        "cache_limit_mb": 2048,      # v7.9 (D): limit cache assetów; po
                                     # przekroczeniu eksmisja LRU (0 = bez limitu)
        "auto_fetch_art": True,      # FIX v7.2: po skanie pobieraj w tle
                                     # plakaty SGDB + IGDB/TGDB dla każdej gry
        "steam_userdata_dir": "",    # ścieżka do userdata Steam (auto-detect)
        "window_geometry": "1400x900",
        # Wybrane gry i indeksy ikon (globalnie, bez profili)
        "enabled_keys": [],
        "selected_indices": {},        # legacy: game_key → int index
        "selected_icon_keys": {},       # stable: game_key → url/path/remote_id
        "selected_game_key": None,
        "rom_support": {
            "enabled":      False,
            "base_rom_dir": "",   # wspólny folder z ROM-ami, np. D:/ROMs
            "base_emu_dir": "",   # wspólny folder z emulatorami, np. D:/Emulatory
            "systems": [
                {"name": "PS1", "rom_dir": "", "emulator": "",
                 "roms_in_subdirs": False, "launch_args": "",
                 "primary_ext": "m3u,cue,iso,chd,bin"},
                {"name": "PS2", "rom_dir": "", "emulator": "",
                 "roms_in_subdirs": False, "launch_args": "",
                 "primary_ext": "m3u,cue,iso,chd,bin"},
            ],
        },
        "last_run_errors": {},
        "extra_sources": {
            "steam_cdn":            True,
            "libretro":             True,
            "igdb":                 False,
            "igdb_client_id":       "",
            "igdb_client_secret":   "",
            "tgdb":                 False,
            "tgdb_key":             "",
            "screenscraper":        False,
            "screenscraper_user":   "",
            "screenscraper_pass":   "",
            "screenscraper_devid":  "",
            "screenscraper_devpass":"",
        },
    }
