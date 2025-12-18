"""
llm_gemini.py - Integración con Gemini API
"""
import asyncio
import re
from typing import AsyncGenerator, Optional
import google.generativeai as genai
from config import Config


class GeminiLLM:
    """Clase para manejo del LLM con Gemini API"""
    
    def __init__(self):
        self.model = None
        self.chat = None
        self.conversation_history = []
        
    def initialize(self):
        """Inicializa la API de Gemini"""
        print("🧠 Inicializando Gemini API...")
        
        try:
            if not Config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY no configurada")
            
            # Configurar API
            genai.configure(api_key=Config.GEMINI_API_KEY)
            
            # Crear modelo con configuración
            generation_config = {
                "temperature": 0.9,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                system_instruction=Config.SYSTEM_INSTRUCTION
            )
            
            # Iniciar chat
            self.chat = self.model.start_chat(history=[])
            
            print("✅ Gemini API inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al inicializar Gemini: {e}")
            print("💡 Verifica tu GEMINI_API_KEY en el archivo .env")
            print("   Obtén una clave en: https://makersuite.google.com/app/apikey")
            return False
    
    async def send_message_stream(
        self, 
        message: str
    ) -> AsyncGenerator[str, None]:
        """
        Envía un mensaje y devuelve la respuesta en streaming
        
        Args:
            message: Mensaje del usuario
            
        Yields:
            Fragmentos de texto de la respuesta
        """
        try:
            print(f"💬 Enviando a Gemini: {message}")
            
            # Enviar mensaje con streaming
            response = await asyncio.to_thread(
                self.chat.send_message,
                message,
                stream=True
            )
            
            # Iterar sobre los chunks de respuesta
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            
            # Guardar en historial
            self.conversation_history.append({
                "user": message,
                "assistant": full_response
            })
            
            print(f"✅ Respuesta completa recibida ({len(full_response)} chars)")
            
        except Exception as e:
            print(f"❌ Error en Gemini: {e}")
            yield "[ERROR] Lo siento, tuve un problema procesando tu mensaje."
    
    async def get_response_with_chunking(
        self, 
        message: str,
        chunk_callback=None
    ) -> str:
        """
        Obtiene respuesta con chunking inteligente (por puntuación)
        
        Args:
            message: Mensaje del usuario
            chunk_callback: Función asíncrona a llamar con cada chunk completo
            
        Returns:
            Respuesta completa
        """
        buffer = ""
        full_response = ""
        
        async for text_chunk in self.send_message_stream(message):
            buffer += text_chunk
            full_response += text_chunk
            
            # Buscar puntos naturales de corte
            chunks = self._split_on_punctuation(buffer)
            
            # Si hay chunks completos, enviarlos
            if len(chunks) > 1:
                for chunk in chunks[:-1]:
                    if chunk.strip() and chunk_callback:
                        await chunk_callback(chunk.strip())
                
                # Mantener el último fragmento incompleto en el buffer
                buffer = chunks[-1]
        
        # Enviar el último chunk si queda algo
        if buffer.strip() and chunk_callback:
            await chunk_callback(buffer.strip())
        
        return full_response
    
    def _split_on_punctuation(self, text: str) -> list[str]:
        """
        Divide el texto en puntos naturales de corte
        
        Args:
            text: Texto a dividir
            
        Returns:
            Lista de fragmentos
        """
        # Dividir por puntos, comas, signos de exclamación/interrogación
        pattern = r'([.!?;,])\s+'
        parts = re.split(pattern, text)
        
        # Reconstruir chunks con su puntuación
        chunks = []
        i = 0
        while i < len(parts):
            if i + 1 < len(parts) and parts[i + 1] in '.!?;,':
                chunks.append(parts[i] + parts[i + 1])
                i += 2
            else:
                chunks.append(parts[i])
                i += 1
        
        return chunks
    
    def extract_emotion(self, text: str) -> tuple[str, str]:
        """
        Extrae la etiqueta de emoción del texto
        
        Args:
            text: Texto con posible etiqueta de emoción
            
        Returns:
            Tupla (emoción, texto_limpio)
        """
        # Buscar etiquetas como [FELIZ], [ENOJADA], etc.
        match = re.match(r'\[(.*?)\]\s*(.*)', text, re.IGNORECASE)
        
        if match:
            emotion = match.group(1).upper()
            clean_text = match.group(2)
            return emotion, clean_text
        
        return "NEUTRAL", text
    
    def add_time_pressure(self, seconds_remaining: int):
        """
        Añade presión de tiempo al contexto para forzar despedida
        
        Args:
            seconds_remaining: Segundos restantes
        """
        if seconds_remaining <= 30:
            time_message = f"[SISTEMA] Quedan {seconds_remaining} segundos. Despídete naturalmente."
            self.conversation_history.append({
                "system": time_message
            })
            print(f"⏰ Presión de tiempo añadida: {seconds_remaining}s restantes")
    
    def reset_conversation(self):
        """Reinicia la conversación"""
        self.chat = self.model.start_chat(history=[])
        self.conversation_history = []
        print("🔄 Conversación reiniciada")


# Ejemplo de uso
async def main():
    llm = GeminiLLM()
    
    if not llm.initialize():
        return
    
    try:
        # Callback para procesar chunks
        async def on_chunk(chunk: str):
            emotion, text = llm.extract_emotion(chunk)
            print(f"🎭 [{emotion}] {text}")
        
        # Prueba de conversación
        test_messages = [
            "Hola, ¿cómo estás?",
            "Cuéntame un chiste",
            "¡Eres muy tonta!" # Debería activar ENOJADA
        ]
        
        for msg in test_messages:
            print(f"\n👤 Usuario: {msg}")
            await llm.get_response_with_chunking(msg, chunk_callback=on_chunk)
            await asyncio.sleep(1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por usuario")


if __name__ == "__main__":
    asyncio.run(main())
