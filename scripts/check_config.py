"""Script para verificar la configuración"""
import sys
from pathlib import Path

# Agregar path del proyecto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings

print("=" * 60)
print("Validacion de Configuracion")
print("=" * 60)
print()

is_valid, errors = settings.validate()

if is_valid:
    print("[OK] Configuracion valida!")
    print()
    settings.print_config()
    print()
    print("=" * 60)
    print("Todo listo! Puedes iniciar el sistema ahora.")
    print("=" * 60)
else:
    print("[ERROR] Problemas encontrados:")
    print()
    for error in errors:
        print(f"  - {error}")
    print()
    print("=" * 60)
    print("Por favor, revisa tu archivo .env y corrige los errores")
    print("=" * 60)

