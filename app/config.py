from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_ids: set[int]
    database_path: str


def load_config() -> Config:
    load_dotenv()

    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Set BOT_TOKEN in .env")

    admin_ids_raw = os.getenv("ADMIN_IDS", "").replace(";", ",")
    admin_ids = {
        int(value.strip())
        for value in admin_ids_raw.split(",")
        if value.strip().isdigit()
    }

    return Config(
        bot_token=token,
        admin_ids=admin_ids,
        database_path=os.getenv("DATABASE_PATH", "data/directory.sqlite3"),
    )
