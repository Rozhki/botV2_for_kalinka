import argparse
import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.db import init_schema 


async def main() -> None:
    parser = argparse.ArgumentParser(description="Create SQLite schema for the directory bot.")
    parser.add_argument("--database", default="data/directory.sqlite3")
    args = parser.parse_args()

    await init_schema(args.database)
    print(f"Database schema is ready: {args.database}")


if __name__ == "__main__":
    asyncio.run(main())
