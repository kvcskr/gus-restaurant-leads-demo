import requests


def send_alert(bot_token, chat_id, restaurant):
    """Wyślij alert o nowej restauracji do handlowca."""
    tekst = (
        f"🍕 *Nowa restauracja w Twoim regionie!*\n\n"
        f"*Nazwa:* {restaurant.get('nazwa', '?')}\n"
        f"*PKD:* {restaurant.get('pkd', '?')}\n"
        f"*Adres:* {restaurant.get('ulica', '')}, {restaurant.get('miasto', '?')}\n"
        f"*Województwo:* {restaurant.get('wojewodztwo', '?')}\n"
        f"*Data rejestracji:* {restaurant.get('data_rejestracji', '?')}\n"
        f"*Źródło:* {restaurant.get('zrodlo', '?')}\n"
        f"*Link:* {restaurant.get('link', '?')}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": tekst,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Telegram błąd: {e}")


def send_summary(bot_token, chat_id, count, region):
    """Wyślij podsumowanie jeśli znaleziono nowe restauracje."""
    tekst = f"📊 Dziennik Specfood: znaleziono *{count}* nowych restauracji w regionie {region}."
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": tekst, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except requests.RequestException as e:
        print(f"Telegram błąd: {e}")
