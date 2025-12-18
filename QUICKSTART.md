# 🚀 Guía de Inicio Rápido

## Pasos para ejecutar el proyecto en 10 minutos

### 1️⃣ Clonar/Descargar el Proyecto
```bash
# Si tienes git
git clone <tu-repo>
cd asistente-voz-hibrido

# O simplemente extrae los archivos en una carpeta
```

### 2️⃣ Crear Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3️⃣ Instalar Dependencias
```bash
# Instalar paquetes Python
pip install -r requirements.txt

# En Ubuntu/Debian, instalar también:
sudo apt-get install portaudio19-dev python3-pyaudio
```

### 4️⃣ Descargar Modelos

**Modelo Vosk (STT) - 42 MB:**
```bash
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip
unzip vosk-model-small-es-0.42.zip
cd ..
```

**Modelo Piper (TTS):**
```bash
mkdir -p models/piper
cd models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json

curl -L -o es_ES-sharvard-medium.onnx \
https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx

curl -L -o es_ES-sharvard-medium.onnx.json \
https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json

cd ../..
```

### 5️⃣ Configurar API de Gemini

1. **Obtener API Key:**
   - Ve a: https://makersuite.google.com/app/apikey
   - Crea una nueva clave API (es gratis)

2. **Configurar el archivo .env:**
```bash
cp .env.example .env
nano .env  # O usa tu editor favorito
```

3. **Editar y guardar:**
```env
GEMINI_API_KEY=AIzaSy...tu_clave_real_aqui
```

### 6️⃣ Verificar Instalación
```bash
python check_system.py
```

Deberías ver:
```
✅ Python 3.8+
✅ Módulo 'pyaudio' instalado
✅ Módulo 'vosk' instalado
✅ Comando 'piper' disponible
✅ GEMINI_API_KEY configurada
✅ Modelo Vosk
✅ Modelo Piper
```

### 7️⃣ ¡Ejecutar!
```bash
python main.py
```

## 🎤 Cómo Usar

1. **Espera** el mensaje de bienvenida
2. **Habla** naturalmente en español
3. **Interrumpe** en cualquier momento si quieres
4. La conversación dura **5 minutos** por defecto

## 🐛 Problemas Comunes

### "No module named 'pyaudio'"
```bash
# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio

# macOS
brew install portaudio
pip install pyaudio
```

### "Piper command not found"
```bash
pip uninstall piper-tts
pip install piper-tts
```

### "GEMINI_API_KEY no configurada"
```bash
# Verifica que el archivo .env existe y contiene tu clave
cat .env
```

### Audio no funciona (WSL/Linux)
```bash
pulseaudio --start
```

## ⚡ Pruebas Individuales

Prueba cada componente por separado:

```bash
# Solo STT (escucha tu voz)
python stt_vosk.py

# Solo TTS (habla un texto)
python tts_piper.py

# Solo LLM (conversa por texto)
python llm_gemini.py
```

## 📝 Personalización Rápida

### Cambiar duración de conversación:
Edita `main.py`, línea ~150:
```python
assistant = HybridVoiceAssistant(conversation_duration=600)  # 10 minutos
```

### Cambiar personalidad:
Edita `config.py`, modifica `SYSTEM_INSTRUCTION`

### Usar otra voz:
Descarga otra voz de Piper y actualiza `PIPER_MODEL_PATH` en `.env`

## 🎯 Siguiente Paso

Una vez que funcione, puedes:
- Añadir efectos visuales para las emociones
- Integrar con hardware (Arduino, LED, pantallas)
- Crear una interfaz web
- Añadir más funcionalidades al LLM

## 📚 Documentación Completa

Lee `README.md` para documentación detallada.

---

**¿Problemas?** Revisa el README.md o ejecuta `python check_system.py`
