"""
llm_groq.py - Integración con Groq API (Alternativa GRATUITA a Gemini)
✅ 14,400 requests/día GRATIS
✅ Streaming REAL (respuesta instantánea)
✅ Modelos rápidos: Llama 3.1, Mixtral
"""
import asyncio
import re
from typing import AsyncGenerator
from groq import AsyncGroq
from config import Config
import unicodedata


class GroqLLM:
    """Clase para manejo del LLM con Groq API"""
    
    def __init__(self):
        self.client = None
        self.system_instruction = Config.SYSTEM_INSTRUCTION
        self.conversation_history = []
        
    def initialize(self):
        """Inicializa la API de Groq"""
        print("🧠 Inicializando Groq API...")
        
        try:
            if not Config.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY no configurada")
            
            # Configurar cliente Groq
            self.client = AsyncGroq(api_key=Config.GROQ_API_KEY)
            self.conversation_history = []

            print("✅ Groq API inicializado correctamente")
            print("💡 Límite: 14,400 requests/día GRATIS")
            return True
            
        except Exception as e:
            print(f"❌ Error al inicializar Groq: {e}")
            print("💡 Verifica tu GROQ_API_KEY en el archivo .env")
            print("   Obtén una clave GRATIS en: https://console.groq.com/keys")
            return False

    def _build_messages(self, user_message: str) -> list:
        """Construye el array de mensajes para Groq"""
        messages = [
            {"role": "system", "content": self.system_instruction}
        ]
        
        # Añadir historial
        for turn in self.conversation_history:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})
        
        # Añadir mensaje actual
        messages.append({"role": "user", "content": user_message})
        
        return messages

    async def send_message_stream(
        self, 
        message: str
    ) -> AsyncGenerator[str, None]:
        """
        Envía un mensaje y devuelve la respuesta en streaming REAL
        
        Args:
            message: Mensaje del usuario
            
        Yields:
            Fragmentos de texto de la respuesta EN TIEMPO REAL
        """
        try:
            print(f"💬 Enviando a Groq: {message}")
            
            messages = self._build_messages(message)
            
            # Hacer streaming con Groq
            stream = await self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",  # Modelo rápido y gratuito
                messages=messages,
                stream=True,
                max_tokens=500,  # Respuestas cortas para conversación
                temperature=0.9,
            )
            
            full_response = ""
            
            # Recibir chunks EN TIEMPO REAL
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_response += text
                    
                    # Normalizar para TTS
                    normalized = self.normalize_for_tts(text)
                    if normalized.strip():
                        yield normalized
            
            # Guardar en historial
            self.conversation_history.append({
                "user": message,
                "assistant": full_response
            })
            
            print(f"✅ Respuesta completa recibida ({len(full_response)} chars)")
            
        except Exception as e:
            print(f"❌ Error en Groq: {e}")
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
        """Divide el texto en puntos naturales de corte"""
        pattern = r'([.!?;,])\s+'
        parts = re.split(pattern, text)
        
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
        """Extrae la etiqueta de emoción del texto"""
        match = re.match(r'\[(.*?)\]\s*(.*)', text, re.IGNORECASE)
        
        if match:
            emotion = match.group(1).upper()
            clean_text = match.group(2)
            return emotion, clean_text
        
        return "NEUTRAL", text
    
    def add_time_pressure(self, seconds_remaining: int):
        """Añade presión de tiempo al contexto"""
        if seconds_remaining <= 30:
            time_message = f"[SISTEMA] Quedan {seconds_remaining} segundos. Despídete naturalmente."
            self.conversation_history.append({
                "user": "",
                "assistant": time_message
            })
            print(f"⏰ Presión de tiempo añadida: {seconds_remaining}s restantes")

    def normalize_for_tts(self, text: str) -> str:
        """Normaliza texto para TTS (sin acentos que Piper pronuncia mal)"""
        # Normalizar unicode
        text = unicodedata.normalize("NFD", text)
        
        # Quitar acentos pero conservar ñ/Ñ
        text = "".join(
            c for c in text
            if unicodedata.category(c) != "Mn" or c.lower() == "n"
        )
        
        # Solo letras, ñ, números, espacio, coma y punto
        text = re.sub(r"[^a-zA-ZñÑ0-9\s.,!?]", "", text)
        
        # Normalizar espacios
        text = re.sub(r"\s+", " ", text).strip()
        
        return text

    def reset_conversation(self):
        """Reinicia la conversación"""
        self.conversation_history = []
        print("🔄 Conversación reiniciada")


# Ejemplo de uso
async def main():
    llm = GroqLLM()
    
    if not llm.initialize():
        return
    
    try:
        async def on_chunk(chunk: str):
            emotion, text = llm.extract_emotion(chunk)
            print(f"🎭 [{emotion}] {text}")
        
        test_messages = [
            "Hola, ¿cómo estás?",
            "Cuéntame un chiste corto",
            "¡Eres muy tonta!"
        ]
        
        for msg in test_messages:
            print(f"\n👤 Usuario: {msg}")
            await llm.get_response_with_chunking(msg, chunk_callback=on_chunk)
            await asyncio.sleep(1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por usuario")


if __name__ == "__main__":
    asyncio.run(main())
