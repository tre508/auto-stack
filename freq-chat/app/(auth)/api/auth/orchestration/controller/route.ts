import { NextResponse, type NextRequest } from 'next/server';
import { auth } from '@/app/(auth)/auth';
import { fetchWithRetries } from '@/lib/http/fetchWithResilience';
import { ChatSDKError } from '@/lib/errors';

export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session?.user) {
    return new ChatSDKError('unauthorized:api', 'User not authenticated').toResponse();
  }

  const controllerBaseUrl = process.env.CONTROLLER_API_URL; // Standardized variable name
  if (!controllerBaseUrl) {
    console.error('[Controller Orchestration] Error: CONTROLLER_API_URL is not set.');
    return new ChatSDKError('bad_request:api', 'Controller URL not configured.').toResponse();
  }

  try {
    const { endpoint, payload, method = 'POST' } = await request.json();

    if (!endpoint) {
      return new ChatSDKError('bad_request:api', 'Controller endpoint not specified in payload.').toResponse();
    }

    const controllerUrl = `${controllerBaseUrl.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`;
    console.log(`[Controller Orchestration] Forwarding request to Controller: ${method} ${controllerUrl} with payload:`, payload);

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      // Add any other necessary headers, e.g., an API key for the controller if configured
    };
    if (process.env.CONTROLLER_API_KEY) {
        headers['X-API-Key'] = process.env.CONTROLLER_API_KEY;
    }

    const response = await fetchWithRetries(controllerUrl, {
      serviceName: 'Controller Orchestration',
      method: method.toUpperCase(),
      headers,
      body: payload ? JSON.stringify(payload) : undefined,
    });

    const responseData = await response.json().catch(() => response.text());

    if (!response.ok) {
      console.warn(
        `[Controller Orchestration] Controller call to ${controllerUrl} failed with status ${response.status}. Response: ${responseData}`,
      );
      return NextResponse.json(
        { error: 'Failed to call controller', details: responseData },
        { status: response.status },
      );
    }
    
    console.log('[Controller Orchestration] Controller call successful. Response:', responseData);
    return NextResponse.json(responseData, { status: response.status });

  } catch (error: any) {
    console.error('[Controller Orchestration] Error processing request:', error.message, error.stack);
    return new ChatSDKError('bad_request:api', `Error calling controller: ${error.message}`).toResponse();
  }
}
