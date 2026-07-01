import json
import gspread
from google.oauth2.service_account import Credentials


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_client(google_credentials_json):
    """Połącz się z Google Sheets."""
    creds_dict = json.loads(google_credentials_json.encode().decode('utf-8-sig'))
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def get_last_krs(client, spreadsheet_id):
    """Odczytaj ostatni znany numer KRS z arkusza Konfiguracja."""
    sh = client.open_by_key(spreadsheet_id)
    config = sh.worksheet("Konfiguracja")
    data = config.get_all_records()
    for row in data:
        if row.get("klucz") == "ostatni_krs":
            return int(row.get("wartość", 0))
    return 0


def update_last_krs(client, spreadsheet_id, new_krs):
    """Zaktualizuj ostatni znany numer KRS w arkuszu Konfiguracja."""
    sh = client.open_by_key(spreadsheet_id)
    config = sh.worksheet("Konfiguracja")
    data = config.get_all_records()
    for i, row in enumerate(data, start=2):
        if row.get("klucz") == "ostatni_krs":
            config.update_cell(i, 2, new_krs)
            return
    config.append_row(["ostatni_krs", new_krs])


def get_existing_ids(client, spreadsheet_id):
    """Pobierz listę już znanych KRS/NIP żeby unikać duplikatów."""
    sh = client.open_by_key(spreadsheet_id)
    leady = sh.worksheet("Leady")
    records = leady.get_all_records()
    return set(str(r.get("krs_nip", "")) for r in records if r.get("krs_nip"))


def save_leads(client, spreadsheet_id, restaurants):
    """Zapisz nowe restauracje do arkusza Leady."""
    if not restaurants:
        return

    sh = client.open_by_key(spreadsheet_id)
    leady = sh.worksheet("Leady")

    rows = []
    for r in restaurants:
        rows.append([
            r.get("data_rejestracji", ""),
            r.get("zrodlo", ""),
            r.get("nazwa", ""),
            r.get("pkd", ""),
            r.get("pkd_nazwa", ""),
            r.get("miasto", ""),
            r.get("wojewodztwo", ""),
            r.get("ulica", ""),
            r.get("krs") or r.get("nip", ""),
            r.get("link", ""),
            "nowy",
            r.get("handlowiec", ""),
            r.get("kontakt", ""),
        ])

    leady.append_rows(rows)
    print(f"Sheets: zapisano {len(rows)} leadów.")
