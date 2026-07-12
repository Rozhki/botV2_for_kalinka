from aiogram import F, Router
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app import context
from app.filters import NotNavigationText
from app.formatters import department_card, employee_card
from app.keyboards import (
    admin_menu,
    department_fields_inline,
    departments_inline,
    edit_type_inline,
    employee_fields_inline,
    employees_inline,
    main_menu,
)
from app.repositories import AdminRepository
from app.states import DepartmentCreate, EditStates, EmployeeCreate
from app.time_utils import format_timestamp


router = Router()


class AdminOnly(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user = event.from_user
        return user is not None and context.is_admin(user.id)


class NotAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user = event.from_user
        return user is None or not context.is_admin(user.id)


def _repo(message_or_query: Message | CallbackQuery) -> AdminRepository:
    return AdminRepository(context.db)


@router.message(AdminOnly(), F.text == "Админ-панель")
async def admin_panel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Админ-панель", reply_markup=admin_menu())


@router.message(AdminOnly(), F.text == "Добавить подразделение")
async def add_department_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(DepartmentCreate.name)
    await message.answer("Название подразделения:")


@router.message(AdminOnly(), DepartmentCreate.name, NotNavigationText())
async def add_department_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text or "")
    await state.set_state(DepartmentCreate.description)
    await message.answer("Краткое описание функций:")


@router.message(AdminOnly(), DepartmentCreate.description, NotNavigationText())
async def add_department_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text or "")
    await state.set_state(DepartmentCreate.internal_phone)
    await message.answer("Внутренний телефон:")


@router.message(AdminOnly(), DepartmentCreate.internal_phone, NotNavigationText())
async def add_department_internal_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(internal_phone=message.text or "")
    await state.set_state(DepartmentCreate.phone)
    await message.answer("Рабочий телефон, если есть. Если нет, отправьте '-'.")


@router.message(AdminOnly(), DepartmentCreate.phone, NotNavigationText())
async def add_department_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(phone=_empty_dash(message.text))
    await state.set_state(DepartmentCreate.email)
    await message.answer("Email, если есть. Если нет, отправьте '-'.")


@router.message(AdminOnly(), DepartmentCreate.email, NotNavigationText())
async def add_department_email(message: Message, state: FSMContext) -> None:
    await state.update_data(email=_empty_dash(message.text))
    await state.set_state(DepartmentCreate.location)
    await message.answer("Кабинет, этаж или место расположения:")


@router.message(AdminOnly(), DepartmentCreate.location, NotNavigationText())
async def add_department_location(message: Message, state: FSMContext) -> None:
    await state.update_data(location=message.text or "")
    await state.set_state(DepartmentCreate.work_schedule)
    await message.answer("График работы:")


@router.message(AdminOnly(), DepartmentCreate.work_schedule, NotNavigationText())
async def add_department_schedule(message: Message, state: FSMContext) -> None:
    await state.update_data(work_schedule=message.text or "")
    await state.set_state(DepartmentCreate.note)
    await message.answer("Примечание. Если нет, отправьте '-'.")


@router.message(AdminOnly(), DepartmentCreate.note, NotNavigationText())
async def add_department_finish(message: Message, state: FSMContext) -> None:
    await state.update_data(note=_empty_dash(message.text))
    data = await state.get_data()
    department_id = await _repo(message).create_department(data)
    department = await _repo(message).get_department(department_id)
    await state.clear()
    await message.answer("Подразделение добавлено.", reply_markup=admin_menu())
    await message.answer(department_card(department))


@router.message(AdminOnly(), F.text == "Добавить сотрудника")
async def add_employee_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(EmployeeCreate.full_name)
    await message.answer("ФИО сотрудника:")


@router.message(AdminOnly(), EmployeeCreate.full_name, NotNavigationText())
async def add_employee_name(message: Message, state: FSMContext) -> None:
    await state.update_data(full_name=message.text or "")
    await state.set_state(EmployeeCreate.position)
    await message.answer("Должность:")


@router.message(AdminOnly(), EmployeeCreate.position, NotNavigationText())
async def add_employee_position(message: Message, state: FSMContext) -> None:
    await state.update_data(position=message.text or "")
    departments = list(await _repo(message).list_departments())
    await state.set_state(EmployeeCreate.department_id)
    if departments:
        await message.answer("Выберите подразделение:", reply_markup=departments_inline(departments, "choose_department"))
    else:
        await message.answer("Подразделений пока нет. Отправьте 0, чтобы оставить без подразделения.")


