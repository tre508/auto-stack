import {
  customProvider, // Keep for test environment
  extractReasoningMiddleware,
  wrapLanguageModel,
  type LanguageModel,
  type ImageModel, // Assuming ImageModel can be imported from 'ai'
} from 'ai';
import { openai } from '@ai-sdk/openai'; // This is the main provider factory

// Log environment variables at module load time to debug
console.log('[providers.ts] Initializing - Environment Variables:');
console.log(`[providers.ts]   process.env.OPENAI_API_KEY: ${process.env.OPENAI_API_KEY}`);
console.log(`[providers.ts]   process.env.OPENAI_BASE_URL: ${process.env.OPENAI_BASE_URL}`);
console.log(`[providers.ts]   process.env.DEFAULT_CHAT_MODEL_ID: ${process.env.DEFAULT_CHAT_MODEL_ID}`);
console.log(`[providers.ts]   process.env.DEFAULT_IMAGE_MODEL_ID: ${process.env.DEFAULT_IMAGE_MODEL_ID}`);

import { isTestEnvironment } from '../constants';
import {
  artifactModel as testArtifactModel,
  chatModel as testChatModel,
  reasoningModel as testReasoningModel,
  titleModel as testTitleModel,
} from './models.test';

// The `openai` object imported from `@ai-sdk/openai` IS the provider factory.
// It will AUTOMATICALLY pick up OPENAI_API_KEY and OPENAI_BASE_URL from Freq-Chat's environment
// IF those variables are correctly set and not overridden when the Next.js process starts.
const openRouterProvider = openai; 

// Define a type for your provider interface
interface MyProvider {
  languageModel: (modelId: string) => LanguageModel;
  imageModel: (modelId: string) => ImageModel; // Uncommented and added
}

export const myProvider: MyProvider = isTestEnvironment
  ? customProvider({ // Test environment uses mock models
      languageModels: {
        'chat-model': testChatModel,
        'chat-model-reasoning': testReasoningModel,
        'title-model': testTitleModel,
        'artifact-model': testArtifactModel,
      },
      imageModels: { // Add mock image model for test environment if needed
        'small-model': {} as ImageModel, // Placeholder, replace with actual mock if test uses it
      }
    })
  : { // Production/Development environment
      languageModel: (modelId: string): LanguageModel => {
        let targetModelId = modelId;
        // Map internal, generic model keys to specific OpenRouter models if needed
        if (modelId === 'chat-model' || modelId === 'chat-model-reasoning' || modelId === 'title-model' || modelId === 'artifact-model') {
          targetModelId = process.env.DEFAULT_CHAT_MODEL_ID || "tngtech/deepseek-r1t-chimera:free";
        }
        
        console.log(`[providers.ts] Using targetModelId: "${targetModelId}" (type: ${typeof targetModelId}) for openRouterProvider.chat`);

        // Use the imported openai provider factory. It should use env vars.
        const languageModelInstance = openRouterProvider.chat(targetModelId as any);

        if (modelId === 'chat-model-reasoning') { // Or use a specific reasoning model ID
          return wrapLanguageModel({
            model: languageModelInstance,
            middleware: extractReasoningMiddleware({ tagName: 'think' }),
          });
        }
        return languageModelInstance;
      },
      imageModel: (modelId: string): ImageModel => {
        // Use a default image model ID from env or a fallback
        const targetImageModelId = process.env.DEFAULT_IMAGE_MODEL_ID || 'stability-ai/sdxl'; // Example fallback
        console.log(`[providers.ts] Using targetImageModelId: "${targetImageModelId}" for openRouterProvider.image`);
        // Ensure the provider has an image generation method, e.g., openai.image()
        // The exact method might vary based on the provider capabilities in @ai-sdk/openai
        // For now, assuming it's `openRouterProvider.image(modelIdentifier)`
        // The `as any` might be needed if the modelId string doesn't perfectly match expected types.
        return openRouterProvider.image(targetImageModelId as any); 
      },
    };
