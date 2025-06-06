// server.js
import express from "express";
import { createProxyMiddleware } from "http-proxy-middleware";
import dotenv from "dotenv";
import cors from "cors";

dotenv.config(); // Load environment variables from .env file

const app = express();

// Enable CORS for all routes and origins (you can configure it more strictly if needed)
app.use(cors());

const OPENROUTER_API_KEY_FROM_ENV = process.env.OPENROUTER_API_KEY;
const PROXY_PORT = parseInt(process.env.PROXY_PORT || "8000", 10);

if (!OPENROUTER_API_KEY_FROM_ENV) {
  console.error("Error: OPENROUTER_API_KEY environment variable is not set.");
  process.exit(1);
}

// Proxy all OpenAI‐style API calls to OpenRouter
app.use(
  "/v1",
  createProxyMiddleware({
    target: "https://openrouter.ai/api/v1",
    changeOrigin: true,
    pathRewrite: {
      "^/v1": "/v1", // preserve path, though OpenRouter might not strictly need /api/v1 in the target path if it's already in target.
    },
    on: {
      proxyReq: (proxyReq, req, res) => {
        console.log(`[Proxy] Incoming request to proxy: ${req.method} ${req.originalUrl}`); // Added log for incoming request
        console.log(`[Proxy] Using OPENROUTER_API_KEY_FROM_ENV (first 5 chars): ${OPENROUTER_API_KEY_FROM_ENV ? OPENROUTER_API_KEY_FROM_ENV.substring(0,5) : 'undefined'}`);

        proxyReq.removeHeader("Authorization");
        if (OPENROUTER_API_KEY_FROM_ENV) {
          proxyReq.setHeader(
            "Authorization",
            `Bearer ${OPENROUTER_API_KEY_FROM_ENV}`
          );
          console.log(`[Proxy] Authorization header set with key starting: ${OPENROUTER_API_KEY_FROM_ENV.substring(0,5)}`);
        } else {
          console.error("[Proxy] CRITICAL: OPENROUTER_API_KEY was unexpectedly undefined or empty when trying to set header.");
        }
        // Optional: Add other headers OpenRouter might recommend or require
        // proxyReq.setHeader("HTTP-Referer", process.env.YOUR_SITE_URL || ""); 
        // proxyReq.setHeader("X-Title", process.env.YOUR_SITE_NAME || "");
      },
      error: (err, req, res) => {
        console.error("Proxy error:", err);
        if (res && !res.headersSent) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Proxy Error', details: err.message }));
        } else if (res && res.headersSent && !res.writableEnded) {
            // If headers were sent but response not finished, try to end it.
            res.end();
        }
      }
    },
    logLevel: process.env.PROXY_LOG_LEVEL || "info", //silent, error, warn, info, debug, HPM outputs a lot of debug info
  })
);

// Simple health check endpoint
app.get("/healthz", (req, res) => {
  res.status(200).send("OK");
});

app.listen(PROXY_PORT, () =>
  console.log(`🚀 OpenRouter Proxy (Node.js) listening on http://localhost:${PROXY_PORT}/v1`)
);
