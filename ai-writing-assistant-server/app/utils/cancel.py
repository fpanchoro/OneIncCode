import asyncio
from typing import Dict


class CancelRegistry:
    def __init__(self):
        self._events: Dict[str, asyncio.Event] = {}

    def create(self, request_id: str) -> asyncio.Event:
        ev = asyncio.Event()
        self._events[request_id] = ev
        return ev

    def get(self, request_id: str):
        return self._events.get(request_id)

    def cancel(self, request_id: str) -> bool:
        ev = self._events.get(request_id)
        if not ev:
            return False
        ev.set()
        return True

    def clear(self, request_id: str) -> None:
        self._events.pop(request_id, None)


cancel_registry = CancelRegistry()
