# PyLinks — dziennik zmian (CHANGELOG)

> Jeden plik na całą historię; sekcje oznaczone wersją (v8.2 → v8.3 → v8.4 → …).
> Najnowsze na górze. Wcześniej dziennik nazywał się CHANGES_v8_2.md.


## Nowa wersja: PyLinks_v8_4.py
- Utworzona z v8_3 (nagłówek v8.4). Zawiera wszystkie zmiany tej sesji.

## NOWE (v8_4): niekwadratowe ikony bez grzbietu → przezroczyste boki
- Grafiki niekwadratowe (np. okładka 600x900), które NIE dostają grzbietu, były
  ROZCIĄGANE do 256x256 (deformacja portretu). Teraz `make_ico_bytes` wpasowuje
  je w kwadrat z PRZEZROCZYSTYMI marginesami po bokach — proporcje zachowane,
  ikona jest kwadratem. Kwadratowe i te z grzbietem (już kwadratowe) bez zmian.
  Zweryfikowane: portret → pełna wysokość + przezroczyste pillarboxy, kwadrat → bez marginesu.

## FIX (v8_4): stara ikona mimo nowej grafiki (cache ikon Windows)
- OBJAW: po zmianie grafiki i utworzeniu skrótów .lnk Explorer pokazywał STARĄ
  ikonę, mimo że .ico był poprawnie zregenerowany (sprawdzone: treść .ico =
  nowo wybrana grafika). Restart explorera nie pomagał.
- PRZYCZYNA: Windows buforuje ikony per ŚCIEŻKA. `.ico` miał stałą nazwę
  `Cache\<uid>.ico`; treść się zmieniała, ścieżka nie → shell serwował starą
  ikonę z bazy iconcache (którą restart explorera nie przebudowuje).
- FIX: `cache_ico` nazywa plik `<uid>_<md5(treści)>.ico`. Zmiana ikony → zmiana
  ścieżki → Explorer ładuje świeżą (ta sama treść = ta sama nazwa, bez śmiecenia;
  stare warianty tego uid sprzątane). Po ponownym utworzeniu skrótów nowe ikony
  pojawiają się od razu, BEZ czyszczenia cache. `_ico_exists_in_output` → glob.

