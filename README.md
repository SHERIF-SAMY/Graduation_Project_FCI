# 🏪 Nexon AI — Intelligent Rental Marketplace Assistant

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
- [Multilingual Support](#-multilingual-support)
- [System Architecture](#-system-architecture)
- [Agent Pipeline](#-agent-pipeline)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Frontend Features](#-frontend-features)
- [Chat Memory](#-chat-memory)
- [Configuration Reference](#-configuration-reference)

---

## 🎯 Overview

Nexon AI is a **Python FastAPI AI microservice** that powers a conversational assistant for a rental marketplace. Users can ask natural language questions in **Arabic or English** like:

> *"I need a Dell laptop in Nasr City under 200 EGP per day"*
> *"عايز لابتوب ديل في مدينة نصر بأقل من ٢٠٠ جنيه في اليوم"*
> *"Show me new Sony cameras"*
> *"فين أرخص كاميرا في المعادي؟"*

The system extracts intent and entities from the query (in any language), builds a parameterized SQL query, retrieves results from the database, ranks them, and generates a helpful natural language response **in the same language the user wrote in** — while maintaining full **conversation memory** across turns.

**Key constraints:**
- 🔒 The LLM only ever reads from the `Products_LLm` **VIEW** — raw tables are never exposed
- 🛡️ All SQL is **parameterized** — zero SQL injection risk
- ⚡ **No embeddings, no vector databases** — purely SQL-first retrieval
- 🌍 **Fully bilingual** — Arabic and English supported end-to-end

---

## 🌍 Multilingual Support

The system supports **Arabic and English** natively across every layer:

### How Arabic Queries Are Handled

```
المستخدم: "عايز لابتوب في المعادي بسعر ٢٠٠ جنيه"
                        │
         ┌──────────────▼──────────────────┐
         │   Entity Extractor (LLM)        │
         │   Understands Arabic query      │
         │   Translates values to English  │
         └──────────────┬──────────────────┘
                        │
         {name_keyword: "laptop", location: "Maadi", max_price: 200}
                        │
         ┌──────────────▼──────────────────┐
         │   SQL Builder                   │
         │   WHERE Name LIKE '%laptop%'    │
         │   AND LocationArea LIKE '%Maadi%'│
         └──────────────┬──────────────────┘
                        │
         ┌──────────────▼──────────────────┐
         │   Response Generator (LLM)      │
         │   Detects user wrote in Arabic  │
         │   → Replies fully in Arabic     │
         └─────────────────────────────────┘
```

### Arabic Translation Layer (`utils/arabic_utils.py`)

A dedicated translation utility handles **live search** (the `/search/live` endpoint) by converting Arabic keywords to English before running SQL `LIKE` queries:

| Arabic Input | English Translation |
|---|---|
| `لابتوب` | `laptop` |
| `كاميرا` | `camera` |
| `سامسونج` | `Samsung` |
| `المعادي` | `Maadi` |
| `إلكترونيات` | `Electronics` |
| `جديد` | `New` (condition) |
| `مستعمل` | `Used` (condition) |

### Supported Arabic Mappings

| Category | Arabic Examples |
|---|---|
| **Products** | لابتوب، كاميرا، تلفزيون، ثلاجة، غسالة، موبايل، بروجيكتور |
| **Brands** | سامسونج، آبل، سوني، شاومي، هواوي، كانون، نيكون |
| **Locations** | المعادي، مدينة نصر، الزمالك، الدقي، الجيزة، الإسكندرية |
| **Categories** | إلكترونيات، أثاث، سيارات، ملابس، أدوات، كاميرات |
| **Condition** | جديد / جديدة → New، مستعمل / مستخدم → Used |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│          Browser / Any HTTP Client              │
│         http://127.0.0.1:8001                   │
└───────────────────────┬─────────────────────────┘
                        │ HTTP
┌───────────────────────▼─────────────────────────┐
│         PYTHON FASTAPI AI SERVICE               │
│  POST /chat   POST /search   GET /health        │
│  GET /categories   GET /products/{id}           │
│  GET /search/live  (Arabic + English)           │
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
│         ┌────────────────────────┐              │
│         │     SQL Builder        │ ← Pure Python │
│         │  Arabic condition fix  │              │
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
│         GROQ RESPONSE GENERATOR (LangChain)     │
│  llama-3.3-70b-versatile                        │
│  System Prompt + 🧠 Chat History + SQL Results  │
│  → Natural language answer (Arabic or English)  │
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
→ {intent, confidence}         → {category, brand,        ← Translates Arabic
   (search/filter/recommend       location, max_price,        values to English
    question/greet)               condition, name_keyword}    for SQL matching
   │                               │
   └──────────────┬────────────────┘
                  ▼
          SQL Builder (Python)
          → Parameterized SQL + params dict
          → SELECT TOP 20 FROM Products_LLm
          → Handles Arabic condition values (جديد/مستعمل)
                  │
                  ▼
          SQL Executor (SQLAlchemy)
          → Raw rows list
                  │
                  ▼
          Ranker (Python scoring)
          → Top 5 ranked products
                  │
                  ▼
          Response Generator
          llama-3.3-70b-versatile
          + MessagesPlaceholder (last 5 turns)
          → Final answer in user's language (Arabic/English)
                  │
                  ▼
          Response Formatter (Pydantic)
          → {answer, products[], intent, latency_ms, cached}
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **API Framework** | FastAPI 0.115 | REST endpoints, Pydantic validation, CORS |
| **AI Agents** | LangChain + LangChain-Groq | Agent chains, prompt templates, memory |
| **LLM (Fast)** | `llama-3.1-8b-instant` via Groq | Intent & Entity extraction — bilingual |
| **LLM (Quality)** | `llama-3.3-70b-versatile` via Groq | Final response generation in user's language |
| **Parallel Execution** | LangChain `RunnableParallel` | Intent + Entity in parallel |
| **Conversation Memory** | LangChain `MessagesPlaceholder` | Multi-turn chat history |
| **Arabic Support** | `utils/arabic_utils.py` | Dictionary-based AR→EN translation for live search |
| **Database** | SQL Server (Azure) | Product data storage |
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
│   ├── intent_agent.py          # Intent classification — Arabic/English (llama-3.1-8b)
│   ├── entity_extractor.py      # Entity extraction — translates AR→EN values (llama-3.1-8b)
│   ├── sql_builder.py           # Parameterized SQL builder — handles Arabic conditions
│   └── response_generator.py   # Final response — replies in user's language (llama-3.3-70b)
│
├── utils/
│   └── arabic_utils.py          # Arabic→English translation dictionary for live search
│
├── pipeline/
│   └── orchestrator.py          # Chains all agents using RunnableParallel
│
├── memory/
│   └── session_store.py         # Per-session conversation history store
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
│   └── query_cache.py           # In-memory TTL cache (5 minutes)
│
├── models/
│   ├── request_models.py        # Pydantic input schemas (ChatRequest, SearchRequest)
│   └── response_models.py       # Pydantic output schemas (ChatResponse, Product...)
│
├── prompts/
│   ├── system_prompt.txt        # Base system prompt — bilingual, replies in user's language
│   ├── intent_prompt.txt        # Intent classification prompt — Arabic/English aware
│   ├── entity_prompt.txt        # Entity extraction prompt — AR→EN translation rules
│   ├── final_response_prompt.txt# Final answer prompt — mirrors user's language
│   └── sql_builder_prompt.txt   # (Reference only — SQL built in Python)
│
└── frontend/
    ├── index.html               # Single-page chat application
    ├── style.css                # Dark theme + animations
    └── app.js                   # API integration + chat logic
```

---

## ✅ Prerequisites

Before running, make sure you have:

| Requirement | Version | Notes |
|---|---|---|
| Python | ≥ 3.11 | Recommended: Anaconda 3.12 |
| ODBC Driver | 17 or 18 | [Download](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) |
| Groq API Key | — | Free at [console.groq.com](https://console.groq.com) |
| SQL Server | Azure / Local | Connection string from backend |

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

This installs:
- `fastapi`, `uvicorn`, `python-multipart`, `aiofiles`
- `sqlalchemy`, `pyodbc`
- `pydantic`, `python-dotenv`
- `groq`
- `langchain`, `langchain-groq`, `langchain-community`, `langchain-core`

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

### 4. Verify Database View Exists

Make sure the `Products_LLm` VIEW exists in your SQL Server database. If it doesn't, run this SQL:

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
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

| Flag | Meaning |
|---|---|
| `--reload` | Auto-restart on code changes (dev only) |
| `--host 127.0.0.1` | Local only. Use `0.0.0.0` to expose on network |
| `--port 8001` | Port number |

### Open in Browser

```
http://127.0.0.1:8001
```

> Redirects automatically to the **Nexon AI chat interface** at `/app`.

### API Documentation (Swagger)

```
http://127.0.0.1:8001/docs
```

---

## 📡 API Endpoints

| Method | Endpoint | Description | Body / Params |
|---|---|---|---|
| `POST` | `/chat` | Full AI pipeline — chat with memory (Arabic/English) | `{query, session_id?}` |
| `POST` | `/search` | Direct filtered product search | `{category?, brand?, location?, max_price?, condition?, name_keyword?}` |
| `GET` | `/search/live?q=` | Real-time search as user types — supports Arabic queries | `?q=لابتوب` or `?q=laptop` |
| `GET` | `/health` | DB connection + API health check | — |
| `GET` | `/categories` | All available categories from DB | — |
| `GET` | `/products/{id}` | Single product by ID | — |

### Example: Arabic Chat Request

```bash
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "عايز لابتوب في مدينة نصر بأقل من ٢٠٠ جنيه", "session_id": "user_123"}'
```

### Example: English Chat Request

```bash
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "I need a laptop in Nasr City under 200 EGP", "session_id": "user_123"}'
```

### Example: Chat Response

```json
{
  "answer": "وجدت لك لابتوب في مدينة نصر بسعر ١٥٠ جنيه في اليوم...",
  "intent": "search",
  "products": [
    {
      "id": 8,
      "name": "HP Laptop",
      "category": "Computers",
      "brand": "HP",
      "condition": "Used",
      "price_per_day": 150.0,
      "location": "Nasr City",
      "rental_guarantee": false,
      "status": "Available"
    }
  ],
  "total_found": 2,
  "latency_ms": 1240,
  "cached": false
}
```

### Example: Arabic Live Search

```bash
curl "http://127.0.0.1:8001/search/live?q=كاميرا"
# Translates "كاميرا" → "camera" internally before SQL search
```

---

## 🖥️ Frontend Features

| Feature | Description |
|---|---|
| 💬 **Chat Interface** | Real-time conversation in Arabic or English with typing indicator |
| 🃏 **Product Cards** | Auto-rendered from AI response with icons, price, location |
| 🟢 **Health Indicator** | Live DB + API status in sidebar |
| 📂 **Category Browser** | Click any category to start a filtered chat |
| 🔍 **Quick Search** | Filter by keyword, location, price, condition |
| 🔎 **Live Search Bar** | Real-time search as you type — supports Arabic input |
| 🔗 **Product Detail** | Click any card for full product information |
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
AI:   "وجدت ٣ لابتوبات..."

User: "في ديل منهم؟"      ← الـ AI فاكر إن الكلام عن لابتوبات
AI:   "أيوه! Dell Laptop في الزمالك بـ ٢٢٠ جنيه في اليوم..."
```

Memory is **in-process** (RAM only). It resets on server restart. For production, replace with Redis.

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
- ✅ The LLM only reads from `Products_LLm` VIEW — no access to user data, passwords, or financial info
- ✅ A keyword blocklist (`insert`, `update`, `delete`, `drop`, `exec`) guards the executor layer
- ⚠️ Keep `.env` out of version control — add to `.gitignore`

---

## 🚀 Performance

| Query Type | Target Latency |
|---|---|
| Cached (same query repeated) | < 50ms |
| Arabic live search (dictionary translation) | < 10ms |
| Simple product search | < 1.5s |
| Complex filtered query | < 2.5s |

**Optimizations applied:**
- `RunnableParallel` — Intent + Entity extracted simultaneously
- `pool_size=5` — SQLAlchemy connection pool pre-warmed
- In-memory MD5-keyed TTL cache (5 min)
- Only Top 5 results sent to Groq (not all 20)
- Dictionary-based Arabic translation (zero latency, no external API)

---

<div align="center">

Built with ❤️ for the Grad Project — FCI

**FastAPI · LangChain · Groq · SQL Server · Arabic/English**

</div>
