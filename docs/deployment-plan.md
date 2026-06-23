# Streamlit Deployment Plan: Zomato AI Restaurant Recommendations

This document outlines the step-by-step deployment plan to host the **Zomato AI Restaurant Recommendations** web application on Streamlit.

---

## 📋 Deployment Metadata

| Component | Detail |
| :--- | :--- |
| **Target Platform** | Streamlit Community Cloud (Recommended) or Docker-based hosting (Render, HF Spaces, GCP/AWS) |
| **Main App File** | `src/presentation/streamlit_app.py` |
| **Primary Dependency File** | `requirements.txt` |
| **Data Dependencies** | `data/restaurant.parquet` (preprocessed in repository) or dynamically from Hugging Face |
| **LLM Provider** | Groq API (`llama-3.3-70b-versatile`) |

---

## 🚀 Deployment Strategy 1: Streamlit Community Cloud (Recommended)

Streamlit Community Cloud is the easiest and most performant way to host this application. It connects directly to your GitHub repository, builds the environment using `requirements.txt`, and serves the app with automated SSL and scaling.

### Step 1: Push Codebase to GitHub
Ensure the codebase is committed to a public or private GitHub repository.

> [!IMPORTANT]
> Do **NOT** commit your `.env` file containing the `GROQ_API_KEY` to GitHub. It is ignored by default in [.gitignore](file:///c:/Users/patil/Downloads/zomato/zomato/.gitignore).

Verify that the preprocessed dataset is included in your commit:
* **File to include:** `data/restaurant.parquet`
* Checking this file in ensures fast startup times (under 2 seconds) and avoids potential rate limits or download timeouts from Hugging Face during serverless cold starts.

### Step 2: Sign in to Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Sign in using your GitHub account.

### Step 3: Deploy the App
1. Once logged in, click the **"New app"** button in the top-right corner of the workspace.
2. Fill in the deployment details:
   * **Repository:** Select your `zomato` repository.
   * **Branch:** Select your main branch (e.g., `main` or `master`).
   * **Main file path:** Set this to `src/presentation/streamlit_app.py` (ensure you use forward slashes).
   * **App URL:** (Optional) Custom subdomain name if available.

### Step 4: Configure Environment Variables & Secrets
Streamlit Community Cloud does not use `.env` files. Instead, it provides a secure **Secrets** management interface that injects values directly into environment variables.

1. Click on **"Advanced settings..."** before deploying (or go to **Settings > Secrets** in the app dashboard after deploying).
2. Paste the following configuration in the text area (TOML format):

```toml
# Groq LLM API Key (Required)
GROQ_API_KEY = "your_actual_groq_api_key_here"

# Model and Engine Configurations (Optional overrides)
LLM_PROVIDER = "groq"
LLM_MODEL = "llama-3.3-70b-versatile"
MAX_CANDIDATES = 20
TOP_K = 5
FILTER_RELAX_ON_EMPTY = true
LLM_TIMEOUT_SECONDS = 30
LLM_MAX_RETRIES = 1
LOG_LEVEL = "INFO"
```

3. Click **"Save"**.

> [!TIP]
> The application uses `os.getenv()` in [src/config.py](file:///c:/Users/patil/Downloads/zomato/zomato/src/config.py) to read settings. Streamlit automatically exposes any key-value pairs defined in the TOML Secrets manager as system environment variables, making this integration seamless.

### Step 5: Launch!
Click the **"Deploy!"** button. Streamlit will:
1. Spin up a container.
2. Install Python dependencies from [requirements.txt](file:///c:/Users/patil/Downloads/zomato/zomato/requirements.txt).
3. Load the pre-processed `data/restaurant.parquet` dataset.
4. Launch the application server.

---

## 🐳 Deployment Strategy 2: Containerized Deployment (Docker)

If you prefer self-hosting (e.g., on Render, AWS EC2, GCP Cloud Run, or Hugging Face Spaces), you can containerize the app using Docker.

### 1. Create a `Dockerfile`
Create a `Dockerfile` in the root of the project:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8501

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Run the application
CMD streamlit run src/presentation/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

### 2. Build and Run Locally
```bash
# Build the Docker image
docker build -t zomato-recommendations .

# Run the container (passing environment secrets)
docker run -p 8501:8501 --env-file .env zomato-recommendations
```

---

## 🛠️ Post-Deployment Verification

After the app finishes building and shows the UI, run these smoke checks to verify functionality:

1. **Verify Home Page Load:** Check if the sidebar loaded correctly with "Concierge Search", the background animations are active, and the 3 mock restaurant cards are loaded on first paint.
2. **Test Search Request:**
   * Select a location (e.g., `Indiranagar`).
   * Choose a budget category.
   * Input a cuisine (e.g., `Italian`).
   * Enter a custom constraint (e.g., `rooftop garden`).
   * Click **"Generate"**.
3. **Verify AI Rank & Explanations:**
   * Ensure that the top header section shows "AI Insights for your Evening".
   * Check if recommendation cards display custom "Why this fits: ..." explanations powered by Groq.

---

## ⚠️ Troubleshooting & Common Pitfalls

### 1. "ModuleNotFoundError: No module named 'src'"
* **Reason:** Python package resolution path issue.
* **Fix:** The code in [src/presentation/streamlit_app.py](file:///c:/Users/patil/Downloads/zomato/zomato/src/presentation/streamlit_app.py) contains a sys-path insertion script at the very top:
  ```python
  ROOT = Path(__file__).resolve().parent.parent.parent
  if str(ROOT) not in sys.path:
      sys.path.insert(0, str(ROOT))
  ```
  Ensure this block remains unmodified and is executed before importing any internal `src.*` modules.

### 2. Streamlit Secrets and TOML Encoding
* **Reason:** Pasting keys with leading/trailing spaces or invalid TOML syntax.
* **Fix:** Do not wrap your API keys in double quotes twice. If formatting as TOML, use `GROQ_API_KEY = "gsk_..."`.

### 3. File System Path Resolution
* **Reason:** In serverless containers, relative paths can sometimes fail if the working directory changes.
* **Fix:** The dataset path in [src/config.py](file:///c:/Users/patil/Downloads/zomato/zomato/src/config.py) resolves dynamically relative to the code location:
  ```python
  root = Path(__file__).resolve().parents[1]
  parquet_path = root / "data" / "restaurant.parquet"
  ```
  This guarantees standard pathing inside the Docker container or Streamlit runtime.

### 4. "Groq API Key Not Set / Fallback Mode"
* **Reason:** Env secret did not save properly or is empty.
* **Fix:** If the `GROQ_API_KEY` environment variable is missing, the app will degrade gracefully, displaying a warning banner and rendering recommendations sorted deterministically by rating. Check the Streamlit logs for: `GROQ_API_KEY is not set. Recommendations will use rating-based fallback.`
