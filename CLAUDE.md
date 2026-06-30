# Projekt: Nowe restauracje dla Specfood

## Cel
Codzienny skrypt Python wykrywający nowo zarejestrowane restauracje (PKD 56.x)
w Polsce i alertujący handlowców Specfood przez Telegram.

## Stack
- **Python** — logika skryptu
- **GitHub Actions** — uruchamianie codziennie o 20:00 (cron, darmowe)
- **Google Sheets** — baza leadów + konfiguracja
- **Telegram Bot** — alerty do handlowców

## Źródła danych

### KRS (~70% restauracji — spółki z o.o.)
- Biuletyn dzienny: `https://api-krs.ms.gov.pl/api/Krs/Biuletyn/{dzien}`
- Odpis firmy: `https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs}?rejestr=P&format=json`
- Bez autoryzacji

### CEIDG (~30% restauracji — jednoosobowe działalności)
- `https://dane.biznes.gov.pl/api/ceidg/v3/firmy?pkd=5610A&...`
- Wymaga Bearer Token JWT (przechowywany w GitHub Secrets)
- Format PKD bez kropek: `5610A`, `5610B`, `5621Z`, `5630Z`

## Jak działa wykrywanie nowych firm z KRS
Numery KRS są sekwencyjne. Najwyższe numery z biuletynu = nowe firmy.
Skrypt przechowuje ostatni znany numer KRS w Google Sheets i porównuje przy każdym uruchomieniu.

## Struktura projektu
```
specfood/
├── main.py              # główny skrypt
├── krs.py               # pobieranie danych z KRS
├── ceidg.py             # pobieranie danych z CEIDG
├── sheets.py            # Google Sheets
├── telegram_bot.py      # Telegram alerts
├── requirements.txt
└── .github/
    └── workflows/
        └── daily.yml    # GitHub Actions cron
```

## Regiony Specfood (do potwierdzenia)
Południe, wschód, środek Polski, Warszawa, okolice morza.
Konkretne województwa do uzupełnienia przez Kacpra.

## GitHub Secrets (credentials)
- `CEIDG_JWT_TOKEN` — token Bearer do CEIDG API
- `GOOGLE_CREDENTIALS` — JSON z credentials Google Service Account
- `TELEGRAM_BOT_TOKEN` — token bota Telegram
- `SPREADSHEET_ID` — ID arkusza Google Sheets

## Styl komunikacji
- Po polsku
- Poziom: początkujący, wyjaśniaj każdy krok
