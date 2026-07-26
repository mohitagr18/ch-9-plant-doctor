# Workflow 1: Agentic Detection & Treatment Flow

> **Chapter 9.1 & 9.2** — Separating diagnosis from downstream action / Integrating specialist tools and external APIs

This diagram illustrates the end-to-end 3-stage agentic pipeline: from image upload through Gemini Vision detection to tool-calling for personalized treatment recommendations.

```mermaid
flowchart LR
    subgraph DET["1. Detection & Assessment"]
        direction TB
        A["📸 Upload Image<br/>or Select Sample"]
        B{"Image Available?"}
        C["🌿 Load Sample Image"]
        D["🔍 Detect Plant, Pest<br/>& Severity"]
        E["📋 Detection Results<br/>Pest · Severity · Plant Type"]
        F["⚡ Brief Assessment"]
        G["⚠️ Risk Summary"]
        H["📝 Enter ZIP Code"]

        A --> B
        B -- Yes --> D
        B -- Use Sample --> C --> D
        D --> E --> F --> G --> H
    end

    subgraph TRT["2. Location-Aware Treatment"]
        direction TB
        I["🌦️ Retrieve Weather Data<br/>Temperature · Wind · Forecast"]
        J["🪨 Retrieve Soil Data<br/>Texture · pH · Drainage"]
        K["🤖 Combine Detection,<br/>ZIP, Weather & Soil"]
        L["💊 Generate Treatment Plan"]
        M["🛒 Find Suitable Products"]
        N["📦 Treatment Plan<br/>+ Product Options"]
        O["📊 Interactive Menu<br/>Soil · Weather · Monitor · Q&A"]

        I --> K
        J --> K
        K --> L --> M --> N --> O
    end

    DET -->|"Detection results + ZIP code"| TRT

    classDef input fill:#4CAF50,color:#fff,stroke:#388E3C
    classDef detect fill:#2196F3,color:#fff,stroke:#1976D2
    classDef context fill:#FF9800,color:#fff,stroke:#F57C00
    classDef agent fill:#9C27B0,color:#fff,stroke:#7B1FA2
    classDef output fill:#607D8B,color:#fff,stroke:#455A64

    class A,C,H input
    class B,D,E,F,G detect
    class I,J context
    class K,L,M agent
    class N,O output
```

## Key Design Principles (Section 9.1)

- **Separation of concerns**: Detection (Gemini Vision) is decoupled from downstream tool-calling (Gemini Agent)
- **Deterministic first step**: Vision identification runs without tools — it cannot call external APIs
- **Tool calls on demand**: The agent autonomously decides when to call `get_weather`, `get_soil_type`, and `search_amazon_products`
- **State machine stages**: `upload → details → recommendations` prevents partial-state errors
