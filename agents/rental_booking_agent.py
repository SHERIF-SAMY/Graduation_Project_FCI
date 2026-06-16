from memory.session_store import get_booking_context, update_booking_context, reset_booking_context
from agents.booking_entity_extractor import extract_booking_entities
from agents.net_api_proxy import create_rental_order, cancel_rental_order
from sql.executor import execute_query
import re

def _detect_lang(text: str) -> str:
    """Returns 'en' if the text is mostly Latin/English, 'ar' otherwise."""
    if not text:
        return "ar"
    latin = sum(1 for c in text if ord(c) < 256 and c.isalpha())
    arabic = sum(1 for c in text if '\u0600' <= c <= '\u06ff')
    return "en" if latin > arabic else "ar"

def _msg(ar: str, en: str, lang: str) -> str:
    return en if lang == "en" else ar

async def handle_booking_flow(
    session_id: str, 
    user_query: str, 
    intent: str, 
    search_entities: dict, 
    products: list, 
    user_id: str = None, 
    auth_token: str = None,
    chat_history: list = None
) -> dict:
    """
    Manages the conversational state machine for booking a rental.
    Returns a dict with {"agent_message": str, "state": str, "order_id": int/None, "summary": dict/None}
    """
    ctx = get_booking_context(session_id)
    lang = _detect_lang(user_query)
    
    # 1. Handle Cancel — ask for which order + confirmation
    if intent == "book_cancel":
        # Try to extract order ID from the user message (e.g. "الغي اوردر 4")
        import re
        order_id_match = re.search(r'\b(\d+)\b', user_query)
        order_id = int(order_id_match.group(1)) if order_id_match else None

        if not auth_token:
            reset_booking_context(session_id)
            return {
                "agent_message": _msg(
                    "لازم تسجّل دخول الأول عشان تقدر تلغي طلب.",
                    "You need to log in first to cancel an order.",
                    lang
                ),
                "state": "IDLE",
                "order_id": None,
                "summary": None
            }

        # If we are already waiting for cancel confirmation, handle it
        if ctx.state == "AWAITING_CANCEL_CONFIRM":
            pass  # will be handled below
        else:
            # First time — go ask which order and confirm
            if order_id:
                update_booking_context(session_id,
                    state="AWAITING_CANCEL_CONFIRM",
                    pending_cancel_order_id=order_id
                )
                return {
                    "agent_message": _msg(
                        f"⚠️ متأكد إنك عايز تلغي الطلب رقم {order_id}؟ قول (أيوه / لأ)",
                        f"⚠️ Are you sure you want to cancel order #{order_id}? (yes / no)",
                        lang
                    ),
                    "state": "AWAITING_CANCEL_CONFIRM",
                    "order_id": None,
                    "summary": None
                }
            else:
                # Ask for the order number first by fetching user orders from DB
                try:
                    rows = execute_query(
                        "SELECT TOP 5 o.Id, p.Name FROM RentalOrders o "
                        "JOIN Products p ON o.ProductId = p.Id "
                        "WHERE o.RenterId = :uid AND o.Status = 0 ORDER BY o.CreatedAt DESC",
                        {"uid": user_id}
                    ) if user_id else []
                except Exception:
                    rows = []

                if rows:
                    orders_text = "\n".join([f"- #{r['Id']}: {r['Name']}" for r in rows])
                    update_booking_context(session_id, state="AWAITING_CANCEL_CONFIRM")
                    return {
                        "agent_message": _msg(
                            f"طلباتك الحالية:\n{orders_text}\n\nادخل رقم الطلب اللي عايز تلغيه:",
                            f"Your current orders:\n{orders_text}\n\nEnter the order number you want to cancel:",
                            lang
                        ),
                        "state": "AWAITING_CANCEL_CONFIRM",
                        "order_id": None,
                        "summary": None
                    }
                else:
                    reset_booking_context(session_id)
                    return {
                        "agent_message": _msg(
                            "مش لاقي طلبات قيد الانتظار عندك دلوقتي.",
                            "You don't have any active orders at the moment.",
                            lang
                        ),
                        "state": "IDLE",
                        "order_id": None,
                        "summary": None
                    }

    # 1b. Handle the confirmation step for cancellation
    if ctx.state == "AWAITING_CANCEL_CONFIRM":
        import re
        booking_entities = extract_booking_entities(user_query, chat_history)
        is_confirmed = booking_entities.get("confirmed")

        # Maybe user just typed the order number (didn't have it before)
        order_id_match = re.search(r'\b(\d+)\b', user_query)
        if order_id_match and not ctx.pending_cancel_order_id:
            order_id = int(order_id_match.group(1))
            update_booking_context(session_id, pending_cancel_order_id=order_id)
            ctx = get_booking_context(session_id)
            return {
                "agent_message": _msg(
                    f"⚠️ متأكد إنك عايز تلغي الطلب رقم {order_id}؟ قول (أيوه / لأ)",
                    f"⚠️ Are you sure you want to cancel order #{order_id}? (yes / no)",
                    lang
                ),
                "state": "AWAITING_CANCEL_CONFIRM",
                "order_id": None,
                "summary": None
            }

        if is_confirmed is True or intent == "book_confirm":
            if not ctx.pending_cancel_order_id:
                reset_booking_context(session_id)
                return {
                    "agent_message": _msg(
                        "مش عارف رقم الطلب المطلوب إلغاؤه.",
                        "I don't know which order you'd like to cancel.",
                        lang
                    ),
                    "state": "IDLE",
                    "order_id": None,
                    "summary": None
                }
            result = await cancel_rental_order(auth_token=auth_token, order_id=ctx.pending_cancel_order_id)
            reset_booking_context(session_id)
            if result["success"]:
                return {
                    "agent_message": _msg(
                        f"✅ تم إلغاء الطلب رقم {ctx.pending_cancel_order_id} بنجاح!",
                        f"✅ Order #{ctx.pending_cancel_order_id} has been successfully cancelled!",
                        lang
                    ),
                    "state": "CANCELLED",
                    "order_id": None,
                    "summary": None
                }
            else:
                return {
                    "agent_message": _msg(
                        f"❌ حصلت مشكلة أثناء الإلغاء: {result['error']}",
                        f"❌ Something went wrong while cancelling: {result['error']}",
                        lang
                    ),
                    "state": "IDLE",
                    "order_id": None,
                    "summary": None
                }
        elif is_confirmed is False or intent == "book_cancel":
            reset_booking_context(session_id)
            return {
                "agent_message": _msg(
                    "تمام، مش هلغي الطلب. لو محتاج حاجة أنا موجود!",
                    "Got it, I won't cancel the order. Let me know if you need anything!",
                    lang
                ),
                "state": "IDLE",
                "order_id": None,
                "summary": None
            }
        else:
            return {
                "agent_message": _msg(
                    f"هل تأكيد إلغاء الطلب رقم {ctx.pending_cancel_order_id}؟ (أيوه / لأ)",
                    f"Please confirm: cancel order #{ctx.pending_cancel_order_id}? (yes / no)",
                    lang
                ),
                "state": "AWAITING_CANCEL_CONFIRM",
                "order_id": None,
                "summary": None
            }

    # 2. Extract booking entities from current message
    booking_entities = extract_booking_entities(user_query, chat_history)

    # 3. State Machine processing
    
    # --- IDLE -> INIT ---
    if ctx.state == "IDLE" and intent == "book_initiate":
        if not user_id or not auth_token:
            return {
                "agent_message": _msg(
                    "عشان أقدر أحجزلك، محتاج تسجّل دخول الأول.",
                    "You need to log in first before making a booking.",
                    lang
                ),
                "state": "IDLE",
                "order_id": None,
                "summary": None
            }

        # Determine which product the user wants
        selected_product = booking_entities.get("selected_product")
        
        # If there's only 1 product in search results and user initiated booking
        if len(products) == 1:
            prod = products[0]
            unavailable_msg = _check_product_available(prod.get("Id"), lang)
            if unavailable_msg:
                reset_booking_context(session_id)
                return {"agent_message": unavailable_msg, "state": "IDLE", "order_id": None, "summary": None}
            update_booking_context(session_id, 
                state="AWAITING_DATES", 
                product_id=prod.get("Id"),
                product_name=prod.get("Name"),
                price_per_day=prod.get("FinalPricePerDay") or prod.get("PricePerDay", 0)
            )
            return _ask_dates(lang)
            
        elif len(products) > 1:
            # We need to know which one
            if selected_product:
                # Try to find by name loosely
                matched = next((p for p in products if selected_product.lower() in str(p.get("Name")).lower()), None)
                if matched:
                    unavailable_msg = _check_product_available(matched.get("Id"), lang)
                    if unavailable_msg:
                        reset_booking_context(session_id)
                        return {"agent_message": unavailable_msg, "state": "IDLE", "order_id": None, "summary": None}
                    update_booking_context(session_id, 
                        state="AWAITING_DATES", 
                        product_id=matched.get("Id"),
                        product_name=matched.get("Name"),
                        price_per_day=matched.get("FinalPricePerDay") or matched.get("PricePerDay", 0)
                    )
                    return _ask_dates(lang)
            
            # Need clarification
            update_booking_context(session_id, state="AWAITING_PRODUCT")
            names = ", ".join([p.get("Name", "product") for p in products[:3]])
            return {
                "agent_message": _msg(
                    f"تقصد أنهي منتج بالظبط؟ (مثلاً: {names} ...)",
                    f"Which product exactly? (e.g. {names} ...)",
                    lang
                ),
                "state": "AWAITING_PRODUCT",
                "order_id": None,
                "summary": None
            }
        else:
            return {
                "agent_message": _msg(
                    "مش لاقي المنتج اللي تقصده. ممكن تدور عليه الأول؟",
                    "I couldn't find the product you're looking for. Can you search for it first?",
                    lang
                ),
                "state": "IDLE",
                "order_id": None,
                "summary": None
            }

    # --- AWAITING_PRODUCT ---
    if ctx.state == "AWAITING_PRODUCT":
        selected_product = booking_entities.get("selected_product") or user_query
        # In a real scenario, we'd search the DB or last results. 
        # For now, we try to match against products passed in.
        matched = next((p for p in products if selected_product.lower() in str(p.get("Name")).lower()), None)
        if not matched and len(products) > 0:
            matched = products[0] # fallback to first if they just said "الاول"

        if matched:
            unavailable_msg = _check_product_available(matched.get("Id"))
            if unavailable_msg:
                reset_booking_context(session_id)
                return {"agent_message": unavailable_msg, "state": "IDLE", "order_id": None, "summary": None}
            update_booking_context(session_id, 
                state="AWAITING_DATES", 
                product_id=matched.get("Id"),
                product_name=matched.get("Name"),
                price_per_day=matched.get("FinalPricePerDay") or matched.get("PricePerDay", 0)
            )
            # Re-process dates in case they provided them
            ctx = get_booking_context(session_id) 
        else:
            return {
                "agent_message": _msg(
                    "لسه مش متأكد تقصد أنهي منتج بالظبط.",
                    "I'm not sure which product you mean. Could you be more specific?",
                    lang
                ),
                "state": "AWAITING_PRODUCT",
                "order_id": None,
                "summary": None
            }

    # Update context with any extracted info
    updates = {}
    if booking_entities.get("start_date"): updates["start_date"] = booking_entities["start_date"]
    if booking_entities.get("end_date"): updates["end_date"] = booking_entities["end_date"]
    if booking_entities.get("delivery_method"): updates["delivery_method"] = booking_entities["delivery_method"]
    if booking_entities.get("city"): updates["city"] = booking_entities["city"]
    if booking_entities.get("street"): updates["street"] = booking_entities["street"]
    if booking_entities.get("governorate"): updates["governorate"] = booking_entities["governorate"]
    
    if updates:
        update_booking_context(session_id, **updates)
    ctx = get_booking_context(session_id) # refresh

    # --- AWAITING_DATES ---
    if ctx.state == "AWAITING_DATES":
        if ctx.start_date and ctx.end_date:
            update_booking_context(session_id, state="AWAITING_DELIVERY_METHOD")
            ctx = get_booking_context(session_id)
        else:
            return _ask_dates()

    # --- AWAITING_DELIVERY_METHOD ---
    if ctx.state == "AWAITING_DELIVERY_METHOD":
        if ctx.delivery_method:
            if ctx.delivery_method.lower() == "delivery":
                update_booking_context(session_id, state="AWAITING_ADDRESS")
                ctx = get_booking_context(session_id)
            else:
                update_booking_context(session_id, state="AWAITING_CONFIRMATION")
                ctx = get_booking_context(session_id)
        else:
            return {
                "agent_message": _msg(
                    "تحب تستلم المنتج بنفسك (Pickup) ولا يوصلك لحد عندك (Delivery)؟",
                    "Would you prefer to pick it up yourself (Pickup) or have it delivered to you (Delivery)?",
                    lang
                ),
                "state": "AWAITING_DELIVERY_METHOD",
                "order_id": None,
                "summary": None
            }

    # --- AWAITING_ADDRESS ---
    if ctx.state == "AWAITING_ADDRESS":
        if ctx.city and ctx.street:
            update_booking_context(session_id, state="AWAITING_CONFIRMATION")
            ctx = get_booking_context(session_id)
        else:
            return {
                "agent_message": _msg(
                    "تمام! العنوان بالتفصيل إيه؟ (المدينة، الشارع، المحافظة)",
                    "What's your delivery address? (city, street, governorate)",
                    lang
                ),
                "state": "AWAITING_ADDRESS",
                "order_id": None,
                "summary": None
            }

    # --- AWAITING_CONFIRMATION ---
    if ctx.state == "AWAITING_CONFIRMATION":
        is_confirmed = booking_entities.get("confirmed")
        if intent == "book_confirm" or is_confirmed is True:
            # DO API CALL
            result = await create_rental_order(
                auth_token=auth_token,
                product_id=ctx.product_id,
                start_date=ctx.start_date,
                end_date=ctx.end_date,
                delivery_method=ctx.delivery_method,
                street=ctx.street or "",
                city=ctx.city or "",
                governorate=ctx.governorate or ""
            )
            
            if result["success"]:
                order_id = result["order_id"]
                reset_booking_context(session_id)
                return {
                    "agent_message": _msg(
                        f"✅ تم تسجيل طلبك بنجاح! رقم الطلب: {order_id}",
                        f"✅ Your booking has been confirmed! Order number: {order_id}",
                        lang
                    ),
                    "state": "CONFIRMED",
                    "order_id": order_id,
                    "summary": None
                }
            else:
                # 401 = session expired — ask user to log in again
                if result.get("status_code") == 401:
                    reset_booking_context(session_id)
                    return {
                        "agent_message": _msg(
                            "⚠️ انتهت جلستك، محتاج تسجّل دخول من تاني وتعيد المحاولة.",
                            "⚠️ Your session has expired. Please log in again and try booking.",
                            lang
                        ),
                        "state": "IDLE",
                        "order_id": None,
                        "summary": None
                    }
                err = result["error"]
                return {
                    "agent_message": _msg(
                        f"للأسف حصلت مشكلة أثناء تأكيد الطلب: {err}",
                        f"Sorry, something went wrong while confirming your order: {err}",
                        lang
                    ),
                    "state": "AWAITING_CONFIRMATION",
                    "order_id": None,
                    "summary": _build_summary(ctx)
                }

        elif is_confirmed is False:
             reset_booking_context(session_id)
             return {
                 "agent_message": _msg(
                     "تم إلغاء الطلب بناء على رغبتك.",
                     "Order cancelled as per your request.",
                     lang
                 ),
                 "state": "CANCELLED",
                 "order_id": None,
                 "summary": None
             }

        else:
            # Need to ask for confirmation
            summary = _build_summary(ctx)

            # Calculate price
            try:
                from datetime import datetime
                d1 = datetime.fromisoformat(ctx.start_date.split("T")[0])
                d2 = datetime.fromisoformat(ctx.end_date.split("T")[0])
                num_days = max((d2 - d1).days + 1, 1)  # inclusive: both start and end day count
                total_price = round(num_days * float(ctx.price_per_day or 0), 2)
                price_line = _msg(
                    f"💰 السعر: {ctx.price_per_day} EGP/يوم × {num_days} يوم = {total_price} EGP\n",
                    f"💰 Price: {ctx.price_per_day} EGP/day x {num_days} days = {total_price} EGP\n",
                    lang
                )
            except Exception:
                price_line = ""

            if lang == "en":
                msg = f"Great! Let me confirm your order:\n"
                msg += f"📦 Product: {ctx.product_name}\n"
                msg += f"📅 From: {ctx.start_date} to {ctx.end_date}\n"
                if ctx.delivery_method.lower() == "delivery":
                    msg += f"🚚 Delivery to: {ctx.street}, {ctx.city}, {ctx.governorate}\n"
                else:
                    msg += f"🏢 Pickup from owner\n"
                msg += price_line
                msg += "\nConfirm? (yes / no)"
            else:
                msg = f"ممتاز! هأكد الطلب ده:\n"
                msg += f"📦 المنتج: {ctx.product_name}\n"
                msg += f"📅 من: {ctx.start_date} إلى {ctx.end_date}\n"
                if ctx.delivery_method.lower() == "delivery":
                    msg += f"🚚 توصيل: {ctx.street}، {ctx.city}، {ctx.governorate}\n"
                else:
                    msg += f"🏢 استلام من المالك\n"
                msg += price_line
                msg += "\nتأكيد؟ (أيوه / لأ)"
            
            return {
                "agent_message": msg,
                "state": "AWAITING_CONFIRMATION",
                "order_id": None,
                "summary": summary
            }

    # Fallback
    return {
        "agent_message": _msg(
            "مش متأكد أنت تقصد إيه في الطلب، ممكن نلغيه ونبدأ من الأول؟",
            "I'm not sure what you mean. Shall we start over?",
            lang
        ),
        "state": ctx.state,
        "order_id": None,
        "summary": None
    }

