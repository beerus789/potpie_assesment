import os
import uuid
from datetime import datetime
from app.constant import FileFormat, DIRECTORY
from app.core.file_parser import FileParser
from app.core.embedder import Embedder
from app.core.db_client import ChromaDBClient

embedder = Embedder()
chroma_client = ChromaDBClient()


def process_document(file_path: str) -> str:
    """
    Process a document: validate, extract text, embed, and store in ChromaDB.
    Returns the new asset_id.
    """
    normalized_path, ext = FileParser.validate_path(file_path)
    file_name = os.path.basename(normalized_path)
    # Check for duplicate file name in ChromaDB
    if chroma_client.file_exists(file_name):
        raise ValueError(f"Duplicate file name detected: {file_name}")
    text = FileParser.extract_text(normalized_path, ext)
    statinfo = os.stat(normalized_path)
    metadata = {
        FileFormat.FILE_NAME.value: file_name,
        FileFormat.FILE_TYPE.value: ext,
        FileFormat.CREATED_AT.value: datetime.utcfromtimestamp(statinfo.st_ctime).isoformat() + "Z",
        FileFormat.FILE_SIZE.value: statinfo.st_size,
    }
    embeddings, texts = embedder.embed(text)
    asset_id = str(uuid.uuid4())
    chroma_client.store(asset_id, embeddings, texts, metadata)
    return asset_id


from app.schemas.document import StoredDocumentInfo, DocumentChunkInfo


def get_all_documents():
    """
    Retrieve all documents and their chunks from ChromaDB, grouped by asset_id.
    Returns a list of StoredDocumentInfo objects.
    """
    results = chroma_client.list_documents()
    # Chroma returns {'ids': [...], 'metadatas': [...], ...}
    metadatas = results.get(FileFormat.METADATAS.value, [])
    ids = results.get(FileFormat.IDS.value, [])

    # Group by asset_id
    documents = {}
    for doc_id, m in zip(ids, metadatas):
        asset_id = m.get(FileFormat.ASSET_ID.value)
        if not asset_id:
            continue  # skip malformed
        if asset_id not in documents:
            documents[asset_id] = {
                FileFormat.ASSET_ID.value: asset_id,
                FileFormat.FILE_NAME.value: m.get(FileFormat.FILE_NAME.value),
                FileFormat.FILE_TYPE.value: m.get(FileFormat.FILE_TYPE.value),
                FileFormat.CREATED_AT.value: m.get(FileFormat.CREATED_AT.value),
                FileFormat.FILE_SIZE.value: m.get(FileFormat.FILE_SIZE.value),
                FileFormat.CHUNKS.value: [],
            }
        documents[asset_id][FileFormat.CHUNKS.value].append(
            DocumentChunkInfo(chunk_id=doc_id, chunk_idx=m.get(FileFormat.CHUNK_IDX, -1))
        )
    # Convert to list of StoredDocumentInfo
    return [StoredDocumentInfo(**doc) for doc in documents.values()]


def list_chroma_files():
    """
    List all files and directories in the ChromaDB persistent directory (for debugging/ops).
    """
    chroma_dir = DIRECTORY.CHROMA_DIR.value
    if not os.path.exists(chroma_dir):
        return []
    files = []
    for root, dirs, filenames in os.walk(chroma_dir):
        for name in filenames:
            files.append(os.path.relpath(os.path.join(root, name), chroma_dir))
        for name in dirs:
            files.append(os.path.relpath(os.path.join(root, name), chroma_dir))
    return files
