# 0001: Implementación de Sinastría Dinámica (Flujo Relacional)

- Estatus: aceptado
- Fecha: 2026-05-15
- Decisores: Antigravity, Usuario

## Contexto y Problema
La aplicación actualmente solo ofrece lecturas individuales de carta natal y tránsitos. Para ofrecer una experiencia de "Observatorio Digital" completa, se requiere una función que analice la relación entre dos personas. Sin embargo, una sinastría estática (natal vs natal) es insuficiente para predecir el estado actual de una relación influenciada por el cielo presente.

## Drivers de Decisión
- Precisión astrológica: Los tránsitos individuales afectan cómo las personas interactúan.
- Estética de ingeniería: El código debe ser modular y no romper la lógica existente de cálculos individuales.
- Escalabilidad: Preparar el motor para interpretaciones multi-agente.

## Opciones Consideradas
- **Opción 1**: Solo Sinastría Natal. (Simple, pero poco precisa para el "hoy").
- **Opción 2**: Sinastría Natal + Tránsitos combinados en un solo prompt. (Riesgo de pérdida de contexto en el LLM).
- **Opción 3**: Flujo de Agentes en Cadena (Estado de Flujo Relacional). Análisis por separado de tránsitos y síntesis final.

## Resultado de la Decisión
Opción elegida: **Opción 3**, porque proporciona la mayor precisión y permite al LLM enfocarse en sub-tareas específicas antes de dar una resolución global.

### Consecuencias
- Positivas: Resultados mucho más profundos y personalizados. Estructura de código más limpia y testeable.
- Negativas: Mayor consumo de tokens (múltiples llamadas a la API de Gemini) y ligero aumento en el tiempo de respuesta.

## Pros y Contras de las Opciones

### Opción 3 (Elegida)
- Bueno, porque separa las preocupaciones (separation of concerns).
- Malo, porque requiere una orquestación más compleja en el servicio de interpretación.
