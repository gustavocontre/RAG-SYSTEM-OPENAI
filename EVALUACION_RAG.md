# Estrategias de Evaluación del Sistema RAG

## 1. Métricas Implementadas

### 1.1 Métricas de Recuperación (Retrieval Metrics)

#### Score de Similitud
- **Métrica**: Cosine similarity entre query y chunks
- **Rango**: 0.0 - 1.0 (más alto = más relevante)
- **Implementación**: Calculado automáticamente en cada búsqueda
- **Umbral recomendado**: > 0.5 para chunks relevantes

#### Número de Chunks Recuperados
- **Métrica**: `top_k` chunks recuperados por consulta
- **Valor óptimo**: 3-5 chunks (balance entre contexto y ruido)
- **Configurable**: Variable `TOP_K_RESULTS` en `.env`

#### Tiempo de Recuperación
- **Métrica**: Tiempo de búsqueda semántica
- **Objetivo**: < 500ms para bases pequeñas (< 10K chunks)
- **Implementado**: Tracking automático en métricas

### 1.2 Métricas de Generación (Generation Metrics)

#### Tiempo de Generación
- **Métrica**: Tiempo de respuesta del LLM
- **Depende de**: 
  - Modelo usado (GPT-4 es más lento que GPT-3.5)
  - Longitud del contexto
  - Longitud de la respuesta

#### Longitud de Respuesta
- **Métrica**: Número de caracteres/tokens generados
- **Análisis**: Respuestas muy cortas pueden indicar falta de contexto

#### Calidad de Respuesta
- **Métrica**: Subjetiva, requiere evaluación humana
- **Indicadores**:
  - Relevancia al contexto
  - Coherencia
  - Precisión de información

### 1.3 Métricas del Sistema

#### Throughput
- **Métrica**: Consultas por segundo
- **Cálculo**: `total_queries / total_time`
- **Implementado**: En sistema de métricas

#### Tamaño de Base de Datos
- **Métrica**: Número de chunks y documentos
- **Monitoreo**: Endpoint `/stats`

## 2. Métodos de Evaluación

### 2.1 Evaluación Automática

#### Script de Métricas
```bash
python scripts/generate_metrics_report.py
```

Este script genera un reporte con:
- Tiempos promedio de respuesta
- Scores de similitud
- Estadísticas de uso
- Últimas 10 consultas

#### Métricas en Tiempo Real
- Endpoint `/metrics` para obtener métricas actuales
- Tracking automático en cada consulta

### 2.2 Evaluación Manual/Subjetiva

#### Checklist de Calidad

Para cada respuesta, evaluar:

1. **Relevancia** (0-5)
   - ¿La respuesta responde a la pregunta?
   - ¿La información es relevante?

2. **Precisión** (0-5)
   - ¿La información es correcta?
   - ¿Hay información incorrecta?

3. **Completitud** (0-5)
   - ¿La respuesta es completa?
   - ¿Falta información importante?

4. **Coherencia** (0-5)
   - ¿La respuesta es coherente?
   - ¿Tiene sentido?

### 2.3 Evaluación con Dataset de Prueba

#### Crear Dataset de Evaluación

1. **Preguntas de prueba** (test queries)
   - Preguntas sobre los documentos indexados
   - Respuestas esperadas conocidas

2. **Métricas de evaluación**:
   - **Precision@K**: ¿Están los chunks relevantes en los top K?
   - **Recall@K**: ¿Se recuperaron todos los chunks relevantes?
   - **MRR (Mean Reciprocal Rank)**: Posición del primer chunk relevante

#### Ejemplo de Dataset

```json
{
  "test_queries": [
    {
      "question": "¿Qué es Python?",
      "expected_chunks": ["doc1_chunk2", "doc2_chunk5"],
      "expected_answer_keywords": ["lenguaje", "programación", "interpretado"]
    }
  ]
}
```

## 3. Optimizaciones Basadas en Métricas

### 3.1 Si el Score de Similitud es Bajo (< 0.5)

**Problema**: Chunks recuperados no son relevantes

**Soluciones**:
- Ajustar `CHUNK_SIZE` (chunks más pequeños o más grandes)
- Cambiar modelo de embeddings
- Mejorar el preprocesamiento de texto

### 3.2 Si el Tiempo de Respuesta es Alto (> 5s)

**Problema**: Sistema lento

**Soluciones**:
- Reducir `TOP_K_RESULTS`
- Usar modelo más rápido (GPT-3.5 en lugar de GPT-4)
- Optimizar búsqueda vectorial (índices)
- Caché de embeddings

### 3.3 Si las Respuestas son Incompletas

**Problema**: Falta contexto

**Soluciones**:
- Aumentar `TOP_K_RESULTS`
- Aumentar `CHUNK_SIZE`
- Mejorar el prompt del LLM

## 4. Benchmarking

### 4.1 Métricas de Referencia

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

### 4.2 Comparación con Baselines

Comparar contra:
- **Baseline 1**: Sin RAG (solo LLM)
- **Baseline 2**: RAG con búsqueda exacta (no semántica)
- **Baseline 3**: RAG con modelo diferente

## 5. Monitoreo Continuo

### 5.1 Métricas a Monitorear

1. **Latencia**: Tiempo de respuesta por consulta
2. **Throughput**: Consultas procesadas por minuto
3. **Calidad**: Scores de similitud promedio
4. **Errores**: Tasa de errores por consulta
5. **Uso de recursos**: CPU, memoria, tokens de OpenAI

### 5.2 Alertas Recomendadas

- Tiempo de respuesta > 10s
- Score de similitud promedio < 0.4
- Tasa de errores > 5%
- Base de datos > 10GB

## 6. Herramientas de Evaluación

### 6.1 Scripts Disponibles

```bash
# Generar reporte de métricas
python scripts/generate_metrics_report.py

# Verificar configuración
python scripts/check_config.py

# Ver métricas en tiempo real
curl http://localhost:8000/metrics
```

### 6.2 Métricas Exportadas

Las métricas se guardan en:
- `data/metrics.json` - Datos raw
- `data/metrics_report.json` - Reporte formateado

## 7. Próximos Pasos para Mejora

1. **Implementar evaluación automática con dataset**
2. **A/B testing** de diferentes configuraciones
3. **Feedback loop** para mejorar basado en uso real
4. **Métricas de negocio** (satisfacción del usuario)
5. **Análisis de errores** comunes

## 8. Referencias

- [RAG Evaluation Best Practices](https://docs.langchain.com/docs/use-cases/question-answering/evaluation)
- [Vector Search Evaluation](https://www.pinecone.io/learn/vector-search-evaluation/)
- [LLM Evaluation Metrics](https://www.anthropic.com/research/evaluating-language-models)

