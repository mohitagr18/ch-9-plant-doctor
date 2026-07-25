# Workflow 4: CI/CD and Cloud Run Deployment Pipeline

> **Chapter 9.4** — Deploying multimodal agents to Google Cloud Run

This diagram shows the full deployment pipeline from a code push on `main` to a live Cloud Run service, as implemented in `.github/workflows/deploy.yml`.

```mermaid
flowchart TD
    A(["👨‍💻 Developer\ngit push main"]) --> B["GitHub Actions Trigger\non: push to main"]

    subgraph GHA["🔄 GitHub Actions — CI/CD Pipeline"]
        B --> C["actions/checkout@v4\nCheckout code"]
        C --> D["google-github-actions/auth@v2\nAuthenticate with GCP SA Key"]
        D --> E["setup-gcloud@v2\nConfigure Cloud SDK"]
        E --> F["Configure Docker\nfor Artifact Registry"]
        F --> G["docker build\nMulti-platform AMD64 image"]
        G --> H["docker push\nTag: :sha + :latest"]
    end

    subgraph GCP["☁️ Google Cloud Platform"]
        H --> I["Google Artifact Registry\nContainer image stored"]
        I --> J["gcloud run deploy\nagri-assistant service"]
        J --> K["Secret Manager\nGOOGLE_API_KEY + SERPER_API_KEY\ninjected at runtime"]
        K --> L["Cloud Run Service\n• Memory: 2Gi\n• CPU: 2\n• Timeout: 300s\n• Max instances: 10\n• Min instances: 0"]
    end

    L --> M(["🌐 Public URL\nhttps://agri-assistant-*.run.app"])

    subgraph Secrets["🔐 GitHub Secrets Required"]
        S1["GCP_PROJECT_ID"]
        S2["GCP_REGION"]
        S3["GCP_SA_KEY (JSON)"]
    end

    Secrets -.-> D

    style A fill:#4CAF50,color:#fff
    style GHA fill:#E3F2FD
    style GCP fill:#E8F5E9
    style Secrets fill:#FFF3E0
    style M fill:#4CAF50,color:#fff
```

## Stateless Deployment Considerations (Section 9.4)

Cloud Run runs the container as **stateless serverless**. Key design choices to handle this:

| Challenge | Solution in Plant Doctor |
|-----------|-------------------------|
| Session state lost between requests | Streamlit `session_state` held in-process per user session |
| Secrets not in env | Google Secret Manager injected at deploy time |
| Image size & cold start | `python:3.11-slim` base + layer caching via `pyproject.toml` and `uv.lock` copy |
| Multi-platform compatibility | `--platform linux/amd64` explicit build flag for Apple Silicon devs |
| Scale to zero | `--min-instances 0` keeps costs at $0 when idle |
