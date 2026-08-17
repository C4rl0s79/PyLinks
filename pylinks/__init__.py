"""pylinks — pakiet powstały z fazowego refaktoru jednoplikowej aplikacji.

Faza 1: wydzielone zostały wyłącznie niskiego ryzyka, czyste moduły
(ścieżki, stałe, domyślny config, helpery naming/matching/rom_args/compression,
presety ROM). Reszta kodu nadal żyje w pliku głównym (PyLinks_v8_4.py) i
importuje stąd te symbole zwrotnie (compatibility bridge). Zachowanie i formaty
bez zmian.
"""
