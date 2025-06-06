import { ChatSDKError } from '@/lib/errors';

const ORCHESTRATION_API_BASE = '/api/orchestration';

async function handleOrchestrationResponse(response: Response, serviceName: string) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Failed to parse error response', details: response.statusText }));
    console.error(`[${serviceName} Client] API call failed:`, errorData);
    throw new ChatSDKError('bad_request:api', errorData.details || errorData.error || `Error with ${serviceName}`);
  }
  return response.json().catch(() => response.text()); // Return text if JSON parsing fails for some valid responses
}

/**
 * Triggers an n8n workflow via the backend orchestration route.
 * @param payload - The payload to send to the n8n webhook.
 * @returns The response from the n8n webhook (usually an ack).
 */
export async function triggerN8nWorkflow(payload: any): Promise<any> {
  const serviceName = 'n8n Workflow';
  try {
    const response = await fetch(`${ORCHESTRATION_API_BASE}/n8n`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    return handleOrchestrationResponse(response, serviceName);
  } catch (error: any) {
    console.error(`[${serviceName} Client] Error triggering workflow:`, error);
    throw error; // Re-throw to be caught by caller
  }
}

/**
 * Calls a FastAPI controller endpoint via the backend orchestration route.
 * @param endpoint - The specific controller endpoint path (e.g., '/users/create').
 * @param controllerPayload - The payload for the controller endpoint.
 * @param method - The HTTP method to use (e.g., 'POST', 'GET'). Defaults to 'POST'.
 * @returns The response from the controller.
 */
export async function callController(endpoint: string, controllerPayload?: any, method: string = 'POST'): Promise<any> {
  const serviceName = 'Controller';
  try {
    const response = await fetch(`${ORCHESTRATION_API_BASE}/controller`, {
      method: 'POST', // The proxy route itself is POST
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ endpoint, payload: controllerPayload, method }),
    });
    return handleOrchestrationResponse(response, serviceName);
  } catch (error: any) {
    console.error(`[${serviceName} Client] Error calling controller endpoint ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Proxies a request to the Mem0 API via the backend orchestration route.
 * @param mem0Endpoint - The Mem0 API endpoint path (e.g., '/memory', '/search').
 * @param method - The HTTP method ('GET', 'POST', 'PUT', 'DELETE', 'PATCH').
 * @param body - The request body for POST/PUT/PATCH requests.
 * @param queryParams - An object representing URL query parameters for GET requests.
 * @returns The response from the Mem0 API.
 */
export async function callMem0Api(
  mem0Endpoint: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH',
  body?: any,
  queryParams?: Record<string, string>,
): Promise<any> {
  const serviceName = 'Mem0 API';
  let url = `${ORCHESTRATION_API_BASE}/mem0${mem0Endpoint.startsWith('/') ? mem0Endpoint : '/' + mem0Endpoint}`;

  if (queryParams && method === 'GET') {
    const params = new URLSearchParams(queryParams);
    url += `?${params.toString()}`;
  }

  try {
    const response = await fetch(url, {
      method,
      headers: {
        ...(body && method !== 'GET' && method !== 'DELETE' ? { 'Content-Type': 'application/json' } : {}),
      },
      ...(body && method !== 'GET' && method !== 'DELETE' ? { body: JSON.stringify(body) } : {}),
    });
    return handleOrchestrationResponse(response, serviceName);
  } catch (error: any) {
    console.error(`[${serviceName} Client] Error calling Mem0 endpoint ${mem0Endpoint}:`, error);
    throw error;
  }
} 