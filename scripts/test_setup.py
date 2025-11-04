#!/usr/bin/env python3
"""
Script de verificación de setup del sistema RAG
Verifica que todas las dependencias estén instaladas correctamente
"""

import sys
import importlib
import os


def check_import(module_name, package_name=None):
    """Verifica si un módulo puede ser importado"""
    try:
        importlib.import_module(module_name)
        print(f"[OK] {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"[ERROR] {package_name or module_name}: {e}")
        return False


def check_directories():
    """Verifica que los directorios necesarios existan"""
    required_dirs = [
        'data/chroma_db',
        'data/uploaded_documents',
        'services',
        'services/document_processor',
        'services/rag_query',
        'services/web_interface'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"[OK] Directorio: {dir_path}")
        else:
            print(f"[ERROR] Directorio faltante: {dir_path}")
            all_exist = False
    
    return all_exist


def check_environment():
    """Verifica variables de entorno"""
    required_vars = ['OPENAI_API_KEY']
    optional_vars = ['API_URL', 'EMBEDDING_MODEL']
    
    print("\nVariables de Entorno:")
    all_set = True
    
    for var in required_vars:
        if os.getenv(var):
            print(f"[OK] {var}: Configurada")
        else:
            print(f"[WARN] {var}: NO configurada (REQUERIDA)")
            all_set = False
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"[OK] {var}: {os.getenv(var)}")
        else:
            print(f"[INFO] {var}: No configurada (opcional)")
    
    return all_set


def main():
    """Función principal de verificación"""
    import sys
    import io
    
    # Configurar encoding UTF-8 para Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("Verificando setup del Sistema RAG\n")
    print("=" * 60)
    
    # Verificar dependencias
    print("\nDependencias Python:")
    print("-" * 60)
    
    dependencies = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pydantic', 'Pydantic'),
        ('langchain', 'LangChain'),
        ('chromadb', 'ChromaDB'),
        ('sentence_transformers', 'Sentence Transformers'),
        ('PyPDF2', 'PyPDF2'),
        ('gradio', 'Gradio'),
        ('openai', 'OpenAI'),
        ('numpy', 'NumPy'),
    ]
    
    all_deps_ok = all(check_import(*dep) for dep in dependencies)
    
    # Verificar directorios
    print("\nEstructura de Directorios:")
    print("-" * 60)
    all_dirs_ok = check_directories()
    
    # Verificar entorno
    all_env_ok = check_environment()
    
    # Resumen
    print("\n" + "=" * 60)
    print("Resumen:")
    print("-" * 60)
    
    if all_deps_ok and all_dirs_ok:
        if all_env_ok:
            print("[OK] Setup completo! Sistema listo para usar.")
            return_code = 0
        else:
            print("[WARN] Setup casi completo, pero faltan variables de entorno.")
            print("   Edita el archivo .env con tu OPENAI_API_KEY")
            return_code = 1
    else:
        print("[ERROR] Setup incompleto. Revisa los errores arriba.")
        return_code = 1
    
    print("\nSiguiente paso:")
    if all_deps_ok and all_dirs_ok and all_env_ok:
        print("   python -m services.web_interface.api")
        print("   # En otra terminal:")
        print("   python -m services.web_interface.gradio_ui")
    elif not all_deps_ok:
        print("   pip install -r requirements.txt")
    elif not all_env_ok:
        print("   cp env.example .env")
        print("   # Editar .env con tu OPENAI_API_KEY")
    
    return return_code


if __name__ == "__main__":
    sys.exit(main())

