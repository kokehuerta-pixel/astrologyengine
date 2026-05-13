"""API endpoints para cálculo de carta natal."""

from fastapi import APIRouter, HTTPException
from ..models import NatalChartRequest
from ..services.natal import calculate_natal_chart
from ..database import get_db
import json

router = APIRouter(prefix="/natal", tags=["natal"])


@router.post("/calculate")
async def calc_natal(req: NatalChartRequest):
    """Calcular carta natal de un usuario y guardar en DB."""
    db = await get_db()
    try:
        user = await db.execute("SELECT * FROM users WHERE id = ?", (req.user_id,))
        user = await user.fetchone()
        if not user:
            raise HTTPException(404, "Usuario no encontrado")

        birth_dt = f"{user['birth_date']} {user['birth_time']}"
        result = calculate_natal_chart(birth_dt, user["birth_city"], name=user["name"])

        # Guardar carta natal en DB
        await db.execute(
            """INSERT OR REPLACE INTO natal_charts (user_id, chart_data_json, prompt_text)
               VALUES (?, ?, ?)""",
            (req.user_id, json.dumps(result["planets"], default=str, ensure_ascii=False),
             result["prompt_text"]),
        )
        await db.commit()
        return {"status": "ok", "natal_chart": result}
    finally:
        await db.close()


@router.get("/{user_id}")
async def get_natal(user_id: int):
    """Obtener carta natal guardada de un usuario."""
    db = await get_db()
    try:
        row = await db.execute("SELECT * FROM natal_charts WHERE user_id = ?", (user_id,))
        row = await row.fetchone()
        if not row:
            raise HTTPException(404, "Carta natal no encontrada. Calcula primero con POST /natal/calculate")
        return dict(row)
    finally:
        await db.close()
