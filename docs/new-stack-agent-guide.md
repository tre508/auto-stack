**AI Agent Orientation Prompt**

> **Context & Background**
> You have been onboarded to a brand‐new “auto-stack” project workspace within a WSL 2 environment. Your project root is at:
>
> ```
> ~/projects/auto-stack
> ```
>
> This directory mirrors (and has superseded) the previous “automation-stack” project. All critical documentation and code have already been migrated into this new folder, but nothing is fully rebuilt or configured. Your job is to get “auto-stack” back up and running from scratch, following WSL-native practices.

---

## 1. Current Workspace Snapshot

1. **Root Directory (`auto-stack/`)**

   * Core files at the top level include:

     ```
     .dockerignore  
     .env             ← (likely a placeholder or legacy)  
     .env.example     ← blank template for service variables  
     compose-mcp.yml  ← legacy or starting point for Docker Compose  
     create_test_workflow.py  
     load-env.sh  
     README.md        ← high-level introduction  
     requirements.txt ← Python requirements (possibly for Controller or mem0)  
     ```
   * Hidden/support folders:

     * `.cursor/` (Cursor-AI rule files)
     * `.gitignore`, `.gitattributes`, `.gitmodules`
   * Top-level code/service directories:

     ```
     controller/      ← FastAPI “Controller” service code  
     freq-chat/       ← Next.js chat UI  
     hf_spaces\bge_embedding-...  ← Hugging Face embedding service code  
     logs/            ← logging or local test artifacts  
     mem0/            ← “Memory” FastAPI service  
     n8n_data/        ← n8n workflows or data folder (if used)  
     openrouter_proxy/ ← LLM proxy service code  
     ```

2. **Documentation Folder (`docs/`)**

   * Under `docs/`, the pre-implementation guide files you authored reside:

     ```
     00_Project_Overview.md  
     01_Architecture_and_Components.md  
     02_Service_Configuration_and_Verification.md  
     03_Cross_Stack_Integration.md  
     04_Environment_Configuration.md  
     05_Agent_and_Workflow_Interaction.md  
     06_Developer_Tools_and_Practices.md  
     07_Freqtrade_Prep.md (placeholder)  
     controller-env.md  
     freqdev.local-env.md  
     main-env.md  
     docs_filetree.txt  
     full_filetree.txt  
     ```
   * There is a `docs/triage/` subfolder containing legacy reference docs from the old “automation-stack.”

