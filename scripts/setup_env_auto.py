"""
Script automático para configurar variables de entorno
Lee de variables de entorno del sistema o usa valores por defecto
"""

import os
import sys
from pathlib import Path

def create_env_file_from_example():
    """Crea archivo .env desde env.example si no existe"""
    env_path = Path(".env")
    env_example_path = Path("env.example")
    
    if env_path.exists():
        print(f"[INFO] Archivo .env ya existe en: {env_path.absolute()}")
        return
    
    if not env_example_path.exists():
        print(f"[ERROR] Archivo env.example no encontrado")
        return
    
    # Leer env.example
    with open(env_example_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar valores si existen en variables de entorno
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if line.strip() and not line.strip().startswith('#') and '=' in line:
            key, default_value = line.split('=', 1)
            key = key.strip()
            
            # Verificar si existe en variables de entorno
            env_value = os.getenv(key)
            if env_value:
                new_lines.append(f"{key}={env_value}")
                print(f"[OK] Configurado {key} desde variable de entorno")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Escribir archivo .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"[OK] Archivo .env creado en: {env_path.absolute()}")
    print()
    print("=" * 60)
    print("Archivo .env creado exitosamente")
    print("=" * 60)
    print()
    print("IMPORTANTE: Edita el archivo .env y configura tu OPENAI_API_KEY")
    print("  Ejemplo: OPENAI_API_KEY=sk-tu_api_key_real_aqui")
    print()
    print("Obtén tu API key en: https://platform.openai.com/api-keys")
    print()


if __name__ == "__main__":
    try:
        create_env_file_from_example()
        
        # Validar configuración
        try:
            from config.settings import settings
            is_valid, errors = settings.validate()
            if is_valid:
                print("[OK] Configuración válida!")
            else:
                print("[ADVERTENCIA] Configuración incompleta:")
                for error in errors:
                    print(f"  - {error}")
        except Exception as e:
            print(f"[INFO] No se pudo validar la configuración: {e}")
            
    except Exception as e:
        print(f"[ERROR] Error durante la configuración: {e}")
        sys.exit(1)

