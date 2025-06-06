import { NextResponse } from 'next/server';
import { openai } from '@ai-sdk/openai'; // The provider we are testing
import { generateText } from 'ai';

export async function GET(request: Request) {
  console.log('[Test SDK API] Testing @ai-sdk/openai provider...');
  console.log(`[Test SDK API]   process.env.OPENAI_API_KEY: ${process.env.OPENAI_API_KEY}`);
  console.log(`[Test SDK API]   process.env.OPENAI_BASE_URL: ${process.env.OPENAI_BASE_URL}`);

  const modelId = process.env.DEFAULT_CHAT_MODEL_ID || "tngtech/deepseek-r1t-chimera:free";
  console.log(`[Test SDK API]   Using modelId: ${modelId}`);

  try {
    // Directly use the imported 'openai' provider factory.
    // It should pick up OPENAI_API_KEY and OPENAI_BASE_URL from the environment.
    const modelInstance = openai.chat(modelId as any);

    const { text, usage, finishReason, warnings } = await generateText({
      model: modelInstance,
      prompt: 'Hello, world! This is a test.',
    });

    console.log('[Test SDK API]   generateText successful:', { text, usage, finishReason, warnings });
    return NextResponse.json({
      message: 'Test successful',
      text,
      usage,
      finishReason,
      warnings,
      apiKeyUsed: process.env.OPENAI_API_KEY ? `${process.env.OPENAI_API_KEY.substring(0, 10)}...` : 'Not Set',
      baseURLUsed: process.env.OPENAI_BASE_URL,
    });
  } catch (error: any) {
    console.error('[Test SDK API]   Error during generateText:', error);
    
    let errorDetails = {
      message: error.message,
      name: error.name,
      stack: error.stack,
      url: error.url, // For AI_APICallError
      statusCode: error.statusCode, // For AI_APICallError
      responseBody: error.responseBody, // For AI_APICallError
    };

    return NextResponse.json(
      { error: 'Test failed', details: errorDetails },
      { status: 500 },
    );
  }
}
