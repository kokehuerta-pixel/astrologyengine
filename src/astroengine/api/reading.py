"""API endpoints para lectura astrológica completa."""

from fastapi import APIRouter, HTTPException
from ..models import TransitRequest
from ..services.natal import calculate_natal_chart
from ..services.transit import calculate_transit
from ..services.interpretation import generate_interpretation
from ..database import get_db
import json

router = APIRouter(prefix="/reading", tags=["reading"])


@router.post("/generate")
async def generate_reading(req: TransitRequest):
    """Generar lectura astrológica completa: natal + tránsito + interpretación LLM."""
    db = await get_db()
    try:
        user = await db.execute("SELECT * FROM users WHERE id = ?", (req.user_id,))
        user = await user.fetchone()
        if not user:
            raise HTTPException(404, "Usuario no encontrado")

        natal_dt = f"{user['birth_date']} {user['birth_time']}"
        location = req.location or user["current_city"]

        # Calcular natal y tránsitos
        natal = calculate_natal_chart(natal_dt, user["birth_city"], name=user["name"])
        transit = calculate_transit(natal_dt, user["birth_city"], location, req.datetime_override)

        # Generar interpretación con LLM
        interpretation = await generate_interpretation(
            natal["prompt_text"],
            transit["prompt_text"],
            depth=user["report_depth"],
            language=user["language"],
            model=user["llm_model"],
        )

        # Guardar lectura en historial
        await db.execute(
            """INSERT INTO readings (user_id, reading_type, chart_data_json, interpretation, location_used)
               VALUES (?, ?, ?, ?, ?)""",
            (req.user_id, "daily_transit",
             json.dumps(transit["cross_aspects"], default=str, ensure_ascii=False),
             interpretation, location),
        )
        await db.commit()

        return {
            "status": "ok",
            "interpretation": interpretation,
            "natal_summary": natal["planets"][:10],
            "transit_aspects": transit["cross_aspects"][:15],
            "location": location,
            "transit_datetime": transit["transit_datetime"],
        }
    finally:
        await db.close()


@router.get("/direct")
async def quick_reading(
    name: str,
    birth_date: str,
    birth_time: str,
    birth_city: str,
    current_city: str,
    lang: str = "es",
    depth: str = "complete"
):
    """
    Endpoint de paso único diseñado para agentes (Hermes/Bots).
    Calcula natal, tránsito e interpretación sin necesidad de gestión previa de usuarios.
    """
    natal_dt = f"{birth_date} {birth_time}"
    try:
        # Calcular natal y tránsitos directamente
        natal = calculate_natal_chart(natal_dt, birth_city, name=name)
        transit = calculate_transit(natal_dt, birth_city, current_city)

        # Generar interpretación
        interpretation = await generate_interpretation(
            natal["prompt_text"],
            transit["prompt_text"],
            depth=depth,
            language=lang
        )

        return {
            "interpretation": interpretation,
            "metadata": {
                "name": name,
                "location": current_city,
                "transit_time": transit["transit_datetime"]
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Error en cálculo directo: {str(e)}")


@router.get("/history/{user_id}")
async def get_history(user_id: int, limit: int = 10):
    """Obtener historial de lecturas de un usuario."""
    db = await get_db()
    try:
        rows = await db.execute(
            "SELECT * FROM readings WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )
        rows = await rows.fetchall()
        return {"readings": [dict(r) for r in rows]}
    finally:
        await db.close()
