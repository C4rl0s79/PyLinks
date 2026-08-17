"""constants — stałe wartościowe aplikacji (bez ścieżek, bez GUI/platform).

Ownership: domyślne wartości konfiguracji, progi dopasowania, słowniki wyboru
w UI oraz paleta motywu C. Ścieżki są w app_paths.py.

Behavior preserved from legacy single-file module.
"""

from __future__ import annotations

DEFAULT_STEAM_EXE = r"D:\Steam\Steam.exe"
DEFAULT_EXTRA_DIR = r"D:\Games"

DEFAULT_STEAM_API_KEY = ""  # FIX v7: klucz wpisz w Ustawieniach (nie trzymamy w kodzie)
DEFAULT_STEAM_ID64 = ""     # FIX v7: SteamID64 wpisz w Ustawieniach
DEFAULT_SGDB_KEY = ""       # FIX v7: klucz SGDB wpisz w Ustawieniach
DEFAULT_MIN_SIZE = 128
DEFAULT_EXE_SKIP_REGEX = (
    r"unins|crash|redist|setup|vcredist|dxsetup|dotnet|vc_redist|directx|"
    r"oalinst|PhysX|CrashReport|UE4|CEFHelper|EasyAnticheat|BattlEye|"
    r"SteamInstall|LaunchHelper"
)
MATCH_THRESHOLD = 0.85
# FIX v8.2: minimalne podobieństwo nazwy przy AUTO-dopasowaniu IGDB/TheGamesDB.
# Chroni przed pobraniem grafik zupełnie innej gry (np. "Turrican 2" dla
# "Final Fight 2"), gdy API zwróci zły tytuł jako pierwszy wynik.
IGDB_TGDB_MATCH_MIN = 0.5
ICON_TYPES = ["any", "square", "circular", "logo"]
ICON_SHAPES = ["any", "square", "circular"]
MAX_ICONS_CHOICES = ["1", "10", "100", "max"]
DEFAULT_MAX_ICONS = 10
UNLIMITED_ICONS_CAP = 500  # twardy limit bezpieczeństwa dla "max"

C = dict(
    bg="#1e1e2e", bg2="#181825", bg3="#313244",
    fg="#cdd6f4", fg2="#6c7086",
    acc="#89b4fa", grn="#a6e3a1", red="#f38ba8",
    yel="#f9e2af", ext="#cba6f7", orn="#fab387",
)

# FIX v7.6: stare per-źródłowe podkatalogi — używane już tylko do
# wykrywania istniejących skrótów (kompatybilność wstecz)
_LEGACY_PC_DIRS = ("Steam", "GOG", "Epic", "Extra")
