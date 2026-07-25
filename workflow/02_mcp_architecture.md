# Workflow 2: MCP Server Architecture

> **Chapter 9.2** — Integrating specialist tools and external APIs via Model Context Protocol

This diagram shows how the agricultural tools are exposed via the Model Context Protocol (MCP), enabling both the internal Gemini agent and external clients (Claude Desktop, etc.) to discover and invoke the same tools.

```mermaid
flowchart LR
    subgraph Clients["🖥️ Clients"]
        A1["🌱 Plant Doctor\nStreamlit App"]
        A2["🤖 Claude Desktop"]
        A3["🔗 Any MCP Client"]
    end

    subgraph Protocol["📡 Interface Layer"]
        B1["Gemini Native\nFunction Calling"]
        B2["MCP Protocol\nFastMCP Server"]
    end

    subgraph MCPServer["⚙️ MCP Server — agri_tools.py"]
        C1["@mcp.tool()\nget_weather()"]
        C2["@mcp.tool()\nget_soil_type()"]
        C3["@mcp.tool()\nsearch_amazon_products()"]
        C4["@mcp.tool()\nget_location_context()"]
    end

    subgraph DataSources["🌐 External APIs"]
        D1["NOAA Weather Service\napi.weather.gov"]
        D2["USDA Soil Data Access\nsdmdataaccess.nrcs.usda.gov"]
        D3["Serper Search API\ngoogle.serper.dev"]
        D4["Amazon Product Listings"]
    end

    A1 --> B1
    A2 --> B2
    A3 --> B2
    B1 --> C1
    B1 --> C2
    B1 --> C3
    B2 --> C1
    B2 --> C2
    B2 --> C3
    B2 --> C4
    C1 --> D1
    C2 --> D2
    C3 --> D3
    C3 --> D4
    C4 --> D1
    C4 --> D2

    style Clients fill:#E3F2FD
    style Protocol fill:#F3E5F5
    style MCPServer fill:#E8F5E9
    style DataSources fill:#FFF3E0
```

## Dual Interface Pattern

The same tool implementations serve two interfaces:

| Interface | Used By | Discovery | Schema |
|-----------|---------|-----------|--------|
| Gemini Native Function Calling | Plant Doctor app internally | Python function signatures | Auto-inferred |
| MCP Protocol (FastMCP) | Claude Desktop, external agents | `@mcp.tool()` decorators | JSON Schema |

This demonstrates **Section 9.2's** principle: specialist tools should be written once and exposed through standardized boundaries so any compliant agent can consume them.
