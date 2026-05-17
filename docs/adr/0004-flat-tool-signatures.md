# 0004: Firmas de Herramientas Planas (Flat Tool Signatures)

- Estatus: aceptado
- Fecha: 2026-05-16
- Decisores: User, Antigravity

## Contexto y Problema

Al exponer `AstroEngine` como un conjunto de herramientas (tools) para `hermes-agent`, debemos definir la estructura de los parámetros que el modelo de lenguaje (LLM) del agente deberá generar en sus llamadas (function calling).

La API actual (REST) espera objetos anidados complejos, especialmente para procesos como la *Sinastría Natal* o el *Estado de Flujo Relacional*, donde se requiere enviar dos perfiles enteros (`profile_a` y `profile_b`) con sus respectivos atributos de fecha y lugar.

## Drivers de Decisión

- Evitar errores de sintaxis JSON o alucinaciones estructurales por parte del LLM.
- Hacer que la extracción de parámetros a partir de una conversación natural sea lo más directa posible para el agente.
- Aumentar la fiabilidad y tasa de éxito en cada invocación de las herramientas.

## Opciones Consideradas

- **Opción A (Objetos Complejos):** Mantener esquemas Pydantic anidados. El LLM tendría que generar un objeto con sub-objetos.
- **Opción B (Parámetros Planos):** Romper (aplanar) los atributos en parámetros simples de nivel superior (`str`).

## Resultado de la Decisión

Opción elegida: **Opción B (Parámetros Planos)**, porque la experiencia empírica con frameworks de agentes (como el de Nous Research) demuestra que los LLMs tienen mucho mejor rendimiento al poblar parámetros de primer nivel (`name_a`, `birth_date_a`) en lugar de construir diccionarios anidados. 

### Consecuencias

- Positivas: Reducción drástica de fallos de *parsing* durante el *function calling*.
- Negativas: Las firmas de funciones Python tendrán muchos argumentos (ej. 6 parámetros para sinastría en lugar de 2 objetos perfil).

## Pros y Contras de las Opciones

### Opción B (Elegida)
- Bueno, porque los LLMs pueden mapear entidades reconocidas en el chat directamente a variables individuales.
- Malo, porque requiere escribir código de "re-ensamblaje" dentro del wrapper de la herramienta para reconstruir los objetos de dominio antes de pasarlos a los servicios internos de `AstroEngine`.
