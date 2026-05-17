"""
Herramientas (Agent Tools) para Hermes-Agent.
Expone la funcionalidad astrológica en formato plano (flat arguments)
y manejando ubicaciones como cadenas de texto (Geocoding interno).
"""

from astroengine.services.natal import calculate_natal_chart
from astroengine.services.transit import calculate_transit
from astroengine.services.synastry import calculate_synastry
from astroengine.services.interpretation import generate_reading
from typing import Optional


def tool_get_natal_reading(
    birth_date_time: str,
    birth_location: str,
    name: Optional[str] = None
) -> str:
    """
    Genera una lectura completa de la Carta Natal de una persona.
    Usa esto cuando el usuario quiera conocer sobre su personalidad, compatibilidad básica, 
    destinos o tendencias psicológicas de nacimiento.

    Args:
        birth_date_time: Fecha y hora de nacimiento exacta en formato "YYYY-MM-DD HH:MM". Ejemplo: "1990-10-12 14:30".
        birth_location: Ciudad y país de nacimiento en texto plano. Ejemplo: "Madrid, España".
        name: Nombre de la persona (opcional, ayuda a personalizar la lectura).

    Returns:
        str: Interpretación astrológica detallada generada por IA.
    """
    try:
        # Geocoding y cálculo matemático (manejado internamente por Stellium en el servicio)
        chart_data = calculate_natal_chart(
            birth_datetime=birth_date_time,
            birth_city=birth_location,
            name=name
        )
        
        # Invocamos la interpretación de Gemini
        return generate_reading("natal", chart_data)
    except Exception as e:
        return f"Error calculando la carta natal: {str(e)}. Pídele al usuario que verifique la ciudad o el formato de fecha."


def tool_get_transit_reading(
    birth_date_time: str,
    birth_location: str,
    current_location: str,
    target_date_time: Optional[str] = None
) -> str:
    """
    Calcula los tránsitos astrológicos actuales respecto a la carta natal de la persona.
    Usa esto para predecir cómo se siente la persona hoy, dar horóscopos diarios o 
    responder a preguntas sobre el presente o futuro cercano.

    Args:
        birth_date_time: Fecha y hora de nacimiento en formato "YYYY-MM-DD HH:MM".
        birth_location: Ciudad y país de nacimiento. Ejemplo: "Bogotá, Colombia".
        current_location: Ubicación actual de la persona para calcular el tránsito. Ejemplo: "Miami, USA".
        target_date_time: Fecha y hora del momento a consultar (opcional, si no se envía usa el momento actual).

    Returns:
        str: Interpretación astrológica de los tránsitos y su impacto.
    """
    try:
        transit_data = calculate_transit(
            natal_datetime=birth_date_time,
            natal_city=birth_location,
            transit_city=current_location,
            transit_datetime=target_date_time
        )
        return generate_reading("transit", transit_data)
    except Exception as e:
        return f"Error calculando tránsitos: {str(e)}. Verifica que las ubicaciones sean reconocidas."


def tool_get_relational_flow_reading(
    person1_name: str,
    person1_birth_date_time: str,
    person1_birth_location: str,
    person2_name: str,
    person2_birth_date_time: str,
    person2_birth_location: str
) -> str:
    """
    Calcula la Sinastría Dinámica (Estado de Flujo Relacional) entre dos personas.
    Usa esto para analizar compatibilidad amorosa, relaciones laborales o resolución de 
    conflictos entre dos individuos. Mide cómo sus cartas chocan o se complementan.

    Args:
        person1_name: Nombre de la primera persona.
        person1_birth_date_time: Fecha/hora de nacimiento P1 ("YYYY-MM-DD HH:MM").
        person1_birth_location: Ciudad natal P1.
        person2_name: Nombre de la segunda persona.
        person2_birth_date_time: Fecha/hora de nacimiento P2 ("YYYY-MM-DD HH:MM").
        person2_birth_location: Ciudad natal P2.

    Returns:
        str: Interpretación sintética de la relación entre ambas personas.
    """
    try:
        synastry_data = calculate_synastry(
            natal_data_1=(person1_birth_date_time, person1_birth_location),
            natal_data_2=(person2_birth_date_time, person2_birth_location),
            name_1=person1_name,
            name_2=person2_name
        )
        return generate_reading("synastry", synastry_data)
    except Exception as e:
        return f"Error calculando la sinastría: {str(e)}. Verifica los datos de ambas personas."
