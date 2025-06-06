import { NextResponse } from 'next/server';

export async function POST(req: Request) {
    const response = await fetch(`${process.env.CONTROLLER_FREQCHAT_URL}/api/v1/trigger_bootstrap`, {
      method: 'POST'
    });
    const data = await response.json();
    return NextResponse.json(data);
  }
