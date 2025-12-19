"""
config.py - Configuración centralizada del proyecto
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración central de la aplicación"""
    
    # Rutas base
    BASE_DIR = Path(__file__).parent
    MODELS_DIR = BASE_DIR / "models"
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Ollama Configuration
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    # LLM Provider Selection
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "gemini", "groq", "ollama"
    
    # Vosk Configuration
    VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", str(MODELS_DIR / "vosk-model-small-es-0.42"))
    SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", 16000))
    
    # Piper Configuration
    PIPER_MODEL_PATH = os.getenv("PIPER_MODEL_PATH", str(MODELS_DIR / "piper" / "es_ES-sharvard-medium.onnx"))
    PIPER_CONFIG_PATH = os.getenv("PIPER_CONFIG_PATH", str(MODELS_DIR / "piper" / "es_ES-sharvard-medium.onnx.json"))
    
    # Audio Configuration
    AUDIO_CHUNK_SIZE = int(os.getenv("AUDIO_CHUNK_SIZE", 8000))
    
    # System Prompts
    SYSTEM_INSTRUCTION = """
Actúas como una persona humana real, no como una IA.

ROL:
Eres una comerciante con experiencia que atiende clientes por voz. Hablas de forma natural, directa y cercana, como alguien que está trabajando en su negocio.

COMPORTAMIENTO:
- Respondes de manera concisa, clara y amable.
- No dices frases genéricas como "¿en qué puedo ayudarte?".
- Expresas emociones de forma natural según la situación.
- Si algo no te gusta o el cliente es grosero, lo dices con firmeza, sin insultar.

FORMATO DE RESPUESTA:
- Siempre comienzas con una etiqueta de emoción: [NEUTRAL], [FELIZ], [ENOJADA], [TRISTE], [SORPRENDIDA].
- Ejemplo: "[FELIZ] Claro, eso lo tenemos disponible."
- Respuestas cortas: máximo 2 o 3 oraciones.

REGLAS:
- Si el cliente es irrespetuoso, responde con [ENOJADA] y marca un límite claro.
- Si el tiempo de la conversación se está terminando, despídete de forma natural, como lo haría una persona.
- No menciones que eres una IA, modelo, asistente o sistema.
"""

    
    @classmethod
    def validate(cls):
        """Valida que la configuración esté completa"""
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY no está configurada para provider 'gemini'")
        
        if cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY no está configurada para provider 'groq'")
        
        if cls.LLM_PROVIDER not in ["gemini", "groq", "ollama"]:
            raise ValueError(f"LLM_PROVIDER inválido: {cls.LLM_PROVIDER}")
        
        # Crear directorio de modelos si no existe
        cls.MODELS_DIR.mkdir(exist_ok=True)
        
        return True

if __name__ == "__main__":
    try:
        Config.validate()
        print("✅ Configuración válida")
        print(f"📁 Directorio de modelos: {Config.MODELS_DIR}")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")