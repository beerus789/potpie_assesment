import logging
from app.celery_app import celery_app
from app.core.file_parser import FileParser
from app.core.embedder import Embedder
from app.core.db_client import ChromaDBClient
import os
import uuid
from datetime import datetime

logger = logging.getLogger("celery-task")

embedder = Embedder()
chroma_client = ChromaDBClient()
import app.core.file_parser as file_parser

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_task(self, file_path):
    try:
        logger.info(f"Processing document: {file_path}")
        # Check if the file exists
        normalized_path, ext = FileParser.validate_path(file_path)
        # text = FileParser.extract_text(normalized_path, ext)
        statinfo = os.stat(normalized_path)
        metadata = {
            "file_name": os.path.basename(normalized_path),
            "file_type": ext,
            "created_at": datetime.utcfromtimestamp(statinfo.st_ctime).isoformat() + "Z",
            "file_size": statinfo.st_size
        }
        # embeddings, texts = embedder.embed(text)
        asset_id = str(uuid.uuid4())
        chunkers = {
        "pdf": file_parser.pdf_file_chunks,
        "txt": file_parser.text_file_chunks,
        "docx": file_parser.docx_file_chunks
        }
        chunk_size = 2000  # adjust for your model

        chunks = []
        embeddings = []

        for chunk in chunkers[ext](normalized_path, chunk_size_words=chunk_size):
            emb = embedder.model.encode([chunk])[0]  # returns a numpy vector (for a single chunk)
            # Optionally: Store each embedding+chunk as you go to DB if you want real streaming!
            chunks.append(chunk)
            embeddings.append(emb.tolist())

        # After all chunks/embeddings are ready:
        chroma_client.store(asset_id, embeddings, chunks, metadata)
            # chroma_client.store(asset_id, embeddings, texts, metadata)
        logger.info(f"Document processed and stored with asset_id: {asset_id}")
        return asset_id
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise self.retry(exc=e, countdown=60)