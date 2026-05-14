# Implementation Plan — Agentic Rental Booking via Chatbot

## الهدف

تحويل الـ chatbot من **assistant بيدور على منتجات** إلى **agent كامل** يقدر يكمّل عملية الإيجار للآخر —
من لحظة ما المستخدم يقول "اجّرهولي" لحد ما الـ `RentalOrder` يتسجّل في الـ DB.

---

## الـ Flow بالكامل (User Journey)

```
User: "عايز أجّر كاميرا Canon بكره"
  ↓
Agent: "تمام! من إمتى لإمتى بالظبط؟"
  ↓
User: "من 15 مايو لـ 18 مايو"
  ↓
Agent: "توصيل ولا استلام؟"
  ↓
User: "توصيل"
  ↓
Agent: "العنوان إيه؟"
  ↓
User: "مدينة نصر، شارع عباس العقاد"
  ↓
Agent: "ممتاز! هكمّل الطلب ده:
         📦 كاميرا Canon EOS R50
         📅 15–18 مايو (3 أيام)
         💰 إجمالي: 450 جنيه
         🚚 توصيل — مدينة نصر
         
         تأكيد؟ (أيوه / لأ)"
  ↓
User: "أيوه"
  ↓
Agent: "✅ تم تسجيل طلبك! رقم الطلب: #1042"
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   orchestrator.py                   │
│                                                     │
│  intent → "book_initiate" / "book_continue"         │
│       ↓                                             │
│  BookingStateMachine (session-aware)                │
│       ↓                                             │
│  RentalBookingAgent (multi-turn dialogue)           │
│       ↓                                             │
│  NET_API_Proxy → POST /api/RentalOrders (C# API)   │
└─────────────────────────────────────────────────────┘
```

---

## الـ Components المطلوبة

### 1. نظام State Machine في الـ Session Memory
حالات الـ booking:

| State | المعنى |
|---|---|
| `IDLE` | مفيش booking جارية |
| `AWAITING_DATES` | محتاجين start & end date |
| `AWAITING_DELIVERY_METHOD` | توصيل ولا استلام؟ |
| `AWAITING_ADDRESS` | لو توصيل: محتاجين العنوان |
| `AWAITING_CONFIRMATION` | عرضنا ملخص وننتظر "أيوه/لأ" |
| `CONFIRMED` | تم تسجيل الطلب ✅ |
| `CANCELLED` | ألغى المستخدم |

### 2. Intents جديدة

| Intent | مثال |
|---|---|
| `book_initiate` | "اجّرهولي" / "حجّزه ليا" / "rent it for me" |
| `book_continue` | أي رسالة وفيه booking state مش IDLE |
| `book_confirm` | "أيوه" / "yes" / "تمام" في context التأكيد |
| `book_cancel` | "لأ" / "cancel" / "مش عايز" |

---

## Proposed Changes

### Component 1 — Session Memory (Booking State)

#### [MODIFY] [session_store.py](file:///c:/Users/Asus/Desktop/Grad_project_FCI/memory/session_store.py)

إضافة `BookingContext` dataclass وتخزينه في الـ session جنب conversation history:

```python
@dataclass
class BookingContext:
    state: str = "IDLE"           # state machine
    product_id: int | None = None
    product_name: str | None = None
    price_per_day: float | None = None
    owner_id: str | None = None
    start_date: str | None = None  # ISO format "2026-05-15"
    end_date: str | None = None
    delivery_method: int | None = None  # 0=Pickup, 1=Delivery
    city: str | None = None
    street: str | None = None
    governorate: str | None = None
    rental_order_id: int | None = None  # set after successful booking
```

إضافة functions:
- `get_booking_context(session_id) -> BookingContext`
- `update_booking_context(session_id, **kwargs)`
- `reset_booking_context(session_id)`

---

### Component 2 — Intent Agent (New Intents)

#### [MODIFY] [intent_prompt.txt](file:///c:/Users/Asus/Desktop/Grad_project_FCI/prompts/intent_prompt.txt)

إضافة intents جديدة للـ prompt:

