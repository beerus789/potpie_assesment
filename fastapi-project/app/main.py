from fastapi import FastAPI
from app.api.endpoints.document import router as document_router

# from app.api import api_router
from app.api.endpoints.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# from app.limiter import limiter
app = FastAPI()
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.limiter import limiter

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# Allow all origins for local testing (change in production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:8080"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(document_router, prefix="/api")
# app.include_router(api_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

# Serve static files from the correct directory
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
