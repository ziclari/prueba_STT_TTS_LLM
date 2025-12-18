#!/usr/bin/env python3
"""
check_system.py - Verifica que todo esté configurado correctamente
"""
import sys
import subprocess
from pathlib import Path
from config import Config

def print_status(message, status):
    """Imprime un mensaje con estado"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {message}")
    return status

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 8
    print_status(
        f"Python {version.major}.{version.minor}.{version.micro}",
        is_valid
    )
    return is_valid

def check_module(module_name):
    """Verifica si un módulo está instalado"""
    try:
        __import__(module_name)
        print_status(f"Módulo '{module_name}' instalado", True)
        return True
    except ImportError:
        print_status(f"Módulo '{module_name}' NO instalado", False)
        return False

def check_command(command):
    """Verifica si un comando está disponible"""
    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        available = result.returncode == 0
        print_status(f"Comando '{command}' disponible", available)
        return available
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_status(f"Comando '{command}' NO disponible", False)
        return False

def check_piper(command):
    """Verifica si piper chambea"""
    try: 
        result = subprocess.run(
            ["pip", "show", "piper-tts"],
            capture_output=True,
            text=True,
            timeout=5
        )
        available = result.returncode == 0
        print_status(f"Comando '{command}' disponible", available)
        return available
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print_status(f"Comando '{command}' NO disponible", False)
        return False
 

def check_file(filepath, description):
    """Verifica si un archivo existe"""
    path = Path(filepath)
    exists = path.exists()
    print_status(f"{description}: {filepath}", exists)
    return exists

def check_api_key():
    """Verifica si la API key está configurada"""
    is_configured = bool(Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != "tu_clave_api_aqui")
    print_status("GEMINI_API_KEY configurada", is_configured)
    return is_configured

def main():
    """Ejecuta todas las verificaciones"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DEL SISTEMA")
    print("=" * 60)
    
    all_ok = True
    
    # Python
    print("\n📦 Python:")
    all_ok &= check_python_version()
    
    # Módulos Python
    print("\n📚 Módulos Python:")
    modules = [
        "pyaudio",
        "vosk",
        "google.generativeai",
        "dotenv"
    ]
    for module in modules:
        all_ok &= check_module(module)
    
    # Comandos del sistema
    print("\n🔧 Comandos del Sistema:")
    all_ok &= check_piper("piper")
    
    # Archivos de configuración
    print("\n⚙️  Configuración:")
    all_ok &= check_file(".env", "Archivo .env")
    all_ok &= check_api_key()
    
    # Modelos
    print("\n🤖 Modelos:")
    all_ok &= check_file(
        Config.VOSK_MODEL_PATH,
        "Modelo Vosk"
    )
    all_ok &= check_file(
        Config.PIPER_MODEL_PATH,
        "Modelo Piper"
    )
    all_ok &= check_file(
        Config.PIPER_CONFIG_PATH,
        "Config Piper"
    )
    
    # Resultado final
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ SISTEMA LISTO - Puedes ejecutar: python main.py")
    else:
        print("❌ FALTAN COMPONENTES - Revisa los errores arriba")
        print("💡 Consulta el README.md para instrucciones de instalación")
    print("=" * 60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
