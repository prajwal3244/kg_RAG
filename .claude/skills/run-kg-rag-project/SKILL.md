---
name: run-kg-rag-project
description: Build, launch, and drive the kg_rag_project Streamlit app on Windows. Use when the user wants to run, start, serve, smoke-test, health-check, or screenshot the KG + RAG hybrid QA app at app.py. Boots streamlit with hot-reload, probes /_stcore/health, and screenshots the rendered UI via Playwright Chromium.
---

# run-kg-rag-project

KG + RAG Intelligence — a Streamlit app that combines FAISS vector search with a NetworkX knowledge graph, both populated from a single uploaded PDF/TXT. Driven by [driver.py](driver.py) (Python + Playwright). Paths below are relative to the project root.

## Prerequisites

- Windows 10/11 with PowerShell
- Python 3.12 at `C:\Users\<you>\AppData\Local\Programs\Python\Python312\python.exe` (3.10+ should also work; older won't because some wheels need cp312)
- A valid `GOOGLE_API_KEY` in `.env` at the project root (the app calls Gemini via `langchain-google-genai`)

The repo ships a `venv/` directory, but it may be a Python 3.9 shim baked on another machine — check `venv\pyvenv.cfg`. If `home =` points to a path that doesn't exist locally (commonly `C:\Users\HP\...`), rebuild it (see Setup).

## Setup

From the project root, in PowerShell:

```powershell
# Rebuild venv with local Python 3.12 (only if the bundled one is broken — see above)
Remove-Item -Recurse -Force venv
& "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe" -m venv venv

# Install runtime deps (gtts is imported by app.py but missing from requirements.txt)
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt gtts

# Install Playwright + bundled chromium for the driver's screenshot mode
.\venv\Scripts\python.exe -m pip install playwright
.\venv\Scripts\python.exe -m playwright install chromium
```

`pip install -r requirements.txt` resolves and unpacks ~240 packages — give it a few minutes.

## Run (agent path)

Use [driver.py](driver.py). It has four subcommands.

**1. Launch the server** (foreground; Ctrl-C to stop):

```powershell
.\venv\Scripts\python.exe .claude\skills\run-kg-rag-project\driver.py serve
```

This runs `streamlit run app.py --server.headless true --server.port 8501 --server.runOnSave true`. The app listens on http://localhost:8501; the `_stcore/health` endpoint returns the literal string `ok` once it's ready.

**2. Health probe** (in a second shell while `serve` runs):

```powershell
.\venv\Scripts\python.exe .claude\skills\run-kg-rag-project\driver.py health
```

Exits 0 if the server returns `ok`, otherwise 1. Polls up to `--timeout` seconds.

**3. Screenshot** (server must be running):

```powershell
.\venv\Scripts\python.exe .claude\skills\run-kg-rag-project\driver.py screenshot
```

Saves a PNG at `.claude\skills\run-kg-rag-project\screenshot.png`. Uses Playwright Chromium, waits for the `.hero-title` element (so it captures the hydrated UI, not the loading skeleton), then waits 800 ms for animations to settle. Override with positional args: `driver.py screenshot URL OUT`.

**4. Smoke test** (does both):

```powershell
.\venv\Scripts\python.exe .claude\skills\run-kg-rag-project\driver.py smoke
```

Health check, then screenshot, asserts PNG > 10 KB. Verified output:

```
health: ok (http://localhost:8501/_stcore/health)
-> http://localhost:8501
saved ...\screenshot.png (226089 bytes)
smoke: ok
```

## Run (human path)

If you just want to use the app yourself:

```powershell
.\venv\Scripts\activate
streamlit run app.py
```

Opens a browser tab at `http://localhost:8501`. Useless when you want a programmatic handle on the running UI — use the driver for that.

## Test

There's a 5-test pytest suite at [test_validation.py](../../../test_validation.py):

```powershell
.\venv\Scripts\python.exe -m pytest test_validation.py -v
```

Takes ~50 s (it imports the heavy Gemini/grpc stack). Run a single test with `pytest test_validation.py::test_validator_logic`.

## Gotchas

- **The shipped `venv/` is almost certainly broken.** Its `python.exe` is a shim that hard-codes the home directory of whoever ran `python -m venv` last. If that wasn't this machine, every Python invocation prints `No Python at 'C:\Users\HP\AppData\Local\Programs\Python\Python39\python.exe'`. Recreate it (see Setup) — don't try to repair it.
- **`requirements.txt` is missing `gtts`** even though [app.py](../../../app.py) imports it for voice readback. Install it explicitly; the import fails at startup otherwise.
- **`config.py` references preview Gemini model IDs** (`gemini-3.1-flash-lite-preview`, `gemini-embedding-2-preview`) while `requirements.txt` pins `langchain-google-genai==0.0.9` (January 2024). The UI renders fine and the index can be built (embeddings) only if those IDs exist server-side; if you hit `404 models/...`, swap to `gemini-1.5-flash` and `models/embedding-001` in [config.py:17-19](../../../config.py#L17-L19).
- **The persisted FAISS at `faiss_index/` does NOT auto-load on startup.** The session flag `is_indexed` is False after every Streamlit restart, so you must click "Build knowledge base" again. The knowledge graph is never persisted at all — it lives only in `st.session_state["kg"]`.
- **Streamlit is a WebSocket SPA.** A plain `chrome --headless --screenshot=URL` captures the skeleton state because virtual time doesn't advance the WebSocket. The driver uses Playwright with `wait_for_selector(".hero-title")` — that's the smallest reliable signal that the first rerun has landed.
- **PowerShell defaults to cp1252.** If you edit `driver.py`, keep `print()` statements ASCII. Unicode arrows (`→`, `·`) in stdout crash with `UnicodeEncodeError`. They're fine inside Playwright selectors / app HTML — only stdout is constrained.
- **OneDrive holds file locks.** During the venv rebuild, `Remove-Item -Recurse -Force venv` may fail on `orjson` `RECORD` because OneDrive sync is still scanning. Python's `venv` module overlays cleanly anyway — leftover dist-info in `site-packages` will be replaced when you `pip install`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `No Python at 'C:\Users\HP\...Python39\python.exe'` | The venv shim points to a foreign machine. Rebuild per Setup. |
| `ModuleNotFoundError: gtts` | `pip install gtts` — it's missing from `requirements.txt`. |
| `playwright._impl._errors.Error: Executable doesn't exist at .../chrome-win/chrome.exe` | Run `.\venv\Scripts\python.exe -m playwright install chromium`. |
| `UnicodeEncodeError: 'charmap' codec can't encode character` | Your edit added non-ASCII to a `print()`. Replace with ASCII. |
| Screenshot is 6–9 KB and shows skeleton bars / "Deploy" button | Driver wasn't used. `chrome --screenshot` against Streamlit needs Playwright to wait for the hydrated DOM. |
| `port 8501 is already in use` | Another `streamlit run` is alive. `Get-NetTCPConnection -LocalPort 8501 \| Select-Object OwningProcess` then `Stop-Process -Id <pid>`. |
