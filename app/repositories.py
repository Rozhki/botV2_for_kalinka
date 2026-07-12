from collections.abc import Sequence
from typing import Any

import aiosqlite

from app.time_utils import now_string, stale_border_string


Row = aiosqlite.Row


class DirectoryRepository:
    def __init__(self, db: aiosqlite.Connection) -> None:
        self.db = db

    async def list_departments(self, include_archived: bool = False) -> Sequence[Row]:
        query = "SELECT * FROM departments"
        params: list[Any] = []
        if not include_archived:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        cursor = await self.db.execute(query, params)
        return await cursor.fetchall()

    async def get_department(self, department_id: int) -> Row | None:
        cursor = await self.db.execute(
            "SELECT * FROM departments WHERE id = ?",
            (department_id,),
        )
        return await cursor.fetchone()

    async def search_departments(self, query: str) -> Sequence[Row]:
        cursor = await self.db.execute(
            """
            SELECT *
            FROM departments
            WHERE is_active = 1 AND name LIKE ?
            ORDER BY name
            LIMIT 10
            """,
            (f"%{query}%",),
        )
        return await cursor.fetchall()

    async def search_employees(self, query: str) -> Sequence[Row]:
        like = f"%{query}%"
        cursor = await self.db.execute(
            """
            SELECT e.*, d.name AS department_name
            FROM employees e
            LEFT JOIN departments d ON d.id = e.department_id
            WHERE e.is_active = 1
              AND (e.full_name LIKE ? OR e.position LIKE ? OR d.name LIKE ?)
            ORDER BY e.full_name
            LIMIT 10
            """,
            (like, like, like),
        )
        return await cursor.fetchall()

    async def get_employee(self, employee_id: int) -> Row | None:
        cursor = await self.db.execute(
            """
            SELECT e.*, d.name AS department_name
            FROM employees e
            LEFT JOIN departments d ON d.id = e.department_id
            WHERE e.id = ?
            """,
            (employee_id,),
        )
        return await cursor.fetchone()

    async def responsible_by_department(self, department_id: int) -> Sequence[Row]:
        cursor = await self.db.execute(
            """
            SELECT e.*, d.name AS department_name
            FROM employees e
            LEFT JOIN departments d ON d.id = e.department_id
            WHERE e.is_active = 1 AND e.is_responsible = 1 AND e.department_id = ?
            ORDER BY e.full_name
            """,
            (department_id,),
        )
        return await cursor.fetchall()

    async def frequent_contacts(self) -> Sequence[Row]:
        cursor = await self.db.execute(
            """
            SELECT e.*, d.name AS department_name
            FROM employees e
            LEFT JOIN departments d ON d.id = e.department_id
            WHERE e.is_active = 1 AND (e.is_responsible = 1 OR e.note LIKE '%важн%')
            ORDER BY d.name, e.full_name
            LIMIT 20
            """
        )
        return await cursor.fetchall()

    async def stale_records(self) -> dict[str, Sequence[Row]]:
        stale_border = stale_border_string()
        departments = await (
            await self.db.execute(
                """
                SELECT * FROM departments
                WHERE updated_at < ?
                ORDER BY updated_at
                LIMIT 20
                """,
                (stale_border,),
            )
        ).fetchall()
        employees = await (
            await self.db.execute(
                """
                SELECT e.*, d.name AS department_name
                FROM employees e
                LEFT JOIN departments d ON d.id = e.department_id
                WHERE e.updated_at < ?
                ORDER BY e.updated_at
                LIMIT 20
                """,
                (stale_border,),
            )
        ).fetchall()
        return {"departments": departments, "employees": employees}


class AdminRepository(DirectoryRepository):
    async def create_department(self, data: dict[str, str]) -> int:
        cursor = await self.db.execute(
            """
            INSERT INTO departments
            (name, description, internal_phone, phone, email, location, work_schedule, note, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data.get("description", ""),
                data.get("internal_phone", ""),
                data.get("phone", ""),
                data.get("email", ""),
                data.get("location", ""),
                data.get("work_schedule", ""),
                data.get("note", ""),
                now_string(),
            ),
        )
        await self.db.commit()
        return int(cursor.lastrowid)

    async def update_department_field(self, department_id: int, field: str, value: str) -> None:
        allowed = {
            "name",
            "description",
            "internal_phone",
            "phone",
            "email",
            "location",
            "work_schedule",
            "note",
        }
        if field not in allowed:
            raise ValueError("Unsupported department field")
        await self.db.execute(
            f"UPDATE departments SET {field} = ?, updated_at = ? WHERE id = ?",
            (value, now_string(), department_id),
        )
        await self.db.commit()

    async def archive_department(self, department_id: int) -> None:
        await self.db.execute(
            "UPDATE departments SET is_active = 0, updated_at = ? WHERE id = ?",
            (now_string(), department_id),
        )
        await self.db.commit()

    async def create_employee(self, data: dict[str, Any]) -> int:
        cursor = await self.db.execute(
            """
            INSERT INTO employees
            (full_name, position, department_id, internal_phone, phone, email, location,
             is_responsible, note, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["full_name"],
                data.get("position", ""),
                data.get("department_id"),
                data.get("internal_phone", ""),
                data.get("phone", ""),
                data.get("email", ""),
                data.get("location", ""),
                int(data.get("is_responsible", False)),
                data.get("note", ""),
                now_string(),
            ),
        )
        await self.db.commit()
        return int(cursor.lastrowid)

    async def update_employee_field(self, employee_id: int, field: str, value: Any) -> None:
        allowed = {
            "full_name",
            "position",
            "department_id",
            "internal_phone",
            "phone",
            "email",
            "location",
            "is_responsible",
            "note",
        }
        if field not in allowed:
            raise ValueError("Unsupported employee field")
        await self.db.execute(
            f"UPDATE employees SET {field} = ?, updated_at = ? WHERE id = ?",
            (value, now_string(), employee_id),
        )
        await self.db.commit()

    async def archive_employee(self, employee_id: int) -> None:
        await self.db.execute(
            "UPDATE employees SET is_active = 0, updated_at = ? WHERE id = ?",
            (now_string(), employee_id),
        )
        await self.db.commit()
