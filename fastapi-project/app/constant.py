from enum import Enum

# --------------------
# Prompt templates for LLM agents
# --------------------
custom_prompt = """
You are an intelligent assistant tasked with answering questions based on a provided document. The document may contain technical content (e.g., code, algorithms, technical specifications) or non-technical content (e.g., reports, manuals, general text). Use the following context from the document to answer the user’s question:

--------------------
{context}
--------------------

User Question: {question}

Instructions:
1. If the question is relevant to the document’s context, provide a precise, accurate, and concise answer. Adapt the response style to the document’s nature:
   - For technical content, include technical details, code snippets, or explanations as needed.
   - For non-technical content, use clear, accessible language suitable for the content.
2. If the question is unrelated to the document’s context (e.g., general knowledge, personal questions like "How are you?"), respond with: "The question is not related to the document’s context."
3. If no relevant information is found in the context to answer the question, respond with: "I can’t find an answer relevant to the provided document."

Your Answer:
"""
# System prompt for relevance agent
relevance_system_prompt = """
You are a helpful assistant. User provided question is {question}. Decide if the user's question can be answered using ONLY the provided document context.
If yes, respond with 'relevant'. If not, respond with 'irrelevant'.
"""
# System prompt for response agent
response_system_prompt = "You are a precise assistant. Use the document context to answer. If not answerable, reply: 'I can’t find an answer relevant to the provided document.' {custom_prompt}"

# --------------------
# Enum classes for file types, formats, and status
# --------------------
class FileType(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"

class FileExtension(str, Enum):
    PDF = ".pdf"
    TXT = ".txt"
    DOCX = ".docx"

class FileFormat(str, Enum):
    FILE_NAME = "file_name"
    FILE_TYPE = "file_type"
    CREATED_AT = "created_at"
    FILE_SIZE = "file_size"
    ASSET_ID = "asset_id"
    CHUNKS = "chunks"
    EMBEDDINGS = "embeddings"
    CHUNK_IDX = "chunk_idx"
    IDS = "ids"
    METADATAS = "metadatas"
    LAST_USED = "last_used"
    DOCUMENTS = "documents"
    FILTER = "filter"
    TASK_ID = "task_id"
    STATUS = "status"
    FILE = "file"
    TASKS = "tasks"

# --------------------
# Settings for file processing and Celery
# --------------------
class FILE_SETTINGS:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    SUPPORTED_FORMATS = {FileType.PDF, FileType.TXT, FileType.DOCX}  # Supported file types
    CHUNK_SIZE_WORDS = 2000  # Number of words per chunk; adjust for your model
    MODEL_NAME = (
        "all-MiniLM-L6-v2"  # Example model name; replace with your actual model
    )
    OPENAI_API_KEY = "OPENAI_API_KEY"  # .env variable name for OpenAI API key
    CHUNK_OVERLAP = 200  # Number of words to overlap between chunks
    CUDA = "cuda"  # Use "cuda" for GPU, "cpu" for CPU
    CPU = "cpu"  # Use "cuda" for GPU, "cpu" for CPU

class CELERY_SETTINGS:
    BROKER_URL = "redis://localhost:6379/0"  # Celery broker URL
    RESULT_BACKEND = "redis://localhost:6379/1"  # Celery result backend
    CELERY_TASK_TIME_LIMIT = 60 * 10  # 10 minutes
    CELERY_PROCESSOR = "doc_processor"

# --------------------
# Directory and file location enums
# --------------------
class DIRECTORY(str, Enum):
    UPLOAD = "uploads"
    EMBEDDINGS = "embeddings"
    CHUNKS = "chunks"
    METADATA = "metadata"
    ASSETS = "assets"
    LOGS = "logs"
    CHAT_HISTORIES = "chat_histories"
    CHROMA_DIR = "./chroma_migrated"
    THREAD_ASSET_MAP = "thread_asset_map.json"
    THREAD_ID = "thread_id"

# --------------------
# Model and chat enums
# --------------------
class OpenEnum(str, Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_32K = "gpt-4-32k"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4_TURBO_32K = "gpt-4-turbo-32k"

class ChatEnum(str, Enum):
    RELEVANT = "relevant"

class FileStatus(str, Enum):
    SUCCESS = "SUCCESS"
