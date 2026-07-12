from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.buttons import NAVIGATION_BUTTONS


class NotNavigationText(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.text) and message.text not in NAVIGATION_BUTTONS
