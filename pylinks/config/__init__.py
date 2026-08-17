"""config — domyślne wartości, migracja i repozytorium ustawień.

Faza 1: wydzielono defaults.py (_default_config) oraz migrate.py
(migrate_config/_migrate_rom_v3). load_config()/save_config() pozostają
chwilowo w pliku głównym (kolejny krok: repository.py).
"""
