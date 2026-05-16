"""API endpoints para Sinastría Dinámica."""

from fastapi import APIRouter, HTTPException
from ..models import SynastryRequest
from ..services.natal import calculate_natal_chart
from ..services.synastry import calculate_synastry
from ..services.transit import calculate_transit
from ..services.interpretation import generate_synastry_interpretation
from ..database import get_db
import json

router = APIRouter(prefix="/synastry", tags=["synastry"])


@router.post("/calculate")
async def calculate_dynamic_synastry(req: SynastryRequest):
    """
    Calcula Sinastría Dinámica (Estado de Flujo Relacional) entre dos personas.
    """
    db = await get_db()
    try:
        # 1. Obtener datos de la Persona 1 (siempre un usuario registrado)
        u1 = await db.execute("SELECT * FROM users WHERE id = ?", (req.user_id_1,))
        u1 = await u1.fetchone()
        if not u1:
            raise HTTPException(404, f"Usuario {req.user_id_1} no encontrado")

        # 2. Obtener datos de la Persona 2 (usuario o invitado)
        p2_data = {}
        if req.user_id_2:
            u2 = await db.execute("SELECT * FROM users WHERE id = ?", (req.user_id_2,))
            u2 = await u2.fetchone()
            if not u2:
                raise HTTPException(404, f"Usuario {req.user_id_2} no encontrado")
            p2_data = {
                "name": u2["name"],
                "birth_dt": f"{u2['birth_date']} {u2['birth_time']}",
                "birth_city": u2["birth_city"],
                "current_city": u2["current_city"]
            }
        elif req.guest_name and req.guest_birth_date:
            p2_data = {
                "name": req.guest_name,
                "birth_dt": f"{req.guest_birth_date} {req.guest_birth_time or '12:00'}",
                "birth_city": req.guest_birth_city or u1["current_city"],
                "current_city": req.guest_birth_city or u1["current_city"]
            }
        else:
            raise HTTPException(400, "Debe proporcionar user_id_2 o datos de invitado")

        # 3. Cálculos Astrológicos
        n1_dt = f"{u1['birth_date']} {u1['birth_time']}"
        loc1 = req.location_override or u1["current_city"]
        loc2 = p2_data["current_city"]

        # Sinastría Natal
        syn = calculate_synastry(
            (n1_dt, u1["birth_city"]),
            (p2_data["birth_dt"], p2_data["birth_city"]),
            name_1=u1["name"],
            name_2=p2_data["name"]
        )

        # Tránsitos Individuales (para ver cómo está cada uno hoy)
        t1 = calculate_transit(n1_dt, u1["birth_city"], loc1)
        t2 = calculate_transit(p2_data["birth_dt"], p2_data["birth_city"], loc2)

        # 4. Interpretación de la Resolución (Estado de Flujo Relacional)
        interpretation = await generate_synastry_interpretation(
            syn["prompt_text"],
            t1["prompt_text"],
            t2["prompt_text"],
            name1=u1["name"],
            name2=p2_data["name"],
            language=u1["language"]
        )

        # 5. Guardar en historial (opcional, pero recomendado)
        await db.execute(
            """INSERT INTO readings (user_id, reading_type, chart_data_json, interpretation, location_used)
               VALUES (?, ?, ?, ?, ?)""",
            (u1["id"], "dynamic_synastry",
             json.dumps({"partner": p2_data["name"]}, ensure_ascii=False),
             interpretation, loc1),
        )
        await db.commit()

        return {
            "status": "ok",
            "resolution": interpretation,
            "synastry_aspects": syn["cross_aspects"][:20],
            "p1_name": u1["name"],
            "p2_name": p2_data["name"]
        }

    finally:
        await db.close()
