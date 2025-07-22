import { NextResponse } from 'next/server'; // Added import
import {
  appendClientMessage,
  // appendResponseMessages, 
  createDataStream,
  // smoothStream, 
  // streamText, 
} from 'ai';
// import { OpenAIStream } from '@ai-sdk/openai'; // Removing this problematic import again
import { auth, type UserType } from '@/app/(auth)/auth';
import { type RequestHints, systemPrompt } from '@/lib/ai/prompts';
import {
  createStreamId,
  deleteChatById,
  getChatById,
  getMessageCountByUserId,
  getMessagesByChatId,
  getStreamIdsByChatId,
  saveChat,
  saveMessages,
} from '@/lib/db/queries';
import { generateUUID, getTrailingMessageId } from '@/lib/utils';
import { generateTitleFromUserMessage } from '../../actions';
import { createDocument } from '@/lib/ai/tools/create-document';
import { updateDocument } from '@/lib/ai/tools/update-document';
import { requestSuggestions } from '@/lib/ai/tools/request-suggestions';
import { getWeather } from '@/lib/ai/tools/get-weather';
import { isProductionEnvironment } from '@/lib/constants';
import { myProvider } from '@/lib/ai/providers';
import { entitlementsByUserType } from '@/lib/ai/entitlements';
import { postRequestBodySchema, type PostRequestBody } from './schema';
import { geolocation } from '@vercel/functions';
import {
  createResumableStreamContext,
  type ResumableStreamContext,
} from 'resumable-stream';
import { after } from 'next/server';
import type { Chat } from '@/lib/db/schema';
import { differenceInSeconds } from 'date-fns';
import { ChatSDKError } from '@/lib/errors';
import { parseBacktestCommand, executeBacktest, getBacktestResults } from '@/lib/backtest-processor';

export const maxDuration = 60;

let globalStreamContext: ResumableStreamContext | null = null;

function getStreamContext() {
  if (!globalStreamContext) {
    try {
      console.log('[getStreamContext] Attempting to create ResumableStreamContext.');
      console.log('[getStreamContext] process.env.REDIS_URL:', process.env.REDIS_URL);
      globalStreamContext = createResumableStreamContext({
        waitUntil: after, // For Vercel environment, might not be strictly needed for local Redis
        // redisUrl: process.env.REDIS_URL, // Explicitly passing if library supports it (check docs)
      });
      console.log('[getStreamContext] ResumableStreamContext created successfully (or no error thrown).');
    } catch (error: any) {
      if (error.message.includes('REDIS_URL')) {
        console.log(
          ' > Resumable streams are disabled due to missing REDIS_URL',
        );
      } else {
        console.error(error);
      }
    }
  }

  return globalStreamContext;
}



