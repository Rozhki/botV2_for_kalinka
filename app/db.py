from pathlib import Path
from typing import Any, Iterable

import aiosqlite


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    internal_phone TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    work_schedule TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    is_active INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M', 'now', '+5 hours'))
);

CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    position TEXT NOT NULL DEFAULT '',
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    internal_phone TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    is_responsible INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    note TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M', 'now', '+5 hours'))
);

CREATE INDEX IF NOT EXISTS idx_departments_name ON departments(name);
CREATE INDEX IF NOT EXISTS idx_employees_name ON employees(full_name);
CREATE INDEX IF NOT EXISTS idx_employees_position ON employees(position);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department_id);
"""


async def connect(database_path: str) -> aiosqlite.Connection:
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(database_path)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON")
    return db


async def init_schema(database_path: str) -> None:
    db = await connect(database_path)
    try:
        await db.executescript(SCHEMA)
        await db.commit()
    finally:
        await db.close()


async def execute_many(database_path: str, query: str, rows: Iterable[Iterable[Any]]) -> None:
    db = await connect(database_path)
    try:
        await db.executemany(query, rows)
        await db.commit()
    finally:
        await db.close()
