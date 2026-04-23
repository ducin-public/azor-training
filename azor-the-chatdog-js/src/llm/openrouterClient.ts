/**
 * OpenRouter LLM Client
 *
 * OpenRouter exposes an OpenAI-compatible API, so we reuse the OpenAI SDK
 * and point it at https://openrouter.ai/api/v1.
 */

import OpenAI from 'openai';
import type {
  ILLMClient,
  ILLMChatSession,
  Message,
  LLMResponse,
} from '../types/index.js';
import { validateOpenRouterConfig } from './openrouterValidation.js';

const OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1';

/**
 * Wrapper for an OpenRouter chat session
 */
class OpenRouterChatSessionWrapper implements ILLMChatSession {
  private client: OpenAI;
  private modelName: string;
  private systemInstruction: string;
  private history: Message[] = [];

  constructor(
    client: OpenAI,
    modelName: string,
    systemInstruction: string,
    initialHistory?: Message[]
  ) {
    this.client = client;
    this.modelName = modelName;
    this.systemInstruction = systemInstruction;
    this.history = initialHistory || [];
  }

  async sendMessage(text: string): Promise<LLMResponse> {
    this.history.push({
      role: 'user',
      parts: [{ text }],
    });

    const messages: OpenAI.Chat.ChatCompletionMessageParam[] = [
      { role: 'system', content: this.systemInstruction },
      ...this.history.map((msg) => ({
        role: msg.role === 'model' ? ('assistant' as const) : ('user' as const),
        content: msg.parts.map((part) => part.text).join(''),
      })),
    ];

    const completion = await this.client.chat.completions.create({
      model: this.modelName,
      messages,
      max_tokens: 4096,
    });

    const responseText = completion.choices[0].message.content?.trim() || '';

    this.history.push({
      role: 'model',
      parts: [{ text: responseText }],
    });

    return { text: responseText };
  }

  getHistory(): Message[] {
    return this.history;
  }
}

/**
 * OpenRouter LLM Client implementation
 */
export class OpenRouterLLMClient implements ILLMClient {
  private client: OpenAI;
  private modelName: string;
  private apiKey: string;

  constructor(modelName: string, apiKey: string) {
    this.modelName = modelName;
    this.apiKey = apiKey;
    this.client = new OpenAI({
      apiKey,
      baseURL: OPENROUTER_BASE_URL,
    });
  }

  static fromEnvironment(): OpenRouterLLMClient {
    const config = validateOpenRouterConfig();
    return new OpenRouterLLMClient(config.modelName, config.openrouterApiKey);
  }

  createChatSession(
    systemInstruction: string,
    history?: Message[],
    _thinkingBudget?: number
  ): ILLMChatSession {
    return new OpenRouterChatSessionWrapper(
      this.client,
      this.modelName,
      systemInstruction,
      history
    );
  }

  countHistoryTokens(history: Message[]): number {
    let totalTokens = 0;
    for (const msg of history) {
      for (const part of msg.parts) {
        totalTokens += Math.ceil(part.text.length / 4);
      }
    }
    return totalTokens;
  }

  getModelName(): string {
    return this.modelName;
  }

  isAvailable(): boolean {
    return !!this.apiKey && this.apiKey.length > 0;
  }

  preparingForUseMessage(): string {
    return `Preparing OpenRouter model ${this.modelName}...`;
  }

  readyForUseMessage(): string {
    const maskedKey = this.apiKey
      ? `${this.apiKey.substring(0, 8)}...${this.apiKey.substring(this.apiKey.length - 4)}`
      : 'NOT SET';
    return `OpenRouter ${this.modelName} ready (API Key: ${maskedKey})`;
  }
}