def _ask_dates(lang: str = "ar"):
    return {
        "agent_message": _msg(
            "تمام! محتاج تأجره من إمتى لإمتى بالظبط؟ (مثلاً: من بكره لمدة 3 أيام، أو من 15 مايو لـ 18 مايو)",
            "When would you like to rent it? (e.g. from tomorrow for 3 days, or May 15 to May 18)",
            lang
        ),
        "state": "AWAITING_DATES",
        "order_id": None,
        "summary": None
    }

def _build_summary(ctx):
    return {
        "product_id": ctx.product_id,
        "product_name": ctx.product_name,
        "start_date": ctx.start_date,
        "end_date": ctx.end_date,
        "delivery_method": ctx.delivery_method,
        "address": f"{ctx.street}, {ctx.city}, {ctx.governorate}"
    }
def _check_product_available(product_id: int, lang: str = "ar") -> str | None:
    """
    Checks if a product has any active orders (Pending=0, Accepted=1, InProgress=4).
    Returns None if available, or an error message string if not.
    """
    if not product_id:
        return None
    try:
        rows = execute_query(
            "SELECT TOP 1 o.Id FROM RentalOrders o "
            "WHERE o.ProductId = :pid AND o.Status IN (0, 1, 4)",
            {"pid": product_id}
        )
        if rows:
            return _msg(
                "عذراً، المنتج ده محجوز دلوقتي ومش متاح للإيجار. اقدر اساعدك تلاقي منتج تاني.",
                "Sorry, this product is currently rented and not available. Can I help you find another one?",
                lang
            )
    except Exception as e:
        print(f"[BookingAgent] Availability check error: {e}")
    return None

