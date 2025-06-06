\\\n# Vercel AI Chat: Next.js AI Chatbot Template Customization

**Last updated:** $(Get-Date -Format \\\'yyyy-MM-dd\\\')

This document outlines how the standard [Vercel Next.js AI Chatbot template](https://vercel.com/templates/ai/nextjs-ai-chatbot) might be customized or extended to serve as the `vercel_chat_mcp` service within the `automation-stack`. It provides conceptual examples and areas for adaptation.

Refer to `docs/Vercel-integration.md` for the initial recommendation of this template.

---

## 1. Forking and Initial Setup

*   **Forking Process:**
    1.  Navigate to the [Next.js AI Chatbot template on Vercel](https://vercel.com/templates/ai/nextjs-ai-chatbot).
    2.  Click the \"Deploy\" button, which will typically guide you to fork the repository to your GitHub (or other Git provider) account and deploy an initial version to Vercel.
    3.  Clone your forked repository to your local machine to begin customization.
        ```bash
        git clone <your_forked_repo_url>
        cd <repository_name>
        ```
*   **Initial Configuration:** Follow the template's README for initial setup, including installing dependencies (`npm install` or `pnpm install`) and setting up required base environment variables (e.g., for an LLM provider like OpenRouter or OpenAI).

---

## 2. Backend API Route Modifications for Stack Integration

The core of customizing the chatbot for the `automation-stack` involves modifying or adding Next.js API routes (typically in the `app/api/` directory) to communicate with `controller_mcp` and `n8n_mcp`.

### Example: Routing to FastAPI Controller (`controller_mcp`)

Let's say you want a chat command like \"`/freqtrade status`\" to get Freqtrade bot status via the `controller_mcp`.

1.  **Define a new API route in your Next.js app (e.g., `app/api/controller-proxy/route.ts`):**

    ```typescript
    // app/api/controller-proxy/route.ts
    import { NextRequest, NextResponse } from 'next/server';

    const CONTROLLER_URL = process.env.FASTAPI_CONTROLLER_URL || 'http://controller_mcp:5050';

    export async function POST(req: NextRequest) {
      try {
        const { command, payload } = await req.json();

        // Example: Route specific commands to specific controller endpoints
        if (command === 'freqtrade_status') {
          const response = await fetch(`${CONTROLLER_URL}/api/v1/freqtrade/status`, {
            method: 'GET', // Assuming controller has a GET endpoint for this
            headers: {
              // Add any necessary headers, like API keys for the controller
            },
          });
          if (!response.ok) {
            throw new Error(`Controller API error: ${response.statusText}`);
          }
          const data = await response.json();
          return NextResponse.json(data);
        } else if (command === 'execute_task') {
          // Example for a generic /execute endpoint on controller
           const response = await fetch(`${CONTROLLER_URL}/api/v1/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload), // payload might be { task_name: '...', data: {...} }
          });
           if (!response.ok) {
            throw new Error(`Controller execute error: ${response.statusText}`);
          }
          const data = await response.json();
          return NextResponse.json(data);
        }

        return NextResponse.json({ error: 'Unknown controller command' }, { status: 400 });
      } catch (error: any) {
        console.error('[Controller Proxy API Error]', error);
        return NextResponse.json({ error: error.message || 'Failed to proxy to controller' }, { status: 500 });
      }
    }
    ```

2.  **Call this API route from your chat component's frontend logic** when a specific command is detected.

### Example: Triggering n8n Workflows (`n8n_mcp`)

Suppose you want to trigger an n8n workflow to log chat interactions or perform a background task.

1.  **Define an API route (e.g., `app/api/n8n-trigger/route.ts`):**

    ```typescript
    // app/api/n8n-trigger/route.ts
    import { NextRequest, NextResponse } from 'next/server';

    const N8N_WEBHOOK_URL = process.env.N8N_CHAT_LOGGING_WEBHOOK_URL; // e.g., http://n8n_mcp:5678/webhook/chat-logger

    export async function POST(req: NextRequest) {
      if (!N8N_WEBHOOK_URL) {
        console.error('N8N_CHAT_LOGGING_WEBHOOK_URL is not configured.');
        return NextResponse.json({ error: 'n8n webhook not configured' }, { status: 500 });
      }
      try {
        const payload = await req.json(); // e.g., { userId, message, timestamp, llmResponse }

        const response = await fetch(N8N_WEBHOOK_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          // n8n webhooks often return 200 even on internal errors, so check response body if needed
          console.error('n8n webhook call failed or returned non-ok status.', await response.text());
          // Decide on error handling - maybe still return success to client if logging is non-critical
        }

        return NextResponse.json({ message: 'Payload sent to n8n' });
      } catch (error: any) {
        console.error('[n8n Trigger API Error]', error);
        return NextResponse.json({ error: error.message || 'Failed to trigger n8n workflow' }, { status: 500 });
      }
    }
    ```

*   Environment variables like `FASTAPI_CONTROLLER_URL` and `N8N_CHAT_LOGGING_WEBHOOK_URL` would need to be set for the Vercel AI Chat application (see `setup.md` and `integration.md`).

---

## 3. Adding Plugin Hooks or Custom Tool Integrations (Conceptual)

The Next.js AI Chatbot template can be extended to support \"tools\" or \"plugins\" that the LLM can decide to use, or that can be triggered by specific user commands.

*   **Frontend Detection:** The chat input logic on the frontend can detect special commands (e.g., `/fetch_data <params>`, `/run_backtest <strategy>`).
*   **Backend Handler:** When such a command is detected, the frontend sends it to a dedicated API route in the Next.js app.
*   **API Route Logic:** This API route then:
    1.  Parses the command and parameters.
    2.  Interacts with the appropriate `automation-stack` service (e.g., calls `controller_mcp` for Freqtrade actions, calls `n8n_mcp` for complex workflows, or directly accesses a data source).
    3.  Returns the result to the frontend, which then displays it or feeds it back into the LLM conversation context.

*   **LLM-Driven Tool Use (Advanced):** If the chosen LLM supports function calling/tool use (like some OpenAI models), you can define available tools (matching stack capabilities) in the LLM API call. The LLM might then respond with a request to call one of your defined tools. Your Next.js backend would then execute this tool (by calling the relevant stack service) and send the result back to the LLM to continue the conversation.
    *   This often involves more complex state management and multiple turns of conversation with the LLM.
    *   The Vercel AI SDK provides utilities that can help manage tool calls with compatible LLMs.

---

## 4. Authentication Changes

The standard Next.js AI Chatbot template comes with NextAuth.js for authentication.

*   **Default Setup:** Typically uses providers like GitHub, Google, or email-based magic links.
*   **Customization for `automation-stack`:**
    *   **No Auth (Internal Docker):** If `vercel_chat_mcp` is run purely on the internal Docker network and not exposed publicly, authentication might be deemed unnecessary for inter-service calls, simplifying setup. UI access would still be managed by Traefik or direct port exposure.
    *   **Shared Authentication:** If a unified authentication system is implemented across the `automation-stack` (e.g., using a central IdP), NextAuth.js in `vercel_chat_mcp` could be configured to use a custom OAuth provider or JWT validation strategy to integrate with it.
    *   **Role-Based Access:** You might extend NextAuth.js to assign roles to users, and then protect certain API routes or plugin actions in `vercel_chat_mcp` based on these roles.
        ```typescript
        // Example: Protecting an API route with NextAuth session check
        import { auth } from 'your-auth-config-file'; // From the template
        import { NextRequest, NextResponse } from 'next/server';

        export async function POST(req: NextRequest) {
          const session = await auth();
          if (!session || !session.user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
          }
          // ... rest of your API logic for authenticated users ...
        }
        ```

---

## 5. UI Changes & Enhancements

The Next.js AI Chatbot template provides a solid UI foundation using shadcn/ui and Tailwind CSS.

*   **Possible Customizations for `automation-stack`:**
    *   **Branding:** Update logos, color schemes, and typography to match the `automation-stack` project if desired.
    *   **Custom Components for Tool Responses:** If tools return structured data (e.g., charts from Freqtrade, tables of data), create custom React components to render this data nicely in the chat interface instead of just plain text.
    *   **Command Palette/Suggestions:** Implement UI elements to suggest available `/commands` or tools to the user.
    *   **Status Indicators:** Add UI elements to show the status of backend services like `controller_mcp` or the LLM provider (e.g., OpenRouter) (could be fetched via a dedicated API route in `vercel_chat_mcp`).
    *   **Integration-Specific UI:** If certain integrations are very common (e.g., initiating a Freqtrade backtest), dedicated UI forms or buttons could be added to simplify these actions beyond just typing commands.

---

## 6. Actual Customizations Applied to `freq-chat` (as of 2025-05-26)

The `freq-chat` project, which was an existing Next.js application, has been significantly refactored to align with the Vercel Next.js AI Chatbot template. Key steps taken include:

*   **`package.json` Merge:** Dependencies and scripts from the Vercel AI Chatbot template's `package.json` were merged into `freq-chat/package.json`. This involved:
    *   Adopting many new dependencies from the template.
    *   Aligning versions of shared dependencies (e.g., Next.js, React, NextAuth.js, Drizzle ORM) to those specified in the template. This included a notable downgrade of Tailwind CSS from a potential v4 to v3.4.1.
    *   Adopting the template's more comprehensive `scripts` for linting, formatting, database operations, and testing.
*   **Dependency Installation:**
    *   Initial `pnpm install` attempts after the merge led to numerous "Module not found" errors during `pnpm run dev`.
    *   The error `next' is not recognized as an internal or external command` was resolved by deleting `node_modules` and `pnpm-lock.yaml`, then running `pnpm install --shamefully-hoist`.
