"""
main.py - Orquestador principal del sistema híbrido
"""
import asyncio
import signal
from datetime import datetime, timedelta
from config import Config
from stt_vosk import VoskSTT
from tts_piper import PiperTTS

# Importar el LLM según configuración
def get_llm_class():
    """Obtiene la clase LLM según configuración"""
    if Config.LLM_PROVIDER == "gemini":
        from llm_gemini import GeminiLLM
        return GeminiLLM
    elif Config.LLM_PROVIDER == "groq":
        from llm_groq import GroqLLM
        return GroqLLM
    elif Config.LLM_PROVIDER == "ollama":
        from llm_ollama import OllamaLLM
        return OllamaLLM
    else:
        raise ValueError(f"LLM_PROVIDER inválido: {Config.LLM_PROVIDER}")


class HybridVoiceAssistant:
    """Asistente de voz híbrido con baja latencia"""
    
    def __init__(self, conversation_duration: int = 300):
        """
        Args:
            conversation_duration: Duración de la conversación en segundos (default: 5 min)
        """
        self.stt = VoskSTT()
        self.tts = PiperTTS()
        
        # Obtener LLM según configuración
        LLMClass = get_llm_class()
        self.llm = LLMClass()
        
        self.is_running = False
        self.conversation_start = None
        self.conversation_duration = conversation_duration
        
        # Control de interrupciones
        self.is_assistant_speaking = False
        self.interrupt_flag = asyncio.Event()
        
    async def initialize(self):
        """Inicializa todos los componentes"""
        print("🚀 Iniciando Asistente de Voz Híbrido...")
        print("=" * 60)
        
        # Validar configuración
        try:
            Config.validate()
            print(f"📡 LLM Provider: {Config.LLM_PROVIDER.upper()}")
        except Exception as e:
            print(f"❌ Error en configuración: {e}")
            return False
        
        # Inicializar componentes
        if not self.stt.initialize():
            return False
        
        if not self.tts.initialize():
            return False
        
        # Inicializar LLM (puede ser async para Ollama)
        llm_init = self.llm.initialize()
        if asyncio.iscoroutine(llm_init):
            if not await llm_init:
                return False
        else:
            if not llm_init:
                return False
        
        print("=" * 60)
        print("✅ Todos los componentes inicializados correctamente")
        return True
    
    async def run(self):
        """Loop principal del asistente"""
        self.is_running = True
        self.conversation_start = datetime.now()
        
        print("\n🎙️  ASISTENTE ACTIVADO")
        print("💡 Habla naturalmente, puedes interrumpir en cualquier momento")
        print(f"⏱️  Duración de conversación: {self.conversation_duration}s")
        print("-" * 60)
        
        try:
            # Mensaje de bienvenida
            await self.speak("[FELIZ] Hola Estoy lista para ayudarte. En que puedo asistirte")
            
            # Crear tareas concurrentes
            listen_task = asyncio.create_task(self.listen_loop())
            timer_task = asyncio.create_task(self.timer_loop())
            
            # Esperar a que terminen
            await asyncio.gather(listen_task, timer_task)
            
        except KeyboardInterrupt:
            print("\n⚠️  Interrumpido por usuario")
        finally:
            await self.shutdown()
    
    async def listen_loop(self):
        """Loop de escucha continua"""
        async def on_user_speech(text: str):
            # Si el asistente está hablando, interrumpir
            if self.is_assistant_speaking:
                print("🚫 Interrupción detectada - Deteniendo respuesta")
                self.interrupt_flag.set()
                self.tts.stop_speaking()
                await asyncio.sleep(0.3)  # Pequeña pausa para que se detenga
            
            # Procesar el mensaje del usuario
            await self.process_user_message(text)
        
        # Iniciar escucha
        await self.stt.listen_continuous(callback=on_user_speech)
    
    async def process_user_message(self, user_text: str):
        """
        Procesa un mensaje del usuario y genera respuesta
        
        Args:
            user_text: Texto transcrito del usuario
        """
        try:
            # Resetear flag de interrupción
            self.interrupt_flag.clear()
            
            # Crear callback para chunks de TTS
            async def tts_chunk_callback(chunk: str):
                if self.interrupt_flag.is_set():
                    print("⚠️  Chunk cancelado por interrupción")
                    return
                
                # Extraer emoción
                emotion, clean_text = self.llm.extract_emotion(chunk)
                
                # Detectar emociones para triggers visuales
                if emotion in ["ENOJADA", "FELIZ"]:
                    print(f"🎭 TRIGGER VISUAL: {emotion}")
                    # Aquí puedes activar efectos visuales/video
                
                # Sintetizar y reproducir
                await self.speak(clean_text)
            
            # Obtener respuesta del LLM con chunking
            self.is_assistant_speaking = True
            await self.llm.get_response_with_chunking(
                user_text,
                chunk_callback=tts_chunk_callback
            )
            
        except Exception as e:
            print(f"❌ Error procesando mensaje: {e}")
        finally:
            self.is_assistant_speaking = False
    
    async def speak(self, text: str):
        """
        Reproduce un texto con TTS
        
        Args:
            text: Texto a sintetizar
        """
        self.is_assistant_speaking = True
        try:
            await self.tts.generate_and_play(text)
        finally:
            self.is_assistant_speaking = False
    
    async def timer_loop(self):
        """Loop de control de tiempo de conversación"""
        while self.is_running:
            elapsed = (datetime.now() - self.conversation_start).seconds
            remaining = self.conversation_duration - elapsed
            
            # Añadir presión de tiempo al LLM
            if remaining <= 30 and remaining > 25:
                self.llm.add_time_pressure(remaining)
            
            # Terminar conversación
            if remaining <= 0:
                print("\n⏰ Tiempo de conversación agotado")
                await self.speak("[NEUTRAL] Ha sido un placer hablar contigo. ¡Hasta luego!")
                self.is_running = False
                break
            
            # Mostrar tiempo restante cada minuto
            if remaining % 60 == 0:
                print(f"⏱️  Tiempo restante: {remaining // 60} minutos")
            
            await asyncio.sleep(1)
    
    async def shutdown(self):
        """Limpia recursos y apaga el asistente"""
        print("\n🛑 Apagando asistente...")
        
        self.is_running = False
        self.stt.stop_listening()
        self.tts.stop_speaking()
        
        # Dar tiempo para que se detengan los procesos
        await asyncio.sleep(0.5)
        
        self.stt.cleanup()
        self.tts.cleanup()
        
        print("👋 Asistente apagado correctamente")


async def main():
    """Función principal"""
    assistant = HybridVoiceAssistant(conversation_duration=300)  # 5 minutos
    
    if not await assistant.initialize():
        print("❌ No se pudo inicializar el asistente")
        return
    # Manejar señal de interrupción
    try:
        await assistant.run()
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por usuario (Ctrl+C)")
        await assistant.shutdown()

    # Manejar señal de interrupción
    """ loop = asyncio.get_running_loop()
    
    def signal_handler():
        print("\n⚠️  Señal de interrupción recibida")
        assistant.is_running = False
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    # Ejecutar asistente
    await assistant.run()"""


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        🎙️  ASISTENTE DE VOZ HÍBRIDO 🤖                  ║
    ║                                                          ║
    ║    Modelo de Baja Latencia con Inteligencia en Nube    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())