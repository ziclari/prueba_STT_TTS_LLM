# 🎙️ Asistente de Voz Híbrido - Modelo de Baja Latencia

Sistema de asistente de voz con arquitectura híbrida que combina procesamiento local (STT/TTS) con inteligencia en la nube (LLM).

## 📋 Características

- ✅ **STT Local (Vosk)**: Transcripción en tiempo real sin latencia de red
- ✅ **TTS Local (Piper)**: Síntesis de voz instantánea
- ✅ **LLM en Nube (Gemini)**: Inteligencia conversacional avanzada
- ✅ **Streaming & Pipelining**: Respuestas fluidas con chunking inteligente
- ✅ **Barge-in**: Interrupciones naturales mientras el asistente habla
- ✅ **Gestión de Emociones**: Detección y expresión de estados emocionales
- ✅ **Timer de Conversación**: Control automático del tiempo de sesión

## 🏗️ Arquitectura

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Usuario   │─────▶│  Vosk (STT)  │─────▶│   Gemini    │
│   (Audio)   │      │   (Local)    │      │    (LLM)    │
└─────────────┘      └──────────────┘      └─────────────┘
                                                   │
                                                   ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Speaker   │◀─────│ Piper (TTS)  │◀─────│  Chunking   │
│   (Audio)   │      │   (Local)    │      │  Pipeline   │
└─────────────┘      └──────────────┘      └─────────────┘
```

## 🚀 Instalación

### 1. Requisitos Previos

- Python 3.8+
- Sistema operativo: Linux, macOS, o Windows (con WSL recomendado)
- Micrófono y altavoces funcionales

### 2. Instalar Dependencias del Sistema

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio
```

#### macOS:
```bash
brew install portaudio
```

#### Windows (WSL):
```bash
sudo apt-get install -y portaudio19-dev python3-pyaudio pulseaudio
```

### 3. Crear Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 4. Instalar Paquetes Python

```bash
pip install -r requirements.txt
```

### 5. Descargar Modelos

#### Modelo Vosk (STT):
```bash
# Crear directorio de modelos
mkdir -p models

# Descargar modelo en español (42 MB)
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip
unzip vosk-model-small-es-0.42.zip
rm vosk-model-small-es-0.42.zip
cd ..
```

**Alternativas de modelos Vosk:**
- `vosk-model-es-0.42` (1.4 GB) - Mayor precisión
- `vosk-model-small-es-0.42` (42 MB) - Rápido, menor precisión

#### Modelo Piper (TTS):
```bash
# Crear directorio para Piper
mkdir -p models/piper

# Descargar modelo en español
cd models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json
cd ../..
```

**Alternativas de voces Piper:**
- `es_ES-sharvard-medium` - Voz femenina clara
- `es_ES-davefx-medium` - Voz masculina
- `es_MX-ald-medium` - Español mexicano

### 6. Configurar API de Gemini

1. Obtén una API key en: https://makersuite.google.com/app/apikey
2. Crea un archivo `.env` (copia desde `.env.example`):

```bash
cp .env.example .env
```

3. Edita el archivo `.env` y añade tu clave:

```env
GEMINI_API_KEY=tu_clave_api_aqui
```

## 🎮 Uso

### Ejecución Básica

```bash
python main.py
```

### Pruebas Individuales

Puedes probar cada componente por separado:

```bash
# Probar STT (Vosk)
python stt_vosk.py

# Probar TTS (Piper)
python tts_piper.py

# Probar LLM (Gemini)
python llm_gemini.py
```

## 🎛️ Configuración

Edita `config.py` o el archivo `.env` para ajustar:

- **Duración de conversación**: Modifica `conversation_duration` en `main.py`
- **Velocidad de muestreo**: Ajusta `SAMPLE_RATE` (16000 Hz por defecto)
- **Modelo de Vosk**: Cambia `VOSK_MODEL_PATH` al modelo deseado
- **Voz de Piper**: Cambia `PIPER_MODEL_PATH` a otra voz
- **Personalidad del asistente**: Edita `SYSTEM_INSTRUCTION` en `config.py`

## 🧪 Solución de Problemas

### Error: "GEMINI_API_KEY no configurada"
```bash
# Verifica que el archivo .env existe y contiene tu clave
cat .env
```

### Error: "Vosk model not found"
```bash
# Verifica que el modelo está en la ubicación correcta
ls -la models/vosk-model-small-es-0.42/
```

### Error: "Piper command not found"
```bash
# Reinstala piper-tts
pip uninstall piper-tts
pip install piper-tts
```

### Audio no funciona (Linux/WSL)
```bash
# Asegúrate de que PulseAudio está corriendo
pulseaudio --start

# Verifica dispositivos de audio
pactl list short sinks
pactl list short sources
```

### Latencia alta en TTS
- Prueba con un modelo de Piper más pequeño
- Verifica que no hay otros procesos consumiendo CPU
- Considera usar GPU si está disponible

## 📚 Estructura del Proyecto

```
.
├── config.py              # Configuración central
├── stt_vosk.py           # Módulo STT con Vosk
├── tts_piper.py          # Módulo TTS con Piper
├── llm_gemini.py         # Módulo LLM con Gemini
├── main.py               # Orquestador principal
├── requirements.txt      # Dependencias Python
├── .env.example          # Plantilla de configuración
└── models/               # Directorio de modelos
    ├── vosk-model-*/     # Modelos Vosk
    └── piper/            # Modelos Piper
```

## 🎯 Funcionalidades Implementadas

### ✅ Fase 1: Estructura de Velocidad
- [x] STT local con Vosk
- [x] TTS local con Piper
- [x] Baja latencia en ambos componentes

### ✅ Fase 2: Inteligencia y Concurrencia
- [x] Integración con Gemini API
- [x] Streaming de respuestas
- [x] Chunking inteligente por puntuación
- [x] Pipelining TTS

### ✅ Fase 3: Control y Emociones
- [x] Interrupción (barge-in)
- [x] Timer de conversación
- [x] Detección de emociones
- [x] Triggers visuales (marcadores)

## 🔮 Próximas Mejoras

- [ ] Implementar efectos visuales reales para emociones
- [ ] Añadir soporte para múltiples idiomas
- [ ] Optimización GPU para TTS (ONNX Runtime)
- [ ] Sistema de memoria conversacional persistente
- [ ] Interfaz web con WebSocket
- [ ] Reconocimiento de emociones en la voz del usuario

## 📝 Notas Importantes

1. **Privacidad**: El audio solo se procesa localmente (Vosk) o se envía a Google Cloud (Gemini). Revisa los términos de servicio de Gemini.

2. **Costos**: Gemini tiene un tier gratuito generoso, pero verifica los límites en la documentación oficial.

3. **Rendimiento**: 
   - CPU: Mínimo Intel i5 o equivalente
   - RAM: Mínimo 4 GB
   - Para mejor rendimiento, usa el modelo pequeño de Vosk

4. **Idiomas**: Esta implementación está optimizada para español. Para otros idiomas, descarga los modelos correspondientes de Vosk y Piper.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🙏 Agradecimientos

- **Vosk**: https://alphacephei.com/vosk/
- **Piper**: https://github.com/rhasspy/piper
- **Google Gemini**: https://ai.google.dev/
- **PyAudio**: https://people.csail.mit.edu/hubert/pyaudio/

---

**Desarrollado con ❤️ para demostraciones de IA conversacional de baja latencia**
