"""
Session-based conversation memory store.
Keeps the last MAX_TURNS turns per session_id in memory.
Each turn = (user_message, ai_message).
"""
from collections import defaultdict
from langchain_core.messages import HumanMessage, AIMessage

MAX_TURNS = 5  # Keep last 5 turns to limit token usage

# { session_id: [(HumanMessage, AIMessage), ...] }
_histories: dict[str, list] = defaultdict(list)


def get_history(session_id: str) -> list:
    """Returns a flat list of LangChain messages for the session."""
    turns = _histories[session_id]
    messages = []
    for human_msg, ai_msg in turns:
        messages.append(human_msg)
        messages.append(ai_msg)
    return messages


def add_turn(session_id: str, user_query: str, ai_response: str) -> None:
    """Appends a new turn to the session history, capped at MAX_TURNS."""
    _histories[session_id].append((
        HumanMessage(content=user_query),
        AIMessage(content=ai_response),
    ))
    # Keep only last MAX_TURNS turns
    if len(_histories[session_id]) > MAX_TURNS:
        _histories[session_id] = _histories[session_id][-MAX_TURNS:]


def clear_session(session_id: str) -> None:
    """Clears the history for a session."""
    _histories[session_id] = []


def get_all_sessions() -> list[str]:
    """Returns all active session IDs."""
    return list(_histories.keys())
