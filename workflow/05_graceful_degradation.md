# Workflow 5: Graceful Degradation Under Incomplete Context

> **Chapter 9.3** — Graceful degradation under incomplete context

This diagram shows how the Plant Doctor handles failures at each external dependency — weather API, soil API, and product search — without crashing or producing empty responses.

```mermaid
flowchart TD
    A["Agentic Session<br/>ZIP Code Provided"]

    B["Retrieve Weather"]
    C["Retrieve Soil"]
    D{"Weather<br/>Available?"}
    E{"Soil<br/>Available?"}
    F["Weather Context<br/>Temperature · Forecast · Wind"]
    G["Soil Context<br/>Texture · pH · Drainage"]
    H["Weather Unavailable<br/>Use Generic Guidance"]
    I["Soil Unavailable<br/>Use Generic Guidance"]

    J["Generate Treatment Plan<br/>Using Available Context"]

    K["Search Product Options"]
    L{"Product Search<br/>Available?"}
    M["Add Amazon Product Links"]
    N["Generate Amazon Search Link<br/>Fallback"]

    O(["Treatment Plan Delivered<br/>Notes Any Data Limitations"])

    A --> B
    A --> C

    B --> D
    D -- Yes --> F --> J
    D -- No / Timeout --> H --> J

    C --> E
    E -- Yes --> G --> J
    E -- No / Timeout --> I --> J

    J --> K --> L
    L -- Yes --> M --> O
    L -- "No / Rate Limit" --> N --> O

    classDef source fill:#2196F3,color:#fff,stroke:#1976D2
    classDef context fill:#FFF3E0,color:#4E342E,stroke:#FF9800
    classDef fallback fill:#FF9800,color:#fff,stroke:#E65100
    classDef output fill:#4CAF50,color:#fff,stroke:#388E3C

    class A,B,C,K source
    class F,G,J,M context
    class H,I,N fallback
    class O output
```

## Degradation Strategy

The system follows a **best-effort delivery** principle:

1. **API failures** return structured error dicts, not exceptions — the agent always receives *something*
2. **`format_*_display()` functions** check for the `"error"` key and return a human-readable warning string
3. **Gemini still generates** useful generic treatment advice even when location data is missing
4. **Product search fallback** builds an Amazon search URL from the query string, so the user always gets a clickable link
5. **No hard crashes** — `try/except` blocks at every external call boundary

This maps directly to **Section 9.3's** principle: an agent that silently degrades is safer than one that throws unhandled exceptions in production.
