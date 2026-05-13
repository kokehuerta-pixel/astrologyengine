"""API endpoints para CRUD de usuarios."""

from fastapi import APIRouter, HTTPException
from ..models import UserCreate, UserResponse, UserUpdate
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """Crear un nuevo usuario con sus datos natales."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO users (name, birth_date, birth_time, birth_city,
               current_city, language, report_depth, llm_model)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user.name, user.birth_date, user.birth_time, user.birth_city,
             user.current_city, user.language, user.report_depth, user.llm_model),
        )
        await db.commit()
        row = await db.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,))
        row = await row.fetchone()
        return dict(row)
    finally:
        await db.close()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Obtener datos de un usuario."""
    db = await get_db()
    try:
        row = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await row.fetchone()
        if not row:
            raise HTTPException(404, "Usuario no encontrado")
        return dict(row)
    finally:
        await db.close()


@router.get("/", response_model=list[UserResponse])
async def list_users():
    """Listar todos los usuarios."""
    db = await get_db()
    try:
        rows = await db.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = await rows.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, update: UserUpdate):
    """Actualizar preferencias de un usuario (ubicación, idioma, etc.)."""
    db = await get_db()
    try:
        fields = {k: v for k, v in update.model_dump().items() if v is not None}
        if not fields:
            raise HTTPException(400, "No hay campos para actualizar")
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [user_id]
        await db.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        await db.commit()
        row = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await row.fetchone()
        if not row:
            raise HTTPException(404, "Usuario no encontrado")
        return dict(row)
    finally:
        await db.close()
