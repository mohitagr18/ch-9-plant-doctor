# Workflow 5: Graceful Degradation Under Incomplete Context

> **Chapter 9.3** — Graceful degradation under incomplete context

This diagram shows how the Plant Doctor handles failures at each external dependency — weather API, soil API, and product search — without crashing or producing empty responses.

```mermaid
flowchart TD
    A["Agentic Session Started\nzipcode provided"] --> B["get_weather(zipcode)"]
    A --> C["get_soil_type(zipcode)"]

    B --> B1{"NOAA API\nReachable?"}
    B1 -- Yes --> B2["✅ Weather Data\nTemperature, Forecast, Wind"]
    B1 -- No / Timeout --> B3["⚠️ Error Dict\n{error: 'Failed to fetch...'}"]
    B3 --> B4["format_weather_display()\nReturns: '⚠️ Weather data unavailable'"]
    B2 --> B5["Weather context\nadded to prompt"]
    B4 --> B5

    C --> C1{"USDA SDA API\nReachable?"}
    C1 -- Yes --> C2["✅ Soil Data\nTexture, pH, Drainage"]
    C1 -- No / Timeout --> C3["⚠️ Error Dict\n{error: 'Failed to fetch...'}"]
    C3 --> C4["format_soil_display()\nReturns: '⚠️ Soil data unavailable'"]
    C2 --> C5["Soil context\nadded to prompt"]
    C4 --> C5

    B5 --> D["Gemini generates\ntreatment text\n(with available context)"]
    C5 --> D

    D --> E["search_amazon_products()"]
    E --> E1{"Serper API\nReachable?"}
    E1 -- Yes --> E2["✅ Real Amazon product links"]
    E1 -- No / Rate limit --> E3["⚠️ Fallback:\nAmazon search URL generated\nfrom query string"]
    E2 --> F["Product links included"]
    E3 --> F

    F --> G(["📋 Treatment Plan Delivered\n(may note data limitations)"])

    B3 -.->|"Gemini still\ngenerates generic advice"| D
    C3 -.->|"Gemini still\ngenerates generic advice"| D

    style B3 fill:#FF9800,color:#fff
    style C3 fill:#FF9800,color:#fff
    style E3 fill:#FF9800,color:#fff
    style B4 fill:#FFF3E0
    style C4 fill:#FFF3E0
    style G fill:#4CAF50,color:#fff
```

## Degradation Strategy

The system follows a **best-effort delivery** principle:

1. **API failures** return structured error dicts, not exceptions — the agent always receives *something*
2. **`format_*_display()` functions** check for the `"error"` key and return a human-readable warning string
3. **Gemini still generates** useful generic treatment advice even when location data is missing
4. **Product search fallback** builds an Amazon search URL from the query string, so the user always gets a clickable link
5. **No hard crashes** — `try/except` blocks at every external call boundary

This maps directly to **Section 9.3's** principle: an agent that silently degrades is safer than one that throws unhandled exceptions in production.
