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
    # Normalise: treat empty string as None so all `if user_id` guards work correctly
    if user_id is not None:
        user_id = user_id.strip() or None
    if auth_token is not None:
        auth_token = auth_token.strip() or None

    # Fallback/second-layer defense: extract user_id from JWT if auth_token is present but user_id is missing
    if not user_id and auth_token:
        from utils.jwt_utils import extract_user_id_from_jwt
        user_id = extract_user_id_from_jwt(auth_token)

    # Debug logging — helps trace what user_id/auth_token actually arrived
    print(f"[BookingAgent] intent={intent!r} | session={session_id!r} | "
          f"user_id={user_id!r} | auth_token={'SET' if auth_token else 'NONE'}")

    ctx = get_booking_context(session_id)
    lang = _detect_lang(user_query)
    
    # 1. Handle View Orders
    if intent == "view_orders":
        if not auth_token:
            reset_booking_context(session_id)
            return {
                "agent_message": _msg(
                    "لازم تسجّل دخول الأول عشان تقدر تشوف أوردراتك اللي حجزتها.",
                    "You need to log in first to view your booked orders.",
                    lang
                ),
                "state": "IDLE",
                "order_id": None,
                "summary": None
            }
        
        from agents.net_api_proxy import get_my_orders
        result = await get_my_orders(auth_token)
        
        if not result["success"]:
            if result.get("status_code") == 401:
                reset_booking_context(session_id)
                return {
                    "agent_message": _msg(
                        "انتهت جلستك، سجّل دخول من تاني.",
                        "Your session expired. Please log in again.",
                        lang
                    ),
                    "state": "IDLE",
                    "order_id": None,
                    "summary": None
                }
            reset_booking_context(session_id)
            return {
                "agent_message": _msg(
                    "حصل خطأ في جلب الطلبات، حاول تاني بعد قليل.",
                    "An error occurred while fetching orders, please try again in a bit.",
                    lang
                ),
                "state": "IDLE",
                "order_id": None,
                "summary": None
            }

        orders = result["orders"]
        if orders:
            # Sort orders descending by ID so the user sees the newest orders first
            try:
                orders = sorted(
                    orders,
                    key=lambda x: int(x.get("orderId") or x.get("id") or x.get("Id") or 0),
                    reverse=True
                )
            except Exception as e:
                print(f"[BookingAgent] Error sorting orders: {e}")

            status_map_ar = {
                0: "⏳ قيد الانتظار (Pending)",
                "Pending": "⏳ قيد الانتظار (Pending)",
                "pending": "⏳ قيد الانتظار (Pending)",
                
                1: "✅ مقبول (Accepted)",
                "Accepted": "✅ مقبول (Accepted)",
                "accepted": "✅ مقبول (Accepted)",
                
                2: "❌ مرفوض (Rejected)",
                "Rejected": "❌ مرفوض (Rejected)",
                "rejected": "❌ مرفوض (Rejected)",
                
                3: "🏁 مكتمل (Completed)",
                "Completed": "🏁 مكتمل (Completed)",
                "completed": "🏁 مكتمل (Completed)",
                
                4: "⚙️ قيد التنفيذ (In Progress)",
                "InProgress": "⚙️ قيد التنفيذ (In Progress)",
                "inprogress": "⚙️ قيد التنفيذ (In Progress)",
                "In Progress": "⚙️ قيد التنفيذ (In Progress)",
                "in progress": "⚙️ قيد التنفيذ (In Progress)",
                
                5: "🔄 تم الإرجاع (Returned)",
                "Returned": "🔄 تم الإرجاع (Returned)",
                "returned": "🔄 تم الإرجاع (Returned)",
                
                6: "🚫 ملغي (Cancelled)",
                "Cancelled": "🚫 ملغي (Cancelled)",
                "cancelled": "🚫 ملغي (Cancelled)",
                "CANCELLED": "🚫 ملغي (Cancelled)",
            }
            status_map_en = {
                0: "⏳ Pending",
                "Pending": "⏳ Pending",
                "pending": "⏳ Pending",
                
                1: "✅ Accepted",
                "Accepted": "✅ Accepted",
                "accepted": "✅ Accepted",
                
                2: "❌ Rejected",
                "Rejected": "❌ Rejected",
                "rejected": "❌ Rejected",
                
                3: "🏁 Completed",
                "Completed": "🏁 Completed",
                "completed": "🏁 Completed",
                
                4: "⚙️ In Progress",
                "InProgress": "⚙️ In Progress",
                "inprogress": "⚙️ In Progress",
                "In Progress": "⚙️ In Progress",
                "in progress": "⚙️ In Progress",
                
                5: "🔄 Returned",
                "Returned": "🔄 Returned",
                "returned": "🔄 Returned",
                
                6: "🚫 Cancelled",
                "Cancelled": "🚫 Cancelled",
                "cancelled": "🚫 Cancelled",
                "CANCELLED": "🚫 Cancelled",
            }
            
            orders_list = []
            for o in orders[:5]: # show up to 5 orders
                order_id = o.get("orderId") or o.get("id") or o.get("Id")
                prod_name = o.get("productName") or o.get("ProductName") or o.get("product", {}).get("name", "?")
                status_val = o.get("status") if o.get("status") is not None else o.get("Status")
                price_per_day = o.get("pricePerDay") or o.get("PricePerDay") or ""
                rental_days = o.get("rentalDays") or o.get("RentalDays") or ""
                time_ago = o.get("timeAgo") or o.get("TimeAgo") or ""
                
                # Fallback: try totalAmount or compute from pricePerDay * rentalDays
                total_amount = o.get("totalAmount") or o.get("TotalAmount") or ""
                if not total_amount and price_per_day and rental_days:
                    try:
                        total_amount = float(price_per_day) * int(rental_days)
                    except Exception:
                        total_amount = ""
                
                status_lbl = _msg(
                    status_map_ar.get(status_val, f"غير معروف ({status_val})"),
                    status_map_en.get(status_val, f"Unknown ({status_val})"),
                    lang
                )
                
                # Build detail parts in a clean and concise layout
                if total_amount and rental_days:
                    amount_lbl_ar = f"{total_amount} EGP ({rental_days} يوم)"
                    amount_lbl_en = f"{total_amount} EGP ({rental_days} days)"
                elif total_amount:
                    amount_lbl_ar = f"{total_amount} EGP"
                    amount_lbl_en = f"{total_amount} EGP"
                elif price_per_day:
                    amount_lbl_ar = f"{price_per_day} EGP/يوم"
                    amount_lbl_en = f"{price_per_day} EGP/day"
                else:
                    amount_lbl_ar = ""
                    amount_lbl_en = ""

                details_ar = f"- 📦 طلب #{order_id}: *{prod_name}* | {status_lbl}"
                details_en = f"- 📦 Order #{order_id}: *{prod_name}* | {status_lbl}"

                if amount_lbl_ar:
                    details_ar += f" | {amount_lbl_ar}"
                    details_en += f" | {amount_lbl_en}"
                if time_ago:
                    details_ar += f" | {time_ago}"
                    details_en += f" | {time_ago}"
                
                orders_list.append(_msg(details_ar, details_en, lang))
            
            agent_msg = _msg(
                "حاضر! دي قائمة بالطلبات اللي حجزتها عندي:",
                "Here is a list of the orders you booked:",
                lang
            )
            
            reset_booking_context(session_id)
            return {
                "agent_message": agent_msg,
                "state": "IDLE",
                "order_id": None,
                "summary": None,
                "orders": orders_list
            }
        else:
            reset_booking_context(session_id)
            return {
                "agent_message": _msg(
                    "مش لاقي أي طلبات محجوزة باسمك حالياً.",
                    "I couldn't find any orders booked under your name at the moment.",
                    lang
                ),
                "state": "IDLE",
                "order_id": None,
                "summary": None
            }


    # 2. Handle Cancel — ask for which order + confirmation
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
                # Ask for the order number first by fetching user orders from .NET API
                from agents.net_api_proxy import get_my_orders
                result = await get_my_orders(auth_token, status_filter=0)
                orders = result["orders"] if (result["success"] and result["orders"]) else []

                if orders:
                    try:
                        orders = sorted(
                            orders,
                            key=lambda x: int(x.get("orderId") or x.get("id") or x.get("Id") or 0),
                            reverse=True
                        )
                    except Exception as e:
                        print(f"[BookingAgent] Error sorting pending orders: {e}")
                    orders_list = [
                        f"- #{o.get('orderId') or o.get('id') or o.get('Id')}: {o.get('productName') or o.get('ProductName') or o.get('product', {}).get('name', '?')}"
                        for o in orders[:5]
                    ]
                    update_booking_context(session_id, state="AWAITING_CANCEL_CONFIRM")
                    return {
                        "agent_message": _msg(
                            "طلباتك الحالية قيد الانتظار، ادخل رقم الطلب اللي عايز تلغيه:",
                            "Your current pending orders. Enter the order number you want to cancel:",
                            lang
                        ),
                        "state": "AWAITING_CANCEL_CONFIRM",
                        "order_id": None,
                        "summary": None,
                        "orders": orders_list
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
        
        # Try to resolve from chat history if there are multiple products and no selected_product
        if len(products) > 1 and not selected_product:
            if chat_history:
                last_ai_msg = next(
                    (m.content for m in reversed(chat_history) 
                     if type(m).__name__ == 'AIMessage'),
                    ""
                )
                if last_ai_msg:
                    for p in products:
                        p_name = p.get("Name", "")
                        if p_name and p_name.lower() in last_ai_msg.lower():
                            selected_product = p_name
                            break

        # If there's only 1 product in search results and user initiated booking
        if len(products) == 1:
            prod = products[0]
            update_booking_context(session_id, 
                state="AWAITING_DATES", 
                product_id=prod.get("Id"),
                product_name=prod.get("Name"),
                price_per_day=prod.get("FinalPricePerDay") or prod.get("PricePerDay", 0),
                owner_id=prod.get("UserId") or prod.get("OwnerId")
            )
            return _ask_dates(lang)
            
        elif len(products) > 1:
            # We need to know which one
            if selected_product:
                # Try to find by name loosely
                matched = next((p for p in products if selected_product.lower() in str(p.get("Name")).lower()), None)
                if matched:
                    update_booking_context(session_id, 
                        state="AWAITING_DATES", 
                        product_id=matched.get("Id"),
                        product_name=matched.get("Name"),
                        price_per_day=matched.get("FinalPricePerDay") or matched.get("PricePerDay", 0),
                        owner_id=matched.get("UserId") or matched.get("OwnerId")
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
            update_booking_context(session_id, 
                state="AWAITING_DATES", 
                product_id=matched.get("Id"),
                product_name=matched.get("Name"),
                price_per_day=matched.get("FinalPricePerDay") or matched.get("PricePerDay", 0),
                owner_id=matched.get("UserId") or matched.get("OwnerId")
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
            unavailable_msg = _check_product_available(ctx.product_id, ctx.start_date, ctx.end_date, lang)
            if unavailable_msg:
                update_booking_context(session_id, start_date=None, end_date=None)
                return {
                    "agent_message": unavailable_msg,
                    "state": "AWAITING_DATES",
                    "order_id": None,
                    "summary": None
                }

            update_booking_context(session_id, state="AWAITING_DELIVERY_METHOD")
            ctx = get_booking_context(session_id)
        else:
            return _ask_dates(lang)

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
            # 1. Calculate total price
            try:
                from datetime import datetime
                d1 = datetime.fromisoformat(ctx.start_date.split("T")[0])
                d2 = datetime.fromisoformat(ctx.end_date.split("T")[0])
                num_days = max((d2 - d1).days + 1, 1)
                total_price = round(num_days * float(ctx.price_per_day or 0), 2)
            except Exception:
                total_price = 0.0
                num_days = 0

            # 2. Concurrent API calls for wallet and insurance
            import asyncio
            from agents.net_api_proxy import get_wallet_balance, get_product_insurance

            wallet_res, insurance_res = await asyncio.gather(
                get_wallet_balance(auth_token),
                get_product_insurance(ctx.product_id)
            )

            # 3. Handle API failures
            if not wallet_res["success"]:
                if wallet_res.get("status_code") == 401:
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
                return {
                    "agent_message": _msg(
                        "⚠️ مش قادر أتحقق من رصيد المحفظة دلوقتي، حاول تاني بعد شوية.",
                        "⚠️ Couldn't verify your wallet balance right now, please try again shortly.",
                        lang
                    ),
                    "state": "AWAITING_CONFIRMATION",
                    "order_id": None,
                    "summary": _build_summary(ctx)
                }

            if not insurance_res["success"]:
                print(f"[BookingAgent] Insurance fetch failed: {insurance_res['error']} — treating as 0")
                insurance_amount = 0.0
            else:
                insurance_amount = insurance_res["insurance_amount"]

            # 4 & 5. Balance Check
            balance = wallet_res["balance"]
            currency = wallet_res["currency"]
            required = round(total_price + insurance_amount, 2)

            if balance < required:
                shortfall = round(required - balance, 2)
                en_msg = (
                    f"❌ Insufficient wallet balance.\n"
                    f"💰 Required: {required} {currency}"
                    + (f" (rental: {total_price} + insurance: {insurance_amount})" if insurance_amount > 0 else "")
                    + f"\n💳 Your balance: {balance} {currency}\n"
                    f"📉 Shortfall: {shortfall} {currency}\n\n"
                    f"Please top up your wallet and try again."
                )
                ar_msg = (
                    f"❌ رصيد محفظتك مش كافي.\n"
                    f"💰 المطلوب: {required} {currency}"
                    + (f" (الإيجار: {total_price} + التأمين: {insurance_amount})" if insurance_amount > 0 else "")
                    + f"\n💳 رصيدك الحالي: {balance} {currency}\n"
                    f"📉 الفرق: {shortfall} {currency}\n\n"
                    f"رجاء اشحن محفظتك وحاول تاني."
                )
                return {
                    "agent_message": _msg(ar_msg, en_msg, lang),
                    "state": "AWAITING_CONFIRMATION",
                    "order_id": None,
                    "summary": _build_summary(ctx)
                }

            # 6. DO API CALL to create order
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

            details_list = []
            if lang == "en":
                msg = "Great! Let me confirm your order. Confirm? (yes / no)"
                details_list.append(f"📦 Product: {ctx.product_name}")
                details_list.append(f"📅 From: {ctx.start_date} to {ctx.end_date}")
                if ctx.delivery_method.lower() == "delivery":
                    details_list.append(f"🚚 Delivery to: {ctx.street}, {ctx.city}, {ctx.governorate}")
                else:
                    details_list.append("🏢 Pickup from owner")
                if price_line:
                    details_list.append(price_line.strip())
            else:
                msg = "ممتاز! هأكد الطلب ده، تأكيد؟ (أيوه / لأ)"
                details_list.append(f"📦 المنتج: {ctx.product_name}")
                details_list.append(f"📅 من: {ctx.start_date} إلى {ctx.end_date}")
                if ctx.delivery_method.lower() == "delivery":
                    details_list.append(f"🚚 توصيل: {ctx.street}، {ctx.city}، {ctx.governorate}")
                else:
                    details_list.append("🏢 استلام من المالك")
                if price_line:
                    details_list.append(price_line.strip())
            
            return {
                "agent_message": msg,
                "state": "AWAITING_CONFIRMATION",
                "order_id": None,
                "summary": summary,
                "orders": details_list
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
def _check_product_available(product_id: int, start_date: str, end_date: str, lang: str = "ar") -> str | None:
    """
    Checks if a product has any active orders (Pending=0, Accepted=1, InProgress=4)
    that overlap with the requested dates.
    Returns None if available, or an error message string if not.
    """
    if not product_id or not start_date or not end_date:
        return None
    try:
        query = """
            SELECT TOP 1 d.StartDate, d.EndDate 
            FROM RentalOrders o
            JOIN RentalOrderDetails d ON o.Id = d.RentalOrderId
            WHERE o.ProductId = :pid 
              AND o.Status IN (0, 1, 4)
              AND (:req_start <= d.EndDate AND :req_end >= d.StartDate)
        """
        rows = execute_query(query, {
            "pid": product_id, 
            "req_start": start_date, 
            "req_end": end_date
        })
        if rows:
            conflict_start = rows[0].get("StartDate")
            conflict_end = rows[0].get("EndDate")
            
            if conflict_start and conflict_end:
                from datetime import datetime
                if isinstance(conflict_start, str):
                    conflict_start = conflict_start.split("T")[0]
                elif isinstance(conflict_start, datetime):
                    conflict_start = conflict_start.strftime("%Y-%m-%d")
                    
                if isinstance(conflict_end, str):
                    conflict_end = conflict_end.split("T")[0]
                elif isinstance(conflict_end, datetime):
                    conflict_end = conflict_end.strftime("%Y-%m-%d")

                return _msg(
                    f"عذراً، المنتج ده محجوز في الفترة دي (من {conflict_start} لـ {conflict_end}). تحب تختار تواريخ تانية؟",
                    f"Sorry, this product is booked during this period (from {conflict_start} to {conflict_end}). Would you like to choose different dates?",
                    lang
                )
            else:
                return _msg(
                    "عذراً، المنتج محجوز في الفترة دي، تحب تختار تواريخ تانية؟",
                    "Sorry, this product is booked during this period. Would you like to choose different dates?",
                    lang
                )
    except Exception as e:
        print(f"[BookingAgent] Availability check error: {e}")
    return None

