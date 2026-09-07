import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from librus_client import LibrusClient
from telegram_notify import (
    format_announcement_message,
    format_homework_message,
    send_message,
)

BASE_DIR = Path(__file__).parent
STATE_PATH = BASE_DIR / "state" / "seen_daniil.json"


def load_state(path: Path) -> tuple[dict, bool]:
    if not path.exists():
        return {"homework": [], "announcements": []}, True
    with path.open(encoding="utf-8") as f:
        return json.load(f), False


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def main() -> int:
    load_dotenv(BASE_DIR / ".env")
    username = os.environ["LIBRUS_USERNAME_DANIIL"]
    password = os.environ["LIBRUS_PASSWORD_DANIIL"]
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    client = LibrusClient(username, password)
    print("Logging in to Librus...")
    client.login()
    print("Login OK")

    homework = client.get_homework()
    announcements = client.get_announcements()
    print(f"Fetched {len(homework)} homework item(s), {len(announcements)} announcement(s)")

    state, is_first_run = load_state(STATE_PATH)
    seen_hw = set(state["homework"])
    seen_ann = set(state["announcements"])

    if is_first_run:
        print("First run: no state file found. Marking all current items as seen, sending nothing.")
        state["homework"] = [h["id"] for h in homework]
        state["announcements"] = [a["id"] for a in announcements]
        save_state(STATE_PATH, state)
        print(f"Baseline saved: {len(homework)} homework, {len(announcements)} announcements.")
        return 0

    new_hw = [h for h in homework if h["id"] not in seen_hw]
    new_ann = [a for a in announcements if a["id"] not in seen_ann]
    print(f"{len(new_hw)} new homework item(s), {len(new_ann)} new announcement(s)")

    for h in new_hw:
        print("Sending homework:", h["przedmiot"], "-", h["id"])
        send_message(bot_token, chat_id, format_homework_message(h))
        seen_hw.add(h["id"])
        state["homework"] = sorted(seen_hw)
        save_state(STATE_PATH, state)
        time.sleep(1)

    for a in new_ann:
        print("Sending announcement:", a["title"])
        send_message(bot_token, chat_id, format_announcement_message(a))
        seen_ann.add(a["id"])
        state["announcements"] = sorted(seen_ann)
        save_state(STATE_PATH, state)
        time.sleep(1)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