async function handleSlashCommands(message: string): Promise<{ message: string } | null> {
  const trimmedMessage = message.trim();
  
  // Handle /backtest command
  const backtestCommand = parseBacktestCommand(trimmedMessage);
  if (backtestCommand) {
    const result = await executeBacktest(backtestCommand);
    return { message: result.message };
  }
  
  // Handle /results command
  if (trimmedMessage.startsWith('/results')) {
    const parts = trimmedMessage.split(' ');
    const runId = parts[1];
    
    if (!runId) {
      return { message: '❌ **Missing Run ID**\n\nUsage: `/results <run_id>`\n\nExample: `/results bt_2024_01_15_14_30_00`' };
    }
    
    try {
      const results = await getBacktestResults(runId);
      if (!results || !results.results || results.results.length === 0) {
        return { message: `❌ **No Results Found**\n\nNo results found for run ID: \`${runId}\`\n\nThis could mean:\n- The backtest is still running\n- The run ID is incorrect\n- The results haven't been stored yet\n\nTry again in a few minutes or check recent backtests with \`/recent-backtests\`.` };
      }
      
      const result = results.results[0];
      const metadata = result.metadata || {};
      
      return { 
        message: `📊 **Backtest Results for ${runId}**\n\n**Strategy:** ${metadata.strategy || 'Unknown'}\n**PnL:** ${metadata.pnl_pct || 'N/A'}%\n**Sharpe Ratio:** ${metadata.sharpe || 'N/A'}\n**Max Drawdown:** ${metadata.drawdown || 'N/A'}%\n**Total Trades:** ${metadata.trades || 'N/A'}\n\n**Memory:** ${result.memory || 'No details available'}\n\n**Created:** ${result.created_at || 'Unknown'}` 
      };
    } catch (error) {
      return { message: `❌ **Error Retrieving Results**\n\nFailed to get results for run ID: \`${runId}\`\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}` };
    }
  }
  
  // Handle /recent-backtests command
  if (trimmedMessage.startsWith('/recent-backtests')) {
    try {
      const controllerUrl = process.env.CONTROLLER_API_URL || 'http://localhost:5050';
      const response = await fetch(`${controllerUrl}/api/recent-backtests?limit=5`);
      
      if (!response.ok) {
        return { message: `❌ **Error Getting Recent Backtests**\n\nController API returned: ${response.status}` };
      }
      
      const data = await response.json();
      
      if (!data.results || data.results.length === 0) {
        return { message: '📊 **No Recent Backtests**\n\nNo backtest results found. Run a backtest first with:\n`/backtest <strategy> <timerange>`' };
      }
      
      let message = '📊 **Recent Backtests**\n\n';
      data.results.forEach((result: any, index: number) => {
        const metadata = result.metadata || {};
        message += `**${index + 1}.** ${metadata.strategy || 'Unknown Strategy'}\n`;
        message += `   • Run ID: \`${metadata.run_id || 'N/A'}\`\n`;
        message += `   • PnL: ${metadata.pnl_pct || 'N/A'}%\n`;
        message += `   • Trades: ${metadata.trades || 'N/A'}\n`;
        message += `   • Created: ${result.created_at || 'Unknown'}\n\n`;
      });
      
      message += '💡 **Get detailed results:** `/results <run_id>`';
      
      return { message };
    } catch (error) {
      return { message: `❌ **Error Getting Recent Backtests**\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}` };
    }
  }
  
  // Handle /logs command
  if (trimmedMessage.startsWith('/logs')) {
    try {
      const controllerUrl = process.env.CONTROLLER_API_URL || 'http://localhost:5050';
      const response = await fetch(`${controllerUrl}/logs/tail?lines=20`);
      
      if (!response.ok) {
        return { message: `❌ **Error Getting Logs**\n\nController API returned: ${response.status}` };
      }
      
      const data = await response.json();
      const logs = data.logs || 'No logs available';
      
      return { message: `📋 **Recent Controller Logs**\n\n\`\`\`\n${logs}\n\`\`\`` };
    } catch (error) {
      return { message: `❌ **Error Getting Logs**\n\nError: ${error instanceof Error ? error.message : 'Unknown error'}` };
    }
  }
  
  // Handle /help command
  if (trimmedMessage === '/help' || trimmedMessage === '/commands') {
    return { 
      message: `🤖 **Available Slash Commands**\n\n**Trading Commands:**\n• \`/backtest <strategy> [timerange] [config]\` - Run a backtest\n• \`/results <run_id>\` - Get backtest results\n• \`/recent-backtests\` - Show recent backtest results\n\n**System Commands:**\n• \`/logs\` - Show recent controller logs\n• \`/help\` - Show this help message\n\n**Examples:**\n• \`/backtest KrakenFreqAI_auto_stack 20240101-20240301\`\n• \`/results bt_2024_01_15_14_30_00\`\n• \`/recent-backtests\`\n\n💡 **Tip:** All commands are case-insensitive and work in any chat.` 
    };
  }
  
  return null; // Not a slash command
}

