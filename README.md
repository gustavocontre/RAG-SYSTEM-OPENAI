# Sistema RAG - Asistente de Conocimiento para Desarrolladores

Sistema de Retrieval-Augmented Generation (RAG) que procesa documentación técnica, la indexa en una base de datos vectorial, y proporciona respuestas precisas a consultas utilizando LLMs. Incluye servicio de procesamiento de documentos, servicio de consultas RAG, interfaz web, y despliegue con Docker.

## 🎯 Características

- ✅ **Procesamiento de Documentos**: Soporta PDF, TXT, MD con chunking inteligente
- ✅ **Búsqueda Semántica**: Embeddings con Sentence-Transformers y ChromaDB
- ✅ **Generación de Respuestas**: Integración con OpenAI GPT-4-turbo
- ✅ **Interfaz Web**: Chat interactivo con Gradio
- ✅ **API REST**: Endpoints completos con documentación Swagger
- ✅ **Métricas y Evaluación**: Sistema de tracking y evaluación de rendimiento
- ✅ **Docker**: Contenerización completa con Docker Compose
- ✅ **Configuración Segura**: Manejo de secrets y variables de entorno

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Interfaz Web  │ (Gradio UI - Puerto 7860)
│   (Gradio)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API REST      │ (FastAPI - Puerto 8000)
│   /query        │
│   /upload       │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ ChromaDB │ │ OpenAI GPT-4 │
│ (Vectors)│ │ (LLM)        │
└─────────┘ └──────────────┘
```

### Componentes

1. **DocumentProcessor**: Procesa y chunking de documentos
2. **RAGQueryService**: Búsqueda semántica y generación de respuestas
3. **API REST**: FastAPI con endpoints para upload, query, stats
4. **Interfaz Web**: Gradio para interacción con usuarios
5. **MetricsCollector**: Sistema de métricas y evaluación

## 📋 Requisitos Previos

- Python 3.9+
- Docker y Docker Compose (opcional, para despliegue)
- API Key de OpenAI (obtener en https://platform.openai.com/api-keys)

## 🚀 Instalación y Configuración

### Opción 1: Instalación Local

#### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd RAG-system-openai
```

#### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 3. Configurar variables de entorno

**Método Rápido (Recomendado):**
```bash
python scripts/setup_env.py
```

**Método Manual:**
```bash
cp env.example .env
# Editar .env y configurar OPENAI_API_KEY
```

Más detalles en [CONFIGURACION.md](CONFIGURACION.md)

#### 4. Iniciar el sistema

**Terminal 1 - API Server:**
```bash
python -m services.web_interface.api
```

**Terminal 2 - Interfaz Web:**
```bash
python -m services.web_interface.gradio_ui
```

### Opción 2: Docker (Recomendado para Producción)

#### 1. Configurar variables de entorno

```bash
cp env.example .env
# Editar .env con tu OPENAI_API_KEY
```

#### 2. Iniciar con Docker Compose

```bash
docker-compose up -d
```

Esto iniciará:
- API en http://localhost:8000
- Interfaz Web en http://localhost:7860

#### 3. Ver logs

```bash
docker-compose logs -f
```

## 📖 Uso

### 1. Subir Documentos

**Desde la Interfaz Web:**
- Abre http://localhost:7860
- Usa la sección de "Subir Documento"
- Selecciona un archivo PDF, TXT o MD

**Desde la API:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@documento.pdf"
```

### 2. Hacer Consultas

**Desde la Interfaz Web:**
- Abre http://localhost:7860
- Escribe tu pregunta en el chat
- El sistema buscará información relevante y generará una respuesta

**Desde la API:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué es Python?",
    "top_k": 5,
    "return_sources": true
  }'
```

### 3. Ver Métricas

```bash
python scripts/generate_metrics_report.py
```

## 📚 Documentación

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)**: Documentación completa de endpoints
- **[CONFIGURACION.md](CONFIGURACION.md)**: Configuración de secrets y variables de entorno
- **[EVALUACION_RAG.md](EVALUACION_RAG.md)**: Estrategias de evaluación del sistema
- **[INICIAR_SISTEMA.md](INICIAR_SISTEMA.md)**: Guía paso a paso para iniciar
- **[EVALUACION_REQUERIMIENTOS.md](EVALUACION_REQUERIMIENTOS.md)**: Checklist de requerimientos

## 🔧 Stack Tecnológico

### Backend
- **Python 3.9+**: Lenguaje principal
- **FastAPI**: Framework web para API REST
- **LangChain**: Framework para aplicaciones LLM
- **ChromaDB**: Base de datos vectorial
- **Sentence-Transformers**: Modelo de embeddings
- **OpenAI GPT-4**: LLM para generación de respuestas