```
- book_initiate: المستخدم يطلب الحجز/التأجير الفعلي
  (مثال: "اجّرهولي"، "حجّزه ليا"، "rent this for me"، "خد الطلب")
- book_continue: رد على سؤال الـ agent أثناء flow الحجز
- book_confirm: تأكيد الطلب ("أيوه"، "yes"، "تمام"، "confirm")
- book_cancel: إلغاء ("لأ"، "no"، "cancel"، "مش عايز")
```

#### [MODIFY] [intent_agent.py](file:///c:/Users/Asus/Desktop/Grad_project_FCI/agents/intent_agent.py)

إضافة context-awareness: لو في booking state مش IDLE، يتحط `booking_state` في الـ prompt علشان الـ LLM يفهم الـ context ويعرف يصنّف `book_continue` / `book_confirm` / `book_cancel`.

---

### Component 3 — [NEW] Booking Entity Extractor

#### [NEW] `agents/booking_entity_extractor.py`

Agent مخصوص لاستخراج entities الـ booking من رسايل المستخدم:

```python
# يستخرج:
{
    "start_date": "2026-05-15",   # normalized ISO date
    "end_date": "2026-05-18",
    "delivery_method": "delivery" | "pickup",
    "city": "Nasr City",
    "street": "Abbas Al-Aqqad",
    "governorate": "Cairo",
    "confirmed": true | false     # للـ confirmation step
}
```

يستخدم `llama-3.1-8b-instant` (fast model) مع prompt متخصص في فهم التواريخ العربية والإنجليزية.

#### [NEW] `prompts/booking_entity_prompt.txt`

Prompt يفهم:
- تواريخ عربية: "بكره"، "الأسبوع الجاي"، "15 مايو"
- تواريخ إنجليزية: "next week", "May 15th", "tomorrow"
- طريقة التسليم: "توصيل"، "delivery"، "هجيب"، "pickup"
- عناوين عربية وإنجليزية

---

### Component 4 — [NEW] Rental Booking Agent

#### [NEW] `agents/rental_booking_agent.py`

الـ agent الرئيسي اللي يدير الـ state machine:

```python
class RentalBookingAgent:
    def handle(session_id, user_query, intent, entities, products) -> dict:
        """
        Returns:
        {
            "agent_message": str,    # الرسالة اللي تتبعتها للمستخدم
            "booking_done": bool,    # True لو تم الطلب
            "order_id": int | None,  # لو booking_done
            "error": str | None
        }
        """
```

**State transitions:**

```
IDLE
  + book_initiate + product known  → AWAITING_DATES
  + book_initiate + no product     → ask user to pick a product first

AWAITING_DATES
  + dates extracted  → AWAITING_DELIVERY_METHOD
  + no dates         → re-ask for dates

AWAITING_DELIVERY_METHOD
  + delivery=pickup  → AWAITING_CONFIRMATION (no address needed)
  + delivery=deliver → AWAITING_ADDRESS

AWAITING_ADDRESS
  + address extracted → AWAITING_CONFIRMATION

AWAITING_CONFIRMATION
  + book_confirm     → call NET_API_Proxy → CONFIRMED
  + book_cancel      → CANCELLED → reset → IDLE
```

---

### Component 5 — [NEW] .NET API Proxy

#### [NEW] `agents/net_api_proxy.py`

طبقة التواصل مع الـ .NET backend الموجود. يعمل `POST` على الـ C# API اللي بيعمل الـ write للـ DB.

```python
import httpx

async def create_rental_order(
    product_id: int,
    renter_id: str,       # من الـ JWT token اللي بييجي مع الـ request
    start_date: str,
    end_date: str,
    delivery_method: int,
    city: str,
    street: str,
    governorate: str,
    terms_agreed: bool = True,
) -> dict:
    """
    Calls: POST {DOTNET_API_BASE}/api/RentalOrders
    Headers: Authorization: Bearer {token}
    Returns: {"success": bool, "order_id": int | None, "error": str | None}
    """
```

