import hashlib
from datetime import date, timedelta
from typing import List, Optional, TypedDict

from librus_apix.announcements import get_announcements
from librus_apix.client import Client, new_client
from librus_apix.homework import get_homework, homework_detail


class HomeworkItem(TypedDict):
    id: str
    przedmiot: str
    termin_wykonania: str
    tresc: str


class AnnouncementItem(TypedDict):
    id: str
    title: str
    author: str
    date: str
    description: str


class LibrusClient:
    """Wrapper over librus-apix for a single Librus account."""

    def __init__(self, username: str, password: str) -> None:
        self._username = username
        self._password = password
        self._client: Optional[Client] = None

    def login(self) -> None:
        self._client = new_client()
        self._client.get_token(self._username, self._password)

    def get_homework(self, days_back: int = 7, days_forward: int = 21) -> List[HomeworkItem]:
        assert self._client is not None, "call login() first"
        date_from = (date.today() - timedelta(days=days_back)).isoformat()
        date_to = (date.today() + timedelta(days=days_forward)).isoformat()
        raw = get_homework(self._client, date_from, date_to)

        items: List[HomeworkItem] = []
        for h in raw:
            detail = homework_detail(self._client, h.href)
            items.append(
                {
                    "id": h.href,
                    "przedmiot": h.lesson,
                    "termin_wykonania": " ".join(h.completion_date.split()),
                    "tresc": detail.get("Treść", ""),
                }
            )
        return items

    def get_announcements(self) -> List[AnnouncementItem]:
        assert self._client is not None, "call login() first"
        raw = get_announcements(self._client)
        return [
            {
                "id": self._hash_announcement(a.title, a.author, a.date),
                "title": a.title,
                "author": a.author,
                "date": a.date,
                "description": a.description,
            }
            for a in raw
        ]

    @staticmethod
    def _hash_announcement(title: str, author: str, date_str: str) -> str:
        payload = f"{title}|{author}|{date_str}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()
