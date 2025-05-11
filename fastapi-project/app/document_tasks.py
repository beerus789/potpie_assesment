"""
Celery document processing task for RAG chatbot backend.
Handles file validation, chunking, embedding, and storage in ChromaDB.

This task is designed to be robust, maintainable, and easy for new developers to understand and extend.
"""
import logging
from app.celery_app import celery_app
from app.core.file_parser import FileParser
from app.core.embedder import Embedder
from app.core.db_client import ChromaDBClient
import os
import uuid
from datetime import datetime

# Set up logger for Celery tasks
logger = logging.getLogger("celery-task")

# Initialize embedder and database client once per worker process
embedder = Embedder()
chroma_client = ChromaDBClient()
import app.core.file_parser as file_parser


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_task(self, file_path):
    """
    Celery task to process a document for RAG ingestion.
    Steps:
        1. Validate file path and type.
        2. Extract file metadata.
        3. Chunk the file using the appropriate parser.
        4. Generate embeddings for each chunk.
        5. Store embeddings, chunks, and metadata in ChromaDB.
    Args:
        self: Celery task instance (for retries).
        file_path (str): Path to the document to process.
    Returns:
        str: Asset ID of the stored document in ChromaDB.
    Raises:
        Retries on failure, logs errors.
    """
    try:
        logger.info(f"Processing document: {file_path}")
        # Validate the file path and get extension
        normalized_path, ext = FileParser.validate_path(file_path)

        # Gather file metadata for traceability and search
        statinfo = os.stat(normalized_path)
        metadata = {
            "file_name": os.path.basename(normalized_path),
            "file_type": ext,
            "created_at": f"{datetime.utcfromtimestamp(statinfo.st_ctime).isoformat()}Z",
            "file_size": statinfo.st_size,
        }

        # Generate a unique asset ID for this document
        asset_id = str(uuid.uuid4())

        # Map file extensions to their chunking functions
        chunkers = {
            "pdf": file_parser.pdf_file_chunks,
            "txt": file_parser.text_file_chunks,
            "docx": file_parser.docx_file_chunks,
        }
        chunk_size = 2000  # Number of words per chunk; adjust for your model

        chunks = []
        embeddings = []

        # Chunk the document and embed each chunk
        for chunk in chunkers[ext](normalized_path, chunk_size_words=chunk_size):
            emb = embedder.model.encode([chunk])[0]  # Numpy vector for the chunk
            # Optionally: Store each embedding+chunk as you go for streaming ingestion
            chunks.append(chunk)
            embeddings.append(emb.tolist())

        # Store all embeddings, chunks, and metadata in ChromaDB
        chroma_client.store(asset_id, embeddings, chunks, metadata)
        logger.info(f"Document processed and stored with asset_id: {asset_id}")
        return asset_id
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60)
