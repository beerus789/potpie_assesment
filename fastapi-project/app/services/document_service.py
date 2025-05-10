import os
import uuid
from datetime import datetime

from app.core.file_parser import FileParser
from app.core.embedder import Embedder
from app.core.db_client import ChromaDBClient

embedder = Embedder()
chroma_client = ChromaDBClient()

def process_document(file_path: str) -> str:
    normalized_path, ext = FileParser.validate_path(file_path)
    text = FileParser.extract_text(normalized_path, ext)
    statinfo = os.stat(normalized_path)
    metadata = {
        "file_name": os.path.basename(normalized_path),
        "file_type": ext,
        "created_at": datetime.utcfromtimestamp(statinfo.st_ctime).isoformat() + "Z",
        "file_size": statinfo.st_size
    }
    embeddings, texts = embedder.embed(text)
    asset_id = str(uuid.uuid4())
    chroma_client.store(asset_id, embeddings, texts, metadata)
    return asset_id

def get_all_documents():
    return chroma_client.list_documents()

def list_chroma_files():
    chroma_dir = './chroma_migrated'
    if not os.path.exists(chroma_dir):
        return []
    files = []
    for root, dirs, filenames in os.walk(chroma_dir):
        for name in filenames:
            files.append(os.path.relpath(os.path.join(root, name), chroma_dir))
        for name in dirs:
            files.append(os.path.relpath(os.path.join(root, name), chroma_dir))
    return files