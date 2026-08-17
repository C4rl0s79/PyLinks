"""core.naming — normalizacja nazw plików/tytułów.

Ownership: safe_name — zamiana tytułu gry na bezpieczną nazwę pliku skrótu.

Behavior preserved from legacy single-file module.
"""

from __future__ import annotations

import re


def safe_name(name: str) -> str:
    for ch in ["\u2122", "\u00ae", "\u2026", "\u2019", "\u2018"]:
        name = name.replace(ch, "")
    name = re.sub(r'[<>:"/\\|?*\']', "_", name)
    name = re.sub(r"[\x00-\x1f]", "", name)
    return re.sub(r"\s+", " ", name).strip().rstrip(". ")[:120]