3. **Service Directories & Notable Files**

   * **controller/**

     * Contains `controller.py`, `requirements.txt`, Node-based EKO integration (`eko_service.js`), and Dockerfiles.
     * There is also a `.env` specifically for the controller.
   * **freq-chat/**

     * Fully fledged Next.js application with its own `.env.development.local`, `Dockerfile`, `package.json` and related configs (`next.config.ts`, `tailwind.config.ts`).
   * **mem0/**

     * FastAPI “memory” service with its own Python requirements, configuration files, and likely a `Dockerfile` (verify).
   * **n8n\_data/**

     * Placeholder or data folder for n8n workflows (if the n8n service is to be reinstalled).
   * **openrouter\_proxy/**

     * Node-based code that proxies external LLM API calls, with its own Dockerfile or `package.json`.
   * **hf\_spaces\bge\_embedding-…**

     * A local embedding service (Hugging Face Space or similar) that must be containerized or configured.

4. **Legacy Files**

   * At the old “automation-stack” location (now deprecated), more extensive “setup/” and backup files exist. All relevant docs have been triaged into `docs/triage`.
   * The old file trees (`old_docs_filetree.txt`, `old_full_filetree.txt`) show many legacy subfolders—these have been archived and need not be modified, but they exist under `docs/triage` if you need historical reference.

---

## 2. Outstanding Tasks & Priorities

Your primary objective: **Build a clean, end-to-end development environment** such that every service runs correctly, uses data volumes on a secondary drive partition accessible to WSL (e.g., `/mnt/d/`), and shares a unified Docker network.

Below is a non-exhaustive list of actionable sub-goals to guide your workflow. You may reorganize or expand these as you see fit, but you must come back to each as checkpoints:

1. **Workspace Environment Setup**

   * Decide which services need their own Python virtual environment (`.venv`) or Node environment.

     * For example:

       * `controller/` and `mem0/` likely require separate Python venvs.
       * `freq-chat/` uses Node (npm/yarn) and may not need a `.venv` but should have a clear `npm install` step.
       * `openrouter_proxy/` is Node-based—decide if you want a standalone `node_modules` or a container-only approach.
   * Coordinate `.env` file usage so that each service directory knows exactly which environment file to read.

     * In `controller/`, ensure `.env` exists and is referenced by its Dockerfile or by `python-dotenv`.
     * In `mem0/`, create a `.env` with keys like `MEM0_API_KEY`, `OPENAI_API_KEY`, `QDRANT_HOST`, etc.
     * In `freq-chat/`, confirm `.env.development.local` is up to date.
     * Consolidate all templates and move any global variables into `docs/04_Environment_Configuration.md` for reference.
   * Configure your editor/IDE (e.g., VS Code with Cursor Ai) so that terminals launched from each service folder automatically activate the correct environment (via a `.vscode/settings.json` or a `load-env.sh` script).

2. **Docker & Compose Reconfiguration**

   * Create or update a unified `docker-compose.yml` (or split into `docker-compose.dev.yml` and `docker-compose.prod.yml`) at the root of `auto-stack/`.

     * Ensure each service's "image:" or "build:" settings point to the correct local folder (e.g., `controller/`, `mem0/`, `openrouter_proxy/`, `freq-chat/`).
     * For `freq-chat/`, confirm its `Dockerfile` builds successfully, exposing port `3000`, and adds Traefik labels (if using Traefik).
     * For `n8n_data/`: decide whether you are going to reinstall n8n, or remove it if you're not using n8n here. If reinstalled, add an `n8n` service referencing a persisted volume (e.g., `/mnt/d/docker-volumes/n8n_data:/home/node/.n8n`).
   * Set up a Docker network (e.g., `auto-stack-net`) so that all containers can communicate via service names.
   * For each service, mount data or volume folders from a drive accessible to WSL (e.g., `/mnt/d/docker-volumes/controller_data`, `/mnt/d/docker-volumes/mem0_data`, `/mnt/d/docker-volumes/qdrant_data`, `/mnt/d/docker-volumes/pg_logs_data`, etc.).

     * **Note on Permissions:** When using bind mounts from the Windows filesystem (`/mnt/c` or `/mnt/d`) into WSL 2, Docker Desktop generally handles permissions correctly. The `icacls` command is not applicable. For files created inside the container, standard Linux permissions apply.

3. **.env File Coordination & Cursor Settings**

   * In the root `auto-stack/` folder, confirm that `.env.example` lists all required variables with placeholder values.
   * For each service, create a `.env` (symlink or copy from `.env.example`) with actual development values (e.g., `POSTGRES_LOGGING_PASSWORD`, `CONTROLLER_API_KEY`, etc.).
   * Update Cursor Ai's settings so that when it spawns terminals in a given service folder (e.g., `controller/`), the proper environment is auto-loaded. For example:

     ```yaml
     # .cursor/config.yaml (example)
     workspaces:
       - name: controller
         path: ./controller
         loadEnvFile: .env
       - name: mem0
         path: ./mem0
         loadEnvFile: .env
       - name: freq-chat
         path: ./freq-chat
         loadEnvFile: .env.development.local
       - name: openrouter_proxy
         path: ./openrouter_proxy
         loadEnvFile: .env
     ```
   * Ensure `load-env.sh` at the root can be used to source environment variables for all services (optional).

4. **Rebuild & Validate All Docker Containers**

   * From the root, run:

     ```bash
     docker-compose down --volumes --remove-orphans
     docker-compose build --no-cache
     docker-compose up -d
     ```
   * Watch logs for each container:

     ```bash
     docker-compose logs -f controller
     docker-compose logs -f mem0
     docker-compose logs -f openrouter_proxy
     docker-compose logs -f freq-chat
     # (plus any others like n8n, qdrant, postgres)
     ```
   * Confirm:

     * Controller starts on port 3000 and responds to `GET /health`.
     * Mem0 starts on port 8000, `GET /health` returns `{"status":"ok"}`.
     * openrouter\_proxy binds port 3000 internally / 8001 externally and proxies LLM requests.
     * freq-chat serves at `http://localhost:3001` (or via Traefik hostnames).
     * Qdrant, Postgres, and any other data stores are running and accessible.

5. **Service Directory Review & Testing**

   * **controller/**

     * Open `controller.py`/`main.py`, verify all imported modules exist in `requirements.txt`, and run `pytest` or equivalent to ensure no immediate errors.
     * Confirm `Dockerfile` is correct (e.g., installs `requirements.txt`, copies source, and sets `CMD ["uvicorn", "controller:app", "--host", "0.0.0.0", "--port", "3000"]`).
   * **mem0/**

     * Inspect `app/main.py` and `config.yaml`. Ensure Qdrant host/port in `.env` matches your Docker Compose.
     * Run unit tests (`pytest`) or at least a manual `curl http://localhost:8000/health`.
   * **freq-chat/**

     * Run `npm install` and `npm run dev` manually to verify no missing dependencies. Confirm environment variables are loaded by Next.js.
     * Validate the REST API endpoints under `pages/api` properly proxy to Controller/Mem0.
     * Confirm the Dockerfile builds the image, and its `CMD ["npm", "run", "start"]` (or equivalent) works.
   * **openrouter\_proxy/**

     * Check that `eko_service.js` or relevant JavaScript code loads its environment (e.g., `process.env.OPENROUTER_API_KEY`) and exposes endpoints at `/v1/chat/completions`.
     * Start locally (`node openrouter_proxy.js`) to verify it can actually connect to the OpenRouter API—then containerize.
   * **n8n\_data/** (if still relevant)

     * If you plan to spin up n8n, you may need a new `n8n/` folder with a Dockerfile or use the official `n8nio/n8n:latest` image. Decide if you want to keep it or remove it entirely.
   * **hf\_spaces\bge\_embedding-…/**

     * Confirm this service (embedding engine) has a working `Dockerfile` or a clear Python script. It should expose an endpoint that Mem0 can call to generate embeddings.

---

## 3. Next Steps & Checkpoints

1. **Confirm Environmental Isolation**

   * Verify that each Python service (controller, mem0) uses its own `.venv` (or remains container-only).
   * Ensure no accidental global installs in your WSL2 environment contaminate dependencies.

2. **Validate Docker Networking**

   * All containers must live on a shared network (e.g., `auto-stack-net`).
   * Each service should reference others by their service name (e.g., `http://mem0_auto:8000`, `http://controller_auto:3000`).

3. **Run End-to-End Smoke Tests**

   * **Controller → Mem0 → Qdrant:**

     ```bash
     curl -X POST http://localhost:3000/api/mem0/echo -H "Authorization: Bearer <MEM0_API_KEY>" -d '{"message":"Hello"}'
     ```
   * **freq-chat → Controller → Mem0:**

     1. Open `http://localhost:3001` in browser.
     2. Send a test chat message—verify it hits Controller, calls Mem0, and returns a meaningful response.
   * **OpenRouter Proxy → External LLM:**

     ```bash
     curl -X POST http://localhost:8001/v1/chat/completions \
       -H "Authorization: Bearer <OPENROUTER_API_KEY>" \
       -H "Content-Type: application/json" \
       -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Test"}]}'
     ```

4. **Prepare Freqtrade Integration**

   * Freqtrade container is not yet implemented; 07\_Freqtrade\_Prep.md is a placeholder. Ensure that when you're ready, the directory `auto-stack/freqtrade/` is created with:

     ```
     Dockerfile  
     user_data/  
     .env (with FREQTRADE_API_URL, credentials)  
     ```
   * Plan how Controller's `/api/freqtrade/backtest` endpoint will call Freqtrade's REST API after that container is live.

5. **Document Any Deviations or Roadblocks**

   * If you discover missing environment variables, outdated legacy code, or broken Dockerfiles, note these issues in a new `docs/auto-stack/TODO.md` so the next agent or developer knows exactly where to pick up.

---

## 4. How to Proceed

1. **Review this Prompt**

   * Make sure you understand the current directory structure, the location of key `.env` files, and the services that must be rebuilt.
   * If any folder or file is unclear, use your unrestricted **browse** capability or promptly ask the user to clarify rather than guessing.

2. **Ask the User for Any Missing Clarifications**

   * Before making changes, confirm:

     * "Which services should use local `.venv` vs. container-only?"
     * "Should n8n be reinstalled or removed entirely?"
     * "Which D:-drive paths have already been created (for volumes), and which need to be?"
   * Wait for the user's confirmation—do not proceed until all critical questions are answered.

3. **Transition to "Act Mode"**

   * Once the user says "Go for it," begin executing the steps above autonomously.
   * Only interrupt to ask for assistance if you are genuinely stuck (e.g., can't find a required `.env` variable or a Dockerfile is missing).

---

> **Remember:** You have **unrestricted tool access**. If you need to verify a Docker image tag, blueprint for Freqtrade, n8n URL format, or Python package details, use the `browse` tool. Do not stop to ask the user for publicly available references.

Good luck! Proceed by summarizing your understanding of this prompt and asking any clarifying questions before moving forward.
