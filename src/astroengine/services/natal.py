"""Servicio de cálculo de carta natal usando Stellium."""

import json
from stellium import ChartBuilder


def calculate_natal_chart(
    birth_datetime: str,
    birth_city: str,
    name: str | None = None,
) -> dict:
    """
    Calcula carta natal completa.

    Args:
        birth_datetime: "1996-06-20 14:00"
        birth_city: "Rancagua, Chile"
        name: Nombre opcional de la persona

    Returns:
        dict con prompt_text, posiciones planetarias y aspectos
    """
    builder = ChartBuilder.from_details(
        birth_datetime,
        birth_city,
        name=name,
    )
    chart = builder.calculate()

    # Extraer posiciones planetarias
    planets = []
    for p in chart.positions:
        planets.append({
            "name": p.name,
            "sign": _sign_from_longitude(p.longitude),
            "longitude": round(p.longitude, 4),
            "retrograde": getattr(p, "is_retrograde", False),
            "object_type": p.object_type.value if hasattr(p.object_type, "value") else str(p.object_type),
        })

    # Extraer aspectos
    aspects = []
    if hasattr(chart, "aspects"):
        for a in chart.aspects:
            aspects.append({
                "planet1": a.object1.name if hasattr(a, "object1") else str(a),
                "planet2": a.object2.name if hasattr(a, "object2") else str(a),
                "type": a.aspect_name if hasattr(a, "aspect_name") else str(a),
                "orb": round(a.orb, 2) if hasattr(a, "orb") else 0,
            })

    return {
        "prompt_text": chart.to_prompt_text(),
        "planets": planets,
        "aspects": aspects,
    }


def _sign_from_longitude(longitude: float) -> str:
    """Convierte longitud eclíptica a signo zodiacal."""
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]
    index = int(longitude / 30) % 12
    return signs[index]
