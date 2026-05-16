"""Servicio de cálculo de sinastría usando Stellium."""

from stellium import MultiChartBuilder


def calculate_synastry(
    natal_data_1: tuple[str, str],
    natal_data_2: tuple[str, str],
    name_1: str | None = None,
    name_2: str | None = None,
) -> dict:
    """
    Calcula la sinastría entre dos cartas natales.

    Args:
        natal_data_1: (datetime, city) de la persona 1
        natal_data_2: (datetime, city) de la persona 2
        name_1: Nombre opcional 1
        name_2: Nombre opcional 2

    Returns:
        dict con prompt_text y aspectos cruzados
    """
    synastry = MultiChartBuilder.synastry(
        person1_data=natal_data_1,
        person2_data=natal_data_2,
        name1=name_1,
        name2=name_2,
    ).calculate()

    # Extraer aspectos cruzados (Persona 1 vs Persona 2)
    cross_aspects = []
    if hasattr(synastry, "cross_aspects"):
        for a in synastry.cross_aspects:
            cross_aspects.append({
                "p1_planet": a.object1.name if hasattr(a, "object1") else str(a),
                "p2_planet": a.object2.name if hasattr(a, "object2") else str(a),
                "type": a.aspect_name if hasattr(a, "aspect_name") else str(a),
                "orb": round(a.orb, 2) if hasattr(a, "orb") else 0,
            })

    return {
        "prompt_text": synastry.to_prompt_text(),
        "cross_aspects": cross_aspects,
        "person1": name_1 or "Persona 1",
        "person2": name_2 or "Persona 2",
    }
