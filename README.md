# Sistema RAG - Asistente de Conocimiento para Desarrolladores

Sistema completo de Retrieval-Augmented Generation (RAG) que procesa documentación técnica, la indexa en una base de datos vectorial, y proporciona respuestas precisas a consultas utilizando LLMs. Implementado con FastAPI, Gradio, ChromaDB y OpenAI GPT-4.

## Tabla de Contenidos

1. [Características](#-características)
2. [Arquitectura](#-arquitectura)
3. [Requisitos Previos](#-requisitos-previos)
4. [Instalación Paso a Paso](#-instalación-paso-a-paso)
5. [Documentación de APIs](#-documentación-de-apis)
6. [Stack Tecnológico](#-stack-tecnológico)
7. [Decisiones Arquitectónicas](#-decisiones-arquitectónicas)
8. [Estrategias de Evaluación](#-estrategias-de-evaluación)
9. [Uso del Sistema](#-uso-del-sistema)
10. [Solución de Problemas](#-solución-de-problemas)

## Características

- **Procesamiento de Documentos**: Soporta PDF, TXT, MD con chunking inteligente
- **Búsqueda Semántica**: Embeddings con Sentence-Transformers y ChromaDB
- **Generación de Respuestas**: Integración con OpenAI GPT-4-turbo
- **Interfaz Web**: Chat interactivo con Gradio
- **API REST**: Endpoints completos con documentación Swagger
- **Métricas y Evaluación**: Sistema de tracking y evaluación de rendimiento
- **Docker**: Contenerización completa con Docker Compose
- **Configuración Segura**: Manejo de secrets y variables de entorno

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Interfaz Web (Gradio)                    │
│                    Puerto: 7860                            │
│  - Chat interactivo                                         │
│  - Subida de documentos                                     │
│  - Visualización de fuentes                                 │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP REST
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    API REST (FastAPI)                        │
│                    Puerto: 8000                             │
│  - /upload: Procesamiento de documentos                     │
│  - /query: Consultas RAG                                    │
│  - /stats: Estadísticas                                     │
│  - /metrics: Métricas del sistema                           │
└───────────┬───────────────────────────────┬─────────────────┘
            │                                │
            ▼                                ▼
┌──────────────────────┐      ┌──────────────────────────────┐
│    ChromaDB          │      │    OpenAI GPT-4               │
│  (Base Vectorial)    │      │    (LLM)                      │
│                      │      │                               │
│  - Embeddings        │      │  - Generación de respuestas   │
│  - Búsqueda semántica│      │  - Contexto aumentado        │
│  - Metadata filtering│      │  - Zero-shot learning         │
└──────────────────────┘      └──────────────────────────────┘
```

### Flujo de Datos

1. **Ingesta de Documentos**:
   ```
   PDF/TXT/MD → Extracción de texto → Chunking → Embeddings → ChromaDB
   ```

2. **Consulta RAG**:
   ```
   Pregunta → Embedding → Búsqueda semántica → Chunks relevantes → 
   Contexto → GPT-4 → Respuesta + Fuentes
   ```

### Componentes Principales

- **DocumentProcessor**: Extrae texto, genera chunks, crea embeddings
- **RAGQueryService**: Búsqueda semántica y generación de respuestas
- **API REST**: FastAPI con endpoints RESTful
- **Interfaz Web**: Gradio para interacción con usuarios
- **MetricsCollector**: Sistema de métricas y evaluación

## Requisitos Previos

### Software Requerido

- **Python 3.9 o superior**
- **pip** (gestor de paquetes Python)
- **Git** (para clonar el repositorio)

### Opcional (para Docker)

- **Docker Desktop** (versión 20.10+)
- **Docker Compose** (versión 2.0+)

### Credenciales

- **API Key de OpenAI**: Obtener en https://platform.openai.com/api-keys
  - Requiere cuenta en OpenAI
  - Costo asociado por uso (ver precios en OpenAI)

## Instalación Paso a Paso

### Opción 1: Instalación Local (Recomendado para Desarrollo)

#### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/TU_USUARIO/rag-system-openai.git
cd rag-system-openai
```

#### Paso 2: Crear Entorno Virtual (Recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Paso 3: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Tiempo estimado**: 2-5 minutos (depende de la conexión)

#### Paso 4: Configurar Variables de Entorno

**Método Rápido (Recomendado):**
```bash
python scripts/setup_env.py
```

Este script te guiará interactivamente para:
- Configurar tu API key de OpenAI
- Ajustar puertos y configuraciones
- Validar la configuración

**Método Manual:**
```bash
# 1. Copiar archivo de ejemplo
cp env.example .env

# 2. Editar .env con tu editor favorito
# Windows: notepad .env
# Linux/Mac: nano .env o vim .env

# 3. Configurar tu API key
OPENAI_API_KEY=sk-tu_api_key_real_aqui
```

**Verificar configuración:**
```bash
python scripts/check_config.py
```

#### Paso 5: Iniciar el Sistema

**Terminal 1 - Servidor API:**
```bash
python -m services.web_interface.api
```

Deberías ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Application startup complete.
```

**Terminal 2 - Interfaz Web:**
```bash
python -m services.web_interface.gradio_ui
```

Deberías ver:
```
Running on local URL:  http://127.0.0.1:7860
```

#### Paso 6: Verificar que Funciona

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```
   O abre en navegador: http://localhost:8000/health

2. **Documentación API:**
   Abre en navegador: http://localhost:8000/docs

3. **Interfaz Web:**
   Abre en navegador: http://localhost:7860

### Opción 2: Docker (Recomendado para Producción)

#### Paso 1: Clonar y Configurar

```bash
git clone https://github.com/TU_USUARIO/rag-system-openai.git
cd rag-system-openai
cp env.example .env
# Editar .env con tu OPENAI_API_KEY
```

#### Paso 2: Construir y Iniciar

```bash
docker-compose up -d --build
```

Este comando:
- Construye las imágenes Docker
- Crea los contenedores
- Inicia los servicios en segundo plano

**Ver logs:**
```bash
docker-compose logs -f
```

#### Paso 3: Verificar

```bash
# Verificar contenedores
docker-compose ps

# Deberías ver:
# rag-api   Up   0.0.0.0:8000->8000/tcp
# rag-ui    Up   0.0.0.0:7860->7860/tcp
```

#### Paso 4: Detener Servicios

```bash
docker-compose down
```

## Documentación de APIs

### Base URL

```
http://localhost:8000
```

### Endpoints Principales

#### 1. Health Check

Verifica el estado del servicio y la base de datos.

**Endpoint:** `GET /health`

**Ejemplo de uso:**
```bash
curl http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "chunks": 718,
    "documents": 6
  }
}
```

---

#### 2. Subir Documento

Procesa y indexa un documento en la base de datos vectorial.

**Endpoint:** `POST /upload`

**Content-Type:** `multipart/form-data`

**Parámetros:**
- `file` (form-data, requerido): Archivo PDF, TXT o MD

**Ejemplo de uso con curl:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@documento.pdf"
```

**Ejemplo con Python:**
```python
import requests

url = "http://localhost:8000/upload"
files = {"file": open("documento.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Respuesta exitosa:**
```json
{
  "doc_id": "doc_5b89c441ba45",
  "chunks_created": 120,
  "total_chars": 45678,
  "filename": "documento.pdf",
  "message": "Documento procesado exitosamente"
}
```

**Errores comunes:**
- `400`: Formato no soportado
- `500`: Error al procesar el documento

---

#### 3. Realizar Consulta RAG

Procesa una consulta y genera una respuesta usando RAG.

**Endpoint:** `POST /query`

**Content-Type:** `application/json`

**Body:**
```json
{
  "question": "¿Qué es Python?",
  "top_k": 5,
  "return_sources": true
}
```

**Parámetros:**
- `question` (string, requerido): Pregunta del usuario
- `top_k` (int, opcional): Número de chunks a recuperar (default: 5)
- `return_sources` (bool, opcional): Si retornar fuentes (default: true)

**Ejemplo de uso con curl:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué es Python?",
    "top_k": 5,
    "return_sources": true
  }'
```

**Ejemplo con Python:**
```python
import requests

url = "http://localhost:8000/query"
payload = {
    "question": "¿Cómo definir una función en Python?",
    "top_k": 5,
    "return_sources": True
}
response = requests.post(url, json=payload)
result = response.json()

print("Respuesta:", result["answer"])
print("Fuentes:", result["sources"])
```

**Respuesta:**
```json
{
  "answer": "Python es un lenguaje de programación de alto nivel...",
  "sources": [
    {
      "filename": "Python para todos.pdf",
      "chunk_index": 2,
      "score": 0.85
    },
    {
      "filename": "Introduccion a Python.pdf",
      "chunk_index": 5,
      "score": 0.78
    }
  ],
  "num_chunks": 5
}
```

**Proceso interno:**
1. Genera embedding de la pregunta
2. Búsqueda semántica en ChromaDB
3. Recupera top-k chunks más relevantes
4. Genera respuesta con GPT-4 usando contexto
5. Retorna respuesta con fuentes

---

#### 4. Listar Documentos

Obtiene la lista de documentos indexados.

**Endpoint:** `GET /documents`

**Ejemplo:**
```bash
curl http://localhost:8000/documents
```

**Respuesta:**
```json
{
  "documents": [
    "doc_5b89c441ba45",
    "doc_7c3d2e1f9a8b"
  ],
  "count": 2
}
```

---

#### 5. Estadísticas

Obtiene estadísticas de la base de datos.

**Endpoint:** `GET /stats`

**Ejemplo:**
```bash
curl http://localhost:8000/stats
```

**Respuesta:**
```json
{
  "total_chunks": 718,
  "unique_documents": 6
}
```

---

#### 6. Métricas del Sistema

Obtiene métricas de rendimiento.

**Endpoint:** `GET /metrics`

**Ejemplo:**
```bash
curl http://localhost:8000/metrics
```

**Respuesta:**
```json
{
  "timestamp": "2025-11-04T18:00:00",
  "system_stats": {
    "total_chunks": 718,
    "unique_documents": 6,
    "db_size_mb": 19.52
  },
  "query_metrics": {
    "total_queries": 25,
    "time_metrics": {
      "total_time": {
        "mean": 2.5,
        "min": 1.2,
        "max": 5.8
      }
    }
  }
}
```

---

#### 7. Eliminar Documento

Elimina un documento y todos sus chunks.

**Endpoint:** `DELETE /delete/{doc_id}`

**Ejemplo:**
```bash
curl -X DELETE "http://localhost:8000/delete/doc_5b89c441ba45"
```

---

### Documentación Interactiva

Accede a la documentación interactiva (Swagger) en:
```
http://localhost:8000/docs
```

O la documentación alternativa (ReDoc) en:
```
http://localhost:8000/redoc
```

### Ejemplo Completo: Flujo de Trabajo

```bash
# 1. Verificar estado
curl http://localhost:8000/health

# 2. Subir documento
curl -X POST "http://localhost:8000/upload" \
  -F "file=@python_tutorial.pdf"

# 3. Ver estadísticas
curl http://localhost:8000/stats

# 4. Hacer consulta
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cómo definir una función en Python?",
    "top_k": 5
  }'

# 5. Ver métricas
curl http://localhost:8000/metrics
```

## Stack Tecnológico

### Backend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.9+ | Lenguaje principal del sistema |
| **FastAPI** | 0.104+ | Framework web moderno y rápido para API REST |
| **Uvicorn** | 0.24+ | Servidor ASGI de alto rendimiento |
| **LangChain** | 0.1+ | Framework para aplicaciones LLM |
| **ChromaDB** | 0.4+ | Base de datos vectorial para embeddings |
| **Sentence-Transformers** | 2.2+ | Modelo de embeddings semánticos |
| **OpenAI** | 1.0+ | SDK para integración con GPT-4 |
| **PyPDF2** | 3.0+ | Extracción de texto de PDFs |
| **python-dotenv** | 1.0+ | Manejo de variables de entorno |

### Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Gradio** | 4.0+ | Interfaz web interactiva para ML/AI |
| **HTML/CSS/JS** | - | Interfaz de usuario (generada por Gradio) |

### Infraestructura

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Docker** | 20.10+ | Contenerización de aplicaciones |
| **Docker Compose** | 2.0+ | Orquestación de servicios |

### Herramientas de Desarrollo

| Tecnología | Propósito |
|------------|-----------|
| **Git** | Control de versiones |
| **pydantic** | Validación de datos |
| **pytest** | Testing (opcional) |

## 🏛️ Decisiones Arquitectónicas

### 1. Base de Datos Vectorial: ChromaDB

**Decisión**: Usar ChromaDB como base de datos vectorial principal.

**Razones:**
- **Simplicidad**: Fácil de instalar y configurar (no requiere servidor externo)
- **Persistencia local**: Almacena datos localmente sin dependencias externas
- **Rendimiento**: Excelente para bases pequeñas-medianas (< 100K vectores)
- **Metadata filtering**: Soporte nativo para filtrar por metadata
- **Open source**: Código abierto y activamente mantenido

**Alternativas consideradas:**
- **Milvus**: Más complejo, requiere servidor separado
- **Pinecone**: Servicio cloud, requiere suscripción
- **Weaviate**: Más pesado, overkill para este caso

**Trade-offs aceptados:**
- Limitado a bases de datos locales
- Rendimiento puede degradarse con > 1M vectores

### 2. Modelo de Embeddings: Sentence-Transformers (all-MiniLM-L6-v2)

**Decisión**: Usar modelo local de Sentence-Transformers.

**Razones:**
- **Sin dependencias externas**: No requiere API keys adicionales
- **Velocidad**: Modelo optimizado para rapidez (6 layers, 384 dimensions)
- **Calidad**: Buen balance calidad/velocidad para español
- **Costo**: Gratis, sin costos por embedding
- **Privacidad**: Datos no salen del servidor

**Alternativas consideradas:**
- **OpenAI Embeddings**: Mayor calidad pero con costo y latencia
- **Cohere**: Similar a OpenAI, requiere API key
- **Modelos más grandes**: Mejor calidad pero más lentos

**Trade-offs aceptados:**
- Calidad ligeramente inferior a embeddings de OpenAI
- Requiere descarga inicial del modelo (~90MB)

### 3. LLM: OpenAI GPT-4-turbo

**Decisión**: Usar GPT-4-turbo como modelo de generación.

**Razones:**
- **Calidad superior**: Mejor entendimiento de contexto y generación
- **API estable**: Servicio confiable y bien documentado
- **Capacidades avanzadas**: Buen manejo de instrucciones complejas
- **Actualización automática**: Siempre última versión sin reentrenamiento

**Alternativas consideradas:**
- **GPT-3.5-turbo**: Más rápido y barato, pero menor calidad
- **Anthropic Claude**: Similar calidad, pero menos integrado
- **Groq**: Muy rápido pero requiere modelo específico
- **Modelos locales (Llama)**: Sin costo pero requiere GPU potente

**Trade-offs aceptados:**
- Costo por token (aproximadamente $0.01-0.03 por consulta)
- Dependencia de conexión a internet
- Latencia de red (~2-5 segundos por consulta)

### 4. Estrategia de Chunking

**Decisión**: Chunking por palabras con overlap.

**Configuración:**
- `CHUNK_SIZE=500` palabras
- `CHUNK_OVERLAP=50` palabras

**Razones:**
- **Preserva contexto**: Overlap evita perder información en límites
- **Tamaño óptimo**: 500 palabras balancea contexto y precisión
- **Por palabras, no caracteres**: Mejor calidad semántica
- **Configurable**: Fácil ajustar según necesidad

**Alternativas consideradas:**
- **Chunking por caracteres**: Más simple pero peor calidad
- **Chunking por párrafos**: Más natural pero tamaño variable
- **Chunking inteligente (semántico)**: Mejor pero más complejo

**Trade-offs aceptados:**
- Puede dividir conceptos entre chunks
- Overlap aumenta tamaño de la BD

### 5. Framework Web: FastAPI

**Decisión**: Usar FastAPI para la API REST.

**Razones:**
- **Rendimiento**: Muy rápido (comparable a Node.js)
- **Documentación automática**: Swagger/OpenAPI integrado
- **Type hints**: Validación automática con Pydantic
- **Async/await**: Soporte nativo para operaciones asíncronas
- **Moderno**: Diseño limpio y Pythonic

**Alternativas consideradas:**
- **Flask**: Más simple pero menos features
- **Django**: Más pesado, overkill para API
- **Express.js**: Requeriría cambiar stack

### 6. Interfaz Web: Gradio

**Decisión**: Usar Gradio para la interfaz de usuario.

**Razones:**
- **Rápido de desarrollar**: Interfaz lista en minutos
- **Interactivo**: Chat, uploads, visualización incluidos
- **Sin frontend**: No requiere HTML/CSS/JS manual
- **Integración fácil**: Se conecta directamente a la API
- **Gratis y open source**: Sin restricciones

**Alternativas consideradas:**
- **Streamlit**: Similar pero menos flexible
- **React/Vue**: Más control pero mucho más trabajo
- **HTML/CSS/JS puro**: Máximo control pero desarrollo largo

### 7. Arquitectura de Servicios

**Decisión**: Separar servicios en módulos independientes.

**Estructura:**
```
services/
├── document_processor/  # Procesamiento
├── rag_query/          # Consultas RAG
├── web_interface/      # API y UI
└── metrics/            # Métricas
```

**Razones:**
- **Separación de responsabilidades**: Cada módulo tiene una función clara
- **Reutilizable**: Módulos pueden usarse independientemente
- **Testeable**: Fácil testear cada componente
- **Escalable**: Fácil agregar nuevos servicios

### 8. Manejo de Configuración

**Decisión**: Sistema centralizado de configuración con `config/settings.py`.

**Razones:**
- **Un solo punto de verdad**: Toda la configuración en un lugar
- **Validación automática**: Verifica configuración al inicio
- **Type-safe**: Type hints para todas las variables
- **Seguridad**: Manejo seguro de secrets

## Estrategias de Evaluación

### 1. Métricas Implementadas

#### Métricas de Recuperación (Retrieval)

**Score de Similitud (Cosine Similarity)**
- **Qué mide**: Relevancia de chunks recuperados
- **Rango**: 0.0 - 1.0 (1.0 = perfectamente relevante)
- **Umbral recomendado**: > 0.5 para chunks útiles
- **Implementación**: Calculado automáticamente en cada búsqueda

**Precision@K**
- **Qué mide**: Porcentaje de chunks relevantes en los top-K
- **Cálculo**: `chunks_relevantes / K`
- **Objetivo**: > 70% para K=5

**Tiempo de Recuperación**
- **Qué mide**: Velocidad de búsqueda semántica
- **Objetivo**: < 500ms para bases < 10K chunks
- **Implementado**: Tracking automático

#### Métricas de Generación

**Tiempo de Generación**
- **Qué mide**: Latencia del LLM
- **Depende de**: Modelo, contexto, longitud de respuesta
- **Objetivo**: 2-5 segundos con GPT-4

**Longitud de Respuesta**
- **Qué mide**: Completitud de la respuesta
- **Análisis**: Respuestas muy cortas (< 50 chars) pueden indicar falta de contexto

**Relevancia de Respuesta**
- **Qué mide**: Si la respuesta responde a la pregunta
- **Evaluación**: Manual o con LLM evaluador
- **Métrica**: 0-5 (subjetiva)

#### Métricas del Sistema

**Throughput**
- **Qué mide**: Consultas procesadas por segundo
- **Cálculo**: `total_queries / total_time`
- **Objetivo**: 0.2-0.5 queries/segundo con GPT-4

**Tasa de Éxito**
- **Qué mide**: Porcentaje de consultas exitosas
- **Objetivo**: > 95%

### 2. Herramientas de Evaluación

#### Script de Métricas

```bash
python scripts/generate_metrics_report.py
```

Genera reporte con:
- Tiempos promedio, mínimos, máximos
- Scores de similitud
- Estadísticas de uso
- Últimas 10 consultas

#### API de Métricas

```bash
curl http://localhost:8000/metrics
```

Retorna métricas en tiempo real en formato JSON.

### 3. Métodos de Evaluación

#### Evaluación Automática

**Métricas cuantitativas**:
- Tiempos de respuesta
- Scores de similitud
- Throughput
- Tasa de errores

**Implementación**:
- Tracking automático en cada consulta
- Almacenamiento en `data/metrics.json`
- Reportes generados automáticamente

#### Evaluación Manual

**Checklist de calidad** (para cada respuesta):
- [ ] Relevancia (0-5): ¿Responde a la pregunta?
- [ ] Precisión (0-5): ¿La información es correcta?
- [ ] Completitud (0-5): ¿Está completa la respuesta?
- [ ] Coherencia (0-5): ¿Tiene sentido?

**Dataset de prueba**:
- Crear conjunto de preguntas con respuestas esperadas
- Comparar respuestas generadas vs esperadas
- Calcular métricas de precisión/recall

### 4. Benchmarking

#### Métricas de Referencia

Para un sistema RAG con:
- Base de datos: 1000-5000 chunks
- Modelo: GPT-4-turbo
- Embeddings: Sentence-Transformers

**Métricas esperadas**:
- Tiempo de recuperación: 200-500ms
- Tiempo de generación: 2-5s
- Tiempo total: 2.5-6s
- Score promedio: 0.6-0.8
- Throughput: 0.15-0.4 queries/segundo

#### Comparación con Baselines

**Baseline 1: Sin RAG (solo LLM)**
- Sin contexto de documentos
- Respuestas genéricas
- No específicas al dataset

**Baseline 2: RAG con búsqueda exacta**
- Búsqueda por palabras clave
- Sin embeddings
- Menor precisión semántica

**Baseline 3: Diferente modelo de embeddings**
- Comparar Sentence-Transformers vs OpenAI embeddings
- Trade-off calidad/velocidad

### 5. Optimización Basada en Métricas

**Si score de similitud < 0.5**:
- Ajustar `CHUNK_SIZE`
- Cambiar modelo de embeddings
- Mejorar preprocesamiento

**Si tiempo de respuesta > 10s**:
- Reducir `TOP_K_RESULTS`
- Usar GPT-3.5 en lugar de GPT-4
- Optimizar búsqueda vectorial

**Si respuestas incompletas**:
- Aumentar `TOP_K_RESULTS`
- Aumentar `CHUNK_SIZE`
- Mejorar prompt del LLM

### 6. Monitoreo Continuo

**Métricas a monitorear**:
1. Latencia por consulta
2. Throughput (consultas/minuto)
3. Score promedio de similitud
4. Tasa de errores
5. Uso de tokens de OpenAI

**Alertas recomendadas**:
- Tiempo de respuesta > 10s
- Score promedio < 0.4
- Tasa de errores > 5%

Para más detalles, ver [EVALUACION_RAG.md](EVALUACION_RAG.md)

## Uso del Sistema

### Flujo de Trabajo Típico

1. **Subir Documentos**
   ```bash
   curl -X POST "http://localhost:8000/upload" \
     -F "file=@documento.pdf"
   ```

2. **Hacer Consultas**
   ```bash
   curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "¿Qué es Python?"}'
   ```

3. **Ver Métricas**
   ```bash
   python scripts/generate_metrics_report.py
   ```

### Desde la Interfaz Web

1. Abre http://localhost:7860
2. Sube un documento PDF/TXT/MD
3. Haz preguntas en el chat
4. El sistema responderá con información de los documentos

## Solución de Problemas

### Error: "OPENAI_API_KEY no está configurada"

**Solución:**
1. Verifica que `.env` existe: `ls .env` o `dir .env`
2. Verifica contenido: `cat .env | grep OPENAI_API_KEY`
3. Debe contener: `OPENAI_API_KEY=sk-...`
4. Ejecuta: `python scripts/check_config.py`

### Error: "Base de datos vacía"

**Solución:**
1. Sube al menos un documento primero
2. Usa endpoint `/upload` o interfaz web
3. Verifica con: `curl http://localhost:8000/stats`

### Error: "Puerto en uso"

**Solución:**
```bash
# Cambiar puerto en .env
API_PORT=8001
UI_PORT=7861
```

### Error: "Connection refused" en Docker

**Solución:**
```bash
# Verificar contenedores
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart
```

### Error: "Module not found"

**Solución:**
```bash
# Reinstalar dependencias
pip install -r requirements.txt

# Verificar entorno virtual activado
which python  # Linux/Mac
where python  # Windows
```

## Estructura del Proyecto

```
RAG-system-openai/
├── config/                      # Configuración centralizada
│   ├── settings.py              # Manejo de secrets y variables
│   └── __init__.py
├── services/                    # Servicios principales
│   ├── document_processor/      # Procesamiento de documentos
│   │   ├── processor.py         # Lógica de chunking y embeddings
│   │   └── __init__.py
│   ├── rag_query/               # Servicio de consultas RAG
│   │   ├── query_service.py     # Búsqueda semántica y generación
│   │   └── __init__.py
│   ├── web_interface/           # API y UI
│   │   ├── api.py               # Endpoints FastAPI
│   │   ├── gradio_ui.py         # Interfaz web
│   │   └── __init__.py
│   └── metrics/                 # Sistema de métricas
│       ├── metrics_collector.py # Colector de métricas
│       └── __init__.py
├── scripts/                     # Scripts utilitarios
│   ├── setup_env.py             # Configuración interactiva
│   ├── setup_env_auto.py        # Configuración automática
│   ├── check_config.py          # Verificar configuración
│   ├── generate_metrics_report.py # Generar reportes
│   └── test_setup.py            # Verificar dependencias
├── docker/                      # Dockerfiles
│   ├── Dockerfile.api           # Imagen para API
│   └── Dockerfile.ui            # Imagen para UI
├── data/                        # Datos (gitignored)
│   ├── chroma_db/              # Base de datos vectorial
│   ├── uploaded_documents/      # Documentos subidos
│   └── metrics.json             # Métricas (gitignored)
├── docker-compose.yml           # Orquestación Docker
├── requirements.txt             # Dependencias Python
├── env.example                  # Plantilla de configuración
├── README.md                    # Este archivo
├── API_DOCUMENTATION.md         # Documentación detallada de APIs
├── CONFIGURACION.md             # Configuración de secrets
├── EVALUACION_RAG.md            # Estrategias de evaluación
└── INICIAR_SISTEMA.md           # Guía de inicio
```

## Seguridad

- Archivo `.env` en `.gitignore` (no se sube al repositorio)
- Secrets nunca se exponen en logs
- Validación de configuración al inicio
- Manejo seguro de variables de entorno

Ver [CONFIGURACION.md](CONFIGURACION.md) para más detalles.

## Documentación Adicional

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)**: Documentación completa de todos los endpoints
- **[CONFIGURACION.md](CONFIGURACION.md)**: Configuración detallada de secrets y variables
- **[EVALUACION_RAG.md](EVALUACION_RAG.md)**: Estrategias completas de evaluación
- **[INICIAR_SISTEMA.md](INICIAR_SISTEMA.md)**: Guía paso a paso para iniciar
- **[EVALUACION_REQUERIMIENTOS.md](EVALUACION_REQUERIMIENTOS.md)**: Checklist de requerimientos

## Próximas Mejoras

- [ ] Autenticación de usuarios
- [ ] Soporte para más formatos (DOCX, HTML)
- [ ] Caché de respuestas frecuentes
- [ ] Evaluación automática con dataset de prueba
- [ ] Soporte para múltiples bases de datos vectoriales
- [ ] Dashboard de métricas en tiempo real
- [ ] API de streaming para respuestas
- [ ] Filtrado avanzado por metadata


---

**Documentación Interactiva**: http://localhost:8000/docs  
**Interfaz Web**: http://localhost:7860  
**Repositorio**: https://github.com/TU_USUARIO/rag-system-openai
