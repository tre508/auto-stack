import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/app/(auth)/auth';

export async function POST(request: NextRequest) {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const { strategy, timerange, config } = body;

    if (!strategy) {
      return NextResponse.json(
        { error: 'Strategy is required' },
        { status: 400 }
      );
    }

    const controllerUrl = process.env.CONTROLLER_API_URL || 'http://controller_auto:5050';
    const url = new URL('/execute', controllerUrl);

    const payload = {
      command: 'backtest',
      strategy: strategy,
      timerange: timerange || '20240101-20241231',
      config: config || '/freqtrade/user_data/config.json'
    };

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(process.env.CONTROLLER_API_KEY && {
          'X-API-Key': process.env.CONTROLLER_API_KEY
        })
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Controller API error: ${response.status} ${errorText}`);
      return NextResponse.json(
        { error: 'Failed to trigger backtest' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json({
      message: 'Backtest initiated successfully',
      data: data
    });

  } catch (error) {
    console.error('Error triggering backtest:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 