# Documentación de API - Sistema RAG

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

Verifica el estado del servicio y la base de datos.

**Endpoint:** `GET /health`

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

**Ejemplo:**
```bash
curl http://localhost:8000/health
```

---

### 2. Subir Documento

Procesa y indexa un documento (PDF, TXT, MD) en la base de datos vectorial.

**Endpoint:** `POST /upload`

**Parámetros:**
- `file` (form-data): Archivo a subir (PDF, TXT, o MD)

**Respuesta:**
```json
{
  "doc_id": "doc_5b89c441ba45",
  "chunks_created": 120,
  "total_chars": 45678,
  "filename": "documento.pdf",
  "message": "Documento procesado exitosamente"
}
```

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@documento.pdf"
```

**Notas:**
- El documento se procesa en chunks de 500 caracteres (configurable)
- Se generan embeddings automáticamente
- Se almacena en ChromaDB con metadatos

---

### 3. Realizar Consulta RAG

Procesa una consulta en lenguaje natural y genera una respuesta usando RAG.

**Endpoint:** `POST /query`

**Body (JSON):**
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
- `return_sources` (bool, opcional): Si retornar información de fuentes (default: true)

**Respuesta:**
```json
{
  "answer": "Python es un lenguaje de programación...",
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

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué es Python?",
    "top_k": 5,
    "return_sources": true
  }'
```

**Proceso:**
1. Búsqueda semántica de chunks relevantes
2. Ranking por similitud (cosine similarity)
3. Generación de respuesta con GPT-4 usando contexto recuperado
4. Retorno de respuesta con fuentes

---

### 4. Listar Documentos

Obtiene la lista de documentos indexados en la base de datos.

**Endpoint:** `GET /documents`

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

**Ejemplo:**
```bash
curl http://localhost:8000/documents
```

---

### 5. Estadísticas de Base de Datos

Obtiene estadísticas de la base de datos vectorial.

**Endpoint:** `GET /stats`

**Respuesta:**
```json
{
  "total_chunks": 718,
  "unique_documents": 6
}
```

**Ejemplo:**
```bash
curl http://localhost:8000/stats
```

---

### 6. Eliminar Documento

Elimina un documento y todos sus chunks de la base de datos.

**Endpoint:** `DELETE /delete/{doc_id}`

**Parámetros:**
- `doc_id` (path): ID del documento a eliminar

**Respuesta:**
```json
{
  "message": "Documento doc_5b89c441ba45 eliminado exitosamente",
  "doc_id": "doc_5b89c441ba45"
}
```

**Ejemplo:**
```bash
curl -X DELETE "http://localhost:8000/delete/doc_5b89c441ba45"
```

---

### 7. Métricas del Sistema

Obtiene métricas de rendimiento del sistema RAG.

**Endpoint:** `GET /metrics`

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

**Ejemplo:**
```bash
curl http://localhost:8000/metrics
```

---

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | Éxito |
| 400 | Solicitud inválida |
| 404 | Recurso no encontrado |
| 500 | Error del servidor |

## Errores Comunes

### Error 400: Formato no soportado
```json
{
  "detail": "Formato no soportado. Formatos permitidos: .pdf, .txt, .md"
}
```

### Error 500: API key no configurada
```json
{
  "detail": "Error: API key de OpenAI no configurada o inválida. Verifica que OPENAI_API_KEY esté configurada."
}
```

### Error 500: Base de datos vacía
```json
{
  "detail": "Error: Base de datos vacía. Por favor sube al menos un documento primero."
}
```

## Documentación Interactiva

Accede a la documentación interactiva (Swagger) en:
```
http://localhost:8000/docs
```

O la documentación alternativa (ReDoc) en:
```
http://localhost:8000/redoc
```

## Ejemplos de Uso Completo

### Flujo completo: Subir documento y hacer consulta

```bash
# 1. Subir documento
curl -X POST "http://localhost:8000/upload" \
  -F "file=@python_tutorial.pdf"

# Respuesta:
# {
#   "doc_id": "doc_abc123",
#   "chunks_created": 120,
#   ...
# }

# 2. Hacer consulta
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Cómo definir una función en Python?",
    "top_k": 5
  }'

# 3. Ver estadísticas
curl http://localhost:8000/stats
```

## Autenticación

Actualmente no se requiere autenticación para los endpoints. Para producción, se recomienda implementar:

- API Keys
- OAuth 2.0
- JWT Tokens

