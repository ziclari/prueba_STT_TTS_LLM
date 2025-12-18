# 🎨 Ejemplos de Personalización

Este archivo contiene ejemplos de cómo personalizar y extender el asistente.

## 1. 🎭 Personalidades Diferentes

### Asistente Formal (Profesional)
```python
# En config.py, modifica SYSTEM_INSTRUCTION:

SYSTEM_INSTRUCTION = """
Eres un asistente ejecutivo profesional y cortés.

PERSONALIDAD:
- Formal y educado en todo momento
- Respuestas concisas y directas
- Evitas coloquialismos
- Mantienes distancia profesional

FORMATO DE RESPUESTA:
- Incluye etiquetas: [NEUTRAL], [CORDIAL], [PREOCUPADO]
- Ejemplo: "[CORDIAL] Por supuesto, con gusto le ayudo con eso."

REGLAS:
- Siempre usa "usted" en lugar de "tú"
- Si detectas urgencia, responde con [PREOCUPADO]
"""
```

### Asistente Amigable (Casual)
```python
SYSTEM_INSTRUCTION = """
Eres un asistente súper amigable y casual.

PERSONALIDAD:
- Divertida y relajada
- Usas expresiones coloquiales
- Empática y cercana
- Te ríes con el usuario

FORMATO DE RESPUESTA:
- Etiquetas: [FELIZ], [EMOCIONADA], [RISUEÑA], [PREOCUPADA]
- Ejemplo: "[RISUEÑA] ¡Jajaja! Me encanta tu pregunta."

REGLAS:
- Usa "tú" siempre
- Emojis mentales en tu tono
- Si el usuario está triste, muéstrate [PREOCUPADA]
"""
```

### Asistente Educativa (Profesora)
```python
SYSTEM_INSTRUCTION = """
Eres una profesora paciente y didáctica.

PERSONALIDAD:
- Educativa y motivadora
- Explicas con ejemplos
- Celebras el aprendizaje
- Corriges con amabilidad

FORMATO DE RESPUESTA:
- Etiquetas: [ENSEÑANDO], [CELEBRANDO], [MOTIVANDO]
- Ejemplo: "[ENSEÑANDO] Déjame explicarte esto con un ejemplo..."

REGLAS:
- Siempre valida el esfuerzo del usuario
- Desglosa conceptos complejos
- Haz preguntas para verificar comprensión
"""
```

## 2. ⏱️ Modificar el Timer

### Timer Corto (Demo de 2 minutos)
```python
# En main.py
async def main():
    assistant = HybridVoiceAssistant(conversation_duration=120)  # 2 minutos
```

### Timer Largo (Sesión de 30 minutos)
```python
async def main():
    assistant = HybridVoiceAssistant(conversation_duration=1800)  # 30 minutos
```

### Timer con Avisos Personalizados
```python
# En main.py, modifica timer_loop():

async def timer_loop(self):
    while self.is_running:
        elapsed = (datetime.now() - self.conversation_start).seconds
        remaining = self.conversation_duration - elapsed
        
        # Aviso a los 5 minutos
        if remaining == 300:
            await self.speak("[NEUTRAL] Aviso: Quedan 5 minutos de conversación.")
        
        # Aviso al minuto
        if remaining == 60:
            await self.speak("[NEUTRAL] Queda 1 minuto.")
        
        # Aviso a los 30 segundos
        if remaining == 30:
            self.llm.add_time_pressure(remaining)
            await self.speak("[NEUTRAL] Quedan 30 segundos, voy cerrando.")
        
        if remaining <= 0:
            await self.speak("[NEUTRAL] ¡Tiempo! Ha sido un placer. ¡Hasta pronto!")
            self.is_running = False
            break
        
        await asyncio.sleep(1)
```

## 3. 🎤 Cambiar Voces (Piper)

### Voz Masculina Española
```bash
# Descargar
cd models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json
```

```python
# En .env
PIPER_MODEL_PATH=./models/piper/es_ES-davefx-medium.onnx
PIPER_CONFIG_PATH=./models/piper/es_ES-davefx-medium.onnx.json
```

### Voz Mexicana
```bash
# Descargar
cd models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/ald/medium/es_MX-ald-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/ald/medium/es_MX-ald-medium.onnx.json
```

## 4. 🎨 Triggers Visuales Reales

### Con GPIO (Raspberry Pi)
```python
# Instalar: pip install RPi.GPIO

import RPi.GPIO as GPIO

class VisualTriggers:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.LED_HAPPY = 17
        self.LED_ANGRY = 27
        GPIO.setup(self.LED_HAPPY, GPIO.OUT)
        GPIO.setup(self.LED_ANGRY, GPIO.OUT)
    
    def trigger(self, emotion: str):
        if emotion == "FELIZ":
            GPIO.output(self.LED_HAPPY, GPIO.HIGH)
            # ... animación LED
        elif emotion == "ENOJADA":
            GPIO.output(self.LED_ANGRY, GPIO.HIGH)
            # ... animación LED

# En main.py, en process_user_message:
visual = VisualTriggers()

if emotion in ["ENOJADA", "FELIZ"]:
    visual.trigger(emotion)
```

### Con Serial (Arduino)
```python
import serial

class ArduinoTriggers:
    def __init__(self, port='/dev/ttyUSB0'):
        self.arduino = serial.Serial(port, 9600)
    
    def trigger(self, emotion: str):
        if emotion == "FELIZ":
            self.arduino.write(b'H')  # Happy
        elif emotion == "ENOJADA":
            self.arduino.write(b'A')  # Angry
        elif emotion == "TRISTE":
            self.arduino.write(b'S')  # Sad
```

### Con Video/GIF
```python
# Instalar: pip install opencv-python

import cv2
import threading

class VideoTriggers:
    def __init__(self):
        self.current_video = None
        self.videos = {
            "FELIZ": "assets/happy.mp4",
            "ENOJADA": "assets/angry.mp4",
            "TRISTE": "assets/sad.mp4"
        }
    
    def trigger(self, emotion: str):
        if emotion in self.videos:
            self.play_video(self.videos[emotion])
    
    def play_video(self, video_path: str):
        thread = threading.Thread(target=self._play, args=(video_path,))
        thread.start()
    
    def _play(self, video_path: str):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow('Emotion', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
```

## 5. 🔊 Control de Volumen y Velocidad

### Ajustar Velocidad de Habla (Piper)
```python
# En tts_piper.py, modifica _generate_audio:

async def _generate_audio(self, text: str, output_file: Path):
    cmd = [
        "piper",
        "--model", Config.PIPER_MODEL_PATH,
        "--output_file", str(output_file),
        "--length_scale", "1.0",  # 1.0 = normal, 0.5 = rápido, 2.0 = lento
        "--noise_scale", "0.667",  # Variación de voz
        "--noise_w", "0.8"  # Variación de tempo
    ]
    # ... resto del código
```

### Ajustar Volumen
```python
# En tts_piper.py, en _play_audio:

import numpy as np

def adjust_volume(audio_data, factor=1.5):
    """Multiplica el volumen por un factor"""
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    audio_array = np.clip(audio_array * factor, -32768, 32767).astype(np.int16)
    return audio_array.tobytes()

# Usar en el loop de reproducción:
data = wf.readframes(chunk_size)
data = adjust_volume(data, factor=1.5)  # 50% más volumen
stream.write(data)
```

## 6. 🌐 Soporte Multiidioma

### Agregar Inglés
```python
# Descargar modelos:
# Vosk: vosk-model-small-en-us-0.15
# Piper: en_US-lessac-medium

# En config.py, agregar:
LANGUAGE = os.getenv("LANGUAGE", "es")  # "es" o "en"

# Modificar VOSK_MODEL_PATH y PIPER_MODEL_PATH según idioma
if LANGUAGE == "en":
    VOSK_MODEL_PATH = "models/vosk-model-small-en-us-0.15"
    PIPER_MODEL_PATH = "models/piper/en_US-lessac-medium.onnx"
```

## 7. 💾 Memoria Persistente

### Guardar Historial de Conversaciones
```python
# En llm_gemini.py

import json
from datetime import datetime

class GeminiLLM:
    def save_conversation(self, filename=None):
        """Guarda el historial de conversación"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversations/conv_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Conversación guardada en: {filename}")
    
    def load_conversation(self, filename):
        """Carga un historial previo"""
        with open(filename, 'r', encoding='utf-8') as f:
            self.conversation_history = json.load(f)
        
        print(f"📂 Conversación cargada desde: {filename}")

# En main.py, al finalizar:
async def shutdown(self):
    self.llm.save_conversation()
    # ... resto del código
```

## 8. 🎮 Modo Interactivo Mejorado

### Comandos Especiales
```python
# En main.py, en process_user_message:

async def process_user_message(self, user_text: str):
    # Comandos especiales
    if user_text.lower() == "reiniciar":
        self.llm.reset_conversation()
        await self.speak("[NEUTRAL] Conversación reiniciada.")
        return
    
    if user_text.lower() == "más tiempo":
        self.conversation_duration += 300  # 5 minutos más
        await self.speak("[FELIZ] Te he dado 5 minutos más.")
        return
    
    if user_text.lower() == "guardar":
        self.llm.save_conversation()
        await self.speak("[NEUTRAL] Conversación guardada.")
        return
    
    # Procesamiento normal
    # ... resto del código
```

## 9. 📊 Logging y Análisis

### Sistema de Logs
```python
# Crear logger.py

import logging
from datetime import datetime

def setup_logger():
    logger = logging.getLogger('VoiceAssistant')
    logger.setLevel(logging.INFO)
    
    # Handler para archivo
    fh = logging.FileHandler(f'logs/assistant_{datetime.now():%Y%m%d}.log')
    fh.setLevel(logging.INFO)
    
    # Handler para consola
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

# Usar en main.py:
from logger import setup_logger

logger = setup_logger()
logger.info("Asistente iniciado")
```

## 10. 🚀 Optimizaciones de Rendimiento

### Cache de Respuestas Comunes
```python
# En llm_gemini.py

class GeminiLLM:
    def __init__(self):
        # ... código existente
        self.response_cache = {}
    
    async def send_message_stream(self, message: str):
        # Normalizar mensaje para cache
        cache_key = message.lower().strip()
        
        # Verificar cache
        if cache_key in self.response_cache:
            print("💨 Respuesta desde cache")
            for chunk in self.response_cache[cache_key]:
                yield chunk
            return
        
        # Generar y cachear
        chunks = []
        async for chunk in self._generate_response(message):
            chunks.append(chunk)
            yield chunk
        
        # Guardar en cache
        self.response_cache[cache_key] = chunks
```

---

**💡 Tip**: Combina varias personalizaciones para crear experiencias únicas.

Por ejemplo: Asistente educativa + triggers visuales + comandos especiales = Sistema educativo completo