> [!IMPORTANT]
> **Critical Design Decision:** الـ AI Python service لا يكتب مباشرة في الـ DB. 
> يروح على الـ .NET API اللي هو المسؤول عن:
> - التحقق من صحة البيانات
> - حساب الأسعار وعمولة البلاتفورم
> - خصم الـ balance / تحديث الـ wallet
> - إرسال الـ notifications
> 
> ده أهم design decision في الـ plan ده.

---

### Component 6 — Updated Request Models

#### [MODIFY] [request_models.py](file:///c:/Users/Asus/Desktop/Grad_project_FCI/models/request_models.py)

إضافة `user_id` و `auth_token` للـ `ChatRequest`:

```python
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"
    user_id: Optional[str] = None      # مطلوب لو عايز يعمل booking
    auth_token: Optional[str] = None   # JWT من الـ .NET API
```

---

### Component 7 — Updated Response Models

#### [MODIFY] `models/response_models.py`

إضافة `booking_action` للـ `ChatResponse`:

```python
class BookingAction(BaseModel):
    state: str                    # current booking state
    order_id: Optional[int] = None
    requires_input: Optional[str] = None  # "dates" | "delivery" | "address" | "confirmation"
    summary: Optional[dict] = None        # ملخص الطلب قبل التأكيد

class ChatResponse(BaseModel):
    answer: str
    intent: str
    products: list[Product]
    total_found: int
    latency_ms: int
    cached: bool
    booking_action: Optional[BookingAction] = None  # ← NEW
```

---

### Component 8 — Updated Orchestrator

#### [MODIFY] [orchestrator.py](file:///c:/Users/Asus/Desktop/Grad_project_FCI/pipeline/orchestrator.py)

إضافة branch جديد للـ booking intents:

```python
SEARCH_INTENTS  = {"search", "filter", "recommend"}
BOOKING_INTENTS = {"book_initiate", "book_continue", "book_confirm", "book_cancel"}

async def run_chat_pipeline(query, session_id, user_id=None, auth_token=None):
    ...
    
    if intent in BOOKING_INTENTS or booking_ctx.state != "IDLE":
        # → Booking path
        booking_result = await RentalBookingAgent.handle(
            session_id, query, intent, entities, 
            user_id=user_id, auth_token=auth_token
        )
        final_answer = booking_result["agent_message"]
        booking_action = BookingAction(state=booking_ctx.state, ...)
    
    elif intent in SEARCH_INTENTS:
        # → Existing search path (unchanged)
        ...
    
    else:
        # → Conversational (greeting, question, etc.)
        ...
```

---

### Component 9 — [NEW] Config

#### [MODIFY] `.env` + `.env.example`

```env
# .NET API Integration
DOTNET_API_BASE=http://localhost:5000
DOTNET_API_TIMEOUT=10
```

---

### Component 10 — Updated `main.py`

#### [MODIFY] [main.py](file:///c:/Users/Asus/Desktop/Grad_project_FCI/main.py)

تمرير `user_id` و `auth_token` من الـ request للـ orchestrator:

```python
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    result = await run_chat_pipeline(
        request.query,
        session_id=request.session_id or "default",
        user_id=request.user_id,
        auth_token=request.auth_token,
    )
    return result
```

---

## ملف جديد: `prompts/booking_entity_prompt.txt`

```
استخرج من رسالة المستخدم المعلومات المتعلقة بطلب الإيجار.

اليوم هو: {today}

الحقول المطلوبة:
- start_date: تاريخ البداية (ISO: YYYY-MM-DD) أو null
- end_date: تاريخ النهاية (ISO: YYYY-MM-DD) أو null
- delivery_method: "delivery" أو "pickup" أو null
- city: المدينة بالإنجليزي أو null
- street: الشارع أو null
- governorate: المحافظة بالإنجليزي أو null
- confirmed: true لو المستخدم بيأكد، false لو بيرفض، null لو مش واضح

تعامل مع التواريخ النسبية: "بكره"=اليوم+1، "الأسبوع الجاي"=اليوم+7، إلخ.

رسالة المستخدم: "{user_query}"

رد بـ JSON فقط.
```

---

## الـ Error Handling

