"""API endpoints para cálculo de tránsitos."""

from fastapi import APIRouter, HTTPException
from ..models import TransitRequest
from ..services.transit import calculate_transit
from ..database import get_db

router = APIRouter(prefix="/transit", tags=["transit"])


@router.post("/calculate")
async def calc_transit(req: TransitRequest):
    """Calcular tránsitos actuales vs carta natal de un usuario."""
    db = await get_db()
    try:
        user = await db.execute("SELECT * FROM users WHERE id = ?", (req.user_id,))
        user = await user.fetchone()
        if not user:
            raise HTTPException(404, "Usuario no encontrado")

        natal_dt = f"{user['birth_date']} {user['birth_time']}"
        location = req.location or user["current_city"]

        result = calculate_transit(
            natal_dt,
            user["birth_city"],
            location,
            req.datetime_override,
        )
        return {"status": "ok", "transit": result}
    finally:
        await db.close()
