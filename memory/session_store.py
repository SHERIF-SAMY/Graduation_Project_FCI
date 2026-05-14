"""
Session-based conversation memory store.
Keeps the last MAX_TURNS turns per session_id in memory.
Each turn = (user_message, ai_message).
"""
from collections import defaultdict
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, AIMessage

@dataclass
class BookingContext:
    state: str = "IDLE"           # IDLE, AWAITING_PRODUCT, AWAITING_DATES, AWAITING_DELIVERY_METHOD, AWAITING_ADDRESS, AWAITING_CONFIRMATION, AWAITING_CANCEL_CONFIRM, CONFIRMED, CANCELLED
    product_id: int | None = None
    product_name: str | None = None
    price_per_day: float | None = None
    owner_id: str | None = None
    start_date: str | None = None  # ISO format "YYYY-MM-DD"
    end_date: str | None = None
    delivery_method: str | None = None  # "Delivery" or "Pickup"
    city: str | None = None
    street: str | None = None
    governorate: str | None = None
    rental_order_id: int | None = None  # set after successful booking
    pending_cancel_order_id: int | None = None  # order id awaiting cancellation confirmation

MAX_TURNS = 5  # Keep last 5 turns to limit token usage

# { session_id: [(HumanMessage, AIMessage), ...] }
_histories: dict[str, list] = defaultdict(list)

# { session_id: BookingContext }
_bookings: dict[str, BookingContext] = defaultdict(BookingContext)


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
    """Clears the history and booking context for a session."""
    _histories[session_id] = []
    _bookings[session_id] = BookingContext()


def get_booking_context(session_id: str) -> BookingContext:
    """Returns the current booking context for the session."""
    return _bookings[session_id]


def update_booking_context(session_id: str, **kwargs) -> None:
    """Updates fields in the booking context for the session."""
    ctx = _bookings[session_id]
    for key, value in kwargs.items():
        if hasattr(ctx, key):
            setattr(ctx, key, value)


def reset_booking_context(session_id: str) -> None:
    """Resets the booking context to IDLE state."""
    _bookings[session_id] = BookingContext()


def get_all_sessions() -> list[str]:
    """Returns all active session IDs."""
    return list(_histories.keys())
