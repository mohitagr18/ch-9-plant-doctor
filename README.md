# 🌱 Agricultural Assistant

> **Book Chapter 9 — *Case study: context-aware actuation with the Plant Doctor architecture***
> 
> *Part of "The Write Path" by Mohit Aggarwal*

AI-powered pest & disease detection with personalized treatment & product recommendations.

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-FF4B4B.svg)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-blue.svg)](https://gemini.google/us/about/?hl=en)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com)
[![Cloud Run](https://img.shields.io/badge/Cloud%20Run-Deployed-4285F4.svg)](https://cloud.google.com/run)

**Live Demo:** [https://agri-assistant-g57ai3hf4a-uc.a.run.app/](https://agri-assistant-g57ai3hf4a-uc.a.run.app/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Chapter 9 Topics](#chapter-9-topics)
- [Features](#features)
- [Workflow Diagrams](#workflow-diagrams)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Docker Setup](#docker-setup)
- [Deployment](#deployment)
- [API Keys & Environment Variables](#api-keys--environment-variables)
- [License](#license)

---

## 🎯 Overview

Agricultural Assistant is an intelligent web application that helps gardeners identify plant pests and diseases through image recognition, then provides personalized treatment recommendations based on local weather conditions, soil types, and severity levels.

The application uses **agentic AI architecture** powered by Google Gemini 2.5 Flash, where the AI autonomously decides when to call tools for weather data, soil information, and product recommendations to generate comprehensive treatment plans. The system also implements **Model Context Protocol (MCP)** standards, allowing the agricultural tools to be exposed to external AI clients like Claude Desktop for broader ecosystem integration.

---

## 📖 Chapter 9 Topics

This project covers the following sections from Chapter 9:

| Section | Topic |
|---------|-------|
| 9.1 | Separating diagnosis from downstream action |
| 9.2 | Integrating specialist tools and external APIs |
| 9.3 | Graceful degradation under incomplete context |
| 9.4 | Deploying multimodal agents to Google Cloud Run |
| 9.5 | Applying the pattern to regulated industries |

---

## ✨ Features

- **🔍 AI-Powered Detection** — Gemini Vision for instant pest/disease identification with severity scoring
- **🌐 Agentic AI Architecture** — Gemini 2.5 Flash autonomously calls tools based on context
- **🔌 MCP Integration** — Tools exposed via Model Context Protocol for Claude Desktop and other clients
- **💊 Personalized Treatment Plans** — Weather- and soil-optimized recommendations with Amazon product links
- **📊 Interactive Menu System** — Soil Impact, Weather Timing, Monitoring, Full Report, Custom Q&A

---

## 🗺️ Workflow Diagrams

Detailed Mermaid workflow diagrams are in the [`workflow/`](workflow/) directory:

| Diagram | Description |
|---------|-------------|
| [`01_agentic_detection_flow.md`](workflow/01_agentic_detection_flow.md) | End-to-end agentic detection and treatment flow |
| [`02_mcp_architecture.md`](workflow/02_mcp_architecture.md) | MCP server architecture and tool exposure |
| [`03_tool_calling_sequence.md`](workflow/03_tool_calling_sequence.md) | Gemini tool-calling sequence diagram |
| [`04_cloud_deployment.md`](workflow/04_cloud_deployment.md) | CI/CD and Cloud Run deployment pipeline |
| [`05_graceful_degradation.md`](workflow/05_graceful_degradation.md) | Graceful degradation under incomplete context |

---

## 🏗️ Architecture

### Agentic AI Workflow

```
User Upload → Gemini Vision (Detection) → Gemini 2.5 Flash Agent (Context Gathering)
                                              ↓
                                         Tool Calls:
                                         - get_weather()
                                         - get_soil_type()
                                         - search_amazon_products()
                                              ↓
                                    Personalized Recommendations
```

### MCP Architecture (Optional)

```
External AI Clients (Claude Desktop, etc.)
              ↓
         MCP Protocol
              ↓
     MCP Server (agri_tools.py)
              ↓
     Tool Implementations
     - Weather API
     - Soil Database
     - Product Search
```

### Technology Stack

**Frontend:** Streamlit, Custom CSS for mobile responsiveness

**Backend:** Google Gemini 2.5 Flash, Python 3.11, PIL, FastMCP

**Data Sources:** NOAA Weather Service API, USDA Web Soil Survey, Serper Google Search API

**Infrastructure:** Docker, Google Cloud Run, Google Artifact Registry, Google Secret Manager, GitHub Actions

---

## 🗂️ Project Structure

```
ch-9-plant-doctor/
│
├── app.py                          # Main Streamlit application
│
├── src/                            # Core application modules
│   ├── plant_pest_detector.py      # Gemini Vision for pest detection
│   ├── qa_engine_agentic.py        # Agentic AI with tool calling
│   ├── location_service.py         # Weather & soil data integration
│   └── __init__.py
│
├── mcp_server/                     # MCP tool definitions
│   └── agri_tools.py               # MCP-decorated tools for external clients
│
├── workflow/                       # Mermaid workflow diagrams (Chapter 9)
│   ├── 01_agentic_detection_flow.md
│   ├── 02_mcp_architecture.md
│   ├── 03_tool_calling_sequence.md
│   ├── 04_cloud_deployment.md
│   └── 05_graceful_degradation.md
│
├── samples/                        # Sample images for testing
├── .github/workflows/deploy.yml   # GitHub Actions CI/CD
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/mohitagr18/ch-9-plant-doctor.git
cd ch-9-plant-doctor
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Run locally**
```bash
streamlit run app.py
```

---

## 🐳 Docker Setup

```bash
docker build -t agri-assistant:local .
docker run -p 8080:8080 --env-file .env agri-assistant:local
```

---

## ☁️ Deployment

See [`workflow/04_cloud_deployment.md`](workflow/04_cloud_deployment.md) for the full CI/CD pipeline diagram.

```bash
gcloud run deploy agri-assistant \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/agri-assistant/agri-assistant:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets=GOOGLE_API_KEY=GOOGLE_API_KEY:latest,SERPER_API_KEY=SERPER_API_KEY:latest \
  --memory 2Gi --cpu 2 --timeout 300
```

---

## 🔧 API Keys & Environment Variables

```
GOOGLE_API_KEY=your_google_gemini_api_key
SERPER_API_KEY=your_serper_api_key
```

- **Google Gemini API:** [Google AI Studio](https://makersuite.google.com/app/apikey) (Free: 60 req/min)
- **Serper API:** [Serper.dev](https://serper.dev/) (Free: 2,500 searches/month)

---

## 📝 License

MIT License — see `LICENSE` file for details.

---

**Built with ❤️ using Google Gemini 2.5 Flash · Chapter 9 of *The Write Path***
