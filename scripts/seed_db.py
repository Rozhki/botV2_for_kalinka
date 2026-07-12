import argparse
import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from dotenv import load_dotenv

from app.db import connect, init_schema  
from app.time_utils import now_string 


DEPARTMENTS = [
    ("ИТ-служба", "Поддержка рабочих мест, сети и корпоративных систем", "123", "8 (343) 200-01-23", "it@example.local", "2 этаж, каб. 205", "Пн-Пт 08:00-17:00", "Обращения по доступам и технике"),
    ("Бухгалтерия", "Расчеты, документы, отчетность", "210", "8 (343) 200-02-10", "accounting@example.local", "1 этаж, каб. 110", "Пн-Пт 08:00-17:00", ""),
    ("Отдел кадров", "Кадровые документы, прием и увольнение", "220", "8 (343) 200-02-20", "hr@example.local", "1 этаж, каб. 115", "Пн-Пт 08:00-17:00", ""),
    ("Склад", "Прием, хранение и выдача материалов", "310", "", "warehouse@example.local", "Складской корпус", "Ежедневно 08:00-20:00", ""),
    ("Снабжение", "Закупки сырья, материалов и оборудования", "330", "8 (343) 200-03-30", "supply@example.local", "2 этаж, каб. 214", "Пн-Пт 08:00-17:00", ""),
    ("Охрана", "Контроль доступа и безопасность", "400", "", "security@example.local", "Пост охраны", "Круглосуточно", "Экстренный контакт"),
    ("Проходная", "Пропуска и регистрация посетителей", "401", "", "gate@example.local", "Главная проходная", "Круглосуточно", "Часто используемый контакт"),
    ("Производственный отдел", "Организация производственных смен", "510", "", "production@example.local", "Производственный корпус", "По графику смен", ""),
    ("Отдел качества", "Контроль качества продукции и сырья", "530", "8 (343) 200-05-30", "quality@example.local", "Лаборатория, 1 этаж", "Пн-Пт 08:00-17:00", ""),
    ("Хозяйственная служба", "Ремонт, уборка и эксплуатация помещений", "610", "", "maintenance@example.local", "Хозблок", "Пн-Пт 08:00-17:00", ""),
]


EMPLOYEES = [
    ("Иванов Иван Иванович", "Системный администратор", "ИТ-служба", "123", "", "ivanov@example.local", "каб. 205", 1, "важный контакт"),
    ("Петрова Анна Сергеевна", "Специалист технической поддержки", "ИТ-служба", "124", "", "petrova@example.local", "каб. 205", 0, ""),
    ("Сидорова Мария Петровна", "Главный бухгалтер", "Бухгалтерия", "210", "", "sidorova@example.local", "каб. 110", 1, "важный контакт"),
    ("Кузнецова Ольга Викторовна", "Бухгалтер", "Бухгалтерия", "211", "", "kuznetsova@example.local", "каб. 110", 0, ""),
    ("Смирнов Павел Андреевич", "Начальник отдела кадров", "Отдел кадров", "220", "", "smirnov@example.local", "каб. 115", 1, "важный контакт"),
    ("Волкова Елена Николаевна", "Инспектор по кадрам", "Отдел кадров", "221", "", "volkova@example.local", "каб. 115", 0, ""),
    ("Морозов Дмитрий Олегович", "Заведующий складом", "Склад", "310", "", "morozov@example.local", "складской корпус", 1, "важный контакт"),
    ("Новиков Артем Игоревич", "Кладовщик", "Склад", "311", "", "novikov@example.local", "складской корпус", 0, ""),
    ("Федорова Наталья Юрьевна", "Менеджер по снабжению", "Снабжение", "330", "", "fedorova@example.local", "каб. 214", 1, "важный контакт"),
    ("Алексеев Сергей Михайлович", "Старший смены охраны", "Охрана", "400", "", "alekseev@example.local", "пост охраны", 1, "экстренный контакт"),
    ("Громова Ирина Валерьевна", "Дежурный проходной", "Проходная", "401", "", "gromova@example.local", "главная проходная", 1, "часто используемый контакт"),
    ("Беляев Константин Романович", "Начальник производства", "Производственный отдел", "510", "", "belyaev@example.local", "производственный корпус", 1, "важный контакт"),
    ("Орлова Татьяна Павловна", "Мастер смены", "Производственный отдел", "511", "", "orlova@example.local", "производственный корпус", 0, ""),
    ("Егоров Максим Денисович", "Инженер по качеству", "Отдел качества", "530", "", "egorov@example.local", "лаборатория", 1, "важный контакт"),
    ("Никитин Андрей Борисович", "Специалист хозяйственной службы", "Хозяйственная служба", "610", "", "nikitin@example.local", "хозблок", 1, "важный контакт"),
]


async def main() -> None:
    parser = argparse.ArgumentParser(description="Fill the directory bot database with test data.")
    parser.add_argument("--database", default="data/directory.sqlite3")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    await init_schema(args.database)
    db = await connect(args.database)
    try:
        await db.execute("DELETE FROM employees")
        await db.execute("DELETE FROM departments")

        await db.executemany(
            """
            INSERT INTO departments
            (name, description, internal_phone, phone, email, location, work_schedule, note, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [department + (now_string(),) for department in DEPARTMENTS],
        )
        cursor = await db.execute("SELECT id, name FROM departments")
        department_ids = {row["name"]: row["id"] for row in await cursor.fetchall()}

        employee_rows = [
            (
                full_name,
                position,
                department_ids[department],
                internal_phone,
                phone,
                email,
                location,
                is_responsible,
                note,
                now_string(),
            )
            for full_name, position, department, internal_phone, phone, email, location, is_responsible, note
            in EMPLOYEES
        ]
        await db.executemany(
            """
            INSERT INTO employees
            (full_name, position, department_id, internal_phone, phone, email, location,
             is_responsible, note, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            employee_rows,
        )
        await db.commit()
    finally:
        await db.close()

    print(f"Seed data loaded: {len(DEPARTMENTS)} departments, {len(EMPLOYEES)} employees")


if __name__ == "__main__":
    asyncio.run(main())