*   **Database Setup (Local PostgreSQL):**
    *   A local PostgreSQL database (`freqchat_db`) and user (`freqchat_user`) were created.
    *   Tablespaces were used to locate the database files on the D: drive.
    *   The `POSTGRES_URL` environment variable in `freq-chat/.env.development.local` was configured to point to this local database.
    *   Drizzle ORM schema (`lib/db/schema.ts`) was established, and database migrations were managed (involving clearing old migration files and ensuring `drizzle-kit generate` and `pnpm db:migrate` completed successfully).
*   **Environment Configuration:**
    *   `freq-chat/.env.development.local` was created/updated with necessary variables like `POSTGRES_URL`, `NEXTAUTH_URL`, `NEXTAUTH_SECRET`, and LLM API keys.
*   **Current Status:**
    *   The `freq-chat` development server (`pnpm run dev`) starts successfully.
    *   The basic UI from the Vercel AI Chatbot template renders at `http://localhost:3000`.
    *   Significant TypeScript errors ("Cannot find module", "Cannot find name 'process'") are present in VS Code, requiring further investigation (e.g., restarting TS server, checking `tsconfig.json`, installing specific `@types/*` packages).
    *   The UI is described as "wonky," likely due to Tailwind CSS version changes and other styling adjustments needed.

These steps represent the initial phase of adapting the existing `freq-chat` project to the structure and dependencies of the Vercel AI Chatbot template. Further work is needed to resolve TypeScript errors and UI issues.

---

These customizations transform the generic chatbot template into a tailored interface for the `automation-stack`, leveraging its underlying services for powerful, AI-assisted operations.
