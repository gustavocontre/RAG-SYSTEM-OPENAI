"""
Script para generar reporte de métricas del sistema RAG
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Agregar paths para imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from services.metrics.metrics_collector import MetricsCollector
from services.document_processor.processor import DocumentProcessor
from services.rag_query.query_service import RAGQueryService

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def format_float(value, decimals=3):
    """Formatea un valor float"""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def format_time(seconds):
    """Formatea tiempo en segundos a formato legible"""
    if seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    return f"{seconds:.3f} s"


def get_db_size_mb(db_path: str) -> float:
    """Calcula el tamaño de la base de datos en MB"""
    try:
        total_size = 0
        db_path = Path(db_path)
        if db_path.exists():
            for file in db_path.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size
        return total_size / (1024 * 1024)
    except Exception:
        return 0.0


def print_report(report: dict):
    """Imprime un reporte formateado"""
    print("\n" + "="*80)
    print("REPORTE DE MÉTRICAS - SISTEMA RAG OpenAI")
    print("="*80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Estadísticas del sistema
    system_stats = report.get('system_stats', {})
    print("[ESTADISTICAS DEL SISTEMA]")
    print("-" * 80)
    print(f"  Total de chunks:           {system_stats.get('total_chunks', 0):,}")
    print(f"  Documentos unicos:         {system_stats.get('unique_documents', 0):,}")
    if system_stats.get('db_size_mb'):
        print(f"  Tamano de BD:              {format_float(system_stats.get('db_size_mb'), 2)} MB")
    print()
    
    # Métricas de consultas
    query_metrics = report.get('query_metrics', {})
    total_queries = query_metrics.get('total_queries', 0)
    
    if total_queries == 0:
        print("[ADVERTENCIA] No hay consultas registradas aun.")
        print("   Realiza algunas consultas para generar metricas.")
        print()
        return
    
    print(f"[METRICAS DE CONSULTAS] (Total: {total_queries})")
    print("-" * 80)
    
    # Métricas de tiempo
    time_metrics = query_metrics.get('time_metrics', {})
    print("\n[TIMPOS DE RESPUESTA]:")
    for metric_name, values in time_metrics.items():
        print(f"\n  {metric_name.replace('_', ' ').title()}:")
        print(f"    Promedio:  {format_time(values.get('mean', 0))}")
        print(f"    Mínimo:    {format_time(values.get('min', 0))}")
        print(f"    Máximo:    {format_time(values.get('max', 0))}")
        print(f"    Mediana:   {format_time(values.get('median', 0))}")
    
    # Métricas de longitud
    length_metrics = query_metrics.get('length_metrics', {})
    print("\n[LONGITUD DE RESPUESTAS]:")
    answer_metrics = length_metrics.get('answer_length', {})
    print(f"    Promedio:  {int(answer_metrics.get('mean', 0)):,} caracteres")
    print(f"    Minimo:    {int(answer_metrics.get('min', 0)):,} caracteres")
    print(f"    Maximo:    {int(answer_metrics.get('max', 0)):,} caracteres")
    print(f"    Mediana:   {int(answer_metrics.get('median', 0)):,} caracteres")
    
    # Métricas de recuperación
    retrieval_metrics = query_metrics.get('retrieval_metrics', {})
    print("\n[METRICAS DE RECUPERACION]:")
    chunks_metrics = retrieval_metrics.get('num_chunks', {})
    print(f"  Chunks recuperados por consulta:")
    print(f"    Promedio:  {format_float(chunks_metrics.get('mean', 0), 1)}")
    print(f"    Mínimo:    {int(chunks_metrics.get('min', 0))}")
    print(f"    Máximo:    {int(chunks_metrics.get('max', 0))}")
    print(f"    Mediana:   {format_float(chunks_metrics.get('median', 0), 1)}")
    
    sources_metrics = retrieval_metrics.get('num_sources', {})
    print(f"  Fuentes recuperadas por consulta:")
    print(f"    Promedio:  {format_float(sources_metrics.get('mean', 0), 1)}")
    print(f"    Mínimo:    {int(sources_metrics.get('min', 0))}")
    print(f"    Máximo:    {int(sources_metrics.get('max', 0))}")
    print(f"    Mediana:   {format_float(sources_metrics.get('median', 0), 1)}")
    
    score_metrics = retrieval_metrics.get('avg_score', {})
    if score_metrics.get('mean') is not None:
        print(f"  Score promedio de similitud:")
        print(f"    Promedio:  {format_float(score_metrics.get('mean', 0))}")
        print(f"    Mínimo:    {format_float(score_metrics.get('min', 0))}")
        print(f"    Máximo:    {format_float(score_metrics.get('max', 0))}")
        print(f"    Mediana:   {format_float(score_metrics.get('median', 0))}")
    
    # Throughput
    throughput = query_metrics.get('throughput', {})
    print("\n[RENDIMIENTO]:")
    qps = throughput.get('queries_per_second', 0)
    print(f"    Consultas por segundo: {format_float(qps, 3)}")
    
    # Últimas consultas
    recent_queries = report.get('recent_queries', [])
    if recent_queries:
        print("\n[ULTIMAS 10 CONSULTAS]:")
        print("-" * 80)
        for i, query in enumerate(recent_queries[-10:], 1):
            timestamp = query.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            print(f"\n  {i}. [{timestamp}]")
            question = query.get('question', '')[:60]
            print(f"     Pregunta: {question}{'...' if len(query.get('question', '')) > 60 else ''}")
            print(f"     Tiempo: {format_time(query.get('total_time', 0))}")
            print(f"     Chunks: {query.get('num_chunks', 0)}")
            print(f"     Longitud respuesta: {query.get('answer_length', 0):,} caracteres")
    
    print("\n" + "="*80)
    print()


def main():
    """Función principal"""
    print("Generando reporte de métricas...")
    print()
    
    # Inicializar colector de métricas
    metrics_collector = MetricsCollector()
    
    # Obtener estadísticas del sistema
    try:
        processor = DocumentProcessor()
        stats = processor.get_stats()
        db_size = get_db_size_mb("./data/chroma_db")
        
        metrics_collector.record_system_stats(
            total_chunks=stats.get('total_chunks', 0),
            unique_documents=stats.get('unique_documents', 0),
            db_size_mb=db_size
        )
    except Exception as e:
        print(f"⚠️  Advertencia: No se pudieron obtener estadísticas del sistema: {e}")
    
    # Generar reporte
    report = metrics_collector.get_metrics_report()
    
    # Imprimir reporte
    print_report(report)
    
    # Guardar reporte en JSON
    report_file = Path("./data/metrics_report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Reporte guardado en: {report_file}")
    print()


if __name__ == "__main__":
    main()

