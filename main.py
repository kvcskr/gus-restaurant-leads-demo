import os
import krs
import ceidg
import sheets
import telegram_bot


# Województwa obsługiwane przez Specfood
REGIONY_SPECFOOD = {
    "PODKARPACKIE",
    "MAŁOPOLSKIE",
    "LUBELSKIE",
    "MAZOWIECKIE",
    "ŚWIĘTOKRZYSKIE",
    "PODLASKIE",
    "WARMIŃSKO-MAZURSKIE",
    "POMORSKIE",
}

# Mapa województwo → handlowiec (uzupełnij!)
HANDLOWCY = {
    "PODKARPACKIE":       {"imie": "Handlowiec 1", "telegram_id": "CHAT_ID_1"},
    "MAŁOPOLSKIE":        {"imie": "Handlowiec 2", "telegram_id": "CHAT_ID_2"},
    "LUBELSKIE":          {"imie": "Handlowiec 3", "telegram_id": "CHAT_ID_3"},
    "MAZOWIECKIE":        {"imie": "Handlowiec 4", "telegram_id": "CHAT_ID_4"},
    "ŚWIĘTOKRZYSKIE":     {"imie": "Handlowiec 5", "telegram_id": "CHAT_ID_5"},
    "PODLASKIE":          {"imie": "Handlowiec 6", "telegram_id": "CHAT_ID_6"},
    "WARMIŃSKO-MAZURSKIE":{"imie": "Handlowiec 7", "telegram_id": "CHAT_ID_7"},
    "POMORSKIE":          {"imie": "Handlowiec 8", "telegram_id": "CHAT_ID_8"},
}


def assign_salesperson(restaurant):
    """Przypisz handlowca na podstawie województwa."""
    woj = restaurant.get("wojewodztwo", "").upper()
    handlowiec = HANDLOWCY.get(woj, {"imie": "Nieprzypisany", "telegram_id": None})
    restaurant["handlowiec"] = handlowiec["imie"]
    restaurant["telegram_id"] = handlowiec["telegram_id"]
    return restaurant


def main():
    # Pobierz credentials z GitHub Secrets (zmienne środowiskowe)
    ceidg_token = os.environ["CEIDG_JWT_TOKEN"]
    google_credentials = os.environ["GOOGLE_CREDENTIALS"]
    telegram_token = os.environ["TELEGRAM_BOT_TOKEN"]
    spreadsheet_id = os.environ["SPREADSHEET_ID"]

    # Połącz z Google Sheets
    client = sheets.get_client(google_credentials)

    # Pobierz ostatni znany numer KRS
    last_krs = sheets.get_last_krs(client, spreadsheet_id)
    print(f"Ostatni znany KRS: {last_krs}")

    # Pobierz nowe restauracje z obu źródeł
    krs_restaurants, new_max_krs = krs.find_new_restaurants(last_krs)
    ceidg_restaurants = ceidg.find_new_restaurants(ceidg_token)

    wszystkie = krs_restaurants + ceidg_restaurants

    # Filtruj tylko regiony Specfood
    in_region = [
        r for r in wszystkie
        if r.get("wojewodztwo", "").upper() in REGIONY_SPECFOOD
    ]
    print(f"Po filtrze regionów: {len(in_region)} restauracji.")

    # Usuń duplikaty (już zapisane w Sheets)
    existing_ids = sheets.get_existing_ids(client, spreadsheet_id)
    nowe = []
    for r in in_region:
        id_ = str(r.get("krs") or r.get("nip") or "")
        if id_ and id_ not in existing_ids:
            nowe.append(r)

    print(f"Nowych leadów (bez duplikatów): {len(nowe)}")

    if not nowe:
        print("Brak nowych restauracji dziś.")
    else:
        # Przypisz handlowców i wyślij alerty
        for r in nowe:
            r = assign_salesperson(r)
            if r["telegram_id"]:
                telegram_bot.send_alert(telegram_token, r["telegram_id"], r)

        # Zapisz do Google Sheets
        sheets.save_leads(client, spreadsheet_id, nowe)

    # Zaktualizuj ostatni znany numer KRS
    if new_max_krs > last_krs:
        sheets.update_last_krs(client, spreadsheet_id, new_max_krs)
        print(f"Zaktualizowano ostatni KRS: {new_max_krs}")


if __name__ == "__main__":
    main()
