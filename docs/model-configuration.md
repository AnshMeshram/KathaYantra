# KathaYantra — Local Model Configuration & Ollama Setup Guide
### *Configuring Open-Weight Gemma 2 on Local Hardware*

---

## 1. Local AI Philosophy

KathaYantra is committed to **open-weight, sovereign, local-first artificial intelligence**.

- **No Remote Vector APIs:** All indexing is local.
- **No Cloud LLM Tokens:** Inference runs on your own hardware via Ollama.
- **Privacy Assurance:** Sensitive folklore research inquiries and notes never leave your personal computer.

---

## 2. Default Configuration

Runtime settings are controlled via `.env` and loaded through `app/core/config.py`:

```ini
# Local AI Engine (Ollama + Gemma 2)
OLLAMA_BASE_URL="http://127.0.0.1:11434"
OLLAMA_MODEL="gemma2"
OLLAMA_CONNECT_TIMEOUT=5.0
OLLAMA_READ_TIMEOUT=120.0
OLLAMA_MAX_RETRIES=2

# Retrieval and Context Constraints
AI_MAX_INPUT_CHARS=1000
AI_MAX_OUTPUT_TOKENS=1024
AI_MAX_CONTEXT_RECORDS=5
AI_MAX_CONTEXT_CHARS=6000
AI_TEMPERATURE=0.2
AI_FICTION_TEMPERATURE=0.7
AI_ENABLE_STORY_GENERATION=true
AI_ENABLE_CHAT_HISTORY=false
AI_RETRIEVAL_MIN_SCORE=0.5
```

---

## 3. Installing & Running Ollama

### Step 1: Install Ollama
Download and install Ollama from [https://ollama.ai/download](https://ollama.ai/download).

### Step 2: Download Gemma 2
Pull Google's open-weight Gemma 2 model:
```bash
ollama pull gemma2
```
*Note: Both `gemma2` and `gemma2:latest` are automatically detected and matched by KathaYantra.*

### Step 3: Start the Ollama Server
If not running as a system service, start Ollama:
```bash
ollama serve
```

### Step 4: Verify Local Model Readiness
Execute KathaYantra's diagnostic script:
```bash
python scripts/check_ollama.py
```

Expected Output:
```
======================================================================
  KATHAYANTRA — LOCAL OLLAMA SERVICE DIAGNOSTICS
======================================================================
Status:            AVAILABLE
Provider:          ollama
Endpoint:          http://127.0.0.1:11434
Configured Model:  gemma2
Model Ready:       YES
Installed Models:  gemma2:latest
----------------------------------------------------------------------
Message: Ollama is running locally and model 'gemma2' is installed and ready.
======================================================================
```

---

## 4. Hardware Optimization & VRAM Offloading

When running Gemma 2 (9.2B parameters) on consumer hardware:
- **Dedicated GPU (4GB–8GB VRAM):** Ollama automatically offloads layers to CUDA / Vulkan while keeping the remaining layers in CPU RAM.
- **CPU RAM:** Ensure at least 8GB of free system memory is available.
- **Read Timeout:** Set `OLLAMA_READ_TIMEOUT=120.0` to permit sufficient time for initial layer allocation and generation on CPU/hybrid memory architectures.

---

## 5. Offline Fallback Behavior

If Ollama is stopped or unavailable, KathaYantra continues to operate gracefully:
- **Dataset Browsing & Search:** SQLite FTS5 search continues working with 100% functionality.
- **Archival Inquiries:** `POST /api/v1/ai/ask` returns `AIAnswerType.MODEL_UNAVAILABLE`, accompanied by the deterministic list of matching story records and authentic bibliographic citations.
- **Backend Health:** `GET /api/v1/health` remains `status: ok` and honestly reports `ollama_available: false`.

