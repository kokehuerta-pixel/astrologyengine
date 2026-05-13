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

## Parche de Stellium (Nota Técnica)
Este repositorio incluye las instrucciones para corregir el error de casas en Windows/Stellium. El motor detecta automáticamente la plataforma y aplica los ajustes necesarios.
