# LLM Black-Box Testing Tool

## Overview

This project provides a lightweight tool to generate **black-box test artifacts** from:
- **requirements** (natural language), or
- **codebase/module context** (API docs/snippets/validation rules),

using an LLM with **technique selection**:
- EP/BVA (`ep_bva`)
- Decision Table Testing (`decision_table`)
- State Transition Testing (`state_transition`)
- Combinatorial (pairwise-focused) (`combinatorial`)

It includes a web UI, an API, and strict JSON output validation.

## Run

### 1) Create and activate a conda environment

```
conda create -n llmtest python=3.11
conda activate llmtest
```

### 2) Install dependencies

```
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a .env file in the project root:

```
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.ohmygpt.com/v1
```

### 4) Start the server

```
uvicorn app.main:app --reload
```

### 5) Open the UI

```
http://127.0.0.1:8000
```

## API

### POST `/api/generate`

Request JSON (requirements input):

```json
{
  "input_type": "requirements",
  "technique": "ep_bva",
  "requirements": "System overview ...",
  "prompt_version": "v4",
  "model": "gpt-4o-mini",
  "temperature": 0.2
}
```

Request JSON (codebase input):

```json
{
  "input_type": "codebase",
  "technique": "decision_table",
  "code_context": "Paste API docs / code snippets here...",
  "prompt_version": "v4",
  "model": "gpt-4o-mini",
  "temperature": 0.2
}
```

Response JSON: see `docs/output_schema.json`.

## Notes

- For OpenAI-compatible proxies, keep the base URL ending with /v1.
- Prefer prompt version `v4` for technique selection and strict JSON.
