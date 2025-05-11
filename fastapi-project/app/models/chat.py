from typing import List
from pydantic import BaseModel

class StartChatRequest(BaseModel):
    asset_id: str

class StartChatResponse(BaseModel):
    thread_id: str

class SendMessageRequest(BaseModel):
    thread_id: str
    message: str

class ChatMessage(BaseModel):
    message: str
    sender: str   # 'user' or 'agent'
    timestamp: str