"""roms.presets — statyczne dane presetów systemów ROM.

Ownership: ROM_SYSTEM_PRESETS — czyste dane (lista dictów) używane przez
migrację configu, autodetekcję katalogów i dialog ustawień ROM. Bez logiki,
bez zależności od GUI/platform.

Behavior preserved from legacy single-file module (przeniesione 1:1).
"""

from __future__ import annotations

ROM_SYSTEM_PRESETS: list[dict] = [
    # Pola:
    #   name         – identyfikator (= klucz LIBRETRO_SYSTEM_MAP)
    #   display      – nazwa w dropdown
    #   dir_names    – foldery w kolejności priorytetu:
    #                    [własna skrótowa, EmulationStation, No-Intro/Libretro, ...]
    #   primary_ext  – kolejność przy wyborze głównego pliku (tryb podkat.)
    #   all_exts     – WSZYSTKIE rozszerzenia platformy do skanowania
    #   roms_in_subdirs – domyślna wartość
    #   note         – popularne emulatory

    # ── Sony ──────────────────────────────────────────────────────────────────
    {"name": "PS1",    "display": "PlayStation 1",
     "dir_names":    ["PS1", "psx", "ps1", "Sony - PlayStation", "Playstation"],
     "primary_ext":  "m3u,cue,iso,chd,bin",
     "all_exts":     "m3u,cue,iso,chd,bin,sub,img,ecm,mdf,nrg,pbp",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "ePSXe / DuckStation / PCSX-Reloaded"},

    {"name": "PS2",    "display": "PlayStation 2",
     "dir_names":    ["PS2", "ps2", "Sony - PlayStation 2"],
     "primary_ext":  "iso,chd,bin,mdf",
     "all_exts":     "iso,chd,bin,mdf,nrg",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "PCSX2"},

    {"name": "PS3",    "display": "PlayStation 3",
     "dir_names":    ["PS3", "ps3", "Sony - PlayStation 3"],
     "primary_ext":  "lnk,iso,pkg",
     "all_exts":     "lnk,iso,pkg,folder",
     "roms_in_subdirs": True, "launch_args": "",
     "note": "RPCS3 — wrzuć skróty .lnk utworzone w RPCS3 do roms/PS3; "
             "PyLinks użyje ich nazw do wyszukania ikon, skopiuje skrót "
             "do LINKS i podmieni w nim ikonę"},

    {"name": "PSP",    "display": "PlayStation Portable",
     "dir_names":    ["PSP", "psp", "Sony - PlayStation Portable"],
     "primary_ext":  "iso,cso,pbp",
     "all_exts":     "iso,cso,pbp,elf,prx",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "PPSSPP"},

    # ── Nintendo ──────────────────────────────────────────────────────────────
    {"name": "NES",    "display": "Nintendo NES",
     "dir_names":    ["NES", "nes", "fc", "famicom",
                      "Nintendo - Nintendo Entertainment System"],
     "primary_ext":  "nes,fds,zip,7z",
     "all_exts":     "nes,fds,unf,unif,zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "FCEUX / Mesen / RetroArch"},

    {"name": "SNES",   "display": "Super Nintendo (SNES)",
     "dir_names":    ["SNES", "snes", "sfc", "superfamicom",
                      "Nintendo - Super Nintendo Entertainment System"],
     "primary_ext":  "sfc,smc,zip,7z",
     "all_exts":     "sfc,smc,fig,swc,bs,st,zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "Snes9x / bsnes / RetroArch"},

    {"name": "N64",    "display": "Nintendo 64",
     "dir_names":    ["N64", "n64", "Nintendo - Nintendo 64"],
     "primary_ext":  "z64,n64,v64,zip",
     "all_exts":     "z64,n64,v64,ndd,zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "Project64 / RetroArch (Mupen64Plus)"},

    {"name": "GB",     "display": "Game Boy",
     "dir_names":    ["GB", "gb", "gameboy", "Nintendo - Game Boy"],
     "primary_ext":  "gb,zip,7z",
     "all_exts":     "gb,sgb,zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "mGBA / RetroArch"},

    {"name": "GBC",    "display": "Game Boy Color",
     "dir_names":    ["GBC", "gbc", "gameboycolor", "Nintendo - Game Boy Color"],
     "primary_ext":  "gbc,gb,zip,7z",
     "all_exts":     "gbc,gb,zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "mGBA / RetroArch"},

    {"name": "GBA",    "display": "Game Boy Advance",
     "dir_names":    ["GBA", "gba", "gameboyadvance",
                      "Nintendo - Game Boy Advance"],
     "primary_ext":  "gba,zip,7z",
     "all_exts":     "gba,zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "mGBA / VisualBoyAdvance-M"},

    {"name": "NDS",    "display": "Nintendo DS",
     "dir_names":    ["NDS", "nds", "ds", "Nintendo - Nintendo DS"],
     "primary_ext":  "nds,zip",
     "all_exts":     "nds,dsi,ids,srl,zip",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "DeSmuME / melonDS"},

    {"name": "GCN",    "display": "GameCube",
     "dir_names":    ["GCN", "gc", "gamecube", "Nintendo - GameCube"],
     "primary_ext":  "iso,rvz,gcm,gcz",
     "all_exts":     "iso,rvz,gcm,gcz,nkit,ciso",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "Dolphin"},

    {"name": "WII",    "display": "Wii",
     "dir_names":    ["WII", "wii", "Nintendo - Wii"],
     "primary_ext":  "iso,rvz,wbfs,gcz",
     "all_exts":     "iso,rvz,wbfs,gcz,nkit,wad,ciso",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "Dolphin"},

    # ── Sega ──────────────────────────────────────────────────────────────────
    {"name": "MD",     "display": "Mega Drive / Genesis",
     "dir_names":    ["MD", "megadrive", "genesis",
                      "Sega - Mega Drive - Genesis", "megadrive-genesis"],
     "primary_ext":  "md,bin,smd,zip,7z",
     "all_exts":     "md,bin,smd,gen,68k,sgd,zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "Fusion / RetroArch (Genesis Plus GX)"},

    {"name": "SMS",    "display": "Master System",
     "dir_names":    ["SMS", "mastersystem", "ms",
                      "Sega - Master System - Mark III"],
     "primary_ext":  "sms,zip,7z",
     "all_exts":     "sms,sg,sc,zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "Fusion / RetroArch"},

    {"name": "GG",     "display": "Game Gear",
     "dir_names":    ["GG", "gamegear", "gg", "Sega - Game Gear"],
     "primary_ext":  "gg,zip,7z",
     "all_exts":     "gg,zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "Fusion / RetroArch"},

    {"name": "SATURN", "display": "Sega Saturn",
     "dir_names":    ["SATURN", "saturn", "Sega - Saturn"],
     "primary_ext":  "cue,iso,bin,chd,mdf",
     "all_exts":     "cue,iso,bin,chd,mdf,img,ccd",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "SSF / Mednafen / Kronos"},

    {"name": "DC",     "display": "Dreamcast",
     "dir_names":    ["DC", "dreamcast", "Sega - Dreamcast"],
     "primary_ext":  "gdi,cdi,chd,cue,iso",
     "all_exts":     "gdi,cdi,chd,iso,cue,bin",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "redream / Flycast / Demul"},

    # ── Arcade / inne ─────────────────────────────────────────────────────────
    {"name": "MAME",   "display": "MAME (Arcade)",
     "dir_names":    ["MAME", "mame", "arcade", "MAME 2003-Plus"],
     "primary_ext":  "zip,7z,chd",
     "all_exts":     "zip,7z,chd",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "MAME"},

    {"name": "NEOGEO", "display": "Neo Geo",
     "dir_names":    ["NEOGEO", "neogeo", "neo-geo", "SNK - Neo Geo"],
     "primary_ext":  "zip,7z",
     "all_exts":     "zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "MAME / FinalBurn Neo"},

    {"name": "PCENGINE", "display": "PC Engine / TurboGrafx-16",
     "dir_names":    ["PCENGINE", "pcengine", "turbografx", "tg16",
                      "NEC - PC Engine - TurboGrafx-16"],
     "primary_ext":  "pce,cue,iso,chd",
     "all_exts":     "pce,sgx,cue,iso,chd,ccd,img",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "Mednafen / RetroArch"},

    {"name": "ATARI2600", "display": "Atari 2600",
     "dir_names":    ["ATARI2600", "atari2600", "atari-2600",
                      "Atari - 2600"],
     "primary_ext":  "a26,bin,zip",
     "all_exts":     "a26,bin,rom,zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "Stella / RetroArch"},

    {"name": "3DO",    "display": "3DO Interactive Multiplayer",
     "dir_names":    ["3DO", "3do", "3DO Interactive Multiplayer"],
     "primary_ext":  "iso,cue,bin,chd",
     "all_exts":     "iso,cue,bin,chd",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "4DO / Opera (RetroArch)"},

    # ── Sega dodatki ──────────────────────────────────────────────────────────
    {"name": "SEGACD", "display": "Sega CD / Mega CD",
     "dir_names":    ["SEGACD", "segacd", "megacd", "Sega - Mega CD",
                      "Sega - Mega CD & Sega CD", "Sega CD"],
     "primary_ext":  "cue,iso,chd,bin",
     "all_exts":     "cue,iso,chd,bin,img,mdf,zip",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "RetroArch (Genesis Plus GX) / Kega Fusion"},

    # ── Atari ─────────────────────────────────────────────────────────────────
    {"name": "JAGUAR", "display": "Atari Jaguar",
     "dir_names":    ["JAGUAR", "atarijaguar", "atari-jaguar", "Atari - Jaguar"],
     "primary_ext":  "jag,j64,rom,zip",
     "all_exts":     "jag,j64,rom,zip,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "Virtual Jaguar / RetroArch (Virtual Jaguar)"},

    # ── Amiga ─────────────────────────────────────────────────────────────────
    {"name": "AMIGA",  "display": "Amiga (WHDLoad)",
     "dir_names":    ["AMIGA", "amiga", "Amiga - WHDLoad", "Commodore - Amiga"],
     "primary_ext":  "lha,lzx,zip",
     "all_exts":     "lha,lzx,zip,adf,hdf,dms,ipf",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "FS-UAE / WinUAE (wymaga WHDLoad)"},

    # ── Arcade NAOMI ──────────────────────────────────────────────────────────
    {"name": "NAOMI",  "display": "Sega NAOMI",
     "dir_names":    ["NAOMI", "naomi", "Sega NAOMI"],
     "primary_ext":  "zip,7z",
     "all_exts":     "zip,7z,chd",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "MAME / Flycast"},

    {"name": "NAOMI2", "display": "Sega NAOMI 2",
     "dir_names":    ["NAOMI2", "naomi2", "Sega NAOMI 2"],
     "primary_ext":  "zip,7z",
     "all_exts":     "zip,7z,chd",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "MAME / Flycast"},

    # ── SNES MSU-1 ────────────────────────────────────────────────────────────
    {"name": "SNESMSU1", "display": "SNES MSU-1 (enhanced soundtrack)",
     "dir_names":    ["SNES-MSU1", "SNESMSU1", "snes-msu1"],
     "primary_ext":  "sfc,smc",
     "all_exts":     "sfc,smc,msu,pcm",
     "roms_in_subdirs": True, "launch_args": "",
     "note": "RetroArch (Snes9x) z obsługą MSU-1 / bsnes"},

    # ── Kolekcje Fan-Tłumaczeń ────────────────────────────────────────────────
    {"name": "MSX2",   "display": "Microsoft MSX2",
     "dir_names":    ["MSX2", "msx2", "Microsoft - MSX2 [T-En] Collection",
                      "Microsoft - MSX2"],
     "primary_ext":  "zip,rom",
     "all_exts":     "zip,rom,mx2,7z",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "openMSX / RetroArch (fMSX)"},

    {"name": "PC98",   "display": "NEC PC-9801",
     "dir_names":    ["PC98", "pc98", "NEC - PC-9801 [T-En] Collection",
                      "NEC - PC-9801"],
     "primary_ext":  "zip,hdi,nhd",
     "all_exts":     "zip,hdi,nhd,hdd,fdi,hdm,2hd,thd,xdf,88d,cmd",
     "roms_in_subdirs": False, "launch_args": "",
     "note": "Neko Project II / RetroArch (Neko Project II Kai)"},
]
