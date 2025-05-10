from pydantic import BaseModel

class DocumentProcessRequest(BaseModel):
    file_path: str

class DocumentProcessResponse(BaseModel):
    asset_id: str