import requests
import time
from datetime import date, timedelta


GASTRONOMY_PKD = {"56"}


def get_yesterdays_bulletin():
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://api-krs.ms.gov.pl/api/Krs/Biuletyn/{yesterday}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def get_new_krs_numbers(bulletin, last_known_krs):
    unique = set(int(x) for x in bulletin)
    return sorted([n for n in unique if n > last_known_krs], reverse=True)


def get_company_details(krs_number):
    krs_str = str(krs_number).zfill(10)
    url = f"https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs_str}?rejestr=P&format=json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def extract_restaurant(data):
    try:
        odpis = data["odpis"]
        nagl = odpis["naglowekA"]
        dane = odpis["dane"]

        pkd_list = (
            dane.get("dzial3", {})
            .get("przedmiotDzialalnosci", {})
            .get("przedmiotPrzewazajacejDzialalnosci", [])
        )

        if not pkd_list:
            return None

        primary_pkd = pkd_list[0]
        if primary_pkd.get("kodDzial") not in GASTRONOMY_PKD:
            return None

        address = dane.get("dzial1", {}).get("siedzibaIAdres", {})
        pkd_code = f"{primary_pkd.get('kodDzial','')}.{primary_pkd.get('kodKlasa','')}{primary_pkd.get('kodPodklasa','')}"

        return {
            "source": "KRS",
            "krs": nagl.get("numerKRS"),
            "name": dane.get("dzial1", {}).get("danePodmiotu", {}).get("nazwa"),
            "pkd": pkd_code,
            "pkd_name": primary_pkd.get("opis"),
            "region": (address.get("wojewodztwo") or "").upper(),
            "city": address.get("miejscowosc"),
            "street": f"{address.get('ulica', '')} {address.get('nrDomu', '')}".strip(),
            "registered_at": nagl.get("dataRejestracjiWKRS"),
            "link": f"https://www.krs.com.pl/krs/{nagl.get('numerKRS')}",
        }
    except (KeyError, TypeError):
        return None


def find_new_restaurants(last_known_krs):
    print("KRS: fetching daily bulletin...")
    bulletin = get_yesterdays_bulletin()
    new_numbers = get_new_krs_numbers(bulletin, last_known_krs)

    if not new_numbers:
        print("KRS: no new companies since last run.")
        return [], last_known_krs

    MAX_TO_CHECK = 300
    if len(new_numbers) > MAX_TO_CHECK:
        print(f"KRS: limiting to {MAX_TO_CHECK} newest numbers ({len(new_numbers)} total)...")
        new_numbers = new_numbers[:MAX_TO_CHECK]

    print(f"KRS: checking {len(new_numbers)} companies for gastronomy PKD...")

    restaurants = []
    new_max_krs = max(new_numbers)

    for krs in new_numbers:
        data = get_company_details(krs)
        if data:
            restaurant = extract_restaurant(data)
            if restaurant:
                restaurants.append(restaurant)
                print(f"  ✓ Restaurant: {restaurant['name']} ({restaurant['city']})")
        time.sleep(0.2)

    print(f"KRS: found {len(restaurants)} restaurants.")
    return restaurants, new_max_krs
