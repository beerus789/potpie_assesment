import uuid
from app.core.chroma import ChromaDBClient

chroma_client = ChromaDBClient()

# services/chat_manager.py

from datetime import datetime
import os, json

_THREAD_DB = "thread_asset_map.json"

def update_last_used(thread_id):
    if not os.path.exists(_THREAD_DB):
        return
    with open(_THREAD_DB, 'r') as f:
        data = json.load(f)
    if thread_id in data:
        data[thread_id]['last_used'] = datetime.utcnow().isoformat() + 'Z'
        with open(_THREAD_DB, 'w') as f2:
            json.dump(data, f2)

def validate_asset_id(asset_id: str) -> bool:
    return chroma_client.asset_exists(asset_id)

from datetime import datetime
import json, os
_THREAD_DB = "thread_asset_map.json"

def create_chat_thread(asset_id: str) -> str:
    import uuid
    thread_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    if os.path.exists(_THREAD_DB):
        with open(_THREAD_DB, "r") as f:
            data = json.load(f)
    else:
        data = {}
    data[thread_id] = {
        "asset_id": asset_id,
        "created_at": now,
        "last_used": now
    }
    with open(_THREAD_DB, "w") as f:
        json.dump(data, f)
    return thread_id

def get_asset_id_for_thread(thread_id: str) -> str:
    if not os.path.exists(_THREAD_DB):
        raise KeyError(f"Thread DB not found: {_THREAD_DB}")
    with open(_THREAD_DB, "r") as f:
        data = json.load(f)
    entry = data.get(thread_id)
    if isinstance(entry, dict):
        return entry.get("asset_id")
    return entry  # fallback for old format

# Local json-based DB for thread<>asset mapping
import os, json
_THREAD_DB = "thread_asset_map.json"

from datetime import datetime

class ChatThreadDB:
    @staticmethod
    def save_thread(thread_id: str, asset_id: str):
        import os, json
        now = datetime.utcnow().isoformat() + "Z"
        _THREAD_DB = "thread_asset_map.json"
        data = {}
        if os.path.exists(_THREAD_DB):
            try:
                data = json.load(open(_THREAD_DB, "r"))
            except Exception:
                pass
        data[thread_id] = {
            "asset_id": asset_id,
            "created_at": now,
            "last_used": now,
        }
        with open(_THREAD_DB, "w") as f:
            json.dump(data, f)

    @staticmethod
    def read_thread(thread_id: str) -> str:
        if not os.path.exists(_THREAD_DB):
            raise KeyError
        data = json.load(open(_THREAD_DB, "r"))
        return data.get(thread_id)