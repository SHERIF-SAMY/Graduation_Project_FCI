# 🏪 RentHub AI — Intelligent Rental Marketplace Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-orange?logo=groq&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-Azure-CC2927?logo=microsoftsqlserver&logoColor=white)
![Multilingual](https://img.shields.io/badge/Multilingual-Arabic%20%2F%20English-green?logo=googletranslate&logoColor=white)

**A multi-agent AI assistant for a rental marketplace platform. Understands Arabic and English, books rentals end-to-end via the .NET API, cancels orders, and responds like a real Egyptian marketplace salesperson — all under 2 seconds.**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Agentic Booking System](#-agentic-booking-system)
- [Order Cancellation](#-order-cancellation)
- [Authentication & Login](#-authentication--login)
- [System Architecture](#-system-architecture)
- [Agent Pipeline](#-agent-pipeline)
- [Recommendation Engine](#-recommendation-engine)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Frontend Features](#-frontend-features)
- [Chat Memory](#-chat-memory)
- [Configuration Reference](#-configuration-reference)
- [Security Notes](#-security-notes)
- [Performance](#-performance)

---

## 🎯 Overview

RentHub AI is a **Python FastAPI AI microservice** that powers a fully conversational rental booking assistant. Users can:

- Search for products in **Arabic or English**
- **Book a rental** end-to-end through natural conversation
- **Cancel an existing order** with confirmation step
- Get **personalized recommendations** based on their history

> *"عايز أجّر لابتوب Dell بكره لمدة 3 أيام، توصيل على مدينة نصر"*
> → The bot collects all details, shows a summary with price, confirms with the user, and registers the order in the .NET backend — all in one conversation.

**Key constraints:**
- 🔒 The LLM only ever reads from the `Products_LLm` **VIEW** — raw tables are never exposed
- 🛡️ All SQL is **parameterized** — zero SQL injection risk
- ⚡ **No embeddings, no vector databases** — purely SQL-first retrieval
- 🌍 **Fully bilingual** — Arabic and English supported end-to-end
- 🎭 **Egyptian salesperson personality** — responds naturally like a real marketplace assistant
- 📦 **Write operations go through the .NET API** — Python never writes directly to the DB

---

## 🤖 Agentic Booking System

The chatbot is now a full **Agentic Booking System** capable of completing an entire rental transaction through natural conversation.

### Booking Flow

```
User: "حجزلي الكاميرا دي"
  ↓
Bot: "من إمتى لإمتى بالظبط؟"
  ↓
User: "من 20 مايو لـ 23 مايو"
  ↓
Bot: "تحب توصيل ولا استلام من المالك؟"
  ↓
User: "توصيل"
  ↓
Bot: "العنوان بالتفصيل؟ (المدينة، الشارع، المحافظة)"
  ↓
User: "شارع التسعين، مدينة نصر، القاهرة"
  ↓
Bot: "ممتاز! هأكد الطلب ده:
      📦 المنتج: Canon DSLR Camera
      📅 من: 2026-05-20 إلى 2026-05-23
      🚚 توصيل: شارع التسعين، مدينة نصر، القاهرة
      💰 السعر: 150 EGP/يوم × 4 يوم = 600 EGP

      تأكيد؟ (أيوه / لأ)"
  ↓
User: "أيوه"
  ↓
Bot: "✅ تم تسجيل طلبك بنجاح! رقم الطلب: 7"
```

### State Machine

| State | المعنى |
|---|---|
| `IDLE` | لا يوجد booking جارية |
| `AWAITING_PRODUCT` | محتاجين تحديد المنتج المطلوب |
| `AWAITING_DATES` | محتاجين تاريخ البداية والنهاية |
| `AWAITING_DELIVERY_METHOD` | توصيل ولا استلام؟ |
| `AWAITING_ADDRESS` | لو توصيل: محتاجين العنوان |
| `AWAITING_CONFIRMATION` | عرضنا ملخص وننتظر تأكيد |
| `AWAITING_CANCEL_CONFIRM` | ننتظر تأكيد الإلغاء |
| `CONFIRMED` | تم تسجيل الطلب ✅ |
| `CANCELLED` | ألغى المستخدم |

### Booking Intents

| Intent | مثال |
|---|---|
| `book_initiate` | "اجّرهولي"، "حجّزه ليا"، "rent this for me" |
| `book_continue` | رد على أي سؤال أثناء الـ booking flow |
| `book_confirm` | "أيوه"، "yes"، "تمام"، "confirm" |
| `book_cancel` | "لأ"، "no"، "cancel"، "مش عايز" |

### Product Availability Check

Before starting any booking flow, the system automatically checks if the product has an active order (Pending, Accepted, or In Progress). If it does, the bot responds:

> *"عذراً، المنتج ده محجوز دلوقتي ومش متاح للإيجار. اقدر اساعدك تلاقي منتج تاني."*

### Price Calculation

The confirmation summary includes an **inclusive day count** (matching the .NET API calculation):
- May 15 → May 17 = **3 days** (15 + 16 + 17)
- Total = price_per_day × num_days

---

## 🚫 Order Cancellation

Users can cancel an existing order through natural conversation.

### Cancellation Flow

```
User: "عايز أكنسل الاوردر"
  ↓
Bot: (يجيب الطلبات من الـ DB)
     "طلباتك الحالية:
      - رقم 4: Dell Laptop
      - رقم 6: Sony Headphones
      ادخل رقم الطلب اللي عايز تلغيه:"
  ↓
User: "4"
  ↓
Bot: "⚠️ متأكد إنك عايز تلغي الطلب رقم 4؟ قول (أيوه / لأ)"
  ↓
User: "أيوه"
  ↓
Bot: "✅ تم إلغاء الطلب رقم 4 بنجاح!"
```

The system calls `PUT /api/RentalOrder/{id}/cancel` on the .NET API with the user's JWT token. The order status in the database is updated to **6 (Cancelled)**.

---

## 🔐 Authentication & Login

### Login Modal (Frontend)

The frontend has a **Login Modal** built into the chat interface. Users can log in without leaving the page:

1. Click **"Login / Signup"** in the top-right header
2. Enter email and password
3. The frontend calls `POST /auth/login` (our Python proxy)
4. The JWT token is stored in `localStorage`
5. The header updates to show the user's name with a Logout button

### Auth Proxy (No CORS Issues)

To avoid browser CORS restrictions, the frontend never calls the .NET API directly. Instead, it calls our Python backend which proxies the request:

```
Browser → POST /auth/login → Python FastAPI → POST /api/Account/login → .NET API → token
```

### Token Forwarding

Every chat message automatically includes the JWT token:

```json
{
  "query": "عايز أجّر لابتوب",
  "session_id": "sess_abc123",
  "user_id": "83e358a2-...",
  "auth_token": "eyJhbGci..."
}
```

The Python backend passes this token to the .NET API when creating or cancelling orders.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│          Browser / Any HTTP Client              │
│         http://127.0.0.1:8000                   │
└───────────────────────┬─────────────────────────┘
                        │ HTTP
┌───────────────────────▼─────────────────────────┐
│         PYTHON FASTAPI AI SERVICE               │
│  POST /chat        POST /search                 │
│  POST /auth/login  (proxy → .NET API)           │
│  GET  /health      GET  /categories             │
│  GET  /search/live GET  /products/{id}          │
│  Pydantic validation · CORS · Static Frontend   │
└───────────────────────┬─────────────────────────┘
                        │
         ┌──────────────┴──────────────┐
         │                             │
┌────────▼─────────────┐   ┌──────────▼──────────────┐
│  AI AGENT PIPELINE   │   │  .NET REST API           │
│  (Search & Booking)  │   │  rentalplatform.runasp.net│
│                      │   │                          │
│  IntentAgent         │   │  POST /api/RentalOrder   │
│  EntityExtractor     │   │  PUT  /api/RentalOrder/  │
│  BookingAgent        │──▶│       {id}/cancel        │
│  BookingEntityExtr.  │   │  POST /api/Account/login │
│  NET_API_Proxy       │   └──────────────────────────┘
└────────┬─────────────┘
         │
┌────────▼─────────────────────────────────────────┐
│            SQL RETRIEVAL LAYER (Read Only)        │
│    SQL Server → Products_LLm VIEW                │
│    RentalOrders (availability check)             │
│    SQLAlchemy · pyodbc · pool_size=5             │
└────────┬─────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────┐
│              RANKING LAYER                        │
│  Python scoring: keyword × 4 + category × 3      │
│  + brand × 3 + price_fit × 2 + condition × 2     │
│  → Returns Top 5                                  │
└────────┬─────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────┐
│     GROQ RESPONSE GENERATOR (LangChain)           │
│  llama-3.3-70b-versatile                          │
│  System Prompt + Chat History + SQL Results       │
│  → Egyptian Arabic or English reply               │
└──────────────────────────────────────────────────┘
```

---

## 🤖 Agent Pipeline

Each `/chat` request flows through this pipeline:

```
User Query (Arabic or English)
   │
   ├──────────────────────────────────┐
   ▼  (RunnableParallel)              ▼
Intent Agent                   Entity Extractor
llama-3.1-8b-instant           llama-3.1-8b-instant
→ {intent, booking_state}      → {dates, address, confirmation...}
   │                               │
   └──────────────┬────────────────┘
                  │
         ┌────────┴──────────┐
         │                   │
  Booking Intent?      Search Intent?
  (or active state)         │
         │                   ▼
         ▼          SQL Builder → DB → Ranker
  BookingAgent        → Response Generator
  (State Machine)
  ├─ check availability
  ├─ collect dates / address
  ├─ confirm with price summary
  └─ call .NET API (create/cancel order)
         │
         ▼
  Response Formatter (Pydantic)
  → {answer, products[], intent, latency_ms, cached, booking_action}
```

### Cache Behavior

The in-memory cache is **bypassed** for booking/cancellation flows to prevent stale state being replayed:
- ✅ Cache used: pure search/recommend queries
- ❌ Cache skipped: any session with active booking state
- ❌ Cache not written: any response containing `booking_action`

### Escape Hatch

If a session gets stuck in a booking state (e.g., `AWAITING_PRODUCT`), sending a non-booking message like a greeting or search query automatically **resets the booking context** back to `IDLE`.

---

## 🌟 Recommendation Engine

The `recommendation/` module provides a **personalized product recommendation system** that learns from each user's behavior over time.

### How It Works

```
User visits /recommendations?session_id=Y
              │
              ▼
   PreferenceBuilder — reads last 50 rows from UserInteractions table
   Applies time-decay weighting (exponential, 30-day half-life)
   Builds UserProfile: favorite_brand, favorite_category,
                        preferred_location, average_budget,
                        top_keywords, profile_confidence
              │
    profile_confidence < 0.15? → cold_start mode (trending/newest)
    profile_confidence ≥ 0.15? → personalized mode
              │
              ▼
   Candidate Expansion Ladder (stops when enough candidates found):
     1. Brand AND Category match
     2. Category only match
     3. Trending products (ProductStats: views+clicks+favorites+rents)
     4. Newest products (Id DESC fallback)
              │
              ▼
   PersonalizedRanker — scores each candidate:
     • keyword_match   → +4  pts
     • category_match  → +5  pts
     • brand_match     → +5  pts
     • location_match  → +3  pts
     • budget_match    → +3  pts
     • popularity      → +2  pts
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **API Framework** | FastAPI 0.115 | REST endpoints, Pydantic validation, CORS |
| **AI Agents** | LangChain + LangChain-Groq | Agent chains, prompt templates, memory |
| **LLM (Fast)** | `llama-3.1-8b-instant` via Groq | Intent & Entity extraction + Booking entities |
| **LLM (Quality)** | `llama-3.3-70b-versatile` via Groq | Final response generation |
| **Parallel Execution** | LangChain `RunnableParallel` | Intent + Entity in parallel |
| **Conversation Memory** | LangChain `MessagesPlaceholder` | Multi-turn chat history (last 5 turns) |
| **Booking State** | In-memory `BookingContext` dataclass | Per-session booking state machine |
| **HTTP Client** | `httpx` (async) | Calls to .NET REST API (create/cancel orders) |
| **Database** | SQL Server (Azure) | Product data + orders storage |
| **DB View** | `Products_LLm` VIEW | Safe read-only layer exposed to LLM |
| **ORM** | SQLAlchemy 2.0 + pyodbc | Type-safe DB access, connection pooling |
| **Caching** | In-memory TTL dict (5 min) | Repeated search query acceleration |
| **Ranking** | Custom Python scorer | Keyword + price + condition weighting |
| **Frontend** | Vanilla HTML/CSS/JS | No framework, no build step |
| **Server** | Uvicorn (ASGI) | Async server for FastAPI |

---

## 📁 Project Structure

```
Grad_project_FCI/
│
├── main.py                      # FastAPI entry point — all endpoints incl. /auth/login proxy
├── requirements.txt             # Python dependencies (includes httpx)
├── .env                         # Environment variables (NOT in git)
├── check_orders.py              # Utility script — displays all rental orders from DB
│
├── agents/
│   ├── intent_agent.py              # Intent classification — booking-state aware
│   ├── entity_extractor.py          # Search entity extraction (translates AR→EN)
│   ├── booking_entity_extractor.py  # Booking entity extraction (dates, address, confirmation)
│   ├── rental_booking_agent.py      # Core booking state machine + cancellation flow
│   ├── net_api_proxy.py             # HTTP proxy → .NET API (create & cancel orders)
│   ├── sql_builder.py               # Parameterized SQL builder
│   └── response_generator.py        # Final response — Egyptian Arabic or English
│
├── pipeline/
│   └── orchestrator.py          # Smart routing: search / booking / cancel + cache bypass
│
├── recommendation/              # 🌟 Personalized Recommendation Engine
│   ├── __init__.py
│   ├── models.py                # Pydantic models
│   ├── recommendation_engine.py # Main engine
│   ├── personalized_ranker.py   # Hybrid scorer
│   ├── preference_builder.py    # UserProfile builder
│   ├── interaction_logger.py    # Fire-and-forget interaction logging
│   └── stats_updater.py         # Updates ProductStats
│
├── memory/
│   └── session_store.py         # Conversation history + BookingContext per session
│
├── sql/
│   ├── db.py                    # SQLAlchemy engine + connection pool
│   └── executor.py              # Read-only query executor with injection guard
│
├── ranking/
│   └── ranker.py                # Weighted product scoring → Top 5
│
├── formatter/
│   └── response_formatter.py    # Pydantic output schema enforcer
│
├── cache/
│   └── query_cache.py           # In-memory TTL cache (5 min, MD5-keyed)
│
├── models/
│   ├── request_models.py        # ChatRequest (query, session_id, user_id, auth_token)
│   └── response_models.py       # ChatResponse + BookingAction
│
├── prompts/
│   ├── system_prompt.txt            # Egyptian salesperson personality
│   ├── intent_prompt.txt            # Intent classification — 10 intents incl. booking
│   ├── entity_prompt.txt            # Search entity extraction prompt
│   ├── booking_entity_prompt.txt    # Booking-specific entity extraction prompt
│   └── final_response_prompt.txt    # Intent-aware response generation
│
└── frontend/
    ├── index.html               # Single-page app with Login Modal
    ├── style.css                # Dark theme + animations
    └── app.js                   # Auth logic, booking flow, chat, live search
```

---

## ✅ Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | ≥ 3.11 | Recommended: Anaconda 3.12 |
| ODBC Driver | 17 or 18 | [Download](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) |
| Groq API Key | — | Free at [console.groq.com](https://console.groq.com) |
| SQL Server | Azure | Connection string from backend developer |
| .NET Backend | Running | `http://rentalplatform.runasp.net` |

---

## ⚙️ Installation & Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

> `requirements.txt` includes `httpx` for the .NET API proxy calls.

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Groq API Key
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# SQL Server connection
DB_SERVER=your-server.database.windows.net
DB_PORT=1433
DB_USER=your_username
DB_PASS=your_password
DB_NAME=your_database_name
DB_DRIVER=ODBC Driver 17 for SQL Server

# .NET API Integration
DOTNET_API_BASE=http://rentalplatform.runasp.net
DOTNET_API_TIMEOUT=10
```

### 3. Start the Server

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Open in Browser

```
http://127.0.0.1:8000
```

---

## 📡 API Endpoints

| Method | Endpoint | Description | Body / Params |
|---|---|---|---|
| `POST` | `/chat` | Full AI pipeline — search + booking + cancel | `{query, session_id?, user_id?, auth_token?}` |
| `POST` | `/auth/login` | **Proxy** → .NET login — returns JWT token | `{email, password}` |
| `POST` | `/search` | Direct filtered product search | `{category?, brand?, location?, max_price?, condition?, name_keyword?}` |
| `GET` | `/search/live?q=` | Real-time search as user types | `?q=laptop` |
| `GET` | `/recommendations` | Personalized product recommendations | `?session_id=...` |
| `GET` | `/health` | DB connection + API health check | — |
| `GET` | `/categories` | All active categories from DB | — |
| `GET` | `/products/{id}` | Single product detail by ID | — |

### Example: Book via Chat

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "عايز أجّر اللابتوب ده",
    "session_id": "user_123",
    "user_id": "83e358a2-997c-...",
    "auth_token": "eyJhbGci..."
  }'
```

### Example: Login (Auth Proxy)

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "MyPassword123"}'
```

Response:
```json
{
  "token": {
    "token": "eyJhbGci...",
    "userId": "83e358a2-...",
    "email": "user@example.com",
    "fullName": "fouad",
    "role": "User"
  }
}
```

### Chat Response Schema

```json
{
  "answer": "تمام! محتاج تأجره من إمتى لإمتى بالظبط؟",
  "intent": "book_initiate",
  "products": [],
  "total_found": 0,
  "latency_ms": 890,
  "cached": false,
  "booking_action": {
    "state": "AWAITING_DATES",
    "order_id": null,
    "requires_input": "dates",
    "summary": null
  }
}
```

---

## 🖥️ Frontend Features

| Feature | Description |
|---|---|
| 💬 **Chat Interface** | Real-time conversation in Arabic or English with typing indicator |
| 🔐 **Login Modal** | Login without leaving the page — JWT token stored in localStorage |
| 👤 **User Header** | Shows logged-in user's name + Logout button after authentication |
| 🃏 **Product Cards** | Only shown when user asks for a product |
| 🟢 **Health Indicator** | Live DB + API status in sidebar |
| 📂 **Category Browser** | Click any category to start a filtered chat |
| 🔎 **Live Search Bar** | Animated dropdown, shows results as you type |
| 🔍 **Quick Search** | Multi-field filter form (keyword, location, price, condition) |
| 🔗 **Product Detail Modal** | Click any card for full product details |
| ⚡ **Cache Indicator** | Shows `⚡ cached` when response served from cache |
| 📱 **Responsive** | Works on mobile with collapsible sidebar |

---

## 🧠 Chat Memory

The system maintains **per-session state** for both conversation history and booking context.

### Conversation History
- Each browser tab gets a unique `session_id` (stored in `sessionStorage`)
- The server keeps the last **5 conversation turns** per session
- Injected into the LLM prompt as context

### Booking Context (`BookingContext`)
- Stored in RAM per `session_id`
- Persists across multiple messages until the booking is completed or cancelled
- Fields: `state`, `product_id`, `product_name`, `price_per_day`, `start_date`, `end_date`, `delivery_method`, `city`, `street`, `governorate`, `rental_order_id`, `pending_cancel_order_id`

> ⚠️ All memory is **in-process** (RAM only). It resets on server restart. For production, use Redis.

---

## 🔧 Utility Scripts

| Script | Purpose |
|---|---|
| `check_orders.py` | Display all rental orders from the DB with human-readable status names |

```bash
python check_orders.py
```

**Status values:**

| Code | Meaning |
|---|---|
| 0 | Pending |
| 1 | Accepted |
| 2 | Rejected |
| 3 | Completed |
| 4 | In Progress |
| 5 | Returned |
| 6 | CANCELLED |

---

## ⚙️ Configuration Reference

| Variable | Description | Example |
|---|---|---|
| `GROQ_API_KEY` | Groq Cloud API key | `gsk_xxx...` |
| `DB_SERVER` | SQL Server hostname | `db46830.public.databaseasp.net` |
| `DB_PORT` | SQL Server port | `1433` |
| `DB_USER` | Database username | `db46830` |
| `DB_PASS` | Database password | `****` |
| `DB_NAME` | Database name | `db46830` |
| `DB_DRIVER` | ODBC Driver name | `ODBC Driver 17 for SQL Server` |
| `DOTNET_API_BASE` | .NET API base URL | `http://rentalplatform.runasp.net` |
| `DOTNET_API_TIMEOUT` | HTTP timeout (seconds) | `10` |

---

## 🔒 Security Notes

- ✅ SQL is **never generated by the LLM** — only `sql_builder.py` builds queries
- ✅ All queries use **SQLAlchemy parameterized execution** — injection-proof
- ✅ The LLM only reads from `Products_LLm` VIEW — no access to users, passwords, or financial data
- ✅ A keyword blocklist (`insert`, `update`, `delete`, `drop`, `exec`) guards the executor layer
- ✅ The AI never reveals internal technical details in responses
- ✅ Auth proxy prevents CORS — browser never calls .NET API directly
- ✅ JWT token is stored in `localStorage` and sent only to our own Python backend
- ⚠️ Keep `.env` out of version control — listed in `.gitignore`

---

## 🚀 Performance

| Query Type | Target Latency |
|---|---|
| Cached search (repeated) | < 50ms |
| Live search (sidebar) | < 300ms |
| Simple product search | < 1.5s |
| Booking step (state update) | < 1s |
| Booking confirmation (.NET API call) | < 2.5s |
| Order cancellation (.NET API call) | < 2s |
| Greeting / general question | < 1s (DB skipped) |

**Optimizations applied:**
- `RunnableParallel` — Intent + Entity extracted simultaneously
- `pool_size=5` — SQLAlchemy connection pool pre-warmed
- In-memory MD5-keyed TTL cache (5 min) — **bypassed** for booking/cancel flows
- Only Top 5 results sent to Groq (not all DB rows)
- DB query entirely skipped for non-search intents (greet/question)
- Booking responses never cached (stateful per session)

---

<div align="center">

Built with ❤️ for the Grad Project — FCI

**FastAPI · LangChain · Groq · SQL Server · .NET REST API · Arabic/English**

</div>