### Frontend
- **Gradio**: Interfaz web interactiva

### Infraestructura
- **Docker**: Contenerización
- **Docker Compose**: Orquestación de servicios

### Herramientas
- **python-dotenv**: Manejo de variables de entorno
- **PyPDF2**: Procesamiento de PDFs
- **Uvicorn**: Servidor ASGI

## 🏛️ Decisiones Arquitectónicas

### 1. Base de Datos Vectorial: ChromaDB

**Razón**: 
- Fácil de usar y configurar
- Persistencia local sin necesidad de servidor externo
- Buen rendimiento para bases pequeñas-medianas
- Soporte nativo para metadata filtering

**Alternativas consideradas**: Milvus, Pinecone, Weaviate

### 2. Modelo de Embeddings: Sentence-Transformers

**Razón**:
- Modelo local, no requiere API externa
- Buen balance entre calidad y velocidad
- Modelo `all-MiniLM-L6-v2` optimizado para velocidad

### 3. LLM: OpenAI GPT-4

**Razón**:
- Alta calidad de respuestas
- Buen entendimiento de contexto
- API estable y confiable
- Alternativa: GPT-3.5 (más rápido, menos costo)

### 4. Chunking Strategy

**Configuración**:
- `CHUNK_SIZE=500`: Balance entre contexto y precisión
- `CHUNK_OVERLAP=50`: Preserva contexto entre chunks
- Chunking por palabras (no por caracteres) para mejor calidad

### 5. Búsqueda Semántica

**Estrategia**:
- Cosine similarity para ranking
- Top-K retrieval (default: 5 chunks)
- Filtrado por metadata para búsquedas específicas

## 📊 Métricas y Evaluación

El sistema incluye un sistema completo de métricas:

- **Tiempos de respuesta**: Retrieval, generación, total
- **Scores de similitud**: Calidad de recuperación
- **Throughput**: Consultas por segundo
- **Estadísticas de uso**: Chunks, documentos, tamaño de BD

Ver [EVALUACION_RAG.md](EVALUACION_RAG.md) para más detalles.

## 🐛 Solución de Problemas

### Error: "OPENAI_API_KEY no está configurada"

1. Verifica que el archivo `.env` existe
2. Verifica que contiene `OPENAI_API_KEY=sk-...`
3. Ejecuta: `python scripts/check_config.py`

### Error: "Base de datos vacía"

1. Sube al menos un documento primero
2. Usa el endpoint `/upload` o la interfaz web

### Error: Puerto en uso

```bash
# Cambiar puerto en .env
API_PORT=8001
UI_PORT=7861
```

Más información en [INICIAR_SISTEMA.md](INICIAR_SISTEMA.md)

## 📝 Estructura del Proyecto

```
RAG-system-openai/
├── config/                 # Configuración centralizada
│   ├── settings.py         # Manejo de secrets y variables
│   └── __init__.py
├── services/               # Servicios principales
│   ├── document_processor/ # Procesamiento de documentos
│   ├── rag_query/          # Servicio de consultas RAG
│   ├── web_interface/      # API y UI
│   └── metrics/            # Sistema de métricas
├── scripts/                # Scripts utilitarios
│   ├── setup_env.py        # Configuración interactiva
│   ├── generate_metrics_report.py
│   └── check_config.py
├── docker/                 # Dockerfiles
│   ├── Dockerfile.api
│   └── Dockerfile.ui
├── data/                   # Datos (gitignored)
│   ├── chroma_db/         # Base de datos vectorial
│   └── uploaded_documents/ # Documentos subidos
├── docker-compose.yml      # Orquestación Docker
├── requirements.txt        # Dependencias Python
├── env.example            # Plantilla de variables de entorno
└── README.md              # Este archivo
```

## 🔒 Seguridad

- El archivo `.env` está en `.gitignore`
- Secrets nunca se exponen en logs
- Validación de configuración al inicio
- Más detalles en [CONFIGURACION.md](CONFIGURACION.md)

## 🚧 Próximas Mejoras

- [ ] Autenticación de usuarios
- [ ] Soporte para más formatos (DOCX, HTML)
- [ ] Caché de respuestas frecuentes
- [ ] Evaluación automática con dataset de prueba
- [ ] Soporte para múltiples bases de datos vectoriales
- [ ] Dashboard de métricas en tiempo real

## 📄 Licencia

Este proyecto es una prueba técnica para evaluación.

## 👤 Autor

Desarrollado como parte de la prueba técnica para AI Developer.

---

**Documentación Interactiva**: http://localhost:8000/docs  
**Interfaz Web**: http://localhost:7860
