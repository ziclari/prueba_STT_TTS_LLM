"""
llm_ollama.py - Integración con Ollama (LLM LOCAL - 100% GRATIS)
✅ Sin límites de uso
✅ Sin costos de API
✅ Privacidad total
✅ Streaming real
⚠️ Requiere GPU para buen rendimiento (o CPU potente)
"""
import asyncio
import re
from typing import AsyncGenerator
import aiohttp
from config import Config
import unicodedata
import json


class OllamaLLM:
    """Clase para manejo del LLM con Ollama (local)"""
    
    def __init__(self):
        self.base_url = Config.OLLAMA_URL
        self.model = Config.OLLAMA_MODEL
        self.system_instruction = Config.SYSTEM_INSTRUCTION
        self.conversation_history = []
        
    async def initialize(self):
        """Inicializa Ollama"""
        print("🧠 Inicializando Ollama (LLM Local)...")
        
        try:
            # Verificar que Ollama esté corriendo
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status != 200:
                        raise ConnectionError("Ollama no está corriendo")
                    
                    data = await resp.json()
                    models = [m["name"] for m in data.get("models", [])]
                    
                    if self.model not in models:
                        print(f"⚠️  Modelo '{self.model}' no encontrado")
                        print(f"📥 Descargando modelo (puede tardar varios minutos)...")
                        await self._pull_model()
            
            self.conversation_history = []
            print(f"✅ Ollama inicializado con modelo: {self.model}")
            print("💡 Modelo local - Sin límites de uso")
            return True
            
        except ConnectionError:
            print("❌ Ollama no está corriendo")
            print("💡 Instala Ollama: https://ollama.ai")
            print("   Luego ejecuta: ollama serve")
            return False
        except Exception as e:
            print(f"❌ Error al inicializar Ollama: {e}")
            return False

    async def _pull_model(self):
        """Descarga el modelo si no existe"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model}
            ) as resp:
                async for line in resp.content:
                    if line:
                        print("📥 Descargando...", end="\r")
                print("✅ Modelo descargado")

    def _build_prompt(self, user_message: str) -> str:
        """Construye el prompt completo"""
        parts = [f"SYSTEM:\n{self.system_instruction}\n"]
        
        for turn in self.conversation_history:
            parts.append(f"USER:\n{turn['user']}\n")
            parts.append(f"ASSISTANT:\n{turn['assistant']}\n")
        
        parts.append(f"USER:\n{user_message}\nASSISTANT:")
        
        return "\n".join(parts)

    async def send_message_stream(
        self, 
        message: str
    ) -> AsyncGenerator[str, None]:
        """
        Envía un mensaje y devuelve la respuesta en streaming REAL
        """
        try:
            print(f"💬 Enviando a Ollama: {message}")
            
            prompt = self._build_prompt(message)
            
            full_response = ""
            
            # Streaming con Ollama
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                    }
                ) as resp:
                    buffer = ""
                    # CAMBIO: usar iter_chunked con tamaño específico
                    async for chunk in resp.content.iter_chunked(1024):
                        buffer += chunk.decode("utf-8", errors="ignore")

                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()

                            if not line:
                                continue

                            try:
                                data = json.loads(line)
                                
                                if "response" in data and data["response"]:
                                    text = data["response"]
                                    full_response += text
                                    text = self.normalize_for_tts(text or "")
                                    yield text

                                if data.get("done"):
                                    break
                                    
                            except json.JSONDecodeError as e:
                                print(f"⚠️  Error decodificando JSON: {e}")
                                print(f"    Línea problemática: {line[:100]}")
                                continue

                    # Procesar cualquier línea restante en el buffer
                    if buffer.strip():
                        try:
                            data = json.loads(buffer)
                            if "response" in data and data["response"]:
                                text = data["response"]
                                full_response += text
                                yield text
                        except json.JSONDecodeError:
                            pass

            # Guardar en historial
            self.conversation_history.append({
                "user": message,
                "assistant": full_response
            })
            
            print(f"✅ Respuesta completa recibida ({len(full_response)} chars)")
            
        except Exception as e:
            print(f"❌ Error en Ollama: {e}")
            import traceback
            traceback.print_exc()
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

    def normalize_for_tts(self, text: str, prev: str = "") -> str:
        # Normalizar unicode
        text = unicodedata.normalize("NFD", text)

        # Quitar acentos pero conservar ñ
        text = "".join(
            c for c in text
            if unicodedata.category(c) != "Mn" or c.lower() == "n"
        )

        # Permitir corchetes
        text = re.sub(r"[^a-zA-ZñÑ0-9\s.,!?\[\]]", "", text)

        # Normalizar espacios internos
        text = re.sub(r"\s+", " ", text)

        # --- FIX CLAVE ---
        if prev and not prev.endswith((" ", "\n")) and not text.startswith((" ", ".", ",", "!", "?", "]")):
            text = " " + text

        return text

    def reset_conversation(self):
        """Reinicia la conversación"""
        self.conversation_history = []
        print("🔄 Conversación reiniciada")


# Ejemplo de uso
async def main():
    llm = OllamaLLM()
    
    if not await llm.initialize():
        return
    
    try:
        async def on_chunk(chunk: str):
            emotion, text = llm.extract_emotion(chunk)
            print(f"🎭 [{emotion}] {text}")
        
        test_messages = [
            "Hola, ¿cómo estás?",
            "Cuéntame un chiste corto",
        ]
        
        for msg in test_messages:
            print(f"\n👤 Usuario: {msg}")
            await llm.get_response_with_chunking(msg, chunk_callback=on_chunk)
            await asyncio.sleep(1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por usuario")


if __name__ == "__main__":
    asyncio.run(main())
