# Contents of the file: /fastapi-project/fastapi-project/app/api/endpoints/__init__.py

from fastapi import APIRouter
from .document import router as document_router

router = APIRouter()

# Here you can define your API endpoints
# Example:
# @router.get("/items/")
# async def read_items():
#     return [{"item_id": "foo"}, {"item_id": "bar"}]

# Include your endpoint routers here
# from . import some_endpoint_file
# router.include_router(some_endpoint_file.router)
