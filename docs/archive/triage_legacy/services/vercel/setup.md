# Vercel AI Chat: Setup Guide

**Last updated:** 2025-05-26

This document provides end-to-end instructions for setting up the Vercel AI Chat service (referred to as `freq-chat` for local development) within the `automation-stack`.

---

## 1. Prerequisites

Before you begin, ensure you have the following installed and configured:

*   **Node.js & pnpm:** Required for Vercel CLI and Next.js development. `pnpm` is the package manager used for `freq-chat`.
    *   Verify installation:
        ```bash
        node -v
        pnpm -v
        ```
*   **Docker & Docker Compose:** Essential for running the `automation-stack` services. While `freq-chat` is run locally with `pnpm run dev` for development, it interacts with other Dockerized services.
    *   Verify installation:
        ```bash
        docker --version
        docker-compose --version
        ```
*   **Vercel Account:** You'll need a Vercel account if you plan to deploy the application to Vercel. Sign up at [vercel.com](https://vercel.com/).
*   **Git:** For version control.
*   **PostgreSQL Server:** Required for local development of `freq-chat`.

---

## 2. Install Vercel CLI

The Vercel Command Line Interface (CLI) allows you to deploy and manage your Vercel projects from your terminal.
*   Install globally using npm (or pnpm):
    ```bash
    npm install -g vercel
    ```
*   Verify installation:
    ```bash
    vercel --version
    ```

---

## 3. Authentication & Login (for Vercel Deployment)

Log in to your Vercel account through the CLI if you plan to deploy:
*   Run the login command:
    ```bash
    vercel login
    ```
*   Follow on-screen prompts.

---

## 4. Project Structure (`freq-chat`)

The `freq-chat` application is based on the Next.js AI Chatbot template and resides in the `freq-chat/` directory within the `automation-stack`.
```
automation-stack/
└── freq-chat/              # Root of the Next.js application
    ├── app/                # Next.js App Router (pages, API routes)
    ├── components/         # UI components
    ├── lib/                # Helper functions, AI SDK configuration, database schema/queries
    ├── public/             # Static assets
    ├── .env.development.local # Local environment variables
    ├── next.config.ts      # Next.js configuration (or .js/.mjs)
    ├── package.json        # Project dependencies and scripts
    ├── pnpm-lock.yaml      # pnpm lockfile
    └── tsconfig.json       # TypeScript configuration
```
*   Refer to `docs/Agent-Orientation.md` and `docs/services/vercel/integration.md` for how this service fits into the broader `automation-stack`.

---

## 5. Local Development Setup for `freq-chat`

Follow these steps to set up `freq-chat` for local development:

### 5.1. PostgreSQL Database Setup
`freq-chat` requires a PostgreSQL database.
1.  **Install PostgreSQL:** If not already installed (e.g., version 17).
2.  **Create Database and User:**
    *   Connect to `psql` as the superuser (e.g., `postgres`).
    *   Create a directory for tablespace on a desired drive (e.g., `D:\pg_data\freqchat_tablespace`) and ensure the PostgreSQL service user has permissions.
    *   Execute SQL commands:
        ```sql
        CREATE TABLESPACE freqchat_ts LOCATION 'D:/pg_data/freqchat_tablespace'; -- Adjust path if needed
        CREATE DATABASE freqchat_db TABLESPACE freqchat_ts;
        CREATE USER freqchat_user WITH PASSWORD 'your_chosen_password'; -- Replace with a strong password
        GRANT ALL PRIVILEGES ON DATABASE freqchat_db TO freqchat_user;
        ALTER DATABASE freqchat_db OWNER TO freqchat_user;
        ```
3.  **Configure `POSTGRES_URL`:** Set this in `freq-chat/.env.development.local`:
    `POSTGRES_URL="postgresql://freqchat_user:your_chosen_password@localhost:5432/freqchat_db"`

