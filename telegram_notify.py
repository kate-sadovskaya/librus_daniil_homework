import html

import requests

TELEGRAM_API_BASE = "https://api.telegram.org"


def send_message(token: str, chat_id: str, text: str) -> None:
    url = f"{TELEGRAM_API_BASE}/bot{token}/sendMessage"
    resp = requests.post(
        url,
        data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        timeout=10,
    )
    resp.raise_for_status()
    body = resp.json()
    if not body.get("ok"):
        raise RuntimeError(f"Telegram API returned ok=false: {body}")


def format_homework_message(item: dict) -> str:
    return (
        "<b>НОВОЕ ДОМАШНЕЕ ЗАДАНИЕ</b>\n\n"
        f"Przedmiot: {html.escape(item['przedmiot'])}\n"
        f"Termin wykonania: {html.escape(item['termin_wykonania'])}\n"
        f"Treść: {html.escape(item['tresc'])}"
    )


def format_announcement_message(item: dict) -> str:
    return (
        "Новое объявление\n"
        f"{html.escape(item['title'])}\n"
        f"От: {html.escape(item['author'])}\n"
        f"Дата: {html.escape(item['date'])}\n\n"
        f"{html.escape(item['description'])}"
    )
