# Freq-Chat LLM Connection Troubleshooting Guide

This document outlines the steps taken, issues encountered, and fixes applied while configuring Freq-Chat to use a custom LLM endpoint (OpenRouter via a local proxy) for its chat and title generation functionalities.

## Objective
Configure Freq-Chat to use the `openrouter_proxy_mcp` service for all LLM calls, specifically targeting models like "tngtech/deepseek-r1t-chimera:free".

## Initial State & Problem
Freq-Chat was initially configured (or defaulted) to use xAI/Grok models or was attempting to call the official OpenAI API endpoint (`https://api.openai.com/v1/chat/completions`) directly, leading to "Incorrect API key" errors when the system tried to use an OpenRouter key or a Hugging Face token with the OpenAI endpoint.

The primary challenge was ensuring that the Vercel AI SDK's `@ai-sdk/openai` provider, used within Freq-Chat, correctly utilized the `OPENAI_BASE_URL` (pointing to the local proxy) and `OPENAI_API_KEY` (the OpenRouter key) from Freq-Chat's environment variables.

## Key Files Involved
-   `freq-chat/.env.development.local`: For setting local environment variables.
-   `freq-chat/lib/ai/providers.ts`: Defines `myProvider` which supplies the LLM instance to the application.
-   `freq-chat/app/(chat)/api/chat/route.ts`: Main backend API route for chat, calls `streamText`.
-   `freq-chat/app/(chat)/actions.ts`: Contains `generateTitleFromUserMessage`.
-   `freq-chat/components/multimodal-input.tsx`: Frontend component for chat input.
-   `freq-chat/app/api/test-sdk/route.ts`: Minimal API route to test SDK behavior.
-   `freq-chat/package.json`: Defines SDK versions (`ai@4.3.13`, `@ai-sdk/openai@1.3.22`).
-   `openrouter_proxy/server.js`: The code for the local OpenRouter proxy.

## Troubleshooting Steps and Fixes Applied

### 1. Environment Variable Loading (Critical Fix)
-   **Initial Hurdle:** Freq-Chat's `pnpm dev` process (when run from Cursor's integrated terminal) was inheriting `OPENAI_API_KEY` (as `hf_...` token) and `OPENAI_BASE_URL` (as controller's Mem0 proxy URL) from the shell environment, overriding values in `freq-chat/.env.development.local`.
-   **Fix:** Running `pnpm dev` for `freq-chat` in a **separate, clean terminal session** (e.g., a new PowerShell window outside of Cursor) where these variables were not pre-set in the shell.
-   **Outcome:** This allowed `freq-chat/.env.development.local` to be correctly loaded. Logs from `providers.ts` and `chat/route.ts` then confirmed that `process.env.OPENAI_API_KEY` was the OpenRouter key (`<OPENROUTER_API_KEY>`) and `process.env.OPENAI_BASE_URL` was the correct local proxy URL (`http://localhost:8001/v1`).

### 2. Title Generation (`freq-chat/app/(chat)/actions.ts`)
-   **Initial Issue:** When using `generateText` via `myProvider` (which used `@ai-sdk/openai`), the call was still defaulting to `https://api.openai.com/v1/...` despite correct env vars being logged.
-   **Fix (Bypassing SDK Provider for this HTTP Call):** Modified `generateTitleFromUserMessage` to use a direct `fetch` call to `process.env.OPENAI_BASE_URL` with `process.env.OPENAI_API_KEY`.
-   **Outcome: SUCCESS!** Title generation now works correctly, hitting the `openrouter_proxy_mcp` service at `http://localhost:8001/v1/chat/completions` and using the correct OpenRouter API key.

### 3. LLM Provider Configuration (`freq-chat/lib/ai/providers.ts`)
-   **Issue:** Attempts to explicitly configure the `openai` provider from `@ai-sdk/openai` with a custom `baseURL` using methods like `openai.withOptions()` or passing options to `openai.chat()` were blocked by:
    -   Persistent TypeScript errors ("Property 'withOptions' does not exist").
    -   Runtime TypeError (`openai.withOptions is not a function`).
-   **Current State:** `providers.ts` uses `const openRouterProvider = openai;`, relying on the SDK to pick up `OPENAI_API_KEY` and `OPENAI_BASE_URL` from `process.env`. While `process.env` values are now correct in the Freq-Chat Node.js environment, the SDK's internal fetch for `streamText` (used by the main chat) might still be defaulting its target URL.

### 4. Main Chat Streaming (`freq-chat/app/(chat)/api/chat/route.ts`)
-   **Current Issue:** The UI shows "Please wait for the model to finish its response!" and no message appears, although the `/api/chat` route returns a 200 OK after a delay.
-   **Diagnosis:** The `streamText` call (using `myProvider`, which uses `@ai-sdk/openai`) is likely still not sending its request to the correct `OPENAI_BASE_URL` (`http://localhost:8001/v1`), or the `openrouter_proxy_mcp` is not handling the streaming response correctly for this call. The fact that title generation (non-streaming `fetch`) works points to an issue specific to the SDK's streaming call or the proxy's stream handling.

### 5. API Route Handler (`freq-chat/app/(chat)/api/chat/route.ts`)
-   **Issue:** "No response is returned from route handler" error.
-   **Fix:** Ensured all code paths in the `POST` handler return a `NextResponse`.

### 6. Frontend UI Error (`freq-chat/components/multimodal-input.tsx`)
-   **Issue:** `TypeError: Cannot read properties of undefined (reading 'preventDefault')`.
-   **Attempted Fix:** Modified `submitForm` to pass a mock event. Efficacy still pending full backend streaming resolution.

## Current Status & Next Steps
-   **Environment variables are correctly loaded by Freq-Chat when `pnpm dev` is run in a clean terminal.**
-   **Title generation (direct `fetch`) works correctly via the proxy.**
-   **Main chat streaming (via `@ai-sdk/openai` and `streamText`) is the primary remaining issue.** The UI doesn't display the response.
-   The `openrouter_proxy/server.js` uses `http-proxy-middleware` which should generally support streaming.

## Debugging Main Chat Streaming:
1.  **Confirm `openrouter_proxy_mcp` Receives the Streaming Request for Main Chat:**
    *   When a main chat message is sent, tail `docker logs -f openrouter_proxy_mcp`.
    *   Does it log an incoming request for this chat message (distinct from title generation)?
    *   If yes, what is the response from OpenRouter.ai (any errors logged by the proxy)?
    *   If no, the `@ai-sdk/openai` provider in `streamText` is still not hitting your proxy.

2.  **If Proxy *Doesn't* Receive Main Chat Request:**
    *   The `@ai-sdk/openai` provider's streaming mechanism is ignoring `OPENAI_BASE_URL`.
    *   **Solution:** Refactor the `streamText` call in `freq-chat/app/(chat)/api/chat/route.ts` to use a direct `fetch` call (similar to `actions.ts` but for streaming). The response stream will then need to be adapted using Vercel AI SDK utilities like `OpenAIStream` or `StreamingTextResponse` to be compatible with the `useChat` hook on the frontend.

3.  **If Proxy *Does* Receive Main Chat Request but UI is Blank:**
    *   The issue could be in the proxy's handling of the stream from OpenRouter.ai, or how the Vercel AI SDK's `DataStream` (from `streamText`) is being handled when returned in the `Response` object, especially with Redis disabled.
    *   Inspect the browser's Network tab for the `/api/chat` POST request: check the raw "Response" or "EventStream" tab. Is any data (even SSE chunks) coming back? What's the `Content-Type`?

This guide should help track the complex debugging process for this LLM connection issue.
