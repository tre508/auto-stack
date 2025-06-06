'use server';

// import { generateText, type UIMessage } from 'ai'; // No longer using generateText here
import type { UIMessage } from 'ai'; // Still need UIMessage type
import { cookies } from 'next/headers';
import {
  deleteMessagesByChatIdAfterTimestamp,
  getMessageById,
  updateChatVisiblityById,
} from '@/lib/db/queries';
import type { VisibilityType } from '@/components/visibility-selector';
// import { myProvider } from '@/lib/ai/providers'; // No longer using myProvider here

export async function saveChatModelAsCookie(model: string) {
  const cookieStore = await cookies();
  cookieStore.set('chat-model', model);
}

export async function generateTitleFromUserMessage({
  message,
}: {
  message: UIMessage;
}) {
  const apiKey = process.env.OPENAI_API_KEY; // Your OpenRouter Key
  const baseURL = process.env.OPENAI_BASE_URL; // Your OpenRouter Proxy URL (e.g., http://localhost:8001/v1)
  const modelId = process.env.DEFAULT_CHAT_MODEL_ID || "tngtech/deepseek-r1t-chimera:free"; // Or a specific lightweight model for titles

  if (!apiKey || !baseURL) {
    console.error('[actions.ts] Missing OPENAI_API_KEY or OPENAI_BASE_URL for title generation.');
    return "Chat Title"; // Fallback title
  }

  const systemPrompt = `
    - you will generate a short title based on the first message a user begins a conversation with
    - ensure it is not more than 80 characters long
    - the title should be a summary of the user's message
    - do not use quotes or colons`;

  const requestBody = {
    model: modelId,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: message.content } // Assuming message.content is the primary text
    ],
    max_tokens: 20, // Keep title generation short
    temperature: 0.3,
  };

  console.log(`[actions.ts] Generating title via fetch to: ${baseURL}/chat/completions`);
  console.log(`[actions.ts]   Using API Key: ${apiKey.substring(0, 10)}...`);
  console.log(`[actions.ts]   Using Model ID: ${modelId}`);

  try {
    const response = await fetch(`${baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error(`[actions.ts] Error generating title: ${response.status} ${response.statusText}`, errorBody);
      return "Chat Title"; // Fallback
    }

    const data = await response.json();
    const title = data.choices?.[0]?.message?.content?.trim() || "Chat Title";
    console.log(`[actions.ts] Generated title: "${title}"`);
    return title;

  } catch (error: any) {
    console.error('[actions.ts] Exception during title generation fetch:', error.message);
    return "Chat Title"; // Fallback
  }
}

export async function deleteTrailingMessages({ id }: { id: string }) {
  const [message] = await getMessageById({ id });

  await deleteMessagesByChatIdAfterTimestamp({
    chatId: message.chatId,
    timestamp: message.createdAt,
  });
}

export async function updateChatVisibility({
  chatId,
  visibility,
}: {
  chatId: string;
  visibility: VisibilityType;
}) {
  await updateChatVisiblityById({ chatId, visibility });
}
