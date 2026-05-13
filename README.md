# AstrologyEngine 🔮

Motor de cálculo astrológico de alto rendimiento con Stellium (Swiss Ephemeris) e interpretación mediante Gemini AI. Diseñado como una PWA (Progressive Web App) instalable y ligera.

## Características
- **Cálculo de Carta Natal**: Posiciones planetarias precisas (20+ cuerpos) usando Swiss Ephemeris.
- **Análisis de Tránsitos**: Comparativa en tiempo real entre la carta natal y la ubicación actual.
- **Interpretación con IA**: Reportes detallados generados por Google Gemini.
- **PWA Instalable**: Interfaz moderna, oscura y optimizada para móviles.
- **API Backend**: Construido con FastAPI y SQLite.

## Instalación en Hermes/VPS

1. **Clonar el repo**:
   ```bash
   git clone https://github.com/kokehuerta-pixel/astrologyengine
   cd astrologyengine
   ```

2. **Configurar el entorno**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Variables de Entorno**:
   Crea un archivo `.env` con tu API Key:
   ```env
   GEMINI_API_KEY=tu_clave_aqui
   ```

4. **Ejecutar**:
   ```bash
   python -m uvicorn src.astroengine.main:app --host 0.0.0.0 --port 8000
   ```

## Flujo de Uso

Para obtener una predicción exacta, el sistema sigue este orden:

1. **Configuración de Perfil**: Ingresa tu nombre, fecha, hora y ciudad de nacimiento. También define tu ciudad actual.
2. **Cálculo de Carta Natal**: Al guardar el perfil, la app calcula automáticamente tu carta natal (puntos base fijos). Sin este paso, no hay referencia para contrastar los tránsitos.
3. **Generación de Lectura**: Presiona "Generar Lectura del Momento". El sistema contrastará tu carta natal guardada con los tránsitos planetarios actuales en tu ubicación y generará un reporte vía IA.

## Nota Técnica (Stellium)
Este motor utiliza `pysweph` bajo el capó. En Windows, se ha implementado un ajuste automático para el sistema de casas para evitar errores de librería C. El sistema de base de datos es SQLite, ligero y persistente.

---
*Desarrollado para la comunidad de astrología open source.*
