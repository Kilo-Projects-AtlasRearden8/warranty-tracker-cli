"""Local JSON storage for warranty items."""

import json
import os
import uuid
from pathlib import Path
from typing import List, Optional

from .models import WarrantyItem


def default_storage_path() -> Path:
    env_path = os.environ.get("WARRANTY_TRACKER_FILE")
    if env_path:
        return Path(env_path)
    return Path.home() / ".warranty-tracker" / "warranties.json"


class WarrantyStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = path or default_storage_path()

    def load(self) -> List[WarrantyItem]:
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return []
        if not isinstance(data, list):
            return []
        items: List[WarrantyItem] = []
        for entry in data:
            try:
                items.append(WarrantyItem.from_dict(entry))
            except (TypeError, KeyError):
                continue
        return items

    def save(self, items: List[WarrantyItem]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [item.to_dict() for item in items]
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        tmp_path.replace(self.path)

    def add(self, item: WarrantyItem) -> WarrantyItem:
        items = self.load()
        if not item.id:
            item.id = str(uuid.uuid4())
        items.append(item)
        self.save(items)
        return item

    def remove(self, item_id: str) -> bool:
        items = self.load()
        remaining = [item for item in items if item.id != item_id]
        if len(remaining) == len(items):
            return False
        self.save(remaining)
        return True

    def find(self, item_id: str) -> Optional[WarrantyItem]:
        for item in self.load():
            if item.id == item_id:
                return item
        return None

    def update(self, item_id: str, **fields) -> Optional[WarrantyItem]:
        items = self.load()
        for index, item in enumerate(items):
            if item.id == item_id:
                data = item.to_dict()
                data.update(fields)
                items[index] = WarrantyItem.from_dict(data)
                self.save(items)
                return items[index]
        return None
