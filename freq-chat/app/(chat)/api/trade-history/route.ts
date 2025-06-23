import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/app/(auth)/auth';

export async function GET(request: NextRequest) {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const runId = searchParams.get('run_id');
    
    const controllerUrl = process.env.CONTROLLER_API_URL || 'http://controller_auto:5050';
    const url = new URL('/api/trade-history', controllerUrl);
    
    if (runId) {
      url.searchParams.set('run_id', runId);
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(process.env.CONTROLLER_API_KEY && {
          'X-API-Key': process.env.CONTROLLER_API_KEY
        })
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Controller API error: ${response.status} ${errorText}`);
      return NextResponse.json(
        { error: 'Failed to fetch trade history' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Error fetching trade history:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 