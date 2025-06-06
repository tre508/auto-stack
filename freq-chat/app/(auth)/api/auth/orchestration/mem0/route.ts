import { NextResponse, type NextRequest } from 'next/server';
import { auth } from '@/app/(auth)/auth';
import { fetchWithRetries } from '@/lib/http/fetchWithResilience';
import { ChatSDKError } from '@/lib/errors';

// This route will proxy requests to the Mem0 API.
// It can handle various Mem0 endpoints like /memory, /search, /sessions etc.
// The specific Mem0 endpoint should be part of the path for this proxy.
// e.g., POST /api/orchestration/mem0/memory will hit MEM0_API_URL/memory
// e.g., GET /api/orchestration/mem0/search?query=... will hit MEM0_API_URL/search?query=...

async function handler(request: NextRequest) {
  const session = await auth();
  if (!session?.user) {
    return new ChatSDKError('unauthorized:api', 'User not authenticated').toResponse();
  }

  const mem0ApiBaseUrl = process.env.MEM0_API_URL;
  if (!mem0ApiBaseUrl) {
    console.error('[Mem0 Proxy] Error: MEM0_API_URL is not set.');
    return new ChatSDKError('bad_request:api', 'Mem0 API URL not configured.').toResponse();
  }

  const mem0ApiKey = process.env.MEM0_API_KEY;
  // MEM0_API_KEY is optional as per Mem0 documentation for some setups.

  // Extract the path from the proxy request to append to the Mem0 base URL
  // e.g. if request is to /api/orchestration/mem0/memory, pathSuffix will be /memory
  const proxyPath = request.nextUrl.pathname.replace(/^\/api\/orchestration\/mem0/, '');
  const searchParams = request.nextUrl.search; // Preserve query parameters
  const mem0TargetUrl = `${mem0ApiBaseUrl.replace(/\/$/, '')}${proxyPath}${searchParams}`;

  try {
    console.log(`[Mem0 Proxy] Forwarding ${request.method} request to Mem0: ${mem0TargetUrl}`);

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      // Forward other relevant headers if necessary, be careful with sensitive ones.
    };

    if (mem0ApiKey) {
      headers['Authorization'] = `Bearer ${mem0ApiKey}`;
    }
    
    // Add user ID or session ID to headers/payload if Mem0 expects it for multi-tenancy
    // headers['X-User-Id'] = session.user.id;
    // headers['X-Session-Id'] = chatId; // if available and needed

    let body;
    if (request.method !== 'GET' && request.method !== 'HEAD') {
        try {
            body = await request.text(); // Read as text to forward raw body, supports empty body
        } catch (e) {
            // If body is not present or not readable, it might be fine for some requests
            console.warn('[Mem0 Proxy] Could not read request body, proceeding without it.');
        }
    }

    const response = await fetchWithRetries(mem0TargetUrl, {
      serviceName: 'Mem0 Proxy',
      method: request.method,
      headers,
      body: body, // Forward the raw body (string or undefined)
    });

    const responseData = await response.text(); // Read as text for generic proxying

    if (!response.ok) {
      console.warn(
        `[Mem0 Proxy] Mem0 call to ${mem0TargetUrl} failed with status ${response.status}. Response: ${responseData}`,
      );
    }
    
    // Return the response from Mem0 as is, including status and headers
    const responseHeaders = new Headers(response.headers);
    responseHeaders.set('X-Proxied-By', 'freq-chat-mem0-proxy');

    console.log('[Mem0 Proxy] Mem0 call successful. Returning response to client.');
    return new NextResponse(responseData, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });

  } catch (error: any) {
    console.error('[Mem0 Proxy] Error processing request:', error.message, error.stack);
    return new ChatSDKError('bad_request:api', `Error calling Mem0: ${error.message}`).toResponse();
  }
}

export { handler as GET, handler as POST, handler as PUT, handler as DELETE, handler as PATCH }; 