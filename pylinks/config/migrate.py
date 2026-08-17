"""config.migrate — migracja starych configów (v1/v2) do schematu v3.

Ownership: migrate_config() + _migrate_rom_v3(). Przeniesione 1:1 z pliku
głównego. Zależności (bez cykli):
  - _default_config     ← pylinks.config.defaults
  - ROM_SYSTEM_PRESETS  ← pylinks.roms.presets

Behavior preserved from legacy single-file module.
"""

from __future__ import annotations

from pylinks.config.defaults import _default_config
from pylinks.roms.presets import ROM_SYSTEM_PRESETS


def migrate_config(raw: dict) -> dict:
    """Migracja starych configów (v1/v2) do v3.

    v3 zmiany:
    - Usunięto profiles / current_profile / cache_dir / output_dir
    - enabled_keys i selected_indices przeniesione na poziom główny
    - rom_support.platforms (dict) → rom_support.systems (list)
    """
    if not raw:
        return _default_config()
    base = _default_config()

    if raw.get("version") == 3:
        # uzupełnij ewentualnie brakujące pola
        for k, v in base.items():
            raw.setdefault(k, v)
        for k, v in base["api_keys"].items():
            raw["api_keys"].setdefault(k, v)
        for k, v in base["filters"].items():
            raw["filters"].setdefault(k, v)
        for k, v in base["extra_sources"].items():
            raw.setdefault("extra_sources", {})
            raw["extra_sources"].setdefault(k, v)
        # FIX v7: weryfikacja ROM przeniesiona do osobnego programu —
        # usuwamy jej osierocone klucze ze starych configów
        for dead in ("tool_paths", "temp_extract_dir", "dat_assignments",
                     "ramdisk", "ramdisk_drive", "ramdisk_size_gb"):
            raw.pop(dead, None)
        _migrate_rom_v3(raw)
        return raw

    # v1 / v2 → v3
    cfg = base.copy()
    cfg["steam_exe"]        = raw.get("steam_exe",        base["steam_exe"])
    cfg["extra_dir"]        = raw.get("extra_dir",        base["extra_dir"])
    cfg["extra_dirs_list"]  = raw.get("extra_dirs_list",  [])
    cfg["steam_lib_dirs"]   = raw.get("steam_lib_dirs",   [])
    cfg["window_geometry"]  = raw.get("window_geometry",  base["window_geometry"])
    cfg["use_steam_web_api"]= raw.get("use_steam_web_api", True)
    cfg["scan_epic"]        = raw.get("scan_epic",        True)
    cfg["scan_gog"]         = raw.get("scan_gog",         True)

    # enabled_keys z profili (zachowane, reszta profilu odpada)
    profs = raw.get("profiles", {})
    cur   = raw.get("current_profile", "")
    if cur and cur in profs:
        cfg["enabled_keys"]     = profs[cur].get("enabled_keys", [])
        cfg["selected_indices"] = profs[cur].get("selected_indices", {})

    # api_keys
    if "api_keys" in raw:
        for k, v in raw["api_keys"].items():
            cfg["api_keys"][k] = v
    if "filters" in raw:
        for k, v in raw["filters"].items():
            cfg["filters"][k] = v
    if "extra_sources" in raw:
        for k, v in raw["extra_sources"].items():
            cfg["extra_sources"][k] = v

    # ROM migracja
    cfg["rom_support"] = raw.get("rom_support", base["rom_support"])
    _migrate_rom_v3(cfg)
    return cfg


def _migrate_rom_v3(cfg: dict):
    """Migruj ROM: platforms (dict) → systems (list), usuń output_dir/icon_dir."""
    rs = cfg.get("rom_support")
    if not isinstance(rs, dict):
        cfg["rom_support"] = _default_config()["rom_support"]
        return
    old_plats = rs.get("platforms")
    if isinstance(old_plats, dict):
        systems = []
        for name, pcfg in old_plats.items():
            systems.append({
                "name":     name,
                "rom_dir":  pcfg.get("rom_dir",  ""),
                "emulator": pcfg.get("emulator", ""),
            })
        rs["systems"] = systems
        del rs["platforms"]
    rs.setdefault("systems", [])
    rs.setdefault("base_rom_dir", "")
    rs.setdefault("base_emu_dir", "")
    # upewnij się że każdy system ma tylko wymagane pola
    clean = []
    for s in rs["systems"]:
        if isinstance(s, dict) and s.get("name"):
            # Jeśli brak all_exts, spróbuj uzupełnić z presetu
            _all_e = str(s.get("all_exts", ""))
            if not _all_e:
                _preset = next(
                    (p for p in ROM_SYSTEM_PRESETS
                     if p["name"] == s.get("name", "").upper()),
                    None
                )
                _all_e = _preset["all_exts"] if _preset else s.get("primary_ext", "")
            _pri = str(s.get("primary_ext", "m3u,cue,iso,chd,bin"))
            # v7.8: PS3 — skróty .lnk z RPCS3 są plikiem głównym gry.
            # Dopisz "lnk" do istniejących configów, żeby stare instalacje
            # też widziały linki bez ręcznej edycji ustawień systemu.
            if str(s.get("name", "")).upper() == "PS3":
                if "lnk" not in [e.strip().lower() for e in _pri.split(",")]:
                    _pri = "lnk," + _pri
                if "lnk" not in [e.strip().lower() for e in _all_e.split(",")]:
                    _all_e = ("lnk," + _all_e) if _all_e else "lnk"
            clean.append({
                "name":            str(s.get("name",     "")),
                "rom_dir":         str(s.get("rom_dir",  "")),
                "emulator":        str(s.get("emulator", "")),
                "roms_in_subdirs": bool(s.get("roms_in_subdirs", False)),
                "launch_args":     str(s.get("launch_args", "")),
                "primary_ext":     _pri,
                "all_exts":        _all_e,
            })
    rs["systems"] = clean
