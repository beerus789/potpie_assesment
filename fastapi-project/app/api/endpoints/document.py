import os
from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.document import DocumentProcessRequest, DocumentProcessResponse
from app.services.document_service import get_all_documents, list_chroma_files

from fastapi import APIRouter, HTTPException
from app.schemas.document import DocumentProcessRequest, DocumentProcessResponse
from app.document_tasks import process_document_task
from celery.result import AsyncResult
from app.limiter import limiter
from fastapi import Request

router = APIRouter()

@router.post("/documents/process", response_model=DocumentProcessResponse)
@limiter.limit("20/minute")
async def process_document_endpoint(request:Request ,body: DocumentProcessRequest):
    task = process_document_task.delay(body.file_path)
    # Return a response with task_id for async processing
    return {"task_id": task.id, "asset_id": None}

@router.get("/documents/status/{task_id}")
@limiter.limit("10/minute")
async def get_status(request: Request, task_id: str):
    result = AsyncResult(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    if result.status == "SUCCESS":
        return {"status": result.status, "asset_id": result.result}
    return {"status": result.status}

from app.schemas.document import (
    DocumentProcessRequest, DocumentProcessResponse, StoredDocumentInfo
)

@router.get('/documents/list', response_model=List[StoredDocumentInfo])
@limiter.limit("10/minute")
async def list_documents_endpoint(request: Request):
    try:
        return get_all_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/chroma/files')
async def list_chroma_files_endpoint():
    try:
        return list_chroma_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx"}

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
        raise HTTPException(status_code=400, detail="No supported files found in folder.")
    # Queue Celery tasks
    tasks = []
    for file_path in all_files:
        task = process_document_task.delay(file_path)
        tasks.append({"file": file_path, "task_id": task.id})
    return {"tasks": tasks}