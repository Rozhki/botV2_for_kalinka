from collections.abc import Sequence

import aiosqlite

from app.time_utils import format_timestamp


Row = aiosqlite.Row


def _line(title: str, value: object) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, str) and len(value) >= 16 and value[4:5] == "-" and value[10:11] == " ":
        value = format_timestamp(value)
    return f"{title}: {value}"


def department_card(department: Row, responsible: Sequence[Row] | None = None) -> str:
    lines = [
        f"<b>{department['name']}</b>",
        _line("Функции", department["description"]),
        _line("Внутренний телефон", department["internal_phone"]),
        _line("Рабочий телефон", department["phone"]),
        _line("Email", department["email"]),
        _line("Расположение", department["location"]),
        _line("График", department["work_schedule"]),
        _line("Примечание", department["note"]),
        _line("Обновлено", department["updated_at"]),
    ]
    clean_lines = [line for line in lines if line]

    if responsible:
        clean_lines.append("")
        clean_lines.append("<b>Ответственные:</b>")
        clean_lines.extend(
            f"{employee['full_name']} - {employee['position']} ({employee['internal_phone'] or 'телефон не указан'})"
            for employee in responsible
        )

    return "\n".join(clean_lines)


def employee_card(employee: Row) -> str:
    lines = [
        f"<b>{employee['full_name']}</b>",
        _line("Должность", employee["position"]),
        _line("Подразделение", employee["department_name"]),
        _line("Внутренний телефон", employee["internal_phone"]),
        _line("Рабочий телефон", employee["phone"]),
        _line("Email", employee["email"]),
        _line("Место работы", employee["location"]),
        "Ответственное лицо: да" if employee["is_responsible"] else "",
        _line("Примечание", employee["note"]),
        _line("Обновлено", employee["updated_at"]),
    ]
    return "\n".join(line for line in lines if line)
