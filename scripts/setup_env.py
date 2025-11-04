"""
Script para configurar variables de entorno y secrets
Ayuda a crear y configurar el archivo .env de forma interactiva
"""

import os
import sys
from pathlib import Path
import secrets
import string

def generate_random_key(length=32):
    """Genera una clave aleatoria para usar como placeholder"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file():
    """Crea o actualiza el archivo .env"""
    env_path = Path(".env")
    env_example_path = Path("env.example")
    
    print("=" * 60)
    print("Configuración de Variables de Entorno - Sistema RAG")
    print("=" * 60)
    print()
    
    # Cargar valores existentes si el archivo existe
    existing_values = {}
    if env_path.exists():
        print(f"[INFO] Archivo .env encontrado. Se cargarán valores existentes.")
        print()
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_values[key.strip()] = value.strip()
    
    # Cargar template desde env.example
    template = {}
    if env_example_path.exists():
        with open(env_example_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    template[key.strip()] = value.strip()
    
    # Configurar OpenAI API Key
    print("1. Configuración de OpenAI API Key")
    print("-" * 60)
    print("Obtén tu API key en: https://platform.openai.com/api-keys")
    print()
    
    current_key = existing_values.get('OPENAI_API_KEY', '')
    if current_key and current_key != 'tu_api_key_aqui' and not current_key.startswith('tu_'):
        print(f"[Actual] API Key: {'*' * (len(current_key) - 4) + current_key[-4:]}")
        use_current = input("¿Usar la API key actual? (S/n): ").strip().lower()
        if use_current != 'n':
            new_key = current_key
        else:
            new_key = input("Ingresa tu nueva OpenAI API Key: ").strip()
    else:
        new_key = input("Ingresa tu OpenAI API Key (o presiona Enter para saltar): ").strip()
    
    if not new_key:
        new_key = 'tu_api_key_aqui'
        print("[ADVERTENCIA] No se configuró la API key. El sistema no funcionará sin ella.")
    
    # Configurar otros valores importantes
    print("\n2. Configuración Opcional")
    print("-" * 60)
    
    # Modelo LLM
    current_model = existing_values.get('LLM_MODEL', template.get('LLM_MODEL', 'gpt-4-turbo'))
    print(f"\nModelo LLM (actual: {current_model})")
    new_model = input("Presiona Enter para mantener o ingresa nuevo modelo: ").strip()
    if not new_model:
        new_model = current_model
    
    # Puerto API
    current_port = existing_values.get('API_PORT', template.get('API_PORT', '8000'))
    print(f"\nPuerto API (actual: {current_port})")
    new_port = input("Presiona Enter para mantener o ingresa nuevo puerto: ").strip()
    if not new_port:
        new_port = current_port
    
    # Puerto UI
    current_ui_port = existing_values.get('UI_PORT', template.get('UI_PORT', '7860'))
    print(f"\nPuerto UI (actual: {current_ui_port})")
    new_ui_port = input("Presiona Enter para mantener o ingresa nuevo puerto: ").strip()
    if not new_ui_port:
        new_ui_port = current_ui_port
    
    # Crear archivo .env
    print("\n3. Generando archivo .env...")
    
    env_lines = []
    env_lines.append("# API Keys - SECRETS")
    env_lines.append(f"OPENAI_API_KEY={new_key}")
    env_lines.append("")
    env_lines.append("# Configuración de la API")
    env_lines.append(f"API_HOST={existing_values.get('API_HOST', template.get('API_HOST', '0.0.0.0'))}")
    env_lines.append(f"API_PORT={new_port}")
    env_lines.append("")
    env_lines.append("# Configuración de la interfaz")
    env_lines.append(f"UI_HOST={existing_values.get('UI_HOST', template.get('UI_HOST', '0.0.0.0'))}")
    env_lines.append(f"UI_PORT={new_ui_port}")
    env_lines.append("")
    env_lines.append("# Base de datos")
    env_lines.append(f"CHROMA_DB_PATH={existing_values.get('CHROMA_DB_PATH', template.get('CHROMA_DB_PATH', './data/chroma_db'))}")
    env_lines.append(f"UPLOAD_DIR={existing_values.get('UPLOAD_DIR', template.get('UPLOAD_DIR', './data/uploaded_documents'))}")
    env_lines.append("")
    env_lines.append("# Modelos")
    env_lines.append(f"EMBEDDING_MODEL={existing_values.get('EMBEDDING_MODEL', template.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'))}")
    env_lines.append(f"LLM_MODEL={new_model}")
    env_lines.append("")
    env_lines.append("# Modelo Local (CodeLlama fine-tuned)")
    env_lines.append("# Configurar USE_LOCAL_LLM=true para usar modelo local en lugar de OpenAI")
    env_lines.append(f"USE_LOCAL_LLM={existing_values.get('USE_LOCAL_LLM', template.get('USE_LOCAL_LLM', 'false'))}")
    env_lines.append(f"LOCAL_MODEL_PATH={existing_values.get('LOCAL_MODEL_PATH', template.get('LOCAL_MODEL_PATH', './models/codellama-7b-programming'))}")
    env_lines.append("# Token de HuggingFace (necesario para descargar el modelo base CodeLlama)")
    env_lines.append("# Obtener en: https://huggingface.co/settings/tokens")
    if existing_values.get('HF_TOKEN'):
        env_lines.append(f"HF_TOKEN={existing_values.get('HF_TOKEN')}")
    else:
        env_lines.append("# HF_TOKEN=tu_token_huggingface")
    env_lines.append("")
    env_lines.append("# RAG Configuration")
    env_lines.append(f"CHUNK_SIZE={existing_values.get('CHUNK_SIZE', template.get('CHUNK_SIZE', '500'))}")
    env_lines.append(f"CHUNK_OVERLAP={existing_values.get('CHUNK_OVERLAP', template.get('CHUNK_OVERLAP', '50'))}")
    env_lines.append(f"TOP_K_RESULTS={existing_values.get('TOP_K_RESULTS', template.get('TOP_K_RESULTS', '5'))}")
    
    # Escribir archivo
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(env_lines))
    
    print(f"[OK] Archivo .env creado en: {env_path.absolute()}")
    print()
    print("=" * 60)
    print("Configuración completada!")
    print("=" * 60)
    print()
    print("Próximos pasos:")
    print("1. Verifica que el archivo .env contenga tu API key correcta")
    print("2. Ejecuta: python -m services.web_interface.api")
    print("3. En otra terminal: python -m services.web_interface.gradio_ui")
    print()
    
    # Validar configuración
    try:
        from config.settings import Settings
        settings = Settings()
        is_valid, errors = settings.validate()
        if is_valid:
            print("[OK] Configuración válida!")
        else:
            print("[ERROR] Problemas en la configuración:")
            for error in errors:
                print(f"  - {error}")
    except Exception as e:
        print(f"[INFO] No se pudo validar la configuración: {e}")


if __name__ == "__main__":
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n\n[INFO] Configuración cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error durante la configuración: {e}")
        sys.exit(1)

