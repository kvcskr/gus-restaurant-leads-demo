import json
import gspread
from google.oauth2.service_account import Credentials


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_client(google_credentials_json):
    creds_dict = json.loads(google_credentials_json.encode().decode('utf-8-sig'))
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def get_last_krs(client, spreadsheet_id):
    sh = client.open_by_key(spreadsheet_id)
    config = sh.worksheet("Konfiguracja")
    data = config.get_all_records()
    for row in data:
        if row.get("klucz") == "ostatni_krs":
            return int(row.get("wartość", 0))
    return 0


def update_last_krs(client, spreadsheet_id, new_krs):
    sh = client.open_by_key(spreadsheet_id)
    config = sh.worksheet("Konfiguracja")
    data = config.get_all_records()
    for i, row in enumerate(data, start=2):
        if row.get("klucz") == "ostatni_krs":
            config.update_cell(i, 2, new_krs)
            return
    config.append_row(["ostatni_krs", new_krs])


def get_existing_ids(client, spreadsheet_id):
    sh = client.open_by_key(spreadsheet_id)
    leads = sh.worksheet("Leady")
    records = leads.get_all_records()
    return set(str(r.get("krs_nip", "")) for r in records if r.get("krs_nip"))


def save_leads(client, spreadsheet_id, restaurants):
    if not restaurants:
        return

    sh = client.open_by_key(spreadsheet_id)
    leads = sh.worksheet("Leady")

    rows = []
    for r in restaurants:
        rows.append([
            r.get("registered_at", ""),
            r.get("source", ""),
            r.get("name", ""),
            r.get("pkd", ""),
            r.get("pkd_name", ""),
            r.get("city", ""),
            r.get("region", ""),
            r.get("street", ""),
            r.get("krs") or r.get("nip", ""),
            r.get("link", ""),
            "new",
            r.get("salesperson", ""),
            r.get("contact", ""),
        ])

    leads.append_rows(rows)
    print(f"Sheets: saved {len(rows)} leads.")
