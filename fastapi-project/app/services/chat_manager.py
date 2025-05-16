import uuid
from app.core.chroma import ChromaDBClient

chroma_client = ChromaDBClient()
from app.constant import DIRECTORY, FileFormat
from datetime import datetime
import os, json

# Path to the thread-asset mapping JSON file
_THREAD_DB = DIRECTORY.THREAD_ASSET_MAP.value


def update_last_used(thread_id):
    """
    Update the 'last_used' timestamp for a chat thread.
    """
    if not os.path.exists(_THREAD_DB):
        return
    with open(_THREAD_DB, "r") as f:
        data = json.load(f)
    if thread_id in data:
        data[thread_id][FileFormat.LAST_USED.value] = datetime.utcnow().isoformat() + "Z"
        with open(_THREAD_DB, "w") as f2:
            json.dump(data, f2)


def validate_asset_id(asset_id: str) -> bool:
    """
    Check if the asset_id exists in ChromaDB.
    """
    return chroma_client.asset_exists(asset_id)


def create_chat_thread(asset_id: str) -> str:
    """
    Create a new chat thread for the given asset_id and store its metadata.
    Returns the new thread_id.
    """
    thread_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    if os.path.exists(_THREAD_DB):
        with open(_THREAD_DB, "r") as f:
            data = json.load(f)
    else:
        data = {}
    data[thread_id] = {FileFormat.ASSET_ID.value: asset_id, FileFormat.CREATED_AT.value: now, FileFormat.LAST_USED.value: now}
    with open(_THREAD_DB, "w") as f:
        json.dump(data, f)
    return thread_id


def get_asset_id_for_thread(thread_id: str) -> str:
    """
    Retrieve the asset_id for a given thread_id from the thread-asset map.
    """
    if not os.path.exists(_THREAD_DB):
        raise KeyError(f"Thread DB not found: {_THREAD_DB}")
    with open(_THREAD_DB, "r") as f:
        data = json.load(f)
    entry = data.get(thread_id)
    if isinstance(entry, dict):
        return entry.get(FileFormat.ASSET_ID.value)
    return entry  # fallback for old format


# Local json-based DB for thread<>asset mapping
class ChatThreadDB:
    @staticmethod
    def save_thread(thread_id: str, asset_id: str):
        """
        Save a new thread with its associated asset_id to the thread-asset map.
        """
        now = datetime.utcnow().isoformat() + "Z"
        data = {}
        if os.path.exists(_THREAD_DB):
            try:
                data = json.load(open(_THREAD_DB, "r"))
            except Exception:
                pass
        data[thread_id] = {
            FileFormat.ASSET_ID.value: asset_id,
            FileFormat.CREATED_AT.value: now,
            FileFormat.LAST_USED.value: now,
        }
        with open(_THREAD_DB, "w") as f:
            json.dump(data, f)

    @staticmethod
    def read_thread(thread_id: str) -> str:
        """
        Retrieve thread metadata for a given thread_id.
        """
        if not os.path.exists(_THREAD_DB):
            raise KeyError(f"Thread DB not found: {_THREAD_DB}")
        data = json.load(open(_THREAD_DB, "r"))
        return data.get(thread_id)
