import requests
from datetime import date


GASTRONOMY_PKD_CODES = ["5610A", "5610B", "5621Z", "5630Z"]


def find_new_restaurants(ceidg_token):
    """Pobierz nowe restauracje z CEIDG zarejestrowane dzisiaj."""
    today = date.today().strftime("%Y-%m-%d")
    headers = {
        "Authorization": f"Bearer {ceidg_token}",
        "Accept": "application/json",
    }

    restaurants = []

    for pkd in GASTRONOMY_PKD_CODES:
        print(f"CEIDG: sprawdzam PKD {pkd}...")
        params = {
            "pkd": pkd,
            "dataod": f"{today}T00:00:00",
            "datado": f"{today}T23:59:59",
            "status": "AKTYWNY",
        }

        try:
            response = requests.get(
                "https://dane.biznes.gov.pl/api/ceidg/v3/firmy",
                headers=headers,
                params=params,
                timeout=30,
            )
            if response.status_code == 204:
                continue
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"  CEIDG błąd dla {pkd}: {e}")
            continue

        for firma in data.get("firmy", []):
            adres = firma.get("adresDzialalnosci", {})
            restaurants.append({
                "zrodlo": "CEIDG",
                "nip": firma.get("wlasciciel", {}).get("nip"),
                "nazwa": firma.get("nazwa"),
                "pkd": pkd,
                "pkd_nazwa": None,
                "wojewodztwo": (adres.get("wojewodztwo") or "").upper(),
                "miasto": adres.get("miasto"),
                "ulica": f"{adres.get('ulica', '')} {adres.get('budynek', '')}".strip(),
                "data_rejestracji": firma.get("dataRozpoczecia"),
                "link": firma.get("link"),
            })

    print(f"CEIDG: znaleziono {len(restaurants)} restauracji.")
    return restaurants
