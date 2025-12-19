"""
stt_whisper.py - Speech-to-Text usando Whisper (LOCAL - GRATIS)
✅ Sin costos de API
✅ Múltiples idiomas
✅ Alta precisión
⚠️ Requiere GPU para tiempo real (o CPU potente)
"""
import asyncio
import numpy as np
import pyaudio
import whisper
import torch
from collections import deque
from config import Config


class WhisperSTT:
    """Clase para manejo de Speech-to-Text con Whisper local"""
    
    def __init__(self, model_size="base"):
        """
        Args:
            model_size: tiny, base, small, medium, large
                       (tiny es más rápido, large más preciso)
        """
        self.model_size = model_size
        self.model = None
        self.audio = None
        self.stream = None
        self.is_listening = False
        self.text_queue = asyncio.Queue()
        
        # Buffer de audio
        self.audio_buffer = deque(maxlen=int(Config.SAMPLE_RATE * 5))  # 5 segundos
        self.silence_threshold = 500  # Ajustar según tu micrófono
        self.silence_duration = 1.5  # Segundos de silencio para procesar
        
    async def initialize(self):
        """Inicializa el modelo de Whisper y el stream de audio"""
        print(f"🎤 Cargando Whisper modelo '{self.model_size}'...")
        
        try:
            # Detectar si hay GPU disponible
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"🖥️  Usando: {device.upper()}")
            
            # Cargar modelo
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: setattr(self, 'model', whisper.load_model(self.model_size, device=device))
            )
            
            # Configurar PyAudio
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=Config.SAMPLE_RATE,
                input=True,
                frames_per_buffer=Config.AUDIO_CHUNK_SIZE
            )
            
            print("✅ Whisper inicializado correctamente")
            print(f"💡 Modelo: {self.model_size} | Device: {device}")
            return True
            
        except Exception as e:
            print(f"❌ Error al inicializar Whisper: {e}")
            print(f"💡 Instala: pip install openai-whisper")
            return False
    
    async def listen_continuous(self, callback=None):
        """
        Escucha continuamente y transcribe cuando detecta silencio
        
        Args:
            callback: Función asíncrona a llamar cuando hay texto nuevo
        """
        self.is_listening = True
        print("👂 Escuchando... (Ctrl+C para detener)")
        print("💡 Habla y haz una pausa para que procese")
        
        silence_chunks = 0
        speech_detected = False
        
        try:
            while self.is_listening:
                # Leer datos de audio
                data = await asyncio.get_event_loop().run_in_executor(
                    None, self.stream.read, Config.AUDIO_CHUNK_SIZE, False
                )
                
                # Convertir a numpy array
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Detectar si hay voz (volumen)
                volume = np.abs(audio_data).mean()
                
                if volume > self.silence_threshold:
                    speech_detected = True
                    silence_chunks = 0
                    self.audio_buffer.extend(audio_data)
                elif speech_detected:
                    silence_chunks += 1
                    self.audio_buffer.extend(audio_data)
                    
                    # Si hay suficiente silencio, procesar
                    silence_seconds = (silence_chunks * Config.AUDIO_CHUNK_SIZE) / Config.SAMPLE_RATE
                    
                    if silence_seconds >= self.silence_duration:
                        await self._process_audio_buffer(callback)
                        speech_detected = False
                        silence_chunks = 0
                        self.audio_buffer.clear()
                
                await asyncio.sleep(0.01)
                
        except Exception as e:
            print(f"❌ Error en escucha continua: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_listening = False
    
    async def _process_audio_buffer(self, callback=None):
        """Procesa el buffer de audio con Whisper"""
        if len(self.audio_buffer) == 0:
            return
        
        try:
            # Convertir buffer a array numpy
            audio_array = np.array(self.audio_buffer, dtype=np.int16)
            
            # Normalizar a float32 [-1, 1]
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Transcribir con Whisper
            print("🔄 Procesando audio...", end="\r")
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.transcribe(
                    audio_float,
                    language="es",  # Español
                    fp16=torch.cuda.is_available()
                )
            )
            
            text = result["text"].strip()
            
            if text:
                print(f"🗣️  Usuario: {text}")
                
                # Enviar a la cola
                await self.text_queue.put(text)
                
                # Llamar callback si existe
                if callback:
                    await callback(text)
            
        except Exception as e:
            print(f"❌ Error procesando audio: {e}")
    
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
        print("🧹 Recursos liberados")


# Ejemplo de uso
async def main():
    # tiny = más rápido, base = equilibrado, small/medium/large = más precisos
    stt = WhisperSTT(model_size="base")
    
    if not await stt.initialize():
        return
    
    async def on_text(text):
        print(f"📝 Texto recibido: {text}")
    
    try:
        listen_task = asyncio.create_task(stt.listen_continuous(callback=on_text))
        await asyncio.sleep(60)  # Escuchar 60 segundos
        stt.stop_listening()
        await listen_task
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por usuario")
    finally:
        stt.cleanup()


if __name__ == "__main__":
    asyncio.run(main())