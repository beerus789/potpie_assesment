from typing import List, Optional
from pydantic import BaseModel


class DocumentProcessRequest(BaseModel):
    file_path: str


class DocumentProcessResponse(BaseModel):
    asset_id: Optional[str] = None
    task_id: Optional[str] = None


class DocumentChunkInfo(BaseModel):
    chunk_id: str
    chunk_idx: int


class StoredDocumentInfo(BaseModel):
    asset_id: str
    file_name: str
    file_type: str
    file_size: int
    created_at: str
    chunks: List[DocumentChunkInfo]
