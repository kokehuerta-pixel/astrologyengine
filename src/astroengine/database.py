import aiosqlite
import os
from .config import settings


async def get_db() -> aiosqlite.Connection:
    """Abre conexión a SQLite y retorna el objeto de conexión."""
    os.makedirs(os.path.dirname(settings.db_path) or ".", exist_ok=True)
    db = await aiosqlite.connect(settings.db_path)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Crea las tablas si no existen."""
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            birth_time TEXT NOT NULL,
            birth_city TEXT NOT NULL,
            current_city TEXT NOT NULL,
            language TEXT DEFAULT 'es',
            report_depth TEXT DEFAULT 'complete',
            llm_model TEXT DEFAULT 'gemini-2.5-flash',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reading_type TEXT NOT NULL,
            chart_data_json TEXT NOT NULL,
            interpretation TEXT NOT NULL,
            location_used TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS natal_charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            chart_data_json TEXT NOT NULL,
            prompt_text TEXT,
            svg_path TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    await db.commit()
    await db.close()
