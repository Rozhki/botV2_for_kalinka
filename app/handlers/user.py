from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app import context
from app.filters import NotNavigationText
from app.formatters import department_card, employee_card
from app.keyboards import departments_inline, employees_inline
from app.repositories import DirectoryRepository
from app.states import SearchStates


router = Router()


def _repo(message_or_query: Message | CallbackQuery) -> DirectoryRepository:
    return DirectoryRepository(context.db)


@router.message(F.text == "Найти сотрудника")
async def ask_employee_query(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(SearchStates.employee_query)
    await message.answer("Введите ФИО, должность или часть слова для поиска сотрудника.")


@router.message(SearchStates.employee_query, NotNavigationText())
async def search_employee(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _send_employee_results(message, message.text or "")


@router.message(F.text == "Найти подразделение")
async def ask_department_query(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(SearchStates.department_query)
    await message.answer("Введите название подразделения или часть названия.")


@router.message(SearchStates.department_query, NotNavigationText())
async def search_department(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _send_department_results(message, message.text or "")


@router.message(F.text == "Список подразделений")
async def list_departments(message: Message, state: FSMContext) -> None:
    await state.clear()
    departments = list(await _repo(message).list_departments())
    if not departments:
        await message.answer("Подразделения пока не добавлены.")
        return
    await message.answer("Выберите подразделение:", reply_markup=departments_inline(departments))


@router.message(F.text == "Частые контакты")
async def frequent_contacts(message: Message, state: FSMContext) -> None:
    await state.clear()
    employees = await _repo(message).frequent_contacts()
    if not employees:
        await message.answer("Частые контакты пока не отмечены.")
        return
    text = "\n\n".join(employee_card(employee) for employee in employees)
    await message.answer(text)


@router.callback_query(F.data.startswith("department:"))
async def show_department(callback: CallbackQuery) -> None:
    department_id = int(callback.data.split(":")[1])
    repo = _repo(callback)
    department = await repo.get_department(department_id)
    if not department:
        await callback.answer("Запись не найдена", show_alert=True)
        return
    responsible = await repo.responsible_by_department(department_id)
    await callback.message.answer(department_card(department, responsible))
    await callback.answer()


@router.callback_query(F.data.startswith("employee:"))
async def show_employee(callback: CallbackQuery) -> None:
    employee_id = int(callback.data.split(":")[1])
    employee = await _repo(callback).get_employee(employee_id)
    if not employee:
        await callback.answer("Запись не найдена", show_alert=True)
        return
    await callback.message.answer(employee_card(employee))
    await callback.answer()


@router.message(F.text)
async def free_text_search(message: Message) -> None:
    query = message.text or ""
    employees = await _repo(message).search_employees(query)
    departments = await _repo(message).search_departments(query)

    if employees:
        await message.answer(
            "Найдены сотрудники:",
            reply_markup=employees_inline(list(employees)),
        )
    if departments:
        await message.answer(
            "Найдены подразделения:",
            reply_markup=departments_inline(list(departments)),
        )
    if not employees and not departments:
        await message.answer("Ничего не найдено. Попробуйте другое слово.")


async def _send_employee_results(message: Message, query: str) -> None:
    employees = list(await _repo(message).search_employees(query))
    if not employees:
        await message.answer("Сотрудники не найдены.")
        return
    await message.answer("Выберите сотрудника:", reply_markup=employees_inline(employees))


async def _send_department_results(message: Message, query: str) -> None:
    departments = list(await _repo(message).search_departments(query))
    if not departments:
        await message.answer("Подразделения не найдены.")
        return
    await message.answer("Выберите подразделение:", reply_markup=departments_inline(departments))
