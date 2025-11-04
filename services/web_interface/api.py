"""
API REST para el sistema RAG
Interfaz web con FastAPI para procesamiento de documentos y consultas
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil
import logging
from pathlib import Path
import sys

# Agregar paths para imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, parent_dir)

# Cargar configuración centralizada
try:
    from config.settings import settings
    # Validar configuración al inicio
    is_valid, errors = settings.validate()
    if not is_valid:
        logger_init = logging.getLogger(__name__)
        logger_init.warning("=" * 60)
        logger_init.warning("ADVERTENCIA: Configuración inválida detectada")
        logger_init.warning("=" * 60)
        for error in errors:
            logger_init.warning(f"  - {error}")
        logger_init.warning("")
        logger_init.warning("Ejecuta: python scripts/setup_env.py para configurar")
        logger_init.warning("=" * 60)
except ImportError:
    # Fallback: cargar variables de entorno desde .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    settings = None

from services.document_processor.processor import DocumentProcessor
from services.rag_query.query_service import RAGQueryService
from services.metrics.metrics_collector import MetricsCollector
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="RAG System API",
    description="Sistema RAG para asistente de conocimiento para desarrolladores",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración
CHROMA_DB_DIR = Path("./data/chroma_db")
UPLOAD_DIR = Path("./data/uploaded_documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Inicializar servicios
processor = None
query_service = None
# Usar ruta absoluta para métricas
metrics_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "metrics.json")
metrics_collector = MetricsCollector(metrics_file=metrics_file)

def get_processor():
    """Lazy loading del procesador"""
    global processor
    if processor is None:
        processor = DocumentProcessor(
            persist_directory=str(CHROMA_DB_DIR)
        )
    return processor

def get_query_service():
    """Lazy loading del servicio de consultas"""
    global query_service
    if query_service is None:
        # Leer modelo desde variable de entorno o usar valor por defecto
        llm_model = os.getenv("LLM_MODEL", "gpt-4-turbo")
        query_service = RAGQueryService(
            persist_directory=str(CHROMA_DB_DIR),
            llm_model=llm_model
        )
    return query_service


# Modelos Pydantic para requests/responses
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    return_sources: bool = True

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    num_chunks: int

class ProcessingResponse(BaseModel):
    doc_id: str
    chunks_created: int
    total_chars: int
    filename: str
    message: str

class StatsResponse(BaseModel):
    total_chunks: int
    unique_documents: int


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "RAG System API",
        "version": "1.0.0",
        "endpoints": {
            "/docs": "Documentación interactiva (Swagger)",
            "/redoc": "Documentación alternativa (ReDoc)",
            "/health": "Health check",
            "/stats": "Estadísticas de la base de datos",
            "/documents": "Lista de documentos",
            "/upload": "POST - Subir y procesar documento",
            "/query": "POST - Realizar consulta",
            "/delete/{doc_id}": "DELETE - Eliminar documento",
            "/metrics": "GET - Ver métricas del sistema"
        }
    }


@app.get("/health")
async def health_check():
    """Health check del servicio"""
    try:
        proc = get_processor()
        stats = proc.get_stats()
        return {
            "status": "healthy",
            "database": {
                "connected": True,
                "chunks": stats['total_chunks'],
                "documents": stats['unique_documents']
            }
        }
    except Exception as e:
        logger.error(f"Health check fallido: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Obtiene estadísticas de la base de datos"""
    try:
        proc = get_processor()
        stats = proc.get_stats()
        
        # Actualizar métricas del sistema
        try:
            from pathlib import Path
            db_path = Path("./data/chroma_db")
            db_size_mb = sum(f.stat().st_size for f in db_path.rglob('*') if f.is_file()) / (1024 * 1024) if db_path.exists() else 0.0
            metrics_collector.record_system_stats(
                total_chunks=stats.get('total_chunks', 0),
                unique_documents=stats.get('unique_documents', 0),
                db_size_mb=db_size_mb
            )
        except Exception as metrics_error:
            logger.warning(f"Error actualizando métricas del sistema: {metrics_error}")
        
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload", response_model=ProcessingResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Sube y procesa un documento (PDF, TXT, MD)
    """
    # Validar tipo de archivo
    allowed_extensions = ['.pdf', '.txt', '.md']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado. Formatos permitidos: {', '.join(allowed_extensions)}"
        )
    
    # Guardar archivo temporalmente
    file_path = UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Archivo guardado: {file_path}")
        
        # Procesar documento
        proc = get_processor()
        result = proc.process_document(str(file_path))
        
        response = ProcessingResponse(
            **result,
            message="Documento procesado exitosamente"
        )
        
        logger.info(f"Documento procesado: {result['doc_id']}")
        return response
        
    except Exception as e:
        logger.error(f"Error procesando documento: {str(e)}")
        # Limpiar archivo si existe
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Realiza una consulta RAG
    """
    start_time = time.time()
    
    try:
        service = get_query_service()
        
        # Medir tiempo de recuperación
        retrieval_start = time.time()
        chunks = service.search_similar_chunks(
            request.question,
            top_k=request.top_k
        )
        retrieval_time = time.time() - retrieval_start
        
        # Calcular score promedio si hay chunks
        avg_score = None
        if chunks:
            scores = [chunk.get('score', 0) for chunk in chunks]
            avg_score = sum(scores) / len(scores) if scores else None
        
        # Medir tiempo de generación
        generation_start = time.time()
        
        # Si no hay chunks, retornar respuesta vacía
        if not chunks:
            result = {
                'answer': "No se encontró información relevante en la base de datos para responder a tu pregunta.",
                'sources': [],
                'num_chunks': 0
            }
        else:
            # Formatear contexto
            context = service.format_context(chunks)
            
            # Generar respuesta con LLM
            logger.info("Generando respuesta con LLM")
            answer = service.chain.invoke({
                "context": context,
                "question": request.question
            })
            
            # Eliminar emojis de la respuesta
            from services.rag_query.query_service import remove_emojis
            answer = remove_emojis(str(answer))
            
            # Preparar respuesta
            result = {
                'answer': answer,
                'num_chunks': len(chunks)
            }
            
            if request.return_sources:
                result['sources'] = [
                    {
                        'filename': chunk['metadata'].get('filename', 'unknown'),
                        'chunk_index': chunk['metadata'].get('chunk_index', -1),
                        'score': chunk['score']
                    }
                    for chunk in chunks
                ]
        
        generation_time = time.time() - generation_start
        total_time = time.time() - start_time
        
        # Registrar métricas
        try:
            metrics_collector.record_query(
                question=request.question,
                answer=result.get('answer', ''),
                sources=result.get('sources', []),
                retrieval_time=retrieval_time,
                generation_time=generation_time,
                total_time=total_time,
                num_chunks=result.get('num_chunks', 0),
                avg_score=avg_score
            )
        except Exception as metrics_error:
            logger.warning(f"Error registrando métricas: {metrics_error}")
        
        return QueryResponse(**result)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error procesando consulta: {error_msg}")
        
        # Mensajes de error más específicos
        if "OPENAI_API_KEY" in error_msg or "api key" in error_msg.lower():
            error_msg = "Error: API key de OpenAI no configurada o inválida. Verifica que OPENAI_API_KEY esté configurada."
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            error_msg = f"Error de conexión: {error_msg}"
        elif "no such collection" in error_msg.lower():
            error_msg = "Error: Base de datos vacía. Por favor sube al menos un documento primero."
        
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/documents")
async def get_documents():
    """Obtiene lista de documentos en la base"""
    try:
        service = get_query_service()
        doc_ids = service.get_all_documents()
        return {
            "documents": doc_ids,
            "count": len(doc_ids)
        }
    except Exception as e:
        logger.error(f"Error obteniendo documentos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """
    Obtiene métricas del sistema RAG
    """
    try:
        report = metrics_collector.get_metrics_report()
        return report
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete/{doc_id}")
async def delete_document(doc_id: str):
    """
    Elimina un documento y todos sus chunks
    """
    try:
        proc = get_processor()
        success = proc.delete_document(doc_id)
        
        if success:
            return {
                "message": f"Documento {doc_id} eliminado exitosamente",
                "doc_id": doc_id
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Documento {doc_id} no encontrado"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


