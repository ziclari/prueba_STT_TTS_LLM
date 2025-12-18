"""
tts_piper.py - Text-to-Speech usando Piper
"""
import asyncio
import subprocess
import wave
import pyaudio
from pathlib import Path
from config import Config


class PiperTTS:
    """Clase para manejo de Text-to-Speech con Piper"""
    
    def __init__(self):
        self.audio = None
        self.is_speaking = False
        self.current_process = None
        
    def initialize(self):
        """Inicializa Piper y PyAudio"""
        print("🔊 Inicializando Piper TTS...")
        
        try:
            # Verificar que piper está instalado
            result = subprocess.run(
                ["pip", "show", "piper-tts"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("❌ Piper no está instalado")
                print("💡 Instala con: pip install piper-tts")
                return False
            
            # Inicializar PyAudio para reproducción
            self.audio = pyaudio.PyAudio()
            
            print("✅ Piper TTS inicializado correctamente")
            return True
            
        except FileNotFoundError:
            print("❌ Comando 'piper' no encontrado")
            print("💡 Instala con: pip install piper-tts")
            return False
        except Exception as e:
            print(f"❌ Error al inicializar Piper: {e}")
            return False
    
    async def generate_and_play(self, text: str, emotion: str = "neutral"):
        """
        Genera audio con Piper y lo reproduce inmediatamente
        
        Args:
            text: Texto a sintetizar
            emotion: Emoción (para futura implementación con modelos específicos)
        """
        if not text.strip():
            return
        
        self.is_speaking = True
        temp_file = Path("./tmp/piper_output.wav")

        
        try:
            # Limpiar etiquetas de emoción del texto
            clean_text = self._clean_emotion_tags(text)
            
            print(f"🔊 Sintetizando: {clean_text[:50]}...")
            
            # Generar audio con Piper
            await self._generate_audio(clean_text, temp_file)
            
            # Reproducir el audio generado
            await self._play_audio(temp_file)
            
        except Exception as e:
            print(f"❌ Error en TTS: {e}")
        finally:
            self.is_speaking = False
            # Limpiar archivo temporal
            if temp_file.exists():
                temp_file.unlink()
    
    async def _generate_audio(self, text: str, output_file: Path):
        """Genera el archivo de audio usando Piper"""
        # Comando Piper
        cmd = [
            "piper",
            "--model", Config.PIPER_MODEL_PATH,
            "--output_file", str(output_file)
        ]
        
        # Ejecutar Piper
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        self.current_process = process
        
        # Enviar texto a Piper
        stdout, stderr = await process.communicate(input=text.encode())
        
        if process.returncode != 0:
            raise Exception(f"Piper falló: {stderr.decode()}")
    
    async def _play_audio(self, audio_file: Path):
        """Reproduce el archivo de audio"""
        # Leer archivo WAV
        wf = wave.open(str(audio_file), 'rb')
        
        # Abrir stream de PyAudio
        stream = self.audio.open(
            format=self.audio.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )
        
        # Reproducir en chunks
        chunk_size = 1024
        data = wf.readframes(chunk_size)
        
        while data and self.is_speaking:
            await asyncio.get_event_loop().run_in_executor(
                None, stream.write, data
            )
            data = wf.readframes(chunk_size)
        
        # Limpiar
        stream.stop_stream()
        stream.close()
        wf.close()
    
    def stop_speaking(self):
        """Detiene la reproducción actual"""
        self.is_speaking = False
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass
        print("🛑 Reproducción detenida")
    
    def _clean_emotion_tags(self, text: str) -> str:
        """Elimina etiquetas de emoción del texto"""
        import re
        # Eliminar etiquetas como [FELIZ], [ENOJADA], etc.
        return re.sub(r'\[.*?\]\s*', '', text).strip()
    
    def cleanup(self):
        """Limpia recursos"""
        if self.audio:
            self.audio.terminate()
        print("🧹 Recursos de Piper liberados")


# Ejemplo de uso
async def main():
    tts = PiperTTS()
    
    if not tts.initialize():
        return
    
    try:
        # Prueba de síntesis
        test_texts = [
            "[NEUTRAL] Hola, soy tu asistente de voz.",
            "[FELIZ] ¡Qué bueno verte de nuevo!",
            "[ENOJADA] No me gusta cuando me interrumpes."
        ]
        
        for text in test_texts:
            print(f"\n📝 Texto: {text}")
            await tts.generate_and_play(text)
            await asyncio.sleep(0.5)
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por usuario")
    finally:
        tts.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
