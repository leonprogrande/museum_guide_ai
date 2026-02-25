# Museum Guide Assistant (Base)

Asistente base por voz para museo:

1. Escucha continuamente.
2. Se activa con la frase: `Ey asistente`.
3. Captura el comando hasta detectar 1 segundo de silencio.
4. Transcribe audio a texto (STT).
5. Envía la pregunta a Gemini con instrucciones de guía de museo.
6. Muestra en terminal la pregunta y la respuesta.

## Requisitos

- Python 3.10+
- Micrófono funcionando
- API key de Gemini

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Si falla `PyAudio` en Windows, instala primero ruedas precompiladas o usa:

```bash
pip install pipwin
pipwin install pyaudio
```

## Configuración

1. Copia `.env.example` a `.env`.
2. Coloca tu key:

```env
GEMINI_API_KEY=tu_api_key
```

## Ejecutar

```bash
python main.py
```

## Notas

- Idioma STT configurado en `es-ES`.
- Wake phrase en código: `ey asistente`.
- Modelo Gemini en código: `gemini-1.5-flash`.
