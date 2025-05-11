import os, json
from datetime import datetime
from app.models.chat import ChatMessage

# Directory where chat histories are stored (one file per thread)
_HISTORY_DIR = "chat_histories"
os.makedirs(_HISTORY_DIR, exist_ok=True)


def _history_file(thread_id):
    """
    Get the file path for a thread's chat history JSON file.
    """
    return os.path.join(_HISTORY_DIR, f"{thread_id}.json")


def add_message(thread_id, message, sender):
    """
    Add a message to the chat history for a thread.
    Each message is timestamped and stored as a ChatMessage dict.
    """
    ts = datetime.utcnow().isoformat() + "Z"
    msg = ChatMessage(message=message, sender=sender, timestamp=ts).dict()
    history = get_history(thread_id)
    history.append(msg)
    with open(_history_file(thread_id), "w") as f:
        json.dump(history, f)


def get_history(thread_id):
    """
    Retrieve the chat history for a thread as a list of messages.
    Returns an empty list if no history exists.
    """
    path = _history_file(thread_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []
