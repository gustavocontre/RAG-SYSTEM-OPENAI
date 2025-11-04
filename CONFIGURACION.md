# Configuración de Secrets y Variables de Entorno

Este documento explica cómo configurar de forma segura los secrets y variables de entorno del sistema RAG.

## 📋 Tabla de Contenidos

1. [Configuración Rápida](#configuración-rápida)
2. [Métodos de Configuración](#métodos-de-configuración)
3. [Variables de Entorno](#variables-de-entorno)
4. [Secrets (API Keys)](#secrets-api-keys)
5. [Validación](#validación)
6. [Seguridad](#seguridad)

## 🚀 Configuración Rápida

### Método 1: Script Interactivo (Recomendado)

```bash
python scripts/setup_env.py
```

Este script te guiará paso a paso para configurar todas las variables necesarias.

### Método 2: Manual

1. Copia el archivo de ejemplo:
   ```bash
   cp env.example .env
   ```

2. Edita el archivo `.env` y configura tu `OPENAI_API_KEY`:
   ```env
   OPENAI_API_KEY=sk-tu_api_key_aqui
   ```

3. Valida la configuración:
   ```python
   python -c "from config.settings import settings; settings.print_config()"
   ```

## 📝 Métodos de Configuración

### Opción 1: Archivo .env (Recomendado para desarrollo)

Crea un archivo `.env` en la raíz del proyecto:

```env
OPENAI_API_KEY=sk-tu_api_key_aqui
LLM_MODEL=gpt-4-turbo
API_PORT=8000
```

**⚠️ IMPORTANTE:** El archivo `.env` está en `.gitignore` y NO debe subirse al repositorio.

### Opción 2: Variables de Entorno del Sistema

#### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY="sk-tu_api_key_aqui"
```

#### Linux/Mac (Bash)
```bash
export OPENAI_API_KEY="sk-tu_api_key_aqui"
```

### Opción 3: Variables de Entorno en Docker

Si usas Docker, configura en `docker-compose.yml`:

```yaml
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}
```

## 🔑 Secrets (API Keys)

### OpenAI API Key

**Obligatoria** si `USE_LOCAL_LLM=false`

1. Obtén tu API key en: https://platform.openai.com/api-keys
2. Formato: `sk-...` (comienza con "sk-")
3. Configura en `.env`:
   ```env
   OPENAI_API_KEY=sk-tu_api_key_real_aqui
   ```

### HuggingFace Token (Opcional)

Solo necesario si descargas modelos de HuggingFace:

1. Obtén tu token en: https://huggingface.co/settings/tokens
2. Configura en `.env`:
   ```env
   HF_TOKEN=tu_token_huggingface
   ```

## 📊 Variables de Entorno

### Configuración de la API

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `API_HOST` | Host donde corre la API | `0.0.0.0` |
| `API_PORT` | Puerto de la API | `8000` |

### Configuración de la Interfaz Web

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `UI_HOST` | Host donde corre la UI | `0.0.0.0` |
| `UI_PORT` | Puerto de la UI | `7860` |

### Base de Datos

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `CHROMA_DB_PATH` | Ruta de la base de datos vectorial | `./data/chroma_db` |
| `UPLOAD_DIR` | Directorio para documentos subidos | `./data/uploaded_documents` |

### Modelos

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `EMBEDDING_MODEL` | Modelo de embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| `LLM_MODEL` | Modelo LLM (OpenAI) | `gpt-4-turbo` |
| `USE_LOCAL_LLM` | Usar modelo local en lugar de OpenAI | `false` |
| `LOCAL_MODEL_PATH` | Ruta al modelo local | `./models/codellama-7b-programming` |

### Configuración RAG

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `CHUNK_SIZE` | Tamaño de chunks de texto | `500` |
| `CHUNK_OVERLAP` | Overlap entre chunks | `50` |
| `TOP_K_RESULTS` | Número de resultados a recuperar | `5` |

## ✅ Validación

El sistema valida automáticamente la configuración al iniciar:

```python
from config.settings import settings

# Validar
is_valid, errors = settings.validate()
if not is_valid:
    for error in errors:
        print(f"Error: {error}")

# Verificar OpenAI
if settings.is_openai_configured():
    print("OpenAI está configurado correctamente")
```

### Ver configuración actual

```python
from config.settings import settings

# Sin mostrar secrets
settings.print_config()

# Mostrando secrets (últimos 4 caracteres)
settings.print_config(show_secrets=True)
```

## 🔒 Seguridad

### Mejores Prácticas

1. **Nunca subas `.env` al repositorio**
   - El archivo `.env` está en `.gitignore`
   - Usa `env.example` como plantilla

2. **No compartas tus API keys**
   - No las incluyas en código
   - No las compartas en chats o emails
   - Rota las keys si se comprometen

3. **Usa variables de entorno del sistema en producción**
   - Más seguro que archivos `.env`
   - Fácil de gestionar con orquestadores (Kubernetes, Docker Swarm, etc.)

4. **Valida antes de desplegar**
   ```bash
   python -c "from config.settings import settings; settings.validate()"
   ```

### Verificar que `.env` está en `.gitignore`

```bash
# Verificar
git check-ignore .env

# Si no está en .gitignore, añádelo:
echo ".env" >> .gitignore
```

## 🐛 Solución de Problemas

### Error: "OPENAI_API_KEY no está configurada"

**Solución:**
1. Verifica que el archivo `.env` existe
2. Verifica que contiene `OPENAI_API_KEY=sk-...`
3. Ejecuta: `python scripts/setup_env.py`

### Error: "OPENAI_API_KEY parece inválida"

**Solución:**
- La key debe comenzar con `sk-`
- Debe tener al menos 20 caracteres
- Verifica que no hay espacios extra

### Error: "Archivo .env no encontrado"

**Solución:**
```bash
cp env.example .env
python scripts/setup_env.py
```

## 📚 Referencias

- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [HuggingFace Tokens](https://huggingface.co/settings/tokens)
- [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)