### 5.2. Align Dependencies with Template
The `freq-chat/package.json` has been merged with dependencies from the Vercel AI Chatbot template. This involved significant version changes for packages like Next.js, React, Tailwind CSS (downgraded to v3.4.1), NextAuth.js, and Drizzle ORM.

### 5.3. Install Dependencies
1.  Navigate to the `freq-chat` directory: `cd freq-chat`
2.  Delete existing `node_modules` and `pnpm-lock.yaml` if present to ensure a clean install:
    ```bash
    # (Optional, but recommended after major package.json changes)
    # del pnpm-lock.yaml 
    # Remove-Item -Recurse -Force node_modules 
    ```
3.  Install dependencies using `pnpm install --shamefully-hoist`. The `--shamefully-hoist` flag helps resolve issues with CLI tools like `next` not being found on some systems (particularly Windows).
    ```bash
    pnpm install --shamefully-hoist
    ```

### 5.4. Database Migrations
1.  Ensure your `freq-chat/drizzle.config.ts` and `freq-chat/lib/db/migrate.ts` are configured to load `.env.development.local`.
2.  The database schema should align with `lib/db/schema.ts`. If issues arise with migrations (e.g., "column already exists"):
    *   Clear the `freq-chat/lib/db/migrations` folder (delete *.sql files and the `meta` subfolder).
    *   Recreate the `migrations` folder.
    *   Run `pnpm db:generate` (which is `drizzle-kit generate`). This should report "No schema changes, nothing to migrate" if the database matches the schema.
    *   Run `pnpm db:migrate` (which is `npx tsx lib/db/migrate.ts`). This should also report no pending migrations or complete successfully.

### 5.5. Run Development Server
```bash
cd freq-chat
pnpm run dev
```
The application should be accessible at `http://localhost:3000`.

---

## 6. Vercel Deployment (Cloud)

Once your project is ready and configured for local development, you can deploy it to Vercel.

1.  **Navigate to your `freq-chat` project directory.**
2.  **Link to Vercel:** `vercel link` (if first time).
3.  **Deploy:** `vercel` (for preview) or `vercel --prod` (for production).

---

## 7. Environment Variable Setup

### For Vercel Deployments:
Manage via Vercel Dashboard (Settings > Environment Variables) or Vercel CLI (`vercel env add ...`).
*   `POSTGRES_URL`: Connection string for your Vercel Postgres or other cloud-hosted PostgreSQL.
*   `NEXTAUTH_URL`: Canonical URL of your Vercel deployment.
*   `NEXTAUTH_SECRET`: Strong secret for NextAuth.js.
*   LLM API Keys (e.g., `OPENROUTER_API_KEY`, `OPENAI_API_KEY`).
*   URLs for other `automation-stack` services if `freq-chat` (deployed on Vercel) needs to call them (e.g., a publicly accessible Controller API).

### For Local Development (`freq-chat/.env.development.local`):
*   `POSTGRES_URL="postgresql://freqchat_user:your_password@localhost:5432/freqchat_db"` (as configured in step 5.1).
*   `NEXTAUTH_URL="http://localhost:3000"`
*   `NEXTAUTH_SECRET="your_local_dev_secret"` (can be any string for local dev)
*   LLM API Keys (e.g., `OPENROUTER_API_KEY`).
*   URLs for other *locally running* `automation-stack` services (e.g., `FASTAPI_CONTROLLER_URL=http://controller_mcp:5050` if `controller_mcp` is running in Docker on `mcp-net` and `freq-chat` needs to access it from the host via a mapped port or if `freq-chat` itself were Dockerized on `mcp-net`).

*   Refer to `docs/services/vercel/integration.md` and `docs/configplan.md` for more on environment variables.

---

This concludes the setup for the `freq-chat` (Vercel AI Chat) service for local development and provides pointers for Vercel deployment. For integration details, see `integration.md`. For troubleshooting, see `troubleshooting.md`.