export async function POST(request: Request) {
  let requestBody: PostRequestBody;

  try {
    const json = await request.json();
    requestBody = postRequestBodySchema.parse(json);
  } catch (_) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  try {
    const { id, message, selectedChatModel, selectedVisibilityType } =
      requestBody;

    const session = await auth();

    if (!session?.user) {
      return new ChatSDKError('unauthorized:chat').toResponse();
    }

    const userType: UserType = session.user.type;

    const messageCount = await getMessageCountByUserId({
      id: session.user.id,
      differenceInHours: 24,
    });

    if (messageCount > entitlementsByUserType[userType].maxMessagesPerDay) {
      return new ChatSDKError('rate_limit:chat').toResponse();
    }

    const chat = await getChatById({ id });

    if (!chat) {
      const title = await generateTitleFromUserMessage({
        message,
      });

      await saveChat({
        id,
        userId: session.user.id,
        title,
        visibility: selectedVisibilityType,
      });
    } else {
      if (chat.userId !== session.user.id) {
        return new ChatSDKError('forbidden:chat').toResponse();
      }
    }

    const previousMessages = await getMessagesByChatId({ id });

    const messages = appendClientMessage({
      // @ts-expect-error: todo add type conversion from DBMessage[] to UIMessage[]
      messages: previousMessages,
      message,
    });

    const { longitude, latitude, city, country } = geolocation(request);

    const requestHints: RequestHints = {
      longitude,
      latitude,
      city,
      country,
    };

    await saveMessages({
      messages: [
        {
          chatId: id,
          id: message.id,
          role: 'user',
          parts: message.parts,
          attachments: message.experimental_attachments ?? [],
          createdAt: new Date(),
        },
      ],
    });

    // Check if this is a slash command
    const messageContent = message.content || '';
    const slashCommandResult = await handleSlashCommands(messageContent);
    
    if (slashCommandResult) {
      // Save the assistant's response
      const assistantMessage = {
        chatId: id,
        id: generateUUID(),
        role: 'assistant' as const,
        parts: [{ type: 'text' as const, text: slashCommandResult.message }],
        attachments: [],
        createdAt: new Date(),
      };
      
      await saveMessages({
        messages: [assistantMessage],
      });
      
      // Return a simple text response for slash commands
      const responseText = slashCommandResult.message;
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode(responseText));
          controller.close();
        },
      });
      
      return new Response(stream, {
        headers: {
          'Content-Type': 'text/plain',
          'Cache-Control': 'no-cache',
        },
      });
    }

    const streamId = generateUUID();
    await createStreamId({ streamId, chatId: id });

    // Use AI SDK's streamText with proper provider integration
    const result = await (async () => {
      // Import streamText from ai
      const { streamText } = await import('ai');

      // Get the language model from our provider
      const model = myProvider.languageModel(selectedChatModel);
      
      console.log('[Chat API POST Handler] Using AI SDK streamText with model:', selectedChatModel);

      return await streamText({
        model,
        system: systemPrompt({ selectedChatModel, requestHints }),
        messages: messages.map(msg => ({
          role: msg.role, 
          content: msg.content,
        })),
        onFinish: async ({ text }) => {
          // Save the complete assistant message when streaming finishes
          try {
            const assistantMessage = {
              chatId: id,
              id: generateUUID(),
              role: 'assistant' as const,
              parts: [{ type: 'text' as const, text: text.trim() }],
              attachments: [],
              createdAt: new Date(),
            };
            
            await saveMessages({
              messages: [assistantMessage],
            });
            
            console.log(`[Chat API] Successfully saved assistant message with ${text.length} characters`);
          } catch (error) {
            console.error('[Chat API] Failed to save assistant message:', error);
          }
        },
      });
    })();
    
    const streamContext = getStreamContext();

    if (streamContext) {
      const resumable = await streamContext.resumableStream(streamId, () => result.textStream);
      return new Response(resumable); 
    } else {
      return result.toTextStreamResponse({
        headers: {
          'Cache-Control': 'no-cache',
        },
      });
    }
  } catch (error) {
    if (error instanceof ChatSDKError) {
      return error.toResponse();
    }
    // Fallback for other types of errors
    console.error('[Chat API] Unhandled error in POST handler:', error);
    return NextResponse.json(
      { error: 'An unexpected error occurred in the chat API.' },
      { status: 500 },
    );
  }
  // Ensure a response is returned if execution somehow reaches here without returning in try/catch
  return NextResponse.json(
    { error: 'Chat API did not produce a response.' },
    { status: 500 },
  );
}

export async function GET(request: Request) {
  const streamContext = getStreamContext();
  const resumeRequestedAt = new Date();

  if (!streamContext) {
    return new Response(null, { status: 204 });
  }

  const { searchParams } = new URL(request.url);
  const chatId = searchParams.get('chatId');

  if (!chatId) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatSDKError('unauthorized:chat').toResponse();
  }

  let chat: Chat;

  try {
    chat = await getChatById({ id: chatId });
  } catch {
    return new ChatSDKError('not_found:chat').toResponse();
  }

  if (!chat) {
    return new ChatSDKError('not_found:chat').toResponse();
  }

  if (chat.visibility === 'private' && chat.userId !== session.user.id) {
    return new ChatSDKError('forbidden:chat').toResponse();
  }

  const streamIds = await getStreamIdsByChatId({ chatId });

  if (!streamIds.length) {
    return new ChatSDKError('not_found:stream').toResponse();
  }

  const recentStreamId = streamIds.at(-1);

  if (!recentStreamId) {
    return new ChatSDKError('not_found:stream').toResponse();
  }

  const emptyDataStream = createDataStream({
    execute: () => {},
  });

  const stream = await streamContext.resumableStream(
    recentStreamId,
    () => emptyDataStream,
  );

  /*
   * For when the generation is streaming during SSR
   * but the resumable stream has concluded at this point.
   */
  if (!stream) {
    const messages = await getMessagesByChatId({ id: chatId });
    const mostRecentMessage = messages.at(-1);

    if (!mostRecentMessage) {
      return new Response(emptyDataStream, { status: 200 });
    }

    if (mostRecentMessage.role !== 'assistant') {
      return new Response(emptyDataStream, { status: 200 });
    }

    const messageCreatedAt = new Date(mostRecentMessage.createdAt);

    if (differenceInSeconds(resumeRequestedAt, messageCreatedAt) > 15) {
      return new Response(emptyDataStream, { status: 200 });
    }

    const restoredStream = createDataStream({
      execute: (buffer) => {
        buffer.writeData({
          type: 'append-message',
          message: JSON.stringify(mostRecentMessage),
        });
      },
    });

    return new Response(restoredStream, { status: 200 });
  }

  return new Response(stream, { status: 200 });
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  if (!id) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatSDKError('unauthorized:chat').toResponse();
  }

  const chat = await getChatById({ id });

  if (chat.userId !== session.user.id) {
    return new ChatSDKError('forbidden:chat').toResponse();
  }

  const deletedChat = await deleteChatById({ id });

  return Response.json(deletedChat, { status: 200 });
}
