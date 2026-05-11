# 🏪 RentHub AI — Intelligent Rental Marketplace Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-orange?logo=groq&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-Azure-CC2927?logo=microsoftsqlserver&logoColor=white)
![Multilingual](https://img.shields.io/badge/Multilingual-Arabic%20%2F%20English-green?logo=googletranslate&logoColor=white)

**A multi-agent AI assistant for a rental marketplace platform. Understands natural language queries in Arabic and English, builds safe SQL on the fly, ranks results intelligently, and responds in the user's own language — all in under 2 seconds.**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [What's New](#-whats-new)
- [Multilingual Support](#-multilingual-support)
- [System Architecture](#-system-architecture)
- [Agent Pipeline](#-agent-pipeline)
- [Intent-Based Product Display](#-intent-based-product-display)
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

RentHub AI is a **Python FastAPI AI microservice** that powers a conversational assistant for a rental marketplace. Users can ask natural language questions in **Arabic or English** like:

> *"I need a laptop in Zamalek under 220 EGP per day"*
> *"عايز لابتوب في الزمالك بأقل من ٢٢٠ جنيه في اليوم"*
> *"كنت بنور على كاميرات"*
> *"Show me new Sony cameras in Nasr City"*

The system extracts intent and entities from the query (in any language), builds a parameterized SQL query, retrieves results from the database, ranks them, and generates a helpful natural language response **in the same language the user wrote in** — while maintaining full **conversation memory** across turns.

**Key constraints:**
- 🔒 The LLM only ever reads from the `Products_LLm` **VIEW** — raw tables are never exposed
- 🛡️ All SQL is **parameterized** — zero SQL injection risk
- ⚡ **No embeddings, no vector databases** — purely SQL-first retrieval
- 🌍 **Fully bilingual** — Arabic and English supported end-to-end
- 🎭 **Egyptian salesperson personality** — responds naturally like a real marketplace assistant

---

## 🆕 What's New

### Bug Fixes & Improvements

#### 1. 🔧 Fixed Broken `Products_LLm` VIEW
The `Products_LLm` database VIEW was referencing a non-existent column `PricePerDay`. It has been recreated correctly to:
- Use `FinalPricePerDay AS PricePerDay` (the actual column name)
- JOIN `Categories` table to expose `CategoryName`
- JOIN `Subcategories` table to expose `SubcategoryName`
- Include `ImageUrl` from `ProductImages`

Run `fix_view.py` to recreate the VIEW if needed.

#### 2. 🔍 Smarter Search — Plural Keyword Normalization
The SQL builder now normalizes plural English keywords before searching:
- `"laptops"` → searches for `"laptop"` (finds "Dell Laptop")
- `"cameras"` → searches for `"camera"` (finds "Canon DSLR Camera")
- `"bikes"` → searches for `"bike"` (finds "Mountain Bike")

This prevents common "no results found" errors caused by plural vs. singular mismatch.

#### 3. 🎯 Category-Free Search with `name_keyword`
When a user mentions a product name (e.g., "laptop"), the SQL builder:
- **Skips** the `CategoryName` filter (the LLM often guesses the wrong category)
- Searches across `Name`, `CategoryName`, AND `ProductType` using `OR`
- Result: "laptop" finds "Dell Laptop" even though its category is "Computers", not "Electronics"

#### 4. 🧠 Intent-Based Product Display
Products are now shown **only when the user is actually asking for a product**. For greetings, general questions, or out-of-scope messages, the DB query is skipped entirely:

| Intent | DB Query | Product Cards |
|--------|----------|---------------|
| `search` | ✅ Yes | ✅ Shown |
| `filter` | ✅ Yes | ✅ Shown |
| `recommend` | ✅ Yes | ✅ Shown |
| `greet` | ❌ Skipped | ❌ Hidden |
| `question` | ❌ Skipped | ❌ Hidden |
| `out_of_scope` | ❌ Skipped | ❌ Hidden |

#### 5. 🌐 Strict Language Mirroring
The AI now strictly replies in the **exact same language** the user used:
- English message → English reply only
- Arabic message → Egyptian Arabic reply only
- Never mixes languages

#### 6. 🤖 Egyptian Salesperson Personality
The system prompt was rewritten to make the AI behave like a friendly, natural Egyptian marketplace salesperson:
- Speaks Egyptian Arabic naturally (not formal/robotic Arabic)
- Greets warmly without mentioning products unprompted
- Asks follow-up questions **only** when: intent is `recommend` AND the query is vague
- Never asks more than one clarifying question

#### 7. 🚫 No Technical Term Leakage
The AI now never mentions "database", "قاعدة بيانات", "SQL", "system", or any technical term in its responses.

#### 8. 🗃️ Fixed Entity Extraction Hallucinations
The entity extractor was incorrectly inferring `location` and `condition` from unrelated Arabic words:
- `"كنت بنور على لابتوبات"` was extracting `location="Maadi"` and `condition="New"` from the words "على" and "بنور"
- Now the prompt explicitly states: **only extract fields the user explicitly mentioned**

#### 9. 🔎 New `/search/live` Endpoint
A new real-time search endpoint for the sidebar search bar:
- Searches as the user types (debounced 200ms)
- Searches across Name, Brand, Category, ProductType, and Location
- Returns top 8 matching products instantly

#### 10. 🖥️ Updated Frontend Sidebar
The Quick Search sidebar section was redesigned:
- **New "Search" section** at the top — single live search bar with animated dropdown
- **Restored "Quick Search" section** below — original multi-field filter form (keyword, location, max price, condition)

---

## 🌍 Multilingual Support

The system supports **Arabic and English** natively across every layer:

### How Arabic Queries Are Handled

```
User: "كنت بنور على لابتوبات في الزمالك"
                    │
     ┌──────────────▼──────────────────┐
     │   Entity Extractor (LLM)        │
     │   Understands Arabic query      │
     │   Translates values to English  │
     │   ONLY extracts explicit fields │
     └──────────────┬──────────────────┘
                    │
     {name_keyword: "laptop", location: "Zamalek"}
     (category=null — skipped intentionally)
                    │
     ┌──────────────▼──────────────────┐
     │   SQL Builder                   │
     │   "laptop" → strips 's' if any  │
     │   WHERE (Name OR CategoryName   │
     │          OR ProductType)        │
     │         LIKE '%laptop%'         │
     │   AND LocationArea LIKE '%Zamalek%'│
     └──────────────┬──────────────────┘
                    │
     ┌──────────────▼──────────────────┐
     │   Response Generator (LLM)      │
     │   Detects user wrote in Arabic  │
     │   → Replies fully in Egyptian   │
     │     Arabic, like a salesperson  │
     └─────────────────────────────────┘
```

### Supported Arabic Mappings (Entity Extractor)

| Category | Arabic Examples |
|---|---|
| **Products** | لابتوب/لابتوبات، كاميرا/كاميرات، تلفزيون، دراجة، موبايل، بروجيكتور، سماعة، طابعة |
| **Brands** | سامسونج، آبل، سوني، شاومي، هواوي، كانون، نيكون، دل |
| **Locations** | المعادي، مدينة نصر، الزمالك، الدقي، الجيزة، الإسكندرية، هليوبوليس |
| **Categories** | إلكترونيات، أثاث، أدوات، كاميرات، رياضة، ألعاب، صوتيات، كمبيوتر |
| **Condition** | جديد/جديدة → New &nbsp;·&nbsp; مستعمل/مستخدم → Used |

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
│  POST /chat   POST /search   GET /health        │
│  GET /categories   GET /products/{id}           │
│  GET /search/live  (live search bar)            │
│  Pydantic validation · CORS · Static Frontend   │
└───────────────────────┬─────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────┐
│          AI AGENT ORCHESTRATION (LangChain)     │
│  ┌──────────────┐  ┌──────────────────────┐     │
│  │ IntentAgent  │  │  EntityExtractorAgent │     │  ← RunnableParallel
│  │ llama-3.1-8b │  │  llama-3.1-8b-instant│     │  ← Bilingual (AR/EN)
│  └──────────────┘  └──────────────────────┘     │
│              ↓               ↓                  │
│    [If intent = search/filter/recommend only]   │
│         ┌────────────────────────┐              │
│         │     SQL Builder        │ ← Pure Python │
│         │  Plural normalization  │              │
│         │  Category-free search  │              │
│         └───────────┬────────────┘              │
└─────────────────────┼───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│            SQL RETRIEVAL LAYER                  │
│    SQL Server → Products_LLm (VIEW only)        │
│    SQLAlchemy · pyodbc · pool_size=5            │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│              RANKING LAYER                      │
│  Python scoring: keyword × 4 + category × 3    │
│  + brand × 3 + price_fit × 2 + condition × 2   │
│  → Returns Top 5                                │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│     GROQ RESPONSE GENERATOR (LangChain)         │
│  llama-3.3-70b-versatile                        │
│  System Prompt + Chat History + SQL Results     │
│  → Egyptian Arabic or English reply             │
│  → Never mentions technical terms               │
└─────────────────────────────────────────────────┘
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
→ {intent, confidence}         → {category=null, brand,    ← Only explicit fields
   (search/filter/recommend       location, max_price,     ← Translates AR→EN
    question/greet/               condition, name_keyword} ← Singular form only
    out_of_scope)
   │                               │
   └──────────────┬────────────────┘
                  │
         Is intent in {search, filter, recommend}?
                  │
         YES ─────┤──────── NO (greet/question/out_of_scope)
                  │                     │
                  ▼                     ▼
         SQL Builder (Python)    ranked_products = []
         → name_keyword plural fix    (skip DB entirely)
         → category skipped if kw
         → Parameterized SQL
                  │
                  ▼
         SQL Executor (SQLAlchemy)
         → Raw rows from Products_LLm VIEW
                  │
                  ▼
         Ranker (Python scoring)
         → Top 5 ranked products
                  │
                  └─────────────────────┘
                                │
                                ▼
                  Response Generator
                  llama-3.3-70b-versatile
                  + MessagesPlaceholder (last 5 turns)
                  + Intent-aware prompt
                  → Reply in user's exact language
                  → Egyptian Arabic salesperson style
                  → No technical terms
                                │
                                ▼
                  Response Formatter (Pydantic)
                  → {answer, products[], intent, latency_ms, cached}
```

---

## 🌟 Recommendation Engine

The `recommendation/` module provides a **personalized product recommendation system** that learns from each user's behavior over time.

### How It Works

```
User visits /recommend?user_id=X&session_id=Y
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
     • keyword_match   → +4  pts  (from user's top keywords)
     • category_match  → +5  pts
     • brand_match     → +5  pts
     • location_match  → +3  pts
     • budget_match    → +3  pts  (soft: 1 - |price-budget|/budget)
     • popularity      → +2  pts  (from ProductStats)
   Hybrid score = (personalization × profile_confidence)
               + (query_relevance × (1 - profile_confidence))
              │
              ▼
   Diversity Penalty Pass (Greedy):
     - same brand again   → -3 pts
     - same category again → -2 pts
     - same price tier    → -1 pt
              │
              ▼
   Dedup → Top-N → LLM Explanation (recommendation_explainer)
   → RecommendationResponse {products, explanation, user_profile, latency_ms}
```

### Module Files

| File | Responsibility |
|---|---|
| `recommendation_engine.py` | Main async entry point — orchestrates the full pipeline |
| `preference_builder.py` | Queries `UserInteractions` table, applies time-decay, builds `UserProfile` |
| `personalized_ranker.py` | Hybrid scoring (personalization + query relevance) + diversity penalty |
| `interaction_logger.py` | Fire-and-forget async logger — writes to `UserInteractions` table |
| `stats_updater.py` | Updates `ProductStats` (views, clicks, favorites, rent requests) |
| `models.py` | Pydantic schemas: `UserProfile`, `RecommendationRequest`, `RecommendationResponse` |

### DB Tables Used

| Table | Purpose |
|---|---|
| `UserInteractions` | Stores every user action (search, view, click, favorite, rent) |
| `ProductStats` | Aggregated product engagement counts for popularity scoring |
| `Products_LLm` | View used for candidate retrieval |

### Key Design Decisions

- **Cold Start** — users with < 3 interactions get trending/newest products instead of personalized ones
- **Time Decay** — older interactions have exponentially less influence (half-life = 30 days)
- **Candidate Ladder** — expands search progressively until enough candidates are found, avoiding empty results
- **Diversity Penalty** — greedy pass prevents recommending 5 cameras in a row
- **Hybrid Weighting** — blends personalization score and query relevance based on `profile_confidence`
- **Fire-and-forget Logging** — interaction logging never blocks the main response

---

## 🎯 Intent-Based Product Display

Products are **only shown when the user is asking for a product**. This prevents unwanted product cards appearing on greetings or general questions.

### Intents that trigger DB search:
- **`search`** — e.g., "عايز كاميرا", "show me laptops"
- **`filter`** — e.g., "كاميرا بأقل من 200 جنيه في المعادي"
- **`recommend`** — e.g., "إيه أحسن لابتوب عندكم؟"

### Intents that skip DB search:
- **`greet`** — e.g., "سالم عليكم", "hi", "أهلاً"
- **`question`** — e.g., "إزاي بشتغل التطبيق؟", "how does renting work?"
- **`out_of_scope`** — anything unrelated to rental products

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **API Framework** | FastAPI 0.115 | REST endpoints, Pydantic validation, CORS |
| **AI Agents** | LangChain + LangChain-Groq | Agent chains, prompt templates, memory |
| **LLM (Fast)** | `llama-3.1-8b-instant` via Groq | Intent & Entity extraction — bilingual |
| **LLM (Quality)** | `llama-3.3-70b-versatile` via Groq | Final response generation in user's language |
| **Parallel Execution** | LangChain `RunnableParallel` | Intent + Entity in parallel |
| **Conversation Memory** | LangChain `MessagesPlaceholder` | Multi-turn chat history (last 5 turns) |
| **Database** | SQL Server (Azure) | Product data storage |
| **DB View** | `Products_LLm` VIEW | Safe read-only layer exposed to LLM |
| **ORM** | SQLAlchemy 2.0 + pyodbc | Type-safe DB access, connection pooling |
| **Caching** | In-memory TTL dict (5 min) | Repeated query acceleration |
| **Ranking** | Custom Python scorer | Keyword + price + condition weighting |
| **Frontend** | Vanilla HTML/CSS/JS | No framework, no build step |
| **Server** | Uvicorn (ASGI) | Async server for FastAPI |

---

## 📁 Project Structure

```
Grad_project_FCI/
│
├── main.py                      # FastAPI entry point — all endpoints
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (NOT in git)
│
├── agents/
│   ├── intent_agent.py          # Intent classification (llama-3.1-8b) — 6 intents
│   ├── entity_extractor.py      # Entity extraction — translates AR→EN, singular only
│   ├── sql_builder.py           # Parameterized SQL builder — plural fix, category skip
│   ├── response_generator.py   # Final response — Egyptian Arabic or English (llama-3.3-70b)
│   └── recommendation_explainer.py  # LLM-generated explanation for recommendations
│
├── pipeline/
│   └── orchestrator.py          # Intent-gated pipeline — skips DB for greet/question
│
├── recommendation/              # 🌟 Personalized Recommendation Engine (see section below)
│   ├── __init__.py
│   ├── models.py                # Pydantic models: UserProfile, RecommendationRequest/Response
│   ├── recommendation_engine.py # Main engine: candidate retrieval ladder + ranking + caching
│   ├── personalized_ranker.py   # Hybrid scorer: personalization + query relevance + diversity
│   ├── preference_builder.py    # Builds UserProfile from UserInteractions table
│   ├── interaction_logger.py    # Fire-and-forget interaction logging to DB
│   └── stats_updater.py         # Updates ProductStats (views, clicks, favorites, rent requests)
│
├── memory/
│   └── session_store.py         # Per-session conversation history (last 5 turns)
│
├── sql/
│   ├── db.py                    # SQLAlchemy engine + connection pool
│   └── executor.py              # Read-only query executor with injection guard
│
├── ranking/
│   └── ranker.py                # Weighted product scoring → Top 5 (for chat search)
│
├── formatter/
│   └── response_formatter.py    # Pydantic output schema enforcer
│
├── cache/
│   └── query_cache.py           # In-memory TTL cache (5 minutes, MD5-keyed)
│
├── models/
│   ├── request_models.py        # Pydantic input schemas (ChatRequest, SearchRequest)
│   └── response_models.py       # Pydantic output schemas (ChatResponse, Product...)
│
├── prompts/
│   ├── system_prompt.txt        # Egyptian salesperson personality — strict language rules
│   ├── intent_prompt.txt        # Intent classification — 6 classes, Arabic/English examples
│   ├── entity_prompt.txt        # Entity extraction — explicit fields only, no guessing
│   └── final_response_prompt.txt# Intent-aware response — language mirroring, no tech terms
│
└── frontend/
    ├── index.html               # Single-page chat application
    ├── style.css                # Dark theme + live search dropdown + animations
    └── app.js                   # API integration, live search, chat logic
```

---

## ✅ Prerequisites

Before running, make sure you have:

| Requirement | Version | Notes |
|---|---|---|
| Python | ≥ 3.11 | Recommended: Anaconda 3.12 |
| ODBC Driver | 17 or 18 | [Download](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) |
| Groq API Key | — | Free at [console.groq.com](https://console.groq.com) |
| SQL Server | Azure / Local | Connection string from backend developer |

---

## ⚙️ Installation & Setup

### 1. Clone / Navigate to Project

```bash
cd "C:\Users\Asus\Desktop\Grad_project_FCI"
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Groq API Key — get from https://console.groq.com
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# SQL Server connection (from your backend developer)
DB_SERVER=your-server.database.windows.net
DB_PORT=1433
DB_USER=your_username
DB_PASS=your_password
DB_NAME=your_database_name
DB_DRIVER=ODBC Driver 17 for SQL Server
```

### 4. Verify & Fix Database VIEW

Run the diagnostic tool to check if `Products_LLm` VIEW exists and is working:

```bash
python diagnose_db.py
```

If the VIEW is broken (references old column names), recreate it:

```bash
python fix_view.py
```

The correct VIEW definition:

```sql
CREATE VIEW Products_LLm AS
SELECT
    p.Id,
    p.Name,
    p.Description,
    p.Brand,
    p.ProductType,
    p.LocationArea,
    p.Condition,
    p.FinalPricePerDay          AS PricePerDay,
    p.FinalPricePerDay,
    p.BasePricePerDay,
    p.Status,
    p.AverageRating,
    p.TotalReviews,
    p.TotalRentalCount,
    p.RentalGuarantee,
    p.TermsConditions,
    p.CreatedAt,
    p.CategoryId,
    c.Name                      AS CategoryName,
    p.SubcategoryId,
    sc.Name                     AS SubcategoryName
FROM Products p
LEFT JOIN Categories c  ON p.CategoryId    = c.Id
LEFT JOIN Subcategories sc ON p.SubcategoryId = sc.Id;
```

---

## 🚀 Running the Application

### Start the Server

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

| Flag | Meaning |
|---|---|
| `--reload` | Auto-restart on code changes (dev only) |
| `--host 127.0.0.1` | Local only. Use `0.0.0.0` to expose on network |
| `--port 8000` | Port number |

### Open in Browser

```
http://127.0.0.1:8000
```

> Redirects automatically to the **RentHub AI chat interface** at `/app`.

### API Documentation (Swagger)

```
http://127.0.0.1:8000/docs
```

---

## 📡 API Endpoints

| Method | Endpoint | Description | Body / Params |
|---|---|---|---|
| `POST` | `/chat` | Full AI pipeline — chat with memory (Arabic/English) | `{query, session_id?}` |
| `POST` | `/search` | Direct filtered product search | `{category?, brand?, location?, max_price?, condition?, name_keyword?}` |
| `GET` | `/search/live?q=` | Real-time search as user types (live search bar) | `?q=laptop` or `?q=كاميرا` |
| `GET` | `/health` | DB connection + API health check | — |
| `GET` | `/categories` | All active categories from DB | — |
| `GET` | `/products/{id}` | Single product detail by ID | — |

### Example: Arabic Chat Request

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "كنت بنور على لابتوبات", "session_id": "user_123"}'
```

### Example: English Chat Request

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "show me cameras under 200 EGP", "session_id": "user_123"}'
```

### Example: Chat Response

```json
{
  "answer": "عندنا كاميرا Canon DSLR في مدينة نصر بـ 150 جنيه في اليوم، حالتها جديدة وفيها ضمان إيجار. في كمان Nikon Camera في حلوان بـ 140 جنيه. أيهم يناسبك أكتر؟",
  "intent": "search",
  "products": [
    {
      "id": 9,
      "name": "Canon DSLR Camera",
      "category": "Cameras",
      "brand": "Canon",
      "condition": "New",
      "price_per_day": 150.0,
      "location": "Nasr City",
      "rental_guarantee": true,
      "status": "Available"
    }
  ],
  "total_found": 2,
  "latency_ms": 1340,
  "cached": false
}
```

### Example: Live Search

```bash
curl "http://127.0.0.1:8000/search/live?q=camera"
# Returns top 8 matching products instantly
```

---

## 🖥️ Frontend Features

| Feature | Description |
|---|---|
| 💬 **Chat Interface** | Real-time conversation in Arabic or English with typing indicator |
| 🃏 **Product Cards** | Only shown when user asks for a product — not on greetings |
| 🟢 **Health Indicator** | Live DB + API status in sidebar |
| 📂 **Category Browser** | Click any category to start a filtered chat |
| 🔎 **Live Search Bar** | New section — single search bar with animated dropdown, shows results as you type |
| 🔍 **Quick Search** | Multi-field filter form — keyword, location, max price, condition + Search button |
| 🔗 **Product Detail Modal** | Click any card or live search result for full product details |
| 💡 **Suggestion Chips** | Ready-to-use example queries on welcome screen |
| ⚡ **Cache Indicator** | Shows when a response is served from cache |
| 📱 **Responsive** | Works on mobile with collapsible sidebar |

---

## 🧠 Chat Memory

The system maintains **per-session conversation history** using LangChain's `MessagesPlaceholder`.

### How It Works

1. Each browser tab gets a unique `session_id` (stored in `sessionStorage`)
2. Every `/chat` request sends the `session_id`
3. The server retrieves the last **5 conversation turns** for that session
4. These turns are injected into the LLM prompt before the current question
5. The new turn is saved to memory after the response

### Result

```
User: "اعرض لي اللابتوبات"
AI:   "عندنا Dell Laptop في الزمالك بـ 220 جنيه في اليوم..."

User: "عندكم ديل؟"      ← AI remembers we're talking about laptops
AI:   "أيوه! Dell Laptop في الزمالك بـ 220 جنيه في اليوم، جديد ومضمون..."
```

> ⚠️ Memory is **in-process** (RAM only). It resets on server restart. For production, replace with Redis.

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

---

## 🔒 Security Notes

- ✅ SQL is **never generated by the LLM** — only the Python `sql_builder.py` builds queries
- ✅ All queries use **SQLAlchemy parameterized execution** — injection-proof
- ✅ The LLM only reads from `Products_LLm` VIEW — no access to users, passwords, or financial data
- ✅ A keyword blocklist (`insert`, `update`, `delete`, `drop`, `exec`) guards the executor layer
- ✅ The AI never reveals internal technical details (no "database", "SQL", "system" in responses)
- ⚠️ Keep `.env` out of version control — it's listed in `.gitignore`

---

## 🚀 Performance

| Query Type | Target Latency |
|---|---|
| Cached (same query repeated) | < 50ms |
| Live search (sidebar bar) | < 300ms |
| Simple product search | < 1.5s |
| Complex filtered query | < 2.5s |
| Greeting / general question | < 1s (DB skipped) |

**Optimizations applied:**
- `RunnableParallel` — Intent + Entity extracted simultaneously
- `pool_size=5` — SQLAlchemy connection pool pre-warmed
- In-memory MD5-keyed TTL cache (5 min)
- Only Top 5 results sent to Groq (not all 20)
- DB query entirely skipped for non-search intents (greet/question)
- Plural normalization avoids redundant "no results" queries

---

<div align="center">

Built with ❤️ for the Grad Project — FCI

**FastAPI · LangChain · Groq · SQL Server · Arabic/English**

</div>
