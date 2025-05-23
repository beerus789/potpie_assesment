# FastAPI endpoints for document processing, status, listing, and folder ingestion
import os
from typing import List
from fastapi import APIRouter, HTTPException, Request
from app.schemas.document import DocumentProcessRequest, DocumentProcessResponse
from app.services.document_service import get_all_documents, list_chroma_files
from app.document_tasks import process_document_task
from celery.result import AsyncResult
from app.limiter import limiter
from app.constant import FileFormat, FileExtension, FileStatus

router = APIRouter()


# Endpoint to process a single document (async via Celery)
@router.post("/documents/process", response_model=DocumentProcessResponse)
@limiter.limit("20/minute")
async def process_document_endpoint(request: Request, body: DocumentProcessRequest):
    task = process_document_task.delay(body.file_path)
    # Return a response with task_id for async processing
    return {FileFormat.TASK_ID.value: task.id, FileFormat.ASSET_ID.value: None}


# Endpoint to check the status of a Celery document processing task
@router.get("/documents/status/{task_id}")
@limiter.limit("10/minute")
async def get_status(request: Request, task_id: str):
    result = AsyncResult(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    if result.status == FileStatus.SUCCESS.value:
        return {
            FileFormat.STATUS.value: result.status,
            FileFormat.ASSET_ID.value: result.result,
        }
    return {FileFormat.STATUS.value: result.status}


from app.schemas.document import (
    DocumentProcessRequest,
    DocumentProcessResponse,
    StoredDocumentInfo,
)


# Endpoint to list all stored documents (from ChromaDB)
@router.get("/documents/list", response_model=List[StoredDocumentInfo])
@limiter.limit("10/minute")
async def list_documents_endpoint(request: Request):
    try:
        return get_all_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


# Endpoint to list raw ChromaDB files (for debugging/ops)
@router.get("/chroma/files")
async def list_chroma_files_endpoint():
    try:
        return list_chroma_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")


# Supported file extensions for folder ingestion
SUPPORTED_EXTENSIONS = {
    FileExtension.PDF.value,
    FileExtension.TXT.value,
    FileExtension.DOCX.value,
}


# Endpoint to process all supported files in a folder (async via Celery)
@router.post("/documents/process_folder")
@limiter.limit("10/minute")
async def process_folder(request: Request, body: DocumentProcessRequest):
    folder_path = body.file_path
    if not folder_path or not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail="Invalid or missing folder path.")
    # Find all supported files, optionally recursively (use os.walk for recursive)
    all_files = []
    for root, dirs, files in os.walk(folder_path):
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                full_path = os.path.abspath(os.path.join(root, name))
                all_files.append(full_path)
    if not all_files:
        raise HTTPException(
            status_code=400, detail="No supported files found in folder."
        )
    # Queue Celery tasks for each file
    tasks = []
    for file_path in all_files:
        task = process_document_task.delay(file_path)
        tasks.append(
            {FileFormat.FILE.value: file_path, FileFormat.TASK_ID.value: task.id}
        )
    return {FileFormat.TASKS.value: tasks}
