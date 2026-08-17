"""core.rom_args — budowanie argumentów wiersza poleceń emulatora.

Ownership: _rom_build_args — wstawianie ścieżki ROM-a do szablonu argumentów
(placeholder %ROM% albo doklejenie na końcu).

Behavior preserved from legacy single-file module.
"""

from __future__ import annotations


def _rom_build_args(launch_args_tpl: str, rom_path: str) -> str:
    """Zbuduj argumenty cmd dla emulatora.

    Obsługa %ROM% placeholder:
      jeśli wpisano: --nosound %ROM% --nogui
      wynik:         --nosound "D:/roms/game.cue" --nogui

    Jeśli brak %ROM%: plik dołączany na końcu:
      wpisano: --fullscreen
      wynik:   --fullscreen "D:/roms/game.cue"

    Jeśli parametry puste: tylko ścieżka pliku.
    """
    rom_quoted = f'"{rom_path}"'
    if not launch_args_tpl:
        return rom_quoted
    if "%ROM%" in launch_args_tpl:
        return launch_args_tpl.replace("%ROM%", rom_quoted)
    return f'{launch_args_tpl} {rom_quoted}'
