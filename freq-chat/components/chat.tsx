'use client';

import type { Attachment, UIMessage } from 'ai';
import { type ChatRequestOptions } from 'ai';
import { useChat } from 'ai/react';
import { useEffect, useState } from 'react';
import useSWR, { useSWRConfig } from 'swr';
import { ChatHeader } from '@/components/chat-header';
import type { Vote } from '@/lib/db/schema';
import { fetcher, fetchWithErrorHandlers, generateUUID } from '@/lib/utils';
import { Artifact } from './artifact';
import { MultimodalInput } from './multimodal-input';
import { Messages } from './messages';
import type { VisibilityType } from './visibility-selector';
import { useArtifactSelector } from '@/hooks/use-artifact';
import { unstable_serialize } from 'swr/infinite';
import { getChatHistoryPaginationKey } from './sidebar-history';
import { toast } from './toast';
import type { Session } from 'next-auth';
import { useSearchParams } from 'next/navigation';
import { useChatVisibility } from '@/hooks/use-chat-visibility';
import { useAutoResume } from '@/hooks/use-auto-resume';
import { ChatSDKError } from '@/lib/errors';
import { triggerN8nWorkflow } from '@/lib/clients/orchestration';

export function Chat({
  id,
  initialMessages,
  initialChatModel,
  initialVisibilityType,
  isReadonly,
  session,
  autoResume,
}: {
  id: string;
  initialMessages: Array<UIMessage>;
  initialChatModel: string;
  initialVisibilityType: VisibilityType;
  isReadonly: boolean;
  session: Session;
  autoResume: boolean;
}) {
  const { mutate } = useSWRConfig();

  const { visibilityType } = useChatVisibility({
    chatId: id,
    initialVisibilityType,
  });

  const {
    messages,
    setMessages,
    handleSubmit: originalHandleSubmit,
    input,
    setInput,
    append,
    status,
    stop,
    reload,
    experimental_resume,
    data,
  } = useChat({
    id,
    initialMessages,
    experimental_throttle: 100,
    sendExtraMessageFields: true,
    generateId: generateUUID,
    fetch: fetchWithErrorHandlers,
    experimental_prepareRequestBody: (body) => ({
      id,
      message: body.messages.at(-1),
      selectedChatModel: initialChatModel,
      selectedVisibilityType: visibilityType,
    }),
    onFinish: () => {
      mutate(unstable_serialize(getChatHistoryPaginationKey));
    },
    onError: (error) => {
      if (error instanceof ChatSDKError) {
        toast({
          type: 'error',
          description: error.message,
        });
      }
    },
  });

  const searchParams = useSearchParams();
  const query = searchParams.get('query');

  const [hasAppendedQuery, setHasAppendedQuery] = useState(false);

  useEffect(() => {
    if (query && !hasAppendedQuery) {
      append({
        role: 'user',
        content: query,
      });

      setHasAppendedQuery(true);
      window.history.replaceState({}, '', `/chat/${id}`);
    }
  }, [query, append, hasAppendedQuery, id]);

  const { data: votes } = useSWR<Array<Vote>>(
    messages.length >= 2 ? `/api/vote?chatId=${id}` : null,
    fetcher,
  );

  const [attachments, setAttachments] = useState<Array<Attachment>>([]);
  const isArtifactVisible = useArtifactSelector((state) => state.isVisible);

  useAutoResume({
    autoResume,
    initialMessages,
    experimental_resume,
    data,
    setMessages,
  });

  // This is the type MultimodalInput seems to provide for its event, or what useChat expects
  type ExpectedSubmitEventType = React.FormEvent<HTMLFormElement> | { preventDefault?: () => void } | undefined;

  const customHandleSubmit = async (
    e?: ExpectedSubmitEventType, // Use the broader type
    chatRequestOptions?: ChatRequestOptions
  ) => {
    if (e && typeof e.preventDefault === 'function') {
      e.preventDefault();
    }
    const messageContent = input.trim();

    const n8nCommandRegex = /^topic:(\S+)(?:\s+(.*))?$/i;
    const match = messageContent.match(n8nCommandRegex);

    if (match) {
      const topic = match[1];
      const params = match[2] ? match[2].trim() : '';
      setInput('');

      const optimisticMessage: UIMessage = {
        id: generateUUID(),
        role: 'user',
        content: messageContent,
        createdAt: new Date(),
        parts: [{ type: 'text', text: messageContent }],
      };
      setMessages([...messages, optimisticMessage]);

      console.log(`[Chat Component] Detected n8n command. Topic: ${topic}, Params: ${params}`);
      try {
        toast({ type: 'success', description: `Triggering workflow for topic: ${topic}...` });
        
        const result = await triggerN8nWorkflow({
          topic,
          params,
          chatId: id,
          userId: session.user.id,
        });
        console.log('[Chat Component] n8n workflow triggered successfully:', result);
        const systemResponse: UIMessage = {
            id: generateUUID(),
            role: 'assistant',
            content: `n8n workflow for topic '${topic}' acknowledged. Result: ${JSON.stringify(result)}`,
            createdAt: new Date(),
            parts: [{ type: 'text', text: `n8n workflow for topic '${topic}' acknowledged. Result: ${JSON.stringify(result)}` }],
        };
        setMessages([...messages, optimisticMessage, systemResponse]);

      } catch (error: any) {
        console.error('[Chat Component] Failed to trigger n8n workflow:', error);
        toast({ type: 'error', description: `Error triggering n8n workflow: ${error.message || 'Unknown error'}` });
         const systemError: UIMessage = {
            id: generateUUID(),
            role: 'assistant',
            content: `Failed to trigger n8n workflow for topic '${topic}'. Error: ${error.message || 'Unknown error'}`,
            createdAt: new Date(),
            parts: [{ type: 'text', text: `Failed to trigger n8n workflow for topic '${topic}'. Error: ${error.message || 'Unknown error'}` }],
        };
        setMessages([...messages, optimisticMessage, systemError]);
      }
    } else {
      // originalHandleSubmit from useChat expects e?: React.FormEvent<HTMLFormElement>
      // Ensure we pass the correct type.
      if (e && 'nativeEvent' in e && 'currentTarget' in e && 'target' in e && 'bubbles' in e) { // More robust check for FormEvent
        originalHandleSubmit(e as React.FormEvent<HTMLFormElement>, chatRequestOptions);
      } else {
        // If 'e' is not a full FormEvent (e.g., programmatic call or simplified event from MultimodalInput without full FormEvent structure)
        // Call originalHandleSubmit without the event argument, which useChat's handleSubmit should support for programmatic submissions.
        originalHandleSubmit(undefined, chatRequestOptions);
      }
    }
  };

  return (
    <>
      <div className="flex flex-col min-w-0 h-dvh bg-background">
        <ChatHeader
          chatId={id}
          selectedModelId={initialChatModel}
          selectedVisibilityType={initialVisibilityType}
          isReadonly={isReadonly}
          session={session}
        />

        <Messages
          chatId={id}
          status={status}
          votes={votes}
          messages={messages}
          setMessages={setMessages}
          reload={reload}
          isReadonly={isReadonly}
          isArtifactVisible={isArtifactVisible}
        />

        <form className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
          {!isReadonly && (
            <MultimodalInput
              chatId={id}
              input={input}
              setInput={setInput}
              handleSubmit={customHandleSubmit}
              status={status}
              stop={stop}
              attachments={attachments}
              setAttachments={setAttachments}
              messages={messages}
              setMessages={setMessages}
              append={append}
              selectedVisibilityType={visibilityType}
            />
          )}
        </form>
      </div>

      <Artifact
        chatId={id}
        input={input}
        setInput={setInput}
        handleSubmit={customHandleSubmit}
        status={status}
        stop={stop}
        attachments={attachments}
        setAttachments={setAttachments}
        append={append}
        messages={messages}
        setMessages={setMessages}
        reload={reload}
        votes={votes}
        isReadonly={isReadonly}
        selectedVisibilityType={visibilityType}
      />
    </>
  );
}
