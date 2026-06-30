import requests
import time
from datetime import date


GASTRONOMY_PKD = {"56"}  # dział 56 = gastronomia


def get_todays_bulletin():
    """Pobierz biuletyn KRS z dzisiaj — lista wszystkich zmienionych numerów KRS."""
    today = date.today().strftime("%Y-%m-%d")
    url = f"https://api-krs.ms.gov.pl/api/Krs/Biuletyn/{today}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def get_new_krs_numbers(bulletin, last_known_krs):
    """Filtruj biuletyn — zostaw tylko numery wyższe niż ostatni znany (czyli nowe firmy)."""
    unique = set(int(x) for x in bulletin)
    new_numbers = sorted([n for n in unique if n > last_known_krs], reverse=True)
    return new_numbers


def get_company_details(krs_number):
    """Pobierz pełne dane firmy z KRS po numerze."""
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
    """Wyciągnij dane restauracji z odpowiedzi KRS. Zwraca None jeśli to nie gastronomia."""
    try:
        odpis = data["odpis"]
        nagl = odpis["naglowekA"]
        dane = odpis["dane"]

        pkd_lista = (
            dane.get("dzial3", {})
            .get("przedmiotDzialalnosci", {})
            .get("przedmiotPrzewazajacejDzialalnosci", [])
        )

        if not pkd_lista:
            return None

        pkd_glowny = pkd_lista[0]
        if pkd_glowny.get("kodDzial") not in GASTRONOMY_PKD:
            return None

        adres = dane.get("dzial1", {}).get("siedzibaIAdres", {})
        pkd_kod = f"{pkd_glowny.get('kodDzial','')}.{pkd_glowny.get('kodKlasa','')}{pkd_glowny.get('kodPodklasa','')}"

        return {
            "zrodlo": "KRS",
            "krs": nagl.get("numerKRS"),
            "nazwa": dane.get("dzial1", {}).get("danePodmiotu", {}).get("nazwa"),
            "pkd": pkd_kod,
            "pkd_nazwa": pkd_glowny.get("opis"),
            "wojewodztwo": (adres.get("wojewodztwo") or "").upper(),
            "miasto": adres.get("miejscowosc"),
            "ulica": f"{adres.get('ulica', '')} {adres.get('nrDomu', '')}".strip(),
            "data_rejestracji": nagl.get("dataRejestracjiWKRS"),
            "link": f"https://www.krs.com.pl/krs/{nagl.get('numerKRS')}",
        }
    except (KeyError, TypeError):
        return None


def find_new_restaurants(last_known_krs):
    """
    Główna funkcja — pobiera nowe restauracje z KRS zarejestrowane od last_known_krs.
    Zwraca: (lista restauracji, nowy max numer KRS)
    """
    print("KRS: pobieranie biuletynu dziennego...")
    bulletin = get_todays_bulletin()
    new_numbers = get_new_krs_numbers(bulletin, last_known_krs)

    if not new_numbers:
        print("KRS: brak nowych firm od ostatniego uruchomienia.")
        return [], last_known_krs

    print(f"KRS: znaleziono {len(new_numbers)} nowych firm, sprawdzam PKD...")

    restaurants = []
    new_max_krs = max(new_numbers)

    for krs in new_numbers:
        data = get_company_details(krs)
        if data:
            restaurant = extract_restaurant(data)
            if restaurant:
                restaurants.append(restaurant)
                print(f"  ✓ Restauracja: {restaurant['nazwa']} ({restaurant['miasto']})")
        time.sleep(0.2)  # żeby nie przeciążyć API

    print(f"KRS: znaleziono {len(restaurants)} restauracji.")
    return restaurants, new_max_krs
