import { NextResponse, type NextRequest } from 'next/server';
import { auth } from '@/app/(auth)/auth';
import { fetchWithRetries } from '@/lib/http/fetchWithResilience';
import { ChatSDKError } from '@/lib/errors';

export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session?.user) {
    return new ChatSDKError('unauthorized:api', 'User not authenticated').toResponse();
  }

  const n8nWebhookUrl = process.env.N8N_FREQCHAT_WEBHOOK_URL;
  if (!n8nWebhookUrl) {
    console.error('[n8n Orchestration] Error: N8N_FREQCHAT_WEBHOOK_URL is not set.');
    return new ChatSDKError('bad_request:api', 'n8n webhook URL not configured.').toResponse();
  }

  try {
    const payload = await request.json();
    console.log('[n8n Orchestration] Triggering n8n workflow with payload:', payload);

    const response = await fetchWithRetries(n8nWebhookUrl, {
      serviceName: 'n8n Orchestration',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Add any other necessary headers, e.g., an API key for n8n if configured
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.warn(
        `[n8n Orchestration] n8n webhook call failed with status ${response.status}. Body: ${errorBody}`,
      );
      return NextResponse.json(
        { error: 'Failed to trigger n8n workflow', details: errorBody },
        { status: response.status },
      );
    }

    // n8n webhooks usually return 200 or 202 immediately if accepted.
    // The actual result of the workflow might be delivered asynchronously.
    const responseData = await response.json().catch(() => response.text()); 
    console.log('[n8n Orchestration] n8n webhook call successful. Response:', responseData);
    return NextResponse.json(responseData, { status: response.status });

  } catch (error: any) {
    console.error('[n8n Orchestration] Error processing request:', error.message, error.stack);
    return new ChatSDKError('bad_request:api', `Error triggering n8n workflow: ${error.message}`).toResponse();
  }
} 