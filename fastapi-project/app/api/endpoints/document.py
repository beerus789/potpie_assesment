from fastapi import APIRouter, HTTPException, status
from app.schemas.document import DocumentProcessRequest, DocumentProcessResponse
from app.services.document_service import process_document, get_all_documents, list_chroma_files

router = APIRouter()

@router.post('/documents/process', response_model=DocumentProcessResponse)
async def process_document_endpoint(request: DocumentProcessRequest):
    try:
        asset_id = process_document(request.file_path)
        return {"asset_id": asset_id}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.get('/documents/list')
async def list_documents_endpoint():
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