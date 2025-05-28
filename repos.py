import os
import json
from typing import Any, Optional



class GroqKeyRepository:
    def __init__(self, KEY_FILE: str):
        self.KEY_FILE = KEY_FILE
        if not os.path.exists(self.KEY_FILE):
            with open(self.KEY_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)

    def get_keys(self) -> dict:
        with open(self.KEY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_key(self, key: str) -> Any:
        with open(self.KEY_FILE, "r", encoding="utf-8") as f:
            content = json.load(f)
            return content.get(key)

    def set_key(self, key: str, value: str):
        keys = self.get_keys()
        keys[key] = value
        with open(self.KEY_FILE, "w", encoding="utf-8") as f:
            json.dump(keys, f, indent=2, ensure_ascii=False)


class HistoryRepository:
    def __init__(self, HISTORY_FILE: str, MAX_HISTORY: int):
        self.HISTORY_FILE = HISTORY_FILE
        self.MAX_HISTORY = MAX_HISTORY
        if not os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def load(self) -> list:
        if os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def write(self, history: list):
        with open(self.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-self.MAX_HISTORY:], f, indent=2, ensure_ascii=False)

    def append(self, role: str, content: Optional[str]):
        history = self.load()
        history.append({"role": role, "content": content})
        self.write(history)

    def reset(self):
        self.write([])
