from app.config import Config


config: Config | None = None
db = None


def is_admin(user_id: int | None) -> bool:
    return bool(config and user_id in config.admin_ids)
