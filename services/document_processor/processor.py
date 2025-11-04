"""
Servicio de Procesamiento de Documentos
Procesa documentos (PDF, TXT, MD), genera chunks y embeddings, 
y almacena vectores en la base de datos vectorial
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path
import PyPDF2
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Procesador de documentos para el sistema RAG"""
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        persist_directory: str = "./data/chroma_db",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        Inicializa el procesador de documentos
        
        Args:
            embedding_model: Modelo de embeddings a usar
            persist_directory: Directorio para persistir ChromaDB
            chunk_size: Tamaño de chunks de texto
            chunk_overlap: Overlap entre chunks
        """
        self.embedding_model = embedding_model
        self.persist_directory = persist_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Cargar modelo de embeddings
        logger.info(f"Cargando modelo de embeddings: {embedding_model}")
        self.model = SentenceTransformer(embedding_model)
        
        # Inicializar ChromaDB
        logger.info(f"Inicializando ChromaDB en {persist_directory}")
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Obtener o crear colección
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("DocumentProcessor inicializado correctamente")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrae texto de un archivo PDF
        
        Args:
            pdf_path: Ruta del archivo PDF
            
        Returns:
            Texto extraído del PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    text += f"\n--- Página {page_num + 1} ---\n"
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error al leer PDF {pdf_path}: {str(e)}")
            raise
    
    def read_text_file(self, file_path: str) -> str:
        """
        Lee contenido de un archivo de texto
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Contenido del archivo
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def chunk_text(self, text: str, doc_id: str) -> List[Dict]:
        """
        Divide el texto en chunks
        
        Args:
            text: Texto a dividir
            doc_id: ID del documento
            
        Returns:
            Lista de chunks con metadatos
        """
        chunks = []
        words = text.split()
        
        # Crear chunks solapados
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_text.strip()) > 0:
                chunks.append({
                    'text': chunk_text,
                    'doc_id': doc_id,
                    'chunk_index': len(chunks),
                    'start_word': i,
                    'end_word': min(i + self.chunk_size, len(words))
                })
        
        return chunks
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de textos
        
        Args:
            texts: Lista de textos
            
        Returns:
            Lista de embeddings
        """
        logger.info(f"Generando {len(texts)} embeddings")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
    
    def process_document(self, file_path: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Procesa un documento completo: extrae, chunkea, genera embeddings y almacena
        
        Args:
            file_path: Ruta del documento
            metadata: Metadatos adicionales del documento
            
        Returns:
            Información del procesamiento
        """
        logger.info(f"Procesando documento: {file_path}")
        
        # Generar ID único para el documento
        file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
        doc_id = f"doc_{file_hash[:12]}"
        
        # Extraer texto según tipo de archivo
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_extension in ['.txt', '.md']:
            text = self.read_text_file(file_path)
        else:
            raise ValueError(f"Formato no soportado: {file_extension}")
        
        logger.info(f"Texto extraído: {len(text)} caracteres")
        
        # Crear chunks
        chunks = self.chunk_text(text, doc_id)
        logger.info(f"Creados {len(chunks)} chunks")
        
        # Generar embeddings
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = self.generate_embeddings(chunk_texts)
        
        # Preparar metadatos para ChromaDB
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                'doc_id': doc_id,
                'chunk_index': chunk['chunk_index'],
                'filename': Path(file_path).name,
                'file_path': file_path
            }
            
            if metadata:
                chunk_metadata.update(metadata)
            
            metadatas.append(chunk_metadata)
            ids.append(f"{doc_id}_chunk_{chunk['chunk_index']}")
        
        # Almacenar en ChromaDB
        logger.info("Almacenando en ChromaDB")
        self.collection.add(
            embeddings=embeddings,
            documents=chunk_texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Documento procesado y almacenado: {doc_id}")
        
        return {
            'doc_id': doc_id,
            'chunks_created': len(chunks),
            'total_chars': len(text),
            'filename': Path(file_path).name
        }
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Elimina un documento y todos sus chunks de la base de datos
        
        Args:
            doc_id: ID del documento
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            # Obtener todos los chunks del documento
            results = self.collection.get(
                where={"doc_id": doc_id}
            )
            
            if results and results['ids']:
                # Eliminar chunks
                self.collection.delete(ids=results['ids'])
                logger.info(f"Documento {doc_id} eliminado ({len(results['ids'])} chunks)")
                return True
            else:
                logger.warning(f"No se encontraron chunks para el documento {doc_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error al eliminar documento {doc_id}: {str(e)}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas de la base de datos vectorial
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Optimización: usar count() directamente sin iterar todos los documentos
            count = self.collection.count()
            unique_docs = set()
            
            # Optimización: usar peek con límite más pequeño y manejo de errores mejorado
            try:
                # Limitar a 500 documentos para contar docs únicos (más rápido)
                results = self.collection.peek(limit=500)
                if results and results.get('metadatas'):
                    unique_docs = set([m.get('doc_id') for m in results['metadatas'] if m and m.get('doc_id')])
            except Exception as e:
                logger.warning(f"Error obteniendo documentos únicos: {str(e)}")
                # Si falla, usar count aproximado
                unique_docs = set()
            
            return {
                'total_chunks': count,
                'unique_documents': len(unique_docs)
            }
        except Exception as e:
            # Si hay un error de esquema incompatible, intentar resetear la base de datos
            error_msg = str(e).lower()
            if "no such column" in error_msg or "schema" in error_msg:
                logger.warning(f"Esquema de base de datos incompatible: {str(e)}")
                logger.info("Intentando resetear la base de datos...")
                try:
                    # Intentar resetear la base de datos
                    self.client.reset()
                    # Recrear la colección
                    self.collection = self.client.get_or_create_collection(
                        name="documents",
                        metadata={"hnsw:space": "cosine"}
                    )
                    logger.info("Base de datos reseteada correctamente")
                    return {
                        'total_chunks': 0,
                        'unique_documents': 0
                    }
                except Exception as reset_error:
                    logger.error(f"Error al resetear base de datos: {str(reset_error)}")
                    raise
            else:
                raise


def main():
    """Función principal para testing"""
    processor = DocumentProcessor()
    
    # Ejemplo de procesamiento de un documento
    # processor.process_document("path/to/document.pdf")
    
    stats = processor.get_stats()
    print(f"Estadísticas: {stats}")


if __name__ == "__main__":
    main()