| Scenario | الاستجابة |
|---|---|
| المستخدم مش logged in | "محتاج تسجّل دخول الأول علشان تعمل طلب" |
| المنتج مش available | "للأسف المنتج ده مش متاح في الفترة دي" |
| الـ .NET API فشل | "حصل خطأ في تسجيل الطلب، جرّب تاني" + log |
| المستخدم يغيّر رأيه | "book_cancel" → reset state → IDLE |
| Dates غلط | start > end → "التاريخ مش صح، ممكن تقولي تاني؟" |
| Timeout للـ .NET API | Retry مرة واحدة ثم error message |

---

## الـ Files Summary

| File | Action | الغرض |
|---|---|---|
| `memory/session_store.py` | MODIFY | Add `BookingContext` state machine |
| `prompts/intent_prompt.txt` | MODIFY | Add 4 new booking intents |
| `agents/intent_agent.py` | MODIFY | Pass booking state to classifier |
| `agents/booking_entity_extractor.py` | **NEW** | Extract dates/address/delivery from messages |
| `prompts/booking_entity_prompt.txt` | **NEW** | Prompt for booking entity extraction |
| `agents/rental_booking_agent.py` | **NEW** | Core booking state machine handler |
| `agents/net_api_proxy.py` | **NEW** | HTTP client → .NET REST API |
| `models/request_models.py` | MODIFY | Add `user_id`, `auth_token` to `ChatRequest` |
| `models/response_models.py` | MODIFY | Add `BookingAction` to `ChatResponse` |
| `pipeline/orchestrator.py` | MODIFY | Add booking intent branch |
| `main.py` | MODIFY | Pass auth fields through |
| `.env` / `.env.example` | MODIFY | Add `DOTNET_API_BASE` |

---

## Open Questions

> [!IMPORTANT]
> **1. هل الـ .NET API موجود ومشغّل؟**
> الـ plan بيعتمد على إن الـ Python service يتصل بالـ C# backend اللي بيكتب في الـ DB.
> لو الـ .NET API مش جاهز أو مش accessible، هنحتاج نغيّر الاستراتيجية.
> 
> **الخيارات:**
> - ✅ **(Preferred)** يكمّل الطلب عن طريق الـ .NET REST API
> - 🔄 **(Fallback)** الـ Python يكتب مباشرة في الـ DB عن طريق SQLAlchemy (بدون business logic)

> [!IMPORTANT]  
> **2. الـ Authentication: إزاي المستخدم يبعت JWT؟**
> عشان الـ Python agent يعمل طلب باسم المستخدم، محتاج الـ JWT token.
> 
> **الخيارات:**
> - A. الـ frontend يبعت الـ `auth_token` مع كل `/chat` request
> - B. الـ Python service يعمل machine-to-machine auth مع الـ .NET API

> [!NOTE]
> **3. الـ product selection: إزاي يعرف المستخدم اختار أنهي منتج؟**
> لو المستخدم شاف كذا منتج في الـ search ثم قال "اجّرهولي"، الـ agent محتاج يعرف قصده إيه.
> 
> **الخيارات:**
> - A. الـ frontend يبعت `selected_product_id` في الـ ChatRequest
> - B. الـ agent يسأل "تقصد أنهي منتج بالظبط؟" لو في أكتر من نتيجة

---

## Verification Plan

### Unit Tests
- `test_booking_state_machine.py` — اختبار كل transition
- `test_booking_entity_extractor.py` — تواريخ عربية وإنجليزية
- `test_net_api_proxy.py` — mock HTTP responses

### Integration Test (Manual)
```
1. POST /chat → "عايز أجّر كاميرا كانون"
   Expected: intent=search, products=[...]

2. POST /chat → "اجّرهولي ده"
   Expected: intent=book_initiate, booking_state=AWAITING_DATES

3. POST /chat → "من 20 مايو لـ 23 مايو"
   Expected: booking_state=AWAITING_DELIVERY_METHOD

4. POST /chat → "توصيل"
   Expected: booking_state=AWAITING_ADDRESS

5. POST /chat → "مدينة نصر شارع التسعين"
   Expected: booking_state=AWAITING_CONFIRMATION + summary

6. POST /chat → "أيوه"
   Expected: booking_state=CONFIRMED + order_id returned
```
