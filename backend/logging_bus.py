import queue
import threading
import time


class LogBus:
    def __init__(self):
        self._q: "queue.Queue[str]" = queue.Queue()
        self._lock = threading.Lock()
        self._subscribers: set[int] = set()
        self._next_id = 1

    def publish(self, msg: str) -> None:
        # Keep it simple: one shared queue, consumers read from it.
        self._q.put(msg)

    def subscribe(self) -> tuple[int, "queue.Queue[str]"]:
        with self._lock:
            sid = self._next_id
            self._next_id += 1
            self._subscribers.add(sid)
        return sid, self._q

    def unsubscribe(self, sid: int) -> None:
        with self._lock:
            self._subscribers.discard(sid)


def sse_format(data: str, event: str | None = None) -> str:
    # SSE format: event/name optional, data required. Blank line ends the message.
    out = []
    if event:
        out.append(f"event: {event}")
    for line in data.splitlines() or [""]:
        out.append(f"data: {line}")
    out.append("")
    return "\n".join(out)


def heartbeat_every(seconds: float):
    last = time.monotonic()
    while True:
        now = time.monotonic()
        if now - last >= seconds:
            yield True
            last = now
        else:
            yield False
