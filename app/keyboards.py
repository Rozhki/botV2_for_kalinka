from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="Найти сотрудника"), KeyboardButton(text="Найти подразделение")],
        [KeyboardButton(text="Список подразделений"), KeyboardButton(text="Частые контакты")],
        [KeyboardButton(text="Помощь")],
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить сотрудника"), KeyboardButton(text="Добавить подразделение")],
            [KeyboardButton(text="Редактировать запись"), KeyboardButton(text="Архивировать запись")],
            [KeyboardButton(text="Проверить неактуальные данные")],
            [KeyboardButton(text="Главное меню")],
        ],
        resize_keyboard=True,
    )


def departments_inline(departments: list, prefix: str = "department") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=row["name"], callback_data=f"{prefix}:{row['id']}")]
        for row in departments
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def employees_inline(employees: list, prefix: str = "employee") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=row["full_name"], callback_data=f"{prefix}:{row['id']}")]
        for row in employees
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def edit_type_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сотрудник", callback_data="edit_type:employee")],
            [InlineKeyboardButton(text="Подразделение", callback_data="edit_type:department")],
        ]
    )


def employee_fields_inline(employee_id: int) -> InlineKeyboardMarkup:
    fields = [
        ("ФИО", "full_name"),
        ("Должность", "position"),
        ("Подразделение", "department_id"),
        ("Внутр. телефон", "internal_phone"),
        ("Телефон", "phone"),
        ("Email", "email"),
        ("Место", "location"),
        ("Ответственный", "is_responsible"),
        ("Примечание", "note"),
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=title, callback_data=f"edit_employee:{employee_id}:{field}")]
            for title, field in fields
        ]
    )


def department_fields_inline(department_id: int) -> InlineKeyboardMarkup:
    fields = [
        ("Название", "name"),
        ("Описание", "description"),
        ("Внутр. телефон", "internal_phone"),
        ("Телефон", "phone"),
        ("Email", "email"),
        ("Расположение", "location"),
        ("График", "work_schedule"),
        ("Примечание", "note"),
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=title, callback_data=f"edit_department:{department_id}:{field}")]
            for title, field in fields
        ]
    )
