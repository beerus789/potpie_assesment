import os, json
from datetime import datetime
from app.models.chat import ChatMessage

_HISTORY_DIR = "chat_histories"
os.makedirs(_HISTORY_DIR, exist_ok=True)

def _history_file(thread_id):
    return os.path.join(_HISTORY_DIR, f"{thread_id}.json")

def add_message(thread_id, message, sender):
    ts = datetime.utcnow().isoformat() + "Z"
    msg = ChatMessage(
        message=message,
        sender=sender,
        timestamp=ts
    ).dict()
    history = get_history(thread_id)
    history.append(msg)
    with open(_history_file(thread_id), "w") as f:
        json.dump(history, f)

def get_history(thread_id):
    path = _history_file(thread_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []