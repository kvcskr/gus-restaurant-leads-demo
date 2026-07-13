import requests
from datetime import date, timedelta


GASTRONOMY_PKD_CODES = ["5610A", "5610B", "5621Z", "5630Z"]


def find_new_restaurants(ceidg_token):
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    headers = {
        "Authorization": f"Bearer {ceidg_token}",
        "Accept": "application/json",
    }

    restaurants = []

    for pkd in GASTRONOMY_PKD_CODES:
        print(f"CEIDG: checking PKD {pkd}...")
        params = {
            "pkd": pkd,
            "dataod": f"{yesterday}T00:00:00",
            "datado": f"{yesterday}T23:59:59",
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
            print(f"  CEIDG error for {pkd}: {e}")
            continue

        for company in data.get("firmy", []):
            start_date = (company.get("dataRozpoczecia") or "")[:10]
            if start_date != yesterday:
                continue
            address = company.get("adresDzialalnosci", {})
            phone = company.get("telefon") or ""
            email = company.get("email") or ""
            contact = " | ".join(filter(None, [phone, email])) or "none"
            restaurants.append({
                "source": "CEIDG",
                "nip": company.get("wlasciciel", {}).get("nip"),
                "name": company.get("nazwa"),
                "pkd": pkd,
                "pkd_name": None,
                "region": (address.get("wojewodztwo") or "").upper(),
                "city": address.get("miasto"),
                "street": f"{address.get('ulica', '')} {address.get('budynek', '')}".strip(),
                "registered_at": company.get("dataRozpoczecia"),
                "link": company.get("link"),
                "contact": contact,
            })

    print(f"CEIDG: found {len(restaurants)} restaurants.")
    return restaurants
