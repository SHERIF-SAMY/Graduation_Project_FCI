# AI Features Workflow Diagrams

ملف بيوضح تدفق العمليات (Workflows) الخاص بكل ميزة من مميزات الـ AI في المشروع بكل التفاصيل والاحتمالات الممكنة، باستخدام `mermaid` diagrams.

## 1. Smart Search Workflow

الرسمة بتوضح إزاي النظام بيتعامل مع أي استعلام بحث (Search Query) من لحظة دخول المستخدم لحد عرض النتائج:

```mermaid
graph TD
    A[User types query] --> B{Check Cache?}
    B -- Cache Hit --> C[Return Cached Results]
    C --> D[Add Turn to Memory]
    B -- Cache Miss --> E[RunnableParallel]
    
    E --> F[Intent Agent<br/>llama-3.1-8b]
    E --> G[Entity Extractor<br/>llama-3.1-8b]
    
    F -- "Classifies as search/filter/recommend" --> H{Is Intent Search?}
    
    H -- Yes --> I[SQL Builder]
    G -- "Extracts: brand, category, price, etc." --> I
    
    I -- Builds Parameterized SQL --> J[SQL Executor]
    J -- "Queries Products_LLm VIEW" --> K[Database]
    K --> L[Raw Products]
    
    L --> M[Custom Ranker]
    M -- "Scores: Keyword*4 + Brand*3..." --> N[Top 5 Ranked Products]
    
    N --> O[Response Generator<br/>llama-3.3-70b]
    O -- "Generates Egyptian Arabic/English Reply" --> P[Response Formatter]
    
    P --> Q[Set Cache TTL=5min]
    Q --> R[Return JSON to User]
    
    H -- No --> S[Other Agent Route]
```

---

## 2. End-to-End Chat Agent (Booking & Cancellation Flow)

الرسمة بتوضح الـ State Machine الخاصة بالحجز، وازاي النظام بيتابع حالة الحجز خطوة بخطوة مع المستخدم (Booking Context):

```mermaid
stateDiagram-v2
    [*] --> IDLE
    
    state "Booking Initialization" as Init
    IDLE --> Init : User says "I want to rent this"
    
    state "Availability Check" as Check
    Init --> Check : Check DB (RentalOrders)
    Check --> IDLE : Product already rented (Reject)
    Check --> AWAITING_DATES : Product Available
    
    AWAITING_DATES --> AWAITING_DELIVERY_METHOD : User provides start & end dates
    
    AWAITING_DELIVERY_METHOD --> AWAITING_ADDRESS : "Delivery"
    AWAITING_DELIVERY_METHOD --> AWAITING_CONFIRMATION : "Pickup from owner"
    
    AWAITING_ADDRESS --> AWAITING_CONFIRMATION : User provides full address
    
    state "Confirmation Summary" as Summary
    AWAITING_CONFIRMATION --> Summary : Show Price & Details
    Summary --> CONFIRMED : User says "Yes/Confirm"
    Summary --> CANCELLED : User says "No/Cancel"
    
    CONFIRMED --> .NET_API_Create : Send HTTP POST to .NET
    .NET_API_Create --> IDLE : Booking Success
    
    CANCELLED --> IDLE : Clear Memory
    
    %% Cancellation Flow %%
    IDLE --> AWAITING_CANCEL_CONFIRM : User says "Cancel my order"
    AWAITING_CANCEL_CONFIRM --> .NET_API_Cancel : User says "Yes"
    .NET_API_Cancel --> IDLE : Send HTTP PUT (Cancel)
    
    %% Escape Hatch %%
    AWAITING_DATES --> IDLE : "Escape Hatch" (User asks general question)
    AWAITING_DELIVERY_METHOD --> IDLE : "Escape Hatch"
    AWAITING_ADDRESS --> IDLE : "Escape Hatch"
```

---

## 3. Personalized Recommendation System

الرسمة بتوضح الـ Recommendation Engine من وقت تجميع البيانات وحتى عرض اقتراحات للمستخدم (Personalized vs Cold-Start):

```mermaid
graph TD
    A[User visits /recommendations] --> B[Fetch Last 50 Interactions<br/>UserInteractions Table]
    
    subgraph Background Task
        Z[User Views/Searches/Clicks] --> Y[Interaction Logger]
        Y -- Asynchronous Insert --> X[(UserInteractions)]
    end
    
    B --> C[Preference Builder]
    C -- "Calculates Time-decay Weights" --> D[User Profile]
    D -- "Includes: favorite_brand, budget, location" --> E{Confidence Check}
    
    E -- Confidence < 0.15 --> F[Cold Start Mode]
    F --> G[Fetch Trending from ProductStats]
    G --> H[Fallback to Newest if no Trending]
    
    E -- Confidence >= 0.15 --> I[Personalized Mode]
    I --> J[Candidate Expansion Ladder]
    J -- Step 1 --> K[Match Brand AND Category]
    J -- Step 2 --> L[Match Category Only]
    J -- Step 3 --> G
    
    H --> M[Personalized Ranker]
    K --> M
    L --> M
    
    M -- "+4 Keyword, +5 Brand, +5 Cat, +3 Location, +3 Budget" --> N[Score Candidates]
    N --> O[Return Top 5 Recommendations]
```
