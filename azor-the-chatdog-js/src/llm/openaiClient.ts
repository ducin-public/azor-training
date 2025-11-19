/**
 * OpenAI API LLM Client
 */

import OpenAI from 'openai';
import type {
  ILLMClient,
  ILLMChatSession,
  Message,
  LLMResponse,
} from '../types/index.js';
import { validateOpenAIConfig } from './openaiValidation.js';

/**
 * Wrapper for OpenAI chat session to provide universal interface
 */
class OpenAIChatSessionWrapper implements ILLMChatSession {
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
    // Add user message to history
    this.history.push({
      role: 'user',
      parts: [{ text }],
    });

    // Convert history to OpenAI format
    const openaiMessages: OpenAI.Chat.ChatCompletionMessageParam[] = [
      {
        role: 'system',
        content: this.systemInstruction,
      },
      ...this.history.map((msg) => ({
        role: msg.role === 'model' ? ('assistant' as const) : ('user' as const),
        content: msg.parts.map((part) => part.text).join(''),
      })),
    ];

    // Send message to OpenAI API
    const completion = await this.client.chat.completions.create({
      model: this.modelName,
      messages: openaiMessages,
      max_completion_tokens: 4096,
    });

    const responseText = completion.choices[0].message.content?.trim() || '';

    // Add assistant response to history
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
 * OpenAI LLM Client implementation
 */
export class OpenAILLMClient implements ILLMClient {
  private client: OpenAI;
  private modelName: string;
  private apiKey: string;

  constructor(modelName: string, apiKey: string) {
    this.modelName = modelName;
    this.apiKey = apiKey;
    this.client = new OpenAI({ apiKey });
  }

  /**
   * Create client from environment variables
   */
  static fromEnvironment(): OpenAILLMClient {
    const config = validateOpenAIConfig();
    return new OpenAILLMClient(config.modelName, config.openaiApiKey);
  }

  /**
   * Create a chat session
   */
  createChatSession(
    systemInstruction: string,
    history?: Message[],
    thinkingBudget?: number
  ): ILLMChatSession {
    // Note: OpenAI doesn't support thinking budget like some other models
    // The parameter is ignored for compatibility with the interface
    return new OpenAIChatSessionWrapper(
      this.client,
      this.modelName,
      systemInstruction,
      history
    );
  }

  /**
   * Count tokens in history
   */
  countHistoryTokens(history: Message[]): number {
    // Rough estimation: 1 token ≈ 4 characters
    // For production, you could use tiktoken library
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
    return `Preparing OpenAI model ${this.modelName}...`;
  }

  readyForUseMessage(): string {
    const maskedKey = this.apiKey
      ? `${this.apiKey.substring(0, 8)}...${this.apiKey.substring(this.apiKey.length - 4)}`
      : 'NOT SET';
    return `OpenAI ${this.modelName} ready (API Key: ${maskedKey})`;
  }
}
