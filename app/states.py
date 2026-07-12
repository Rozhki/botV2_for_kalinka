from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    employee_query = State()
    department_query = State()


class DepartmentCreate(StatesGroup):
    name = State()
    description = State()
    internal_phone = State()
    phone = State()
    email = State()
    location = State()
    work_schedule = State()
    note = State()


class EmployeeCreate(StatesGroup):
    full_name = State()
    position = State()
    department_id = State()
    internal_phone = State()
    phone = State()
    email = State()
    location = State()
    is_responsible = State()
    note = State()


class EditStates(StatesGroup):
    search = State()
    value = State()
    archive_search = State()
