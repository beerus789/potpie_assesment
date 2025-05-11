# File: /fastapi-project/fastapi-project/app/api/__init__.py

# This file sets up the main API router for the FastAPI app.
# It imports and includes endpoint routers (e.g., document, chat) for modular API structure.

from fastapi import APIRouter
from .endpoints import document_router  # from endpoints/__init__.py

api_router = APIRouter()
api_router.include_router(document_router)
# To add more endpoints, import and include them here, e.g.:
# from .endpoints import chat_router
# api_router.include_router(chat_router)
