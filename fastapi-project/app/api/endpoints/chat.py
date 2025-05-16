# FastAPI endpoints for chat functionality (start, message, history, threads)
import json
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
import os, json

# Send a message to the chat thread and get a response
from app.core.rag_agent import is_question_relevant, stream_rag_response
from app.constant import DIRECTORY, FileFormat

# from app.core.rag_agent import RAGAgent
import logging
from app.limiter import limiter
from fastapi import Request

logger = logging.getLogger(__name__)
router = APIRouter()
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
    return {DIRECTORY.THREAD_ID.value: thread_id}


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

    # [1] Retrieve context
    # [1] Retrieve context
    docs = retriever.get_relevant_documents(message)
    context = "\n\n".join([getattr(doc, "page_content", str(doc)) for doc in docs[:2]])

    if not context.strip():

        async def response_stream():
            yield "No relevant document context found for this thread. Please upload a document or check your thread."

        return StreamingResponse(response_stream(), media_type="application/json")

    meta_questions = [
        "what kind of question is relevant",
        "how to use",
        "what can you answer",
    ]
    if any(q in message.lower() for q in meta_questions):

        async def response_stream():
            yield (
                "You can ask any question that can be answered using the uploaded document. "
                "For example: 'Summarize this document', 'What kind of data contain in file?', or what this file is about ?."
            )

        return StreamingResponse(response_stream(), media_type="application/json")

    # [2] Check relevance
    is_relevant = await is_question_relevant(context, message)

    async def response_stream():
        try:
            if not is_relevant:
                logger.info(
                    f"[STREAM] Question unrelated. Sending fallback for thread_id={thread_id}"
                )
                answer = "The question is not related to the document’s context."
                yield answer
            else:
                answer = ""
                async for token in stream_rag_response(context, message):
                    answer += token
                    yield token
                add_message(thread_id, answer, sender="agent")
                logger.info(f"[STREAM] Streaming complete for thread_id={thread_id}")
        except Exception as ex:
            logger.error(f"[STREAM] Streaming response error: {ex}")
            yield "Agent error: problem generating answer."
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

    _THREAD_DB = DIRECTORY.THREAD_ASSET_MAP.value
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
        out.append(
            {
                DIRECTORY.THREAD_ID.value: tid,
                FileFormat.ASSET_ID.value: raw[FileFormat.ASSET_ID.value],
                FileFormat.CREATED_AT.value: raw.get(FileFormat.CREATED_AT.value, ""),
                FileFormat.LAST_USED.value: raw.get(FileFormat.LAST_USED.value, ""),
            }
        )
    # Optionally sort by last_used newest first
    out.sort(key=lambda x: x[FileFormat.LAST_USED.value], reverse=True)
    return out
