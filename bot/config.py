"""Configuration helpers."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    bot_token: str
    storage_path: Path

    @classmethod
    def load(cls) -> "Config":
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise RuntimeError("BOT_TOKEN environment variable is required")
        storage = Path(os.getenv("BOT_STORAGE", "./var/bot.sqlite"))
        return cls(bot_token=token, storage_path=storage)
