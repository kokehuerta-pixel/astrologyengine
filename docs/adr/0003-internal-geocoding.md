# 0003: Geocodificación Interna en Capa de Herramientas

- Estatus: aceptado
- Fecha: 2026-05-16
- Decisores: User, Antigravity

## Contexto y Problema

Para calcular la Carta Natal y los Tránsitos (basado en efemérides como Swiss Ephemeris), el motor matemático requiere coordenadas exactas: Latitud y Longitud (floats).
Sin embargo, los usuarios de `hermes-agent` se comunican en lenguaje natural (ej. "Nací en Madrid, España"). 

Necesitábamos decidir si delegar la responsabilidad de la resolución geográfica (Geocoding) al LLM / Framework del agente (requiriendo `lat` y `lon` en la firma de la herramienta) o encapsularla dentro de nuestras herramientas (aceptando un `str` como "Madrid").

## Drivers de Decisión

- Minimizar la carga cognitiva y las alucinaciones del LLM del agente.
- Simplificar el esquema de la herramienta (`function calling`) para aumentar el éxito de la llamada.
- Evitar que el agente deba hacer llamadas a múltiples herramientas encadenadas solo para obtener una lectura astrológica.

## Opciones Consideradas

- **Opción A (Externa):** Requerir `latitude` y `longitude` explícitamente en el Pydantic schema de la herramienta, confiando en que el agente lo resolverá por su cuenta.
- **Opción B (Interna):** Aceptar `birth_location: str` y usar `geopy` (u otra librería/API de geocoding) internamente dentro del código de la herramienta para obtener las coordenadas y pasarlas a la capa de servicios.

## Resultado de la Decisión

Opción elegida: **Opción B (Interna)**, porque una revisión del repositorio de `hermes-agent` no mostró un estándar nativo universal para resolución de ubicaciones para cálculos especializados. Encapsular el geocoding en nuestra herramienta garantiza precisión matemática para las efemérides y permite una firma de herramienta simple y amigable para el LLM.

### Consecuencias

- Positivas: La firma de la herramienta es muy fácil de usar para el agente. No hay riesgo de que el LLM invente coordenadas.
- Negativas: Añadimos una dependencia de red (ej. Nominatim API) dentro del flujo de ejecución de la herramienta local, lo que podría fallar si la API de geocoding tiene rate-limits.

## Pros y Contras de las Opciones

### Opción B (Elegida)
- Bueno, porque reduce los errores de *tool calling* drásticamente.
- Malo, porque requiere manejar timeouts o errores si el usuario ingresa un lugar que el geocoder no reconoce ("Nací en Narnia"). (Esto se mitigará devolviendo un error claro al agente para que pida aclaración al usuario).