## FIX (v8_4): plakaty/IGDB/TGDB nie pojawiały się (regresja po zmianie klucza)
- PRZYCZYNA: po zmianie `_game_key` na stabilny (rom::plat::nazwa) rozjechały się
  klucze DOPASOWANIA wyników wątków. Producent (`_poster_thread`, `_auto_art_worker`)
  kluczował po `_poster_key`/`uid` (pozycyjny „ps2_50"), a konsument w `_tick`
  (`posters_ready`/`art_ready`) szukał gry po NOWYM `_game_key` („rom::ps2::…") →
  `target=None` → pobrane plakaty i grafiki IGDB/TGDB nie dołączały się do gry.
- FIX: osobny `_async_key` (tożsamość SESYJNA: `_poster_key`/`uid`, nie-ROM →
  `_game_key`) używany SPÓJNIE przez producentów i konsumentów wątków. `_game_key`
  zostaje wyłącznie do ZAPISU (trwały), `_async_key` do dopasowania w locie.
- Przy okazji: „Plakaty" (SGDB) miały filtr `dimensions=512x512,1024x1024` (tylko
  kwadraty) → 0 dla gier bez kwadratowych gridów.

## FIX (v8_4): „Plakaty" nie pobierały ładnych okładek (a Sync tak)
- PRZYCZYNA: „Plakaty"/auto-art (`_fetch_grids`) pytały SGDB TYLKO o kwadraty
  (`dimensions=512x512,1024x1024`), a większość gier ma okładki 600x900 (portret).
  „Sync cache" (`_fetch_asset_list`) pyta BEZ filtra → dostawał te okładki. Stąd
  „dobre okładki tylko po Sync". IGDB/TGDB to osobne bazy (często screeny/artworki).
- FIX: `_fetch_grids` pobiera teraz WSZYSTKIE wymiary (jak Sync). Dowód na żywo
  (Shadow of Destiny, sgdb_id 38110): kwadraty=0 → wszystkie=20 (15× 600x900).
  `grids_to_cands` nie filtruje po wymiarach, więc okładki wchodzą do kandydatów.
- FIX 2 (regresja powyższego): bez filtra SGDB zwracał top wg trafności = same
  portrety, a KWADRATY (na ikonę) wypadały poza pierwsze 20 → „przestał pobierać
  kwadratowe". Teraz `_fetch_grids` robi DWA zapytania (kwadraty + wszystkie) i
  scala: kwadraty PIERWSZE, potem reszta, bez duplikatów po id. Zweryfikowane:
  gry z kwadratami mają je na początku listy, gry bez — same okładki.

## FIX KRYTYCZNY (v8_4): gubienie powiązań ikon ROM (klucz pozycyjny!)
- PRZYCZYNA (powtarzająca się): `_game_key` dla ROM-ów brał `uid` = `{plat}_{idx}`
  — POZYCJĘ w skanie. selected_icon_keys/steam_art_by_key były kluczowane po
  pozycji („ps2_6", „x 360_5"). Każda zmiana kolejności/zestawu (dodanie pliku,
  scalanie multi-disc — .m3u idą na PRZÓD listy!, dodanie skanu .lnk dla X360)
  przesuwała indeksy → wszystkie powiązania od tego miejsca się rozjeżdżały.
  Realny config: 2145 wpisów, ROM-owe wszystkie pozycyjne (ps1_…, ps2_…).
- FIX: `_game_key` dla ROM = `rom::{platforma}::{znormalizowana nazwa}` (bez
  regionu/dysku). Ta sama gra = ten sam klucz niezależnie od pozycji i pliku
  (iso↔lnk↔m3u, Disc 1↔Disc 2). Nie-ROM bez zmian (appid/game_dir stabilne).
- MIGRACJA jednorazowa: `_cfg_map_migrate` przenosi stary klucz pozycyjny (uid)
  na nowy stabilny przy odczycie (selected_icon_keys, selected_indices,
  steam_art_by_key, enabled). Bezpieczne dla ikon — `_candidate_matches_key`
  dopasuje identyfikator tylko gdy należy do kandydatów TEJ gry (błędne pozycyjnie
  po prostu nie dopasują → gra do ponownego wyboru, bez fałszywej ikony).
- Kopia configu: config.json.bak-20260814-102527.
- ODZYSK po treści (skrypt jednorazowy): migracja pozycyjna zawiodła (pozycje
  PS2 przesunięte przez .m3u na przodzie listy), więc powiązania odtworzono
  z bazy SQLite: stary `{plat}_{N}` → wartość=id ikony → asset→game.name (JOIN
  assets/games) → nowy `rom::{plat}::{norm_name}`. Niezależne od pozycji, bo
  identyfikator ikony należy w bazie do gry, dla której go wybrano. Odzyskano
  540: PS2 150/152, X360 35/42, GCN 43, PSP 22, PS3 21, SNESMSU1 139, PS1 118.
  (PS1 częściowo — reszta to stare URL-e / ikony skasowane dawną eksmisją.)
  Zweryfikowane: klucz zgodny z `_game_key`, wartość zgodna z asset danej gry.

## FIX (v8_4): X360 — .lnk w folderze ROM-ów jak PS3 (kopiuj + ikona)
- PRZYCZYNA: folder roms/x360 miał 38 gotowych .lnk (Xenia) I 47 .iso. `_rom_scan`
  NIE skanował .lnk (brak w extensions) → brały się tylko surowe .iso, a że
  emulator systemu to „D:\Emu" (KATALOG, nie .exe) → skróty z PUSTYM targetem.
- FIX: `.lnk` zawsze skanowane (dodane do `_rom_scan` exts). `.lnk` POKRYWA
  surowy plik, który uruchamia (jak .m3u pokrywa dyski): `_lnk_referenced_files`
  czyta target/args skrótu, plus fallback po znormalizowanej nazwie
  (`_norm_rom_stem`, region/tag pominięte). Dzięki temu .iso z własnym .lnk nie
  staje się drugą, niedziałającą grą. Na realnym X360: 38 .lnk-gier + 4 .iso bez
  .lnk (reszta .iso pokryta).
- FIX: surowy ROM bez emulatora NIE tworzy już skrótu z pustym targetem —
  trafia do raportu jako błąd „Brak emulatora dla systemu … — ustaw .exe w ⚙
  ROMy albo dodaj .lnk gry". `_MAIN_FILE_EXT_RANK`: .lnk najwyższy priorytet.

## FIX (v8_4): grzbiet dla Xbox 360 (nazwa systemu ≠ nazwa pliku logo)
- PRZYCZYNA: system ROM nazwany „X 360" (ze spacją), a plik logo to „X360.png".
  `_spine_canon_key` tylko uppercase'owało klucz → „X 360" nie trafiało w plik →
  brak grzbietu.
- FIX: `_spine_canon_key` NORMALIZUJE klucz — usuwa spacje/`._-` i uppercase, więc
  „X 360"/„x-360"/„X_360"/„XBOX 360" → „X360". Aliasy: XBOX360→X360, XBOXONE/
  XBONE→XONE, VITA→PSVITA, DS→NDS. Priorytet konkretnego logo (np. SNESMSU1.png)
  zachowany — add_platform_spine dalej próbuje najpierw oryginalnego klucza.

## Grafiki Steam: trwałe zapamiętywanie + zapis natychmiast po kliknięciu
- FIX: grafiki Steam (`steam_art = {typ: url}`) NIE były zapisywane do configu —
  `_save_settings` zapisywał tylko wybór ikon .lnk. Znikały po skanie/restarcie.
  Teraz trzymane w `steam_art_by_key` (po `game_key`), przywracane przez
  `_restore_steam_art` (wpięte w `_restore_selected_icon` i
  `_apply_saved_state_to_games`) — symetrycznie do ikon .lnk. Klucz przeżywa
  migrację configu v3 (round-trip zweryfikowany). `_clear_cache` czyści też mapę.
- NOWE `_persist_now(game)`: wybór ikony .lnk ORAZ grafiki Steam zapisywany
  NATYCHMIAST po kliknięciu (bez 500 ms debounce), lekko (tylko ta gra). Dzięki
  temu po nagłym zamknięciu można dokończyć wybór, a nie zaczynać od nowa.
  Podpięte pod klik ikony (`_draw_detail.on_click`) i grafiki (`_steam_choose`).



## FIX: tryb Steam — nie dało się przewijać kółkiem
- PRZYCZYNA: przewijanie włączane przez `bind_all("<MouseWheel>")` na `<Enter>`
  i wyłączane na `<Leave>` canvasu/`_grid`. W trybie Steam ramka `thumbs`
  (fill+expand) zakrywa cały `_grid`; najechanie na kartę dawało `_grid <Leave>`
  (detal NotifyInferior) → handler ODPINAŁ kółko. W trybie .lnk karty leżą wprost
  w `_grid`, zostają gołe obszary, więc problem nie występował.
- FIX: `_on_grid_leave` ignoruje `<Leave>` z detalem NotifyInferior (wjazd w
  dziecko, nie opuszczenie siatki). Dodatkowo handlery Enter/Leave podpięte pod
  ramkę `thumbs` w trybie Steam. Kółko działa nad miniaturami jak w .lnk.

## FIX: tryb Steam zawieszał się przy ładowaniu miniatur
- PRZYCZYNA: `_steam_load_thumb` był wołany przez `self.after(...)` (wątek UI) i
  w środku robił `steam_fetch_cached` → przy zimnym cache `fetch_api` (timeout do
  25 s). 30 miniatur × synchronicznie na wątku UI = program „momentalnie" zamarza.
  Tryb .lnk tego nie miał (lokalne pliki/bajty w RAM, bez sieci).
- FIX: pobieranie bajtów przeniesione na ograniczoną pulę wątków
  (`_steam_thumb_pool`, max 6). Dekodowanie do `PhotoImage` (obiekt Tk) wraca na
  wątek UI przez `after(0, …)`. Strażnik tokenu + `winfo_exists` na obu etapach.
  Pula zamykana w `_on_close`.

## Skróty: .m3u dla frontendów, ale .lnk/Steam z Disc 1 (tylko PS2)
- .m3u ZOSTAJE w skanie/liście i eksporcie do frontendów (Playnite/LaunchBox) —
  filtrują powtarzające się płyty (jedna pozycja na grę).
- Ale skróty `.lnk` i wpisy Steam dla emulatorów BEZ obsługi .m3u (PS2/PCSX2,
  Dolphin) celują w prawdziwy DYSK, nie w playlistę. Emulatory z .m3u
  (DuckStation/PS1, RetroArch, PPSSPP) dalej dostają playlistę — zmiana dotyczy
  praktycznie tylko PS2.
- `first_existing_disc()`: WERYFIKUJE istnienie — Disc 1 preferowany, ale gdy go
  brak (jak przy Star Ocean, gdzie chwilowo był tylko Disc 2) bierze najniższy
  ISTNIEJĄCY dysk zamiast martwej ścieżki. Zestaw ustalany z zawartości .m3u
  (własnej lub siostrzanej obejmującej dany dysk). `_disc_number`, `_m3u_disc_list`.
- Zastosowane w: `_build_entry` (Steam), tworzeniu `.lnk` (`_create_thread`) i
  podglądzie (`_build_plan`). `disc_path_for_emulator(rom, exe)` = punkt decyzji.

## FIX: .m3u tylko dla emulatorów, które ją obsługują (PCSX2 nie!)
- BŁĄD z poprzedniego kroku: bezwarunkowe podstawianie `.m3u` zepsuło PS2 —
  „Failed to open CDVD …m3u: Unable to identify the ISO image type". PCSX2 i
  Dolphin NIE czytają playlist .m3u (w przeciwieństwie do DuckStation/RetroArch).
- `emulator_supports_m3u(exe)`: whitelist (duckstation, swanstation, retroarch,
  mednafen, beetle, mgba, ppsspp) + jawny blacklist (pcsx2, dolphin, rpcs3,
  xemu, cemu, vita3k); nieznany → False (bezpiecznie: pojedynczy dysk).
- `disc_path_for_emulator(rom, exe)` DWUKIERUNKOWO:
  - emulator z .m3u: dysk → .m3u (jeśli istnieje);
  - emulator bez .m3u: .m3u → pierwszy dysk (`first_disc_from_m3u`); dysk zostaje.
  Dzięki temu nawet gdy skan zbundluje PS2 do `.m3u`, PCSX2 dostanie Disc 1.
- `_collapse_by_appid`: gdy brak wariantu `.m3u`, preferuje zachowanie Disc 1.

## Eksport do Steam — multi-disc .m3u + zbijanie duplikatów
- FIX: gry wielopłytowe uruchamiane pojedynczym dyskiem (np. „…(Disc 1).chd")
  → jeśli obok jest `.m3u` obejmujący ten dysk, wpis Steam używa `.m3u`
  (wszystkie dyski). `resolve_multidisc_m3u()` czyta ZAWARTOŚĆ playlisty, nie
  zgaduje po nazwie. Naprawia i uruchamianie, i stabilizuje wpis (jeden appid).
- FIX: zbijanie duplikatów po **appid** przy eksporcie. appid=crc32(Exe+nazwa),
  więc ten sam appid = definicyjnie ta sama gra (np. Disc 1 i Disc 2 tego
  samego tytułu bez `.m3u`, albo stary+nowy eksport). Zostaje JEDEN wpis
  (preferencja: uruchamiany `.m3u`), tagi+ikona scalone, reszta usunięta.
  `_collapse_by_appid()`. Różny appid = różna gra → NIE łączone (PaRappa PS1
  vs PSP, bonusowy „Making of" — zostają osobno).
- Dopasowanie nowego wpisu NAJPIERW po appid: gdy ta sama gra ma inną komendę
  (np. Disc 1 → `.m3u`), AKTUALIZUJE Exe/StartDir/LaunchOptions do poprawnej.
- Raport: kategoria „usunięty duplikat" + licznik w podsumowaniu.
- PRZYCZYNA duplikatów u usera: `.m3u` powstały PO zeskanowaniu gier do
  trwałego indeksu (scalanie w `.m3u` działa tylko przy skanie) → Disc 1 i
  Disc 2 były osobnymi „grami", każda wyeksportowana. Rescan czyści źródło;
  powyższe zabezpiecza eksport niezależnie od świeżości indeksu.

## Eksport do Steam — raport (plik)
- NOWE: eksport do Steam zapisuje raport HTML do `Reports\` (obok raportów
  skrótów): `steam_export_report_<data>.html`. Po jednym wierszu na WYBRANĄ grę
  z wynikiem: **dodane / zaktualizowane / pominięte — bez zmian / pominięte —
  błąd** (+ powód). Kolumny: wynik, gra, źródło/platforma, appid, exe,
  argumenty, tagi, uwagi. Nagłówek: ścieżka shortcuts.vdf, kopia zapasowa,
  łączna liczba wpisów, podsumowanie kolekcji i grafik SGDB.
  Ścieżka raportu pokazywana też w końcowym okienku. `write_steam_report()`
  (fmt html/txt). Nie zawiera kluczy API.

## Eksport do Steam — ROM-y uruchamiane przez .lnk (PS3/RPCS3)
- FIX: `_build_entry` pomijał ROM-y z pustym launch_exe (PS3 uruchamiane przez
  .lnk) → nie trafiały do biblioteki Steam. Teraz dla ROM-a z .lnk czyta skrót
  (`read_lnk_target`) i używa docelowego EXE (rpcs3.exe) + argumentów
  (--no-gui "...:GAMEID") + katalogu roboczego. Osobny appid per gra (nazwa).
- Uwaga: eksport do Steam to OSOBNA akcja („Eksport → Steam"), pokazuje
  podsumowanie w okienku (dodane/zaktualizowane/pominięte), nie plik-raport
  (jak przy .lnk). Raport skrótów dotyczy tylko LINKS\.


Log wszystkich zmian wprowadzanych w tej sesji, żeby było jasne co i kiedy
zostało zmienione. Najnowsze na górze.

## Windows — strzałki na skrótach
- NOWE: Ustawienia → „Windows — strzałki na skrótach" → „Usuń strzałki" /
  „Przywróć strzałki". Zmiana SYSTEMOWA (HKLM\...\Shell Icons\29), z UAC
  (reg.exe runas) + restart Eksploratora. Pusta ikona generowana w
  %LOCALAPPDATA%\PyLinks\blank_arrow.ico. Odwracalne.
  Funkcje: `set_shortcut_arrows`, `restart_explorer`, `shortcut_arrows_state`.

## Ikony / grzbiet platformy
- NOWE: w oknie „Grzbiety platform" przycisk „Wybierz plik z dysku…" — własne
  logo dla platformy z dowolnego pliku (PNG/WEBP/JPG/ICO/…), konwersja do
  <KEY>.png (obsługuje WEBP). Backup poprzedniego jako .png.bak.
- FIX: warianty/rozszerzenia konsol dostają grzbiet konsoli bazowej przez
  `PLATFORM_SPINE_ALIAS` (SNESMSU1→SNES, PSX→PS1, FDS→NES, SEGACD/32X→MD,
  TG16→PCENGINE…). PRIORYTET: najpierw KONKRETNE logo platformy (np. własny
  SNESMSU1.png), a dopiero gdy go brak — alias do konsoli bazowej. `_spine_canon_key`
  rozwija alias też przy auto-pobieraniu logo. Wcześniej SNES MSU-1 nie miał grzbietu.
- NOWE OKNO „Grzbiety platform: wybór logo i kolorystyki" (Ustawienia →
  przycisk pod opcją grzbietu). Pozwala: wybrać kolorystykę logotypów
  (Białe/Kolorowe/Czarne) i „Zastosuj do wszystkich", oraz per platforma
  wybrać wariant logo z siatki miniatur (klik = ustaw <KEY>.png).
  Helpery: `list_platform_logo_variants`, `install_logo_from_url`,
  `download_platform_logos(style=..., overwrite=...)`. Config: `spine_logo_style`.
- PS2: podmieniono na czysty wordmark (1920×332, jak PS1) zamiast monogramu;
  GameCube na szerszy wariant. (Backupy .bak w platform_logos.)
- ŚWIADOMOŚĆ PROPORCJI: `add_platform_spine` nie wymusza już kwadratu na
  starcie. Supersampling zachowuje proporcje (dłuższy bok ~512). Decyzja:
  - PORTRET (H>W, np. 810×1080, 600×900): grzbiet wchodzi w naturalny margines
    (S−W) potrzebny do zrobienia kwadratu → grafiki NIE zmniejszamy;
  - KWADRAT/poziom (np. 400×400): grafika zwężana, żeby zrobić miejsce na grzbiet.
  Grzbiet i logo składane przy boku S=max(W,H); wynik zawsze kwadratowy.
- `make_ico_bytes`: UJEDNOLICENIE — każda ikona zawsze pełny wpis 256×256 +
  mniejsze (128/64/48/32/16). 256 to MAKS formatu .ico (nagłówek katalogu
  koduje bok na 1 bajcie, 0=256; wpisy >256 są pomijane — sprawdzone: PIL
  wyrzuca 512). Wcześniej małe źródła dawały max 128 → niespójność.
- `add_platform_spine`: normalizacja bazy do 512×512 (supersampling), potem
  zejście do 256 w make_ico_bytes → ostre, spójne logo/grzbiet na każdej ikonie.
- Grzbiet: TYLKO białe logo (wariant `Light - Just White` z pakietu
  console-logos), bez osobnej nazwy platformy; logo obrócone wzdłuż grzbietu,
  stała szerokość, wyśrodkowane. `_ensure_logo_contrast` rozjaśnia ciemne logo.
- Ikona NIE jest zasłaniana: grafika ZWĘŻA się do obszaru obok grzbietu
  (pełna wysokość), grzbiet w swoim pasku.
- Auto-pobieranie logotypów: tylko BRAKUJĄCE platformy z bieżącego zestawu.
- Opcja w Ustawieniach: „Grzbiet platformy na ikonie ROM-a" + strona; osobny
  plik .ico per platforma (te same tytuły się nie nadpisują).

## Skróty .lnk — katalog roboczy / argumenty  ⚠ SPORNE (patrz niżej)
- `make_lnk` + `make_extra_shortcut` + `make_gog_shortcut`: dodane
  `work_dir` (Windows „Rozpocznij w") i argumenty.
  - GOG/extra: „Rozpocznij w" = z `goggame-*.info` (workingDir) lub folder EXE.
  - ROM: BEZ „Rozpocznij w" (na życzenie użytkownika — cofnięte).
- `gog_playtask()`: czyta `goggame-*.info` → (exe, argumenty, workingDir);
  poprawny launcher GOG (Windows/DOSBox/ScummVM) zamiast zgadywania find_exes.
- Diagnostyka niepowodzeń: każdy błąd tworzenia skrótu ma powód w raporcie
  (pusty target, brak EXE, brak pywin32, wyjątek).

## Steam
- Naprawiony binarny `shortcuts.vdf` (znaczniki typów 0x00/0x01/0x02, 0x08).
- Tagi + kolekcje per system w `config/cloudstorage/*.json` (nie leveldb).
- Pobieranie grafik SGDB do `grid/` + pasek postępu; trwały cache w Cache/.
- Tryb Desktop(.lnk)/Steam w głównym oknie (edycja grafik Steam).

## SGDB / IGDB / TheGamesDB
- FIX: `sgdb_get_by_id` → `/api/v2/games/id/{id}` (było 405).
- IGDB/TGDB: próg podobieństwa nazwy + świadomość platformy (remake na innej
  platformie nie podmienia gry).
- Przycisk „Wyczyść grafiki" (cache) dla bieżącej gry.

---

## Cache grafik „znika po każdej zmianie/restarcie" — PRZYCZYNA i naprawa
- PRZYCZYNA: `cache_limit_mb` = **512 MB** (nie 2048). Eksmisja LRU
  (`evict_lru`) przy 4605 ROM-ach bez przerwy przycinała cache < 512 MB i
  KASOWAŁA nie-wybrane (a przez błąd `keep` czasem i wybrane) grafiki.
- FIX: ustawiono `cache_limit_mb = 0` w config.json (bez limitu → eksmisja OFF).
- FIX `_selected_asset_keys`: chroni wybraną ikonę też z ZAPISANEGO wyboru
  (config), nie tylko z kandydatów w pamięci — inaczej eksmisja kasowała
  wybraną grafikę gier, których się nie kliknęło.
- FIX `upsert_game`: gry bez appid (ROM/extra/gog) dopasowywane po (source,
  name), nie po sgdb_id — koniec duplikatów game_id i osieroconych grafik.
- NOWE `reconcile_from_disk`: jednorazowa odbudowa wpisów `assets` z plików na
  dysku (auto raz na starcie, flaga `assets_reconciled_v82`). Backup bazy przed
  zmianą. UWAGA: przy tej bazie odzyskało tylko 12 wpisów — bo pliki większości
  gier były już SKASOWANE przez eksmisję (nie da się ich odzyskać, dociągną się
  z sieci przy skanie; teraz już nie znikną).

## Rozwiązane
- Front Mission 3 (GOG) puste „Rozpocznij w": USTALONE po datach plików.
  Skrót utworzony 2026-07-23 20:48; obsługę `work_dir` dodano do kodu
  2026-08-07 18:30. Plik jest STARSZY niż funkcja → stąd pusty. Test
  `make_extra_shortcut` na tym folderze ustawia „Rozpocznij w" poprawnie.
  ROZWIĄZANIE: utworzyć skrót ponownie dzisiejszym kodem.
