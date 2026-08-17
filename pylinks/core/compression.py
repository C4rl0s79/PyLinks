"""core.compression — kompresja/dekompresja stubów gier (zstd → fallback gzip).

Ownership: stan globalny _ZSTD_OK oraz funkcje _init_zstd / compress_stub /
decompress_stub. _init_zstd() ustawia _ZSTD_OK w TYM module — plik główny
importuje te symbole i woła _init_zstd() przy starcie dokładnie jak dawniej.

Behavior preserved from legacy single-file module.
"""

from __future__ import annotations

import sys
import subprocess


_ZSTD_OK = False   # ustalone przez _init_zstd() przy starcie


def _init_zstd() -> bool:
    """Zainicjuj zstandard: spróbuj importu → auto-pip → fallback gzip."""
    global _ZSTD_OK
    try:
        import zstandard  # noqa
        _ZSTD_OK = True
        return True
    except ImportError:
        pass
    # Auto-install
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "zstandard",
             "--quiet", "--no-input"],
            capture_output=True, timeout=40,
        )
        if r.returncode == 0:
            import importlib
            importlib.invalidate_caches()
            try:
                import zstandard  # noqa
                _ZSTD_OK = True
                return True
            except ImportError:
                pass
    except Exception:
        pass
    return False


def compress_stub(data: bytes) -> bytes:
    """Skompresuj bajty stuba.  Prefiks: b'Z'=zstd, b'G'=gzip."""
    if _ZSTD_OK:
        import zstandard as zstd
        return b"Z" + zstd.ZstdCompressor(level=3).compress(data)
    import gzip
    return b"G" + gzip.compress(data, compresslevel=6)


def decompress_stub(data: bytes) -> bytes:
    """Dekompresuj bajty stuba."""
    marker, payload = data[:1], data[1:]
    if marker == b"Z":
        import zstandard as zstd
        return zstd.ZstdDecompressor().decompress(payload)
    import gzip
    return gzip.decompress(payload)
