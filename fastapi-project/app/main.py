from fastapi import FastAPI
from app.api.endpoints.document import router as document_router

app = FastAPI()
app.include_router(document_router, prefix="/api")