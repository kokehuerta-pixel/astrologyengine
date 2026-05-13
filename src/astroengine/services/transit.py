"""Servicio de cálculo de tránsitos usando Stellium."""

from datetime import datetime, timezone
from stellium import MultiChartBuilder


def calculate_transit(
    natal_datetime: str,
    natal_city: str,
    transit_city: str,
    transit_datetime: str | None = None,
) -> dict:
    """
    Calcula tránsitos actuales vs carta natal.

    Args:
        natal_datetime: "1996-06-20 14:00"
        natal_city: "Rancagua, Chile"
        transit_city: "Rancagua, Chile"
        transit_datetime: Opcional, "2026-05-13 14:00". Si None, usa ahora.

    Returns:
        dict con prompt_text y aspectos cruzados
    """
    if transit_datetime is None:
        now = datetime.now(timezone.utc)
        transit_datetime = now.strftime("%Y-%m-%d %H:%M")

    transit = MultiChartBuilder.transit(
        natal_data=(natal_datetime, natal_city),
        transit_data=(transit_datetime, transit_city),
    ).calculate()

    # Extraer aspectos cruzados (natal vs tránsito)
    cross_aspects = []
    if hasattr(transit, "cross_aspects"):
        for a in transit.cross_aspects:
            cross_aspects.append({
                "natal_planet": a.object1.name if hasattr(a, "object1") else str(a),
                "transit_planet": a.object2.name if hasattr(a, "object2") else str(a),
                "type": a.aspect_name if hasattr(a, "aspect_name") else str(a),
                "orb": round(a.orb, 2) if hasattr(a, "orb") else 0,
            })
    elif hasattr(transit, "aspects"):
        for a in transit.aspects:
            cross_aspects.append({
                "natal_planet": a.object1.name if hasattr(a, "object1") else str(a),
                "transit_planet": a.object2.name if hasattr(a, "object2") else str(a),
                "type": a.aspect_name if hasattr(a, "aspect_name") else str(a),
                "orb": round(a.orb, 2) if hasattr(a, "orb") else 0,
            })

    return {
        "prompt_text": transit.to_prompt_text(),
        "cross_aspects": cross_aspects,
        "transit_datetime": transit_datetime,
        "transit_location": transit_city,
    }
