import json
import os
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, TypeVar

T = TypeVar("T")

_locks: Dict[str, threading.Lock] = {}


def _get_lock(path: Path) -> threading.Lock:
    key = str(path.resolve())
    if key not in _locks:
        _locks[key] = threading.Lock()
    return _locks[key]


class JsonStore:
    """Persistencia en archivo JSON con lock y escritura atomica."""

    def __init__(self, file_path: Path):
        self._path = file_path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write_raw({"items": []})

    def read_all(self) -> List[Dict[str, Any]]:
        with _get_lock(self._path):
            return self._read_raw()["items"]

    def write_all(self, items: List[Dict[str, Any]]) -> None:
        with _get_lock(self._path):
            self._write_raw({"items": items})

    def update(self, mutator: Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]]) -> None:
        with _get_lock(self._path):
            data = self._read_raw()
            data["items"] = mutator(data["items"])
            self._write_raw(data)

    def is_empty(self) -> bool:
        return len(self.read_all()) == 0

    def _read_raw(self) -> Dict[str, Any]:
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_raw(self, data: Dict[str, Any]) -> None:
        tmp = self._path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        os.replace(tmp, self._path)
