# 0002: Integración Nativa con Hermes Agent vía Python Tools

- Estatus: aceptado
- Fecha: 2026-05-16
- Decisores: User, Antigravity

## Contexto y Problema

El proyecto `AstroEngine` fue concebido inicialmente como una API web (FastAPI). Sin embargo, necesitamos que funcione de forma nativa dentro de [hermes-agent](https://github.com/NousResearch/hermes-agent), un framework de agentes autónomos desarrollado por Nous Research. 

El problema radica en cómo exponer los cálculos matemáticos (efemérides) y la IA de interpretación (Resolución de Observatorio) para que el LLM del agente pueda descubrirlos, comprenderlos e invocarlos de la manera más fluida y autónoma posible.

## Drivers de Decisión

- Minimizar la sobrecarga de red y la complejidad de despliegue (evitar tener que levantar servidores secundarios como MCP o FastAPI solo para el agente).
- Maximizar la comprensión del LLM sobre qué hace cada herramienta.
- Compatibilidad con el ecosistema Python de `hermes-agent` (que utiliza representaciones de herramientas como `agentskills.io` o *function calling* con esquemas de Pydantic).

## Opciones Consideradas

- **Opción 1: Python Tool Registry (Pydantic Wrappers):** Exponer los servicios internos como funciones puras de Python con esquemas estrictos de entrada/salida y docstrings ricos, listas para ser inyectadas en el entorno del agente.
- **Opción 2: Model Context Protocol (MCP) Server:** Crear un servidor MCP que actúe como middleware.
- **Opción 3: Consumo de OpenAPI Spec:** Proveer un archivo swagger y obligar al agente a hacer llamadas HTTP.

## Resultado de la Decisión

Opción elegida: **Opción 1 (Python Tool Registry)**, porque elimina la necesidad de procesos intermedios, permite una integración real de código (el agente importa la librería directamente) y facilita la validación de tipos a través de Pydantic, lo cual es el estándar de oro para *function calling* en LLMs actuales.

### Consecuencias

- Positivas: Menor latencia, integración transparente, fuertemente tipado.
- Negativas: Acopla parcialmente la firma de nuestras funciones a los estándares que espera la capa de herramientas del framework de Python subyacente.

## Pros y Contras de las Opciones

### Opción 1: Python Tool Registry
- Bueno, porque aprovecha que tanto el motor como el agente están en Python.
- Bueno, porque Pydantic es el formato preferido por la mayoría de LLMs para generar llamadas a funciones.
- Malo, porque no es agnóstico del lenguaje (no funcionaría si el agente estuviera en TypeScript, a diferencia de MCP).

### Opción 2: MCP Server
- Bueno, porque es un estándar abierto y agnóstico del framework.
- Malo, porque añade la sobrecarga de un servidor adicional y serialización JSON-RPC, lo cual es excesivo si el agente corre en el mismo entorno Python.
