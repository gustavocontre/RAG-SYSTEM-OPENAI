"""
Colector de Métricas para el Sistema RAG
Recopila y analiza métricas de rendimiento, calidad y uso del sistema
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Colector de métricas para el sistema RAG"""
    
    def __init__(self, metrics_file: str = "./data/metrics.json"):
        """
        Inicializa el colector de métricas
        
        Args:
            metrics_file: Archivo donde guardar las métricas
        """
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics = {
            'queries': [],
            'system_stats': {},
            'aggregated': {}
        }
        self.load_metrics()
    
    def load_metrics(self):
        """Carga métricas desde archivo si existe"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    self.metrics = json.load(f)
            except Exception as e:
                logger.warning(f"Error cargando métricas: {e}")
                self.metrics = {'queries': [], 'system_stats': {}, 'aggregated': {}}
    
    def save_metrics(self):
        """Guarda métricas en archivo"""
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando métricas: {e}")
    
    def record_query(
        self,
        question: str,
        answer: str,
        sources: List[Dict],
        retrieval_time: float,
        generation_time: float,
        total_time: float,
        num_chunks: int,
        avg_score: Optional[float] = None
    ):
        """
        Registra una consulta y sus métricas
        
        Args:
            question: Pregunta del usuario
            answer: Respuesta generada
            sources: Lista de fuentes recuperadas
            retrieval_time: Tiempo de recuperación en segundos
            generation_time: Tiempo de generación en segundos
            total_time: Tiempo total en segundos
            num_chunks: Número de chunks recuperados
            avg_score: Score promedio de similitud (opcional)
        """
        query_metric = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'answer_length': len(answer),
            'question_length': len(question),
            'num_sources': len(sources),
            'num_chunks': num_chunks,
            'retrieval_time': retrieval_time,
            'generation_time': generation_time,
            'total_time': total_time,
            'avg_score': avg_score,
            'sources': sources
        }
        
        self.metrics['queries'].append(query_metric)
        self.save_metrics()
    
    def record_system_stats(
        self,
        total_chunks: int,
        unique_documents: int,
        db_size_mb: Optional[float] = None
    ):
        """
        Registra estadísticas del sistema
        
        Args:
            total_chunks: Número total de chunks
            unique_documents: Número de documentos únicos
            db_size_mb: Tamaño de la base de datos en MB
        """
        self.metrics['system_stats'] = {
            'timestamp': datetime.now().isoformat(),
            'total_chunks': total_chunks,
            'unique_documents': unique_documents,
            'db_size_mb': db_size_mb
        }
        self.save_metrics()
    
    def calculate_aggregated_metrics(self) -> Dict:
        """
        Calcula métricas agregadas de todas las consultas
        
        Returns:
            Diccionario con métricas agregadas
        """
        queries = self.metrics.get('queries', [])
        
        if not queries:
            return {
                'total_queries': 0,
                'message': 'No hay consultas registradas'
            }
        
        # Métricas de tiempo
        total_times = [q['total_time'] for q in queries]
        retrieval_times = [q['retrieval_time'] for q in queries]
        generation_times = [q['generation_time'] for q in queries]
        
        # Métricas de longitud
        answer_lengths = [q['answer_length'] for q in queries]
        question_lengths = [q['question_length'] for q in queries]
        
        # Métricas de recuperación
        num_chunks = [q['num_chunks'] for q in queries]
        num_sources = [q['num_sources'] for q in queries]
        avg_scores = [q['avg_score'] for q in queries if q['avg_score'] is not None]
        
        aggregated = {
            'total_queries': len(queries),
            'time_metrics': {
                'total_time': {
                    'mean': sum(total_times) / len(total_times),
                    'min': min(total_times),
                    'max': max(total_times),
                    'median': sorted(total_times)[len(total_times) // 2]
                },
                'retrieval_time': {
                    'mean': sum(retrieval_times) / len(retrieval_times),
                    'min': min(retrieval_times),
                    'max': max(retrieval_times),
                    'median': sorted(retrieval_times)[len(retrieval_times) // 2]
                },
                'generation_time': {
                    'mean': sum(generation_times) / len(generation_times),
                    'min': min(generation_times),
                    'max': max(generation_times),
                    'median': sorted(generation_times)[len(generation_times) // 2]
                }
            },
            'length_metrics': {
                'answer_length': {
                    'mean': sum(answer_lengths) / len(answer_lengths),
                    'min': min(answer_lengths),
                    'max': max(answer_lengths),
                    'median': sorted(answer_lengths)[len(answer_lengths) // 2]
                },
                'question_length': {
                    'mean': sum(question_lengths) / len(question_lengths),
                    'min': min(question_lengths),
                    'max': max(question_lengths),
                    'median': sorted(question_lengths)[len(question_lengths) // 2]
                }
            },
            'retrieval_metrics': {
                'num_chunks': {
                    'mean': sum(num_chunks) / len(num_chunks),
                    'min': min(num_chunks),
                    'max': max(num_chunks),
                    'median': sorted(num_chunks)[len(num_chunks) // 2]
                },
                'num_sources': {
                    'mean': sum(num_sources) / len(num_sources),
                    'min': min(num_sources),
                    'max': max(num_sources),
                    'median': sorted(num_sources)[len(num_sources) // 2]
                },
                'avg_score': {
                    'mean': sum(avg_scores) / len(avg_scores) if avg_scores else None,
                    'min': min(avg_scores) if avg_scores else None,
                    'max': max(avg_scores) if avg_scores else None,
                    'median': sorted(avg_scores)[len(avg_scores) // 2] if avg_scores else None
                }
            },
            'throughput': {
                'queries_per_second': len(queries) / sum(total_times) if sum(total_times) > 0 else 0
            }
        }
        
        self.metrics['aggregated'] = aggregated
        self.save_metrics()
        return aggregated
    
    def get_metrics_report(self) -> Dict:
        """
        Genera un reporte completo de métricas
        
        Returns:
            Diccionario con reporte completo
        """
        aggregated = self.calculate_aggregated_metrics()
        system_stats = self.metrics.get('system_stats', {})
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system_stats': system_stats,
            'query_metrics': aggregated,
            'recent_queries': self.metrics['queries'][-10:]  # Últimas 10 consultas
        }
    
    def clear_metrics(self):
        """Limpia todas las métricas"""
        self.metrics = {'queries': [], 'system_stats': {}, 'aggregated': {}}
        self.save_metrics()