@router.callback_query(AdminOnly(), EmployeeCreate.department_id, F.data.startswith("choose_department:"))
async def choose_employee_department(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(department_id=int(callback.data.split(":")[1]))
    await state.set_state(EmployeeCreate.internal_phone)
    await callback.message.answer("Внутренний телефон:")
    await callback.answer()


@router.message(AdminOnly(), EmployeeCreate.department_id, NotNavigationText())
async def type_employee_department(message: Message, state: FSMContext) -> None:
    value = (message.text or "").strip()
    await state.update_data(department_id=int(value) if value.isdigit() and value != "0" else None)
    await state.set_state(EmployeeCreate.internal_phone)
    await message.answer("Внутренний телефон:")


@router.message(AdminOnly(), EmployeeCreate.internal_phone, NotNavigationText())
async def add_employee_internal_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(internal_phone=message.text or "")
    await state.set_state(EmployeeCreate.phone)
    await message.answer("Рабочий телефон, если есть. Если нет, отправьте '-'.")


@router.message(AdminOnly(), EmployeeCreate.phone, NotNavigationText())
async def add_employee_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(phone=_empty_dash(message.text))
    await state.set_state(EmployeeCreate.email)
    await message.answer("Email, если есть. Если нет, отправьте '-'.")


@router.message(AdminOnly(), EmployeeCreate.email, NotNavigationText())
async def add_employee_email(message: Message, state: FSMContext) -> None:
    await state.update_data(email=_empty_dash(message.text))
    await state.set_state(EmployeeCreate.location)
    await message.answer("Кабинет или место работы:")


@router.message(AdminOnly(), EmployeeCreate.location, NotNavigationText())
async def add_employee_location(message: Message, state: FSMContext) -> None:
    await state.update_data(location=message.text or "")
    await state.set_state(EmployeeCreate.is_responsible)
    await message.answer("Ответственное лицо подразделения? Отправьте 'да' или 'нет'.")


@router.message(AdminOnly(), EmployeeCreate.is_responsible, NotNavigationText())
async def add_employee_responsible(message: Message, state: FSMContext) -> None:
    await state.update_data(is_responsible=(message.text or "").strip().lower() in {"да", "yes", "1", "+"})
    await state.set_state(EmployeeCreate.note)
    await message.answer("Примечание. Если нет, отправьте '-'.")


@router.message(AdminOnly(), EmployeeCreate.note, NotNavigationText())
async def add_employee_finish(message: Message, state: FSMContext) -> None:
    await state.update_data(note=_empty_dash(message.text))
    data = await state.get_data()
    employee_id = await _repo(message).create_employee(data)
    employee = await _repo(message).get_employee(employee_id)
    await state.clear()
    await message.answer("Сотрудник добавлен.", reply_markup=admin_menu())
    await message.answer(employee_card(employee))


@router.message(AdminOnly(), F.text == "Редактировать запись")
async def edit_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(EditStates.search)
    await message.answer("Что редактируем?", reply_markup=edit_type_inline())


@router.callback_query(AdminOnly(), EditStates.search, F.data.startswith("edit_type:"))
async def edit_type(callback: CallbackQuery, state: FSMContext) -> None:
    record_type = callback.data.split(":")[1]
    await state.update_data(record_type=record_type)
    await callback.message.answer("Введите часть названия или ФИО для поиска записи.")
    await callback.answer()


@router.message(AdminOnly(), EditStates.search, NotNavigationText())
async def edit_search(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    record_type = data.get("record_type")
    if record_type == "employee":
        employees = list(await _repo(message).search_employees(message.text or ""))
        await message.answer("Выберите сотрудника:", reply_markup=employees_inline(employees, "edit_select_employee"))
    elif record_type == "department":
        departments = list(await _repo(message).search_departments(message.text or ""))
        await message.answer("Выберите подразделение:", reply_markup=departments_inline(departments, "edit_select_department"))
    else:
        await message.answer("Сначала выберите тип записи.")


@router.callback_query(AdminOnly(), F.data.startswith("edit_select_employee:"))
async def edit_select_employee(callback: CallbackQuery) -> None:
    employee_id = int(callback.data.split(":")[1])
    await callback.message.answer("Выберите поле:", reply_markup=employee_fields_inline(employee_id))
    await callback.answer()


@router.callback_query(AdminOnly(), F.data.startswith("edit_select_department:"))
async def edit_select_department(callback: CallbackQuery) -> None:
    department_id = int(callback.data.split(":")[1])
    await callback.message.answer("Выберите поле:", reply_markup=department_fields_inline(department_id))
    await callback.answer()


@router.callback_query(AdminOnly(), F.data.startswith("edit_employee:"))
async def edit_employee_field(callback: CallbackQuery, state: FSMContext) -> None:
    _, record_id, field = callback.data.split(":")
    await state.set_state(EditStates.value)
    await state.update_data(record_type="employee", record_id=int(record_id), field=field)
    await callback.message.answer("Введите новое значение.")
    await callback.answer()


@router.callback_query(AdminOnly(), F.data.startswith("edit_department:"))
async def edit_department_field(callback: CallbackQuery, state: FSMContext) -> None:
    _, record_id, field = callback.data.split(":")
    await state.set_state(EditStates.value)
    await state.update_data(record_type="department", record_id=int(record_id), field=field)
    await callback.message.answer("Введите новое значение.")
    await callback.answer()


@router.message(AdminOnly(), EditStates.value, NotNavigationText())
async def edit_save_value(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    record_type = data["record_type"]
    record_id = data["record_id"]
    field = data["field"]
    value: str | int | None = _empty_dash(message.text)
    if field == "is_responsible":
        value = int((message.text or "").strip().lower() in {"да", "yes", "1", "+"})
    elif field == "department_id":
        value = int(value) if str(value).isdigit() and value != "0" else None

    repo = _repo(message)
    if record_type == "employee":
        await repo.update_employee_field(record_id, field, value)
        employee = await repo.get_employee(record_id)
        await message.answer("Запись обновлена.", reply_markup=admin_menu())
        await message.answer(employee_card(employee))
    else:
        await repo.update_department_field(record_id, field, str(value or ""))
        department = await repo.get_department(record_id)
        await message.answer("Запись обновлена.", reply_markup=admin_menu())
        await message.answer(department_card(department))
    await state.clear()


@router.message(AdminOnly(), F.text == "Архивировать запись")
async def archive_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(EditStates.archive_search)
    await message.answer("Что архивируем?", reply_markup=edit_type_inline())


@router.callback_query(AdminOnly(), EditStates.archive_search, F.data.startswith("edit_type:"))
async def archive_type(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(record_type=callback.data.split(":")[1])
    await callback.message.answer("Введите часть названия или ФИО для поиска записи.")
    await callback.answer()


@router.message(AdminOnly(), EditStates.archive_search, NotNavigationText())
async def archive_search(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("record_type") == "employee":
        employees = list(await _repo(message).search_employees(message.text or ""))
        await message.answer("Выберите сотрудника:", reply_markup=employees_inline(employees, "archive_employee"))
    elif data.get("record_type") == "department":
        departments = list(await _repo(message).search_departments(message.text or ""))
        await message.answer("Выберите подразделение:", reply_markup=departments_inline(departments, "archive_department"))


@router.callback_query(AdminOnly(), F.data.startswith("archive_employee:"))
async def archive_employee(callback: CallbackQuery, state: FSMContext) -> None:
    await _repo(callback).archive_employee(int(callback.data.split(":")[1]))
    await state.clear()
    await callback.message.answer("Сотрудник архивирован.", reply_markup=admin_menu())
    await callback.answer()


@router.callback_query(AdminOnly(), F.data.startswith("archive_department:"))
async def archive_department(callback: CallbackQuery, state: FSMContext) -> None:
    await _repo(callback).archive_department(int(callback.data.split(":")[1]))
    await state.clear()
    await callback.message.answer("Подразделение архивировано.", reply_markup=admin_menu())
    await callback.answer()


@router.message(AdminOnly(), F.text == "Проверить неактуальные данные")
async def stale_records(message: Message) -> None:
    stale = await _repo(message).stale_records()
    parts = ["Записи старше 180 дней:"]
    parts.append("\nПодразделения:")
    parts.extend(f"- {row['name']} ({format_timestamp(row['updated_at'])})" for row in stale["departments"][:10])
    parts.append("\nСотрудники:")
    parts.extend(f"- {row['full_name']} ({format_timestamp(row['updated_at'])})" for row in stale["employees"][:10])
    if len(parts) == 3:
        parts.append("Таких записей нет.")
    await message.answer("\n".join(parts), reply_markup=admin_menu())


@router.message(NotAdmin(), F.text.in_({
    "Админ-панель",
    "Добавить сотрудника",
    "Добавить подразделение",
    "Редактировать запись",
    "Архивировать запись",
    "Проверить неактуальные данные",
}))
async def deny_admin(message: Message) -> None:
    await message.answer("Это действие доступно только администратору.", reply_markup=main_menu(False))


def _empty_dash(value: str | None) -> str:
    value = (value or "").strip()
    return "" if value == "-" else value
