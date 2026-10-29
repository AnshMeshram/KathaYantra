# KathaYantra Deployment and Operations Guide

> **Central Principle:**  
> _Preserve the story. Trace the source. Respect the culture. Keep the AI honest._

KathaYantra is designed as a **local-first, privacy-respecting backend service**. This guide documents setup and deployment for local development, home lab servers, and reverse-proxied production environments.

---

## 1. Local Development Setup (Windows PowerShell)

### Prerequisites
- Python 3.11, 3.12, or 3.13
- Git 2.20+
- Ollama (optional for browsing, required for local AI inference)

### Step 1: Clone Repository
```powershell
git clone https://github.com/AnshMeshram/KathaYantra.git
cd KathaYantra
```

### Step 2: Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Environment Configuration
```powershell
Copy-Item .env.example .env
```
Default configuration parameters in `.env`:
```ini
PROJECT_NAME="KathaYantra"
HOST="127.0.0.1"
PORT=8000
DEBUG=false
LOG_LEVEL="info"
CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"

# Local AI Configuration
OLLAMA_BASE_URL="http://127.0.0.1:11434"
OLLAMA_MODEL="gemma2"
OLLAMA_CONNECT_TIMEOUT=5.0
OLLAMA_READ_TIMEOUT=120.0
AI_MAX_INPUT_CHARS=1000
AI_MAX_OUTPUT_TOKENS=1024
AI_MAX_CONTEXT_RECORDS=5
```

### Step 5: Verify Retrieval Index & Seed Files
```powershell
python scripts/validate_json_datasets.py
python scripts/audit_retrieval_index.py
```

### Step 6: Launch Backend Server
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## 2. Local Ollama & Gemma 2 Setup

### Step 1: Install Ollama
Download and install Ollama from [https://ollama.ai/download](https://ollama.ai/download).

### Step 2: Pull the Gemma 2 Model
```powershell
ollama pull gemma2
```
*(Uses Google's open-weight Gemma 2 9.2B parameter model).*

### Step 3: Verify Model Diagnostics
```powershell
python scripts/check_ollama.py
```
Expected output:
```
[SUCCESS] Local Ollama daemon is reachable!
Configured Model: gemma2 (Available: YES)
Installed Models: ['gemma2:latest']
Response Time:    12.4 ms
```

---

## 3. Production Deployment with Reverse Proxy

When exposing KathaYantra to internal networks or a web frontend:

### Recommended Architecture
```
Client / Browser
      │
      ▼ (HTTPS: 443)
┌─────────────────────────┐
│ Reverse Proxy           │ (Nginx / Caddy / Traefik)
│ - TLS Termination       │
│ - Security Headers      │
│ - Request Rate Limiting │
└────────────┬────────────┘
             │ (HTTP: 8000)
             ▼
┌─────────────────────────┐
│ KathaYantra (FastAPI)   │
│ - In-Memory Repository  │
│ - SQLite FTS5 Index     │
└────────────┬────────────┘
             │ (HTTP: 11434)
             ▼
┌─────────────────────────┐
│ Local Ollama Daemon     │
│ - Gemma 2 (9.2B)        │
└─────────────────────────┘
```

### Nginx Reverse Proxy Configuration Example
```nginx
server {
    listen 443 ssl http2;
    server_name archive.kathayantra.local;

    ssl_certificate /etc/ssl/certs/kathayantra.crt;
    ssl_certificate_key /etc/ssl/private/kathayantra.key;

    # Timeouts for local LLM inference
    proxy_connect_timeout 10s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;

    # Security Buffers
    client_max_body_size 2M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Process Management via Systemd (Linux)
Create `/etc/systemd/system/kathayantra.service`:
```ini
[Unit]
Description=KathaYantra World Folklore Archive Backend
After=network.target ollama.service

[Service]
Type=simple
User=kathayantra
WorkingDirectory=/opt/KathaYantra
ExecStart=/opt/KathaYantra/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5
EnvironmentFile=/opt/KathaYantra/.env

[Install]
WantedBy=multi-user.target
```
