"""
stt_vosk.py - Speech-to-Text usando Vosk
"""
import asyncio
import json
import queue
import pyaudio
from vosk import Model, KaldiRecognizer
from config import Config


class VoskSTT:
    """Clase para manejo de Speech-to-Text con Vosk"""
    
    def __init__(self):
        self.model = None
        self.recognizer = None
        self.audio = None
        self.stream = None
        self.is_listening = False
        self.text_queue = asyncio.Queue()
        
    def initialize(self):
        """Inicializa el modelo de Vosk y el stream de audio"""
        print(f"🎤 Cargando modelo Vosk desde: {Config.VOSK_MODEL_PATH}")
        
        try:
            self.model = Model(Config.VOSK_MODEL_PATH)
            self.recognizer = KaldiRecognizer(self.model, Config.SAMPLE_RATE)
            self.recognizer.SetWords(True)
            
            # Configurar PyAudio
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=Config.SAMPLE_RATE,
                input=True,
                frames_per_buffer=Config.AUDIO_CHUNK_SIZE
            )
            
            print("✅ Vosk inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al inicializar Vosk: {e}")
            print(f"💡 Descarga el modelo desde: https://alphacephei.com/vosk/models")
            print(f"   Extráelo en: {Config.MODELS_DIR}")
            return False
    
    async def listen_continuous(self, callback=None):
        """
        Escucha continuamente y envía transcripciones
        
        Args:
            callback: Función asíncrona a llamar cuando hay texto nuevo
        """
        self.is_listening = True
        print("👂 Escuchando... (Ctrl+C para detener)")
        
        try:
            while self.is_listening:
                # Leer datos de audio
                data = await asyncio.get_event_loop().run_in_executor(
                    None, self.stream.read, Config.AUDIO_CHUNK_SIZE, False
                )
                
                # Procesar con Vosk
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    
                    if text:
                        print(f"🗣️  Usuario: {text}")
                        
                        # Enviar a la cola
                        await self.text_queue.put(text)
                        
                        # Llamar callback si existe
                        if callback:
                            await callback(text)
                
                # Pequeña pausa para no saturar la CPU
                await asyncio.sleep(0.01)
                
        except Exception as e:
            print(f"❌ Error en escucha continua: {e}")
        finally:
            self.is_listening = False
    
    def stop_listening(self):
        """Detiene la escucha"""
        self.is_listening = False
        print("🛑 Escucha detenida")
    
    async def get_text(self):
        """Obtiene el siguiente texto transcrito de la cola"""
        return await self.text_queue.get()
    
    def cleanup(self):
        """Limpia recursos"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        print("🧹 Recursos de Vosk liberados")


# Ejemplo de uso
async def main():
    stt = VoskSTT()
    
    if not stt.initialize():
        return
    
    # Callback de ejemplo
    async def on_text(text):
        print(f"📝 Texto recibido: {text}")
    
    try:
        # Escuchar por 30 segundos
        listen_task = asyncio.create_task(stt.listen_continuous(callback=on_text))
        await asyncio.sleep(30)
        stt.stop_listening()
        await listen_task
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por usuario")
    finally:
        stt.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
