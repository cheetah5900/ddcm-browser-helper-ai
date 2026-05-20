import threading

from browser_bot import BrowserBot


class BrowserManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._bot: BrowserBot | None = None

    def get(self) -> BrowserBot:
        with self._lock:
            if self._bot is None:
                self._bot = BrowserBot()
                ok = self._bot.start_browser(attach=True)
                if not ok:
                    raise RuntimeError("Failed to attach to Chrome on port 9222")
            return self._bot


browser_manager = BrowserManager()
