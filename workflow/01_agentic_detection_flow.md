# Workflow 1: Agentic Detection & Treatment Flow

> **Chapter 9.1 & 9.2** — Separating diagnosis from downstream action / Integrating specialist tools and external APIs

This diagram illustrates the end-to-end 3-stage agentic pipeline: from image upload through Gemini Vision detection to tool-calling for personalized treatment recommendations.

```mermaid
flowchart TD
    A(["👤 User"]) --> B["📸 Upload Plant Image"]
    B --> C{"Image Available?"}
    C -- Yes --> D["🔍 Gemini Vision\nPlantPestDetector.identify()"]
    C -- "Use Sample" --> E["🌿 Load Sample Image"]
    E --> D

    D --> F["📋 Detection Results\n• Pest/Disease\n• Severity\n• Plant Type\n• Subject Type"]
    F --> G["⚡ generate_brief_assessment()\nGemini 2.5 Flash (no tools)"]
    G --> H["⚠️ Risk Summary\nDisplayed to User"]

    H --> I["📝 User Enters Details\n• ZIP Code\n• Plant Type\n• Infestation Level"]
    I --> J["🤖 create_agentic_session()\nGemini 2.5 Flash + Tools"]

    J --> K["🔧 TOOL CALL: get_weather(zipcode)\nNOAA Weather Service API"]
    J --> L["🔧 TOOL CALL: get_soil_type(zipcode)\nUSDA Soil Data Access"]
    K --> M["🌤️ Weather Data\n• Temperature, Wind\n• 3-Day Forecast"]
    L --> N["🪨 Soil Data\n• Texture, pH\n• Drainage Class"]

    M --> O["📝 generate_treatment_recommendations()\nGemini synthesizes context"]
    N --> O

    O --> P["🔧 TOOL CALL: search_amazon_products()\nSerper Google Search API"]
    P --> Q["🛒 Product Links\nOrganic/Natural treatments"]

    O --> R["💊 Treatment Plan\n+ Product Recommendations"]
    Q --> R

    R --> S(["📊 Interactive Menu\nSoil · Weather · Monitor · Report · Q&A"])

    style A fill:#4CAF50,color:#fff
    style D fill:#2196F3,color:#fff
    style J fill:#9C27B0,color:#fff
    style K fill:#FF9800,color:#fff
    style L fill:#FF9800,color:#fff
    style P fill:#FF9800,color:#fff
    style R fill:#4CAF50,color:#fff
    style S fill:#607D8B,color:#fff
```

## Key Design Principles (Section 9.1)

- **Separation of concerns**: Detection (Gemini Vision) is decoupled from downstream tool-calling (Gemini Agent)
- **Deterministic first step**: Vision identification runs without tools — it cannot call external APIs
- **Tool calls on demand**: The agent autonomously decides when to call `get_weather`, `get_soil_type`, and `search_amazon_products`
- **State machine stages**: `upload → details → recommendations` prevents partial-state errors
