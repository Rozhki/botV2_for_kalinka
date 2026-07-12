from datetime import datetime, timedelta, timezone
import os
import re


OFFSET_PATTERN = re.compile(r"^([+-])(\d{2}):?(\d{2})$")
RUSSIA_UTC_OFFSET = "+05:00"
TIME_FORMAT = "%Y-%m-%d %H:%M"
DISPLAY_TIME_FORMAT = "%d-%m-%Y %H:%M"


def now_string() -> str:
    return datetime.now(_local_timezone()).strftime(TIME_FORMAT)


def stale_border_string(days: int = 180) -> str:
    return (datetime.now(_local_timezone()) - timedelta(days=days)).strftime(TIME_FORMAT)


def format_timestamp(value: str) -> str:
    """Formats stored timestamps for display without seconds."""
    try:
        return datetime.strptime(value[:16], TIME_FORMAT).strftime(DISPLAY_TIME_FORMAT)
    except ValueError:
        return value[:16]


def _local_timezone() -> timezone:
    offset = os.getenv("LOCAL_UTC_OFFSET", RUSSIA_UTC_OFFSET).strip() or RUSSIA_UTC_OFFSET
    return _fixed_timezone(offset)


def _fixed_timezone(offset: str) -> timezone:
    match = OFFSET_PATTERN.match(offset)
    if not match:
        raise RuntimeError("LOCAL_UTC_OFFSET must look like +05:00 or -03:00")

    sign, hours, minutes = match.groups()
    delta = timedelta(hours=int(hours), minutes=int(minutes))
    if sign == "-":
        delta = -delta
    return timezone(delta)
