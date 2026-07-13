import os
import krs
import ceidg
import sheets
import telegram_bot


# Regions covered
REGIONS = {
    "PODKARPACKIE",
    "MAŁOPOLSKIE",
    "LUBELSKIE",
    "MAZOWIECKIE",
    "ŚWIĘTOKRZYSKIE",
    "PODLASKIE",
    "WARMIŃSKO-MAZURSKIE",
    "POMORSKIE",
}

# Region → salesperson mapping
SALESPERSONS = {
    "PODKARPACKIE":        {"name": "Salesperson 1", "telegram_id": "CHAT_ID_1"},
    "MAŁOPOLSKIE":         {"name": "Salesperson 2", "telegram_id": "CHAT_ID_2"},
    "LUBELSKIE":           {"name": "Salesperson 3", "telegram_id": "CHAT_ID_3"},
    "MAZOWIECKIE":         {"name": "Salesperson 4", "telegram_id": "CHAT_ID_4"},
    "ŚWIĘTOKRZYSKIE":      {"name": "Salesperson 5", "telegram_id": "CHAT_ID_5"},
    "PODLASKIE":           {"name": "Salesperson 6", "telegram_id": "CHAT_ID_6"},
    "WARMIŃSKO-MAZURSKIE": {"name": "Salesperson 7", "telegram_id": "CHAT_ID_7"},
    "POMORSKIE":           {"name": "Salesperson 8", "telegram_id": "CHAT_ID_8"},
}


def assign_salesperson(restaurant):
    region = restaurant.get("region", "").upper()
    person = SALESPERSONS.get(region, {"name": "Unassigned", "telegram_id": None})
    restaurant["salesperson"] = person["name"]
    restaurant["telegram_id"] = person["telegram_id"]
    return restaurant


def main():
    ceidg_token = os.environ["CEIDG_JWT_TOKEN"]
    google_credentials = os.environ["GOOGLE_CREDENTIALS"]
    telegram_token = os.environ["TELEGRAM_BOT_TOKEN"]
    spreadsheet_id = os.environ["SPREADSHEET_ID"]

    client = sheets.get_client(google_credentials)

    last_krs = sheets.get_last_krs(client, spreadsheet_id)
    print(f"Last known KRS: {last_krs}")

    krs_restaurants, new_max_krs = krs.find_new_restaurants(last_krs)
    ceidg_restaurants = ceidg.find_new_restaurants(ceidg_token)

    all_restaurants = krs_restaurants + ceidg_restaurants

    # Filter by active regions
    in_region = [
        r for r in all_restaurants
        if r.get("region", "").upper() in REGIONS
    ]
    print(f"After region filter: {len(in_region)} restaurants.")

    # Remove duplicates (already saved + duplicates within this run)
    existing_ids = sheets.get_existing_ids(client, spreadsheet_id)
    new_leads = []
    seen_this_run = set()
    for r in in_region:
        id_ = str(r.get("krs") or r.get("nip") or "")
        if id_ and id_ not in existing_ids and id_ not in seen_this_run:
            seen_this_run.add(id_)
            new_leads.append(r)

    print(f"New leads (no duplicates): {len(new_leads)}")

    if not new_leads:
        print("No new restaurants today.")
    else:
        for r in new_leads:
            r = assign_salesperson(r)
            if r["telegram_id"]:
                telegram_bot.send_alert(telegram_token, r["telegram_id"], r)

        sheets.save_leads(client, spreadsheet_id, new_leads)

    if new_max_krs > last_krs:
        sheets.update_last_krs(client, spreadsheet_id, new_max_krs)
        print(f"Updated last KRS: {new_max_krs}")


if __name__ == "__main__":
    main()
