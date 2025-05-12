# FastAPI endpoints for chat functionality (start, message, history, threads)
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat import StartChatRequest, StartChatResponse, SendMessageRequest
from app.services.chat_manager import (
    update_last_used,
    validate_asset_id,
    create_chat_thread,
    get_asset_id_for_thread,
)
from app.services.history import add_message, get_history
from app.core.chroma import ChromaDBClient
from app.core.rag_agent import RAGAgent
import logging
from app.limiter import limiter
from fastapi import Request

logger = logging.getLogger(__name__)
router = APIRouter()
rag_agent = RAGAgent()
chroma_client = ChromaDBClient()

# Start a new chat thread for a given asset/document
@router.post("/chat/start", response_model=StartChatResponse)
@limiter.limit("5/minute")
async def start_chat(request: Request, req: StartChatRequest):
    asset_id = req.asset_id
    if not asset_id:
        raise HTTPException(status_code=400, detail="Missing or invalid asset ID")
    if not validate_asset_id(asset_id):
        logger.warning(f"Asset ID not found: {asset_id}")
        raise HTTPException(status_code=404, detail="Asset ID not found in database")
    thread_id = create_chat_thread(asset_id)
    return {"thread_id": thread_id}

# Send a message to a chat thread and stream the agent's response
@router.post("/chat/message")
@limiter.limit("30/minute")
async def send_message(request: Request, req: SendMessageRequest):
    thread_id = req.thread_id
    message = req.message
    if not thread_id or not message:
        raise HTTPException(status_code=400, detail="Missing thread ID or message")
    try:
        asset_id = get_asset_id_for_thread(thread_id)
        if not asset_id:
            logger.warning(f"Thread ID not found: {thread_id}")
            raise HTTPException(status_code=404, detail="Thread ID not found")
    except Exception as e:
        logger.error(f"Error fetching thread/asset ID: {e}")
        raise HTTPException(status_code=404, detail="Thread ID not found")

    update_last_used(thread_id)
    add_message(thread_id, message, sender="user")
    retriever = chroma_client.get_retriever(asset_id)

    async def response_stream():
        logger.info(
            f"[STREAM] Starting streaming response for thread_id={thread_id}, asset_id={asset_id}"
        )
        answer = ""
        try:
            async for token in rag_agent.rag_answer_stream(retriever, message):
                answer += token
                logger.info(f"[STREAM] Yielding token: {token}")
                yield f"{token}"
            add_message(thread_id, answer, sender="agent")
            logger.info(f"[STREAM] Streaming complete for thread_id={thread_id}")
        except Exception as ex:
            logger.error(f"[STREAM] Streaming response error: {ex}")
            yield '{"response": "Agent error: problem generating answer."}\n'
        finally:
            logger.info(
                f"[STREAM] Streaming response generator finished for thread_id={thread_id}"
            )
    return StreamingResponse(response_stream(), media_type="application/json")

# Get chat history for a thread
@router.get("/chat/history")
@limiter.limit("3/minute")
async def chat_history(request: Request, thread_id: str):
    if not thread_id:
        raise HTTPException(status_code=400, detail="Missing thread ID")
    try:
        history = get_history(thread_id)
        if not history:
            logger.warning(f"History not found for thread: {thread_id}")
            raise HTTPException(status_code=404, detail="Thread ID not found")
        update_last_used(thread_id)
        return history
    except Exception as e:
        logger.error(f"Error loading history for thread {thread_id}: {e}")
        raise HTTPException(status_code=404, detail="Thread ID not found")

# List all chat threads, optionally filtered by asset_id
@router.get("/chat/threads")
@limiter.limit("60/minute")
async def list_threads(request: Request, asset_id: str = None):
    """
    List all chat threads. If asset_id is provided, filter threads for that asset only.
    Returns: List of {"thread_id": str, "asset_id": str, "created_at": str, "last_used": str}
    """
    import os, json
    _THREAD_DB = "thread_asset_map.json"
    if not os.path.exists(_THREAD_DB):
        return []
    try:
        with open(_THREAD_DB, "r") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error reading thread-asset map: {e}")
        return []
    out = []
    for tid, raw in data.items():
        if asset_id and raw["asset_id"] != asset_id:
            continue
        out.append({
            "thread_id": tid,
            "asset_id": raw["asset_id"],
            "created_at": raw.get("created_at", ""),
            "last_used": raw.get("last_used", ""),
        })
    # Optionally sort by last_used newest first
    out.sort(key=lambda x: x["last_used"], reverse=True)
    return out
