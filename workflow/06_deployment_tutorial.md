# Workflow 6: Step-by-Step Deployment Tutorial

> **Chapter 9.4 Supplement** — Deploying Plant Doctor from Scratch
> 
> *Part of "The Write Path" by Mohit Aggarwal*

This guide provides a comprehensive, step-by-step walkthrough to deploy the Plant Doctor application to a brand-new Google Cloud Project. If you are following along in the book and want to deploy the app manually from your terminal, this is the exact sequence of commands to use.

---

## Prerequisites

- **Google Cloud SDK (`gcloud`)** installed and authenticated.
- **Billing enabled** on your Google Cloud project.
- **Two API Keys**:
  - **Google Gemini API Key**: *(Important: To avoid "ResourceExhausted" billing errors, generate this key by importing your Google Cloud Project into [Google AI Studio](https://aistudio.google.com/apikey) rather than creating it directly in the GCP console).*
  - **Serper.dev API Key**

---

## Step 1: Set Your Project

First, ensure `gcloud` is pointing to your newly created project. 

```bash
# Replace <YOUR_PROJECT_ID> with your actual Google Cloud Project ID
gcloud config set project <YOUR_PROJECT_ID>
```

---

## Step 2: Enable Required APIs

A fresh Google Cloud project has most APIs disabled. You need to enable the services for Cloud Run, Artifact Registry, Secret Manager, Cloud Build, and Generative Language (for Gemini).

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  apikeys.googleapis.com \
  generativelanguage.googleapis.com
```

*Note: This step might take a minute to complete.*

---

## Step 3: Create an Artifact Registry Repository

We need a secure place to store our Docker container images before deploying them to Cloud Run.

```bash
gcloud artifacts repositories create agri-assistant \
  --repository-format=docker \
  --location=us-central1 \
  --description="Plant Doctor container images"
```

---

## Step 4: Securely Store API Keys in Secret Manager

Cloud Run applications should never hardcode API keys. We use Google Secret Manager to inject these keys safely at runtime. 

*Run these commands and paste your actual API keys when prompted (or pipe them directly if you prefer).*

```bash
# Create GOOGLE_API_KEY secret
printf "YOUR_GEMINI_API_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=-

# Create SERPER_API_KEY secret
printf "YOUR_SERPER_API_KEY" | gcloud secrets create SERPER_API_KEY --data-file=-
```

---

## Step 5: Grant IAM Permissions

Cloud Build and Cloud Run use the **Compute Engine default service account** to perform actions. In newer GCP projects, this account does not have default permissions, so we must explicitly grant it access to read storage and secrets, and write logs/artifacts.

1. **Find your Project Number:**
   ```bash
   gcloud projects describe <YOUR_PROJECT_ID> --format='value(projectNumber)'
   ```

2. **Grant the required roles:** (Replace `<PROJECT_NUMBER>` below)
   ```bash
   # Allow Cloud Build to read source code from Cloud Storage
   gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
     --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
     --role="roles/storage.admin"

   # Allow pushing the Docker image to Artifact Registry
   gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
     --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
     --role="roles/artifactregistry.writer"

   # Allow Cloud Build to write build logs
   gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
     --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
     --role="roles/logging.logWriter"

   # Allow Cloud Run to access your API keys in Secret Manager
   gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
     --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

---

## Step 6: Build the Docker Image

Using **Cloud Build** ensures your container is built in the cloud. This avoids frustrating "exec format errors" that happen when trying to deploy a container built on an Apple Silicon (M1/M2/M3) Mac to an AMD64 server.

```bash
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/<YOUR_PROJECT_ID>/agri-assistant/agri-assistant:latest
```

---

## Step 7: Deploy to Cloud Run

Finally, deploy the image to Cloud Run. This command maps the secrets we created earlier directly into the container as environment variables.

```bash
gcloud run deploy agri-assistant \
  --image us-central1-docker.pkg.dev/<YOUR_PROJECT_ID>/agri-assistant/agri-assistant:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets=GOOGLE_API_KEY=GOOGLE_API_KEY:latest,SERPER_API_KEY=SERPER_API_KEY:latest \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0
```

---

## Step 8: Verification

Once the deployment finishes, the terminal will print a public `Service URL` (e.g., `https://agri-assistant-...run.app`).

You can verify the deployment health endpoint via `curl`:
```bash
curl -sI https://<YOUR_CLOUD_RUN_URL>/_stcore/health
```

If it returns `HTTP/2 200 OK`, your application is successfully live on the internet and ready to diagnose plants!
