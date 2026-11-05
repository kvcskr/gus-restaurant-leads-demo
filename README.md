# Python + GitHub Actions — Daily Restaurant Lead Detection (KRS & CEIDG)

Automated daily script that detects newly registered restaurants in Poland and alerts the right salesperson via Telegram.

## The Problem It Solves

Sales teams have no systematic way to identify newly registered restaurants in their regions. Manually browsing KRS and CEIDG databases daily is time-consuming and error-prone, causing missed commercial opportunities in the critical early weeks after a restaurant opens.

This script runs automatically every day, finds new registrations from both government databases, and pushes the right lead to the right salesperson — without any manual work.

## How It Works

### Part 1 — KRS (Companies / ~70% of restaurants)
Fetches the daily KRS bulletin (list of all changed company numbers). Since KRS numbers are sequential, any number higher than the last known one is a new registration. Each new company is checked for PKD code 56.x (gastronomy) and its details are extracted.

### Part 2 — CEIDG (Sole proprietors / ~30% of restaurants)
Queries the CEIDG API with PKD filters (5610A, 5610B, 5621Z, 5630Z) and today's date range to get newly registered sole proprietors in the food service sector.

### Part 3 — Processing & Distribution

```
KRS bulletin + CEIDG API
        ↓
Merge results from both sources
        ↓
Deduplicate (vs. existing Google Sheets records)
        ↓
Filter by active sales regions
        ↓
Assign to salesperson by województwo
        ↓
Save to Google Sheets + send Telegram alert to assigned salesperson
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Script runtime | Python 3.12 |
| Scheduling | GitHub Actions (cron) |
| KRS data | api-krs.ms.gov.pl (no auth required) |
| CEIDG data | dane.biznes.gov.pl API v3 (JWT) |
| Lead storage | Google Sheets (gspread) |
| Alerts | Telegram Bot API |

## File Structure

```
main.py                          # orchestrator
krs.py                           # KRS bulletin + company details
ceidg.py                         # CEIDG API queries
sheets.py                        # Google Sheets read/write
telegram_bot.py                  # Telegram alerts
requirements.txt
.github/workflows/daily.yml      # runs daily at 20:00 Polish time
```

## Setup

1. Create a Google Service Account and share your Sheets spreadsheet with it
2. Enable Google Sheets API in Google Cloud Console
3. Create a Telegram bot via BotFather and collect salesperson chat IDs
4. Add the following GitHub Secrets to your repository:

| Secret | Description |
|--------|-------------|
| `CEIDG_JWT_TOKEN` | CEIDG API authentication token |
| `GOOGLE_CREDENTIALS` | Google Service Account JSON (full content) |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token |
| `SPREADSHEET_ID` | Google Sheets spreadsheet ID |
5. Push to GitHub — Actions will run automatically every day at 20:00

