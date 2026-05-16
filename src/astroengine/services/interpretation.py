"""Servicio de interpretacion astrologica usando Gemini API."""

from google import genai
from ..config import settings


SYSTEM_PROMPT = """Eres un astrologo profesional con profundo conocimiento de astrologia occidental moderna y tradicional.

INSTRUCCIONES:
- Analiza los datos astrologicos proporcionados con precision tecnica.
- Cita posiciones exactas (grados, signos, casas).
- Identifica los transitos mas relevantes del momento.
- Ofrece interpretacion practica y accionable.
- Tono: calido, directo, sin esoterismo vacio.
- Idioma: {language}.
- IMPORTANTE: Debes seguir estrictamente la estructura solicitada segun el nivel de profundidad ({depth}). NO omitas ninguna seccion marcada como obligatoria.

ESTRUCTURA OBLIGATORIA DEL REPORTE ({depth}):

- BASIC (Breve): 
  ### Resumen General
  ### Transitos Clave del Dia
  ### Consejo del Dia

- COMPLETE (Completo): 
  ### Resumen General
  ### Transitos Clave del Dia
  ### Analisis por Areas (Obligatorio: incluir Amor, Trabajo, Salud, Finanzas)
  ### La Luna del Dia
  ### Consejo del Dia

- PROFESSIONAL (Profesional): 
  ### Resumen General
  ### Analisis de Dignidades y Regencias
  ### Patrones de Aspectos y Configuracion
  ### Analisis Detallado por Areas (Obligatorio: Amor, Trabajo, Salud, Finanzas, Evolucion Personal)
  ### Profecciones y Timing
  ### Guia de Accion Estelar
"""

SYNASTRY_SYSTEM_PROMPT = """Eres el Maestro del Observatorio Digital, experto en Sinastria y Astrologia Dinamica.

INSTRUCCIONES:
- Analiza la relacion entre {name1} y {name2}.
- Integra tres niveles de analisis:
    1. Sinastria Natal: La base estructural de la relacion.
    2. Clima Astrologico Individual: Como estan viviendo sus transitos personales en sus respectivas ubicaciones.
    3. Estado de Flujo Relacional: Como el cielo de hoy activa o tensiona la relacion.
- Tono: Mistico pero tecnico, premium, revelador.
- Idioma: {language}.

ESTRUCTURA OBLIGATORIA DEL REPORTE DE RESOLUCION:

### Alquimia de Almas (Base Natal)
- Describe la compatibilidad fundamental.

### El Cielo de Hoy para Ambos
- Resumen de los transitos mas fuertes para cada uno.

### Estado de Flujo Relacional
- Como les afecta el presente a su interaccion? (Puntos de friccion o armonia temporal).

### Guia de Accion en Pareja
- Recomendaciones concretas para navegar las proximas 24-48 horas.

### Veredicto del Observatorio
- Una frase final contundente sobre la energia actual de la union.
"""


async def generate_interpretation(
    natal_prompt_text: str,
    transit_prompt_text: str,
    depth: str = "complete",
    language: str = "es",
    model: str | None = None,
) -> str:
    """
    Genera interpretacion astrologica personalizada usando Gemini.
    """
    client = genai.Client(api_key=settings.gemini_api_key)
    model_name = model or settings.llm_model

    system = SYSTEM_PROMPT.format(language=language, depth=depth.upper())

    user_msg = f"""## CARTA NATAL DEL USUARIO
{natal_prompt_text}

## TRANSITOS ACTUALES
{transit_prompt_text}

Genera la interpretacion astrologica personalizada en nivel {depth.upper()}."""

    response = await client.aio.models.generate_content(
        model=model_name,
        contents=user_msg,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.7,
        ),
    )
    return response.text


async def generate_synastry_interpretation(
    synastry_prompt_text: str,
    p1_transit_prompt: str,
    p2_transit_prompt: str,
    name1: str,
    name2: str,
    language: str = "es",
    model: str | None = None,
) -> str:
    """
    Genera la interpretacion de Sinastria Dinamica (Estado de Flujo Relacional).
    """
    client = genai.Client(api_key=settings.gemini_api_key)
    model_name = model or settings.llm_model

    system = SYNASTRY_SYSTEM_PROMPT.format(
        name1=name1, 
        name2=name2, 
        language=language
    )

    user_msg = f"""## DATOS DE SINASTRIA NATAL
{synastry_prompt_text}

## TRANSITOS ACTUALES - {name1}
{p1_transit_prompt}

## TRANSITOS ACTUALES - {name2}
{p2_transit_prompt}

Genera la Resolucion del Observatorio para el Estado de Flujo Relacional entre {name1} y {name2}."""

    response = await client.aio.models.generate_content(
        model=model_name,
        contents=user_msg,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.8,
        ),
    )
    return response.text
