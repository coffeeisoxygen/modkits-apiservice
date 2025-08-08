import pathlib
import threading
from collections.abc import Callable
from typing import Any

from app.utils.log_setup import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def ensure_str_path(path: pathlib.Path | str | bytes) -> str:
    """Ensure the given path is a str, decoding if necessary."""
    if isinstance(path, bytes):
        return path.decode("utf-8")
    return str(path)


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path: pathlib.Path, callback: Callable):
        self.file_path = file_path
        self.callback = callback
        self.debounce_timer: threading.Timer | None = None

    def on_modified(self, event: Any) -> None:
        """Handle file modification event with debouncing."""
        event_path = ensure_str_path(event.src_path)
        if not event.is_directory and pathlib.Path(event_path) == self.file_path:
            logger.info("Change detected. Debouncing for 1 second.")

            # Cancel the old timer if it exists
            if self.debounce_timer:
                self.debounce_timer.cancel()

            # Schedule a new timer to trigger reload after debounce period
            self.debounce_timer = threading.Timer(1.0, self._trigger_reload)
            self.debounce_timer.start()

    def _trigger_reload(self):
        """Trigger the reload callback after debounce period."""
        logger.info("Triggering reload after a brief pause.")
        self.callback()

    def stop(self):
        """Stop the debounce timer if it's running."""
        if self.debounce_timer:
            self.debounce_timer.cancel()
            self.debounce_timer = None


class FileWatcher:
    def __init__(self, file_path: pathlib.Path, callback: Callable):
        self._observer = Observer()
        self._event_handler = ChangeHandler(file_path, callback)
        self._path_to_watch = file_path.parent

    def start(self):
        """Starts the file system observer."""
        self._observer.schedule(
            self._event_handler,
            str(self._path_to_watch),
            recursive=False,  # <-- str()
        )
        self._observer.start()
        logger.info("File watcher started.", path=str(self._path_to_watch))

    def stop(self):
        """Stops the file system observer and waits for it to finish."""
        # Stop the event handler first
        self._event_handler.stop()

        # Then stop the observer
        self._observer.stop()
        self._observer.join()
        logger.info("File watcher stopped.")
