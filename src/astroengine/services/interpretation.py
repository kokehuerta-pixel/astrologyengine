"""Servicio de interpretación astrológica usando Gemini API."""

from google import genai
from ..config import settings


SYSTEM_PROMPT = """Eres un astrólogo profesional con profundo conocimiento de astrología occidental moderna y tradicional.

INSTRUCCIONES:
- Analiza los datos astrológicos proporcionados con precisión técnica.
- Cita posiciones exactas (grados, signos, casas).
- Identifica los tránsitos más relevantes del momento.
- Ofrece interpretación práctica y accionable.
- Tono: cálido, directo, sin esoterismo vacío.
- Idioma: {language}.
- IMPORTANTE: Debes seguir estrictamente la estructura solicitada según el nivel de profundidad ({depth}). No omitas ninguna sección.

ESTRUCTURA OBLIGATORIA DEL REPORTE ({depth}):
- BASIC: 
  ### Resumen General
  ### Tránsitos Clave del Día
  ### Consejo del Día

- COMPLETE: 
  ### Resumen General
  ### Tránsitos Clave del Día
  ### Análisis por Áreas (Amor, Trabajo, Salud, Finanzas)
  ### La Luna del Día
  ### Consejo del Día

- PROFESSIONAL: 
  ### Resumen General
  ### Análisis de Dignidades y Regencias
  ### Patrones de Aspectos y Configuración
  ### Análisis Detallado por Áreas
  ### Profecciones y Timing
  ### Guía de Acción Estelar
"""


async def generate_interpretation(
    natal_prompt_text: str,
    transit_prompt_text: str,
    depth: str = "complete",
    language: str = "es",
    model: str | None = None,
) -> str:
    """
    Genera interpretación astrológica personalizada usando Gemini.

    Args:
        natal_prompt_text: Texto de la carta natal (de Stellium)
        transit_prompt_text: Texto de los tránsitos (de Stellium)
        depth: Nivel de profundidad (basic, complete, professional)
        language: Idioma de la interpretación
        model: Modelo LLM a usar (None = usa el configurado)

    Returns:
        Texto de la interpretación generada
    """
    client = genai.Client(api_key=settings.gemini_api_key)
    model_name = model or settings.llm_model

    system = SYSTEM_PROMPT.format(language=language, depth=depth.upper())

    user_msg = f"""## CARTA NATAL DEL USUARIO
{natal_prompt_text}

## TRÁNSITOS ACTUALES
{transit_prompt_text}

Genera la interpretación astrológica personalizada en nivel {depth.upper()}."""

    response = await client.aio.models.generate_content(
        model=model_name,
        contents=user_msg,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.7,
        ),
    )
    return response.text
