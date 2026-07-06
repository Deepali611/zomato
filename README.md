# Zomato AI Restaurant Recommendations (Monorepo)

An AI-powered restaurant discovery and recommendation engine. This repository is organized as a decoupled monorepo:
* **Frontend**: Next.js (TypeScript/React) located at the root level `/`.
* **Backend**: Python 3.10 HTTP API Server located inside `/backend`.

---

## 🎨 Frontend Setup (Next.js)

The frontend is hosted at the root level.

### Installation
```bash
npm install
```

### Run Locally
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.

### Configuration
Set the following environment variable in a `.env.local` file or in your hosting provider (e.g. Vercel):
* `NEXT_PUBLIC_API_URL`: The URL of the backend API (defaults to `http://localhost:8000`).

---

## ⚙️ Backend Setup (Python API)

The backend is located in `/backend`.

### Installation
```bash
cd backend
.python-embed/python.exe -m pip install -r requirements.txt
```

### Configuration
Create a `backend/.env` file with the following variables:
```env
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
```

### Run API Server Locally
```bash
.python-embed/python.exe backend/src/presentation/api.py
```
The API server will listen on `http://localhost:8000`.

### Run Tests
```bash
.python-embed/python.exe backend/scripts/run_tests.py
```
