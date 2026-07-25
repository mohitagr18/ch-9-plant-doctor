# Workflow 3: Gemini Tool-Calling Sequence

> **Chapter 9.2** — Integrating specialist tools: how Gemini autonomously orchestrates multi-tool calls

This sequence diagram traces the exact message flow between the Streamlit UI, the Gemini agent, and each external tool during a treatment recommendation generation.

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant Agent as Gemini 2.5 Flash Agent
    participant Weather as NOAA Weather API
    participant Soil as USDA Soil API
    participant Search as Serper/Amazon Search

    User->>UI: Enter ZIP code + infestation level
    UI->>Agent: create_agentic_session(pest, severity, plant, zipcode)
    Note over Agent: Session initialized with<br/>tools: [get_weather, get_soil_type,<br/>search_amazon_products]

    UI->>Agent: generate_treatment_recommendations(context)
    Note over Agent: STEP 1: Treatment text (no products)

    Agent->>Weather: get_weather(zipcode)
    Weather-->>Agent: {temperature, forecast_3day, wind}

    Agent->>Soil: get_soil_type(zipcode)
    Soil-->>Agent: {soil_name, texture, pH, drainage}

    Note over Agent: Gemini synthesizes weather + soil<br/>→ writes treatment paragraphs
    Agent-->>UI: treatment_text

    Note over Agent: STEP 2: Product search
    Agent->>Search: search_amazon_products("organic neem oil")
    Search-->>Agent: [{name, url}, ...]

    Agent->>Search: search_amazon_products("Bt spray caterpillars")
    Search-->>Agent: [{name, url}, ...]

    Agent-->>UI: products_text

    UI-->>User: Treatment Plan + Product Links

    User->>UI: Click "Soil Impact" tab
    UI->>Agent: answer_menu_option(context, option=2)
    Note over Agent: Re-uses existing chat session<br/>(conversation history preserved)
    Agent-->>UI: Soil analysis paragraph
    UI-->>User: Soil impact analysis
```

## Agentic Autonomy

The agent decides **which tools to call and in what order** based solely on the prompt. There is no hard-coded orchestration — Gemini reads the context and determines:
1. Weather data is needed → calls `get_weather()`
2. Soil data is needed → calls `get_soil_type()`
3. Products are requested → calls `search_amazon_products()` 2–3 times with specific queries

This is the core demonstration of **Section 9.2**: the LLM acts as the orchestrator, not as a simple function router.
