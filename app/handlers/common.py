from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.context import is_admin
from app.keyboards import main_menu


router = Router()


def _is_admin(message: Message) -> bool:
    return message.from_user is not None and is_admin(message.from_user.id)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Внутренний справочник контактов мясокомбината.\n"
        "Выберите действие в меню или отправьте часть ФИО, должности или названия подразделения.",
        reply_markup=main_menu(_is_admin(message)),
    )


@router.message(F.text == "Главное меню")
async def menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Главное меню", reply_markup=main_menu(_is_admin(message)))


@router.message(F.text == "Помощь")
async def help_message(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Что можно сделать:\n"
        "- найти сотрудника по ФИО, должности или подразделению;\n"
        "- найти подразделение по названию;\n"
        "- открыть список подразделений;\n"
        "- посмотреть частые контакты.\n\n"
        "Для поиска нажмите кнопку меню или просто отправьте поисковый запрос."
    )
