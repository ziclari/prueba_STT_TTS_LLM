"""
llm_gemini.py - Integración con Gemini API
"""
import asyncio
import re
from typing import AsyncGenerator, Optional
from google import genai
from config import Config
import unicodedata

class GeminiLLM:
    """Clase para manejo del LLM con Gemini API"""
    
    def __init__(self):
        self.client = None
        self.system_instruction = Config.SYSTEM_INSTRUCTION
        self.conversation_history = []
        
    def initialize(self):
        """Inicializa la API de Gemini"""
        print("🧠 Inicializando Gemini API...")
        
        try:
            if not Config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY no configurada")
            
            # Configurar API
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            # Iniciar chat
            self.conversation_history = []

            print("✅ Gemini API inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al inicializar Gemini: {e}")
            print("💡 Verifica tu GEMINI_API_KEY en el archivo .env")
            print("   Obtén una clave en: https://makersuite.google.com/app/apikey")
            return False

    def _build_prompt(self, user_message: str) -> str:
        parts = []

        # 1. SYSTEM SIEMPRE ARRIBA
        parts.append(f"SYSTEM:\n{self.system_instruction}\n")

        # 2. HISTORIAL
        for turn in self.conversation_history:
            parts.append(f"USER:\n{turn['user']}\n")
            parts.append(f"ASSISTANT:\n{turn['assistant']}\n")

        # 3. MENSAJE ACTUAL
        parts.append(f"USER:\n{user_message}\nASSISTANT:")

        return "\n".join(parts)

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
            prompt = self._build_prompt(message)

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            text = self.normalize_for_tts(response.text or "")
            yield text

            self.conversation_history.append({
                "user": message,
                "assistant": text
            })

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
                "user": "",
                "assistant": time_message
            })

            print(f"⏰ Presión de tiempo añadida: {seconds_remaining}s restantes")

    def normalize_for_tts(self, text: str) -> str:
        # 1. Normalizar unicode
        text = unicodedata.normalize("NFD", text)

        # 2. Quitar acentos, pero conservar ñ / Ñ
        text = "".join(
            c for c in text
            if unicodedata.category(c) != "Mn"
            or c.lower() == "n"
        )

        # 3. Filtrar caracteres permitidos:
        # letras, ñ, números, espacio, coma y punto
        text = re.sub(r"[^a-zA-ZñÑ0-9\s.,]", "", text)

        # 4. Normalizar espacios
        text = re.sub(r"\s+", " ", text).strip()

        return text


    def reset_conversation(self):
        """Reinicia la conversación"""
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
