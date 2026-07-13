import requests


def send_alert(bot_token, chat_id, restaurant):
    text = (
        f"🍕 *New restaurant in your region!*\n\n"
        f"*Name:* {restaurant.get('name', '?')}\n"
        f"*PKD:* {restaurant.get('pkd', '?')}\n"
        f"*Address:* {restaurant.get('street', '')}, {restaurant.get('city', '?')}\n"
        f"*Region:* {restaurant.get('region', '?')}\n"
        f"*Registered:* {restaurant.get('registered_at', '?')}\n"
        f"*Source:* {restaurant.get('source', '?')}\n"
        f"*Link:* {restaurant.get('link', '?')}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Telegram error: {e}")


def send_summary(bot_token, chat_id, count, region):
    text = f"📊 Daily report: found *{count}* new restaurants in {region}."
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except requests.RequestException as e:
        print(f"Telegram error: {e}")
