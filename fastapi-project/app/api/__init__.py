# # File: /fastapi-project/fastapi-project/app/api/__init__.py

# from fastapi import APIRouter
# from .endpoints import *  # Import all endpoints to register them with the router

# router = APIRouter()
# api_router = router  # Expose the router as api_router for import in app/__init__.py

from fastapi import APIRouter
from .endpoints import document_router  # from endpoints/__init__.py

api_router = APIRouter()
api_router.include_router(document_router)