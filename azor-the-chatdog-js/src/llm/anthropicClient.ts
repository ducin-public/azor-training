/**
 * Anthropic Claude API LLM Client
 */

import Anthropic from '@anthropic-ai/sdk';
import type {
  ILLMClient,
  ILLMChatSession,
  Message,
  LLMResponse,
} from '../types/index.js';
import { validateAnthropicConfig } from './anthropicValidation.js';

/**
 * Wrapper for Anthropic chat session to provide universal interface
 */
class AnthropicChatSessionWrapper implements ILLMChatSession {
  private client: Anthropic;
  private modelName: string;
  private systemInstruction: string;
  private history: Message[] = [];
  private thinkingBudget?: number;

  constructor(
    client: Anthropic,
    modelName: string,
    systemInstruction: string,
    initialHistory?: Message[],
    thinkingBudget?: number
  ) {
    this.client = client;
    this.modelName = modelName;
    this.systemInstruction = systemInstruction;
    this.history = initialHistory || [];
    this.thinkingBudget = thinkingBudget;
  }

  async sendMessage(text: string): Promise<LLMResponse> {
    // Add user message to history
    this.history.push({
      role: 'user',
      parts: [{ text }],
    });

    // Convert history to Anthropic format
    const anthropicMessages: Anthropic.MessageParam[] = this.history.map((msg) => ({
      role: msg.role === 'model' ? 'assistant' : 'user',
      content: msg.parts.map((part) => part.text).join(''),
    }));

    // Create message parameters
    const messageParams: Anthropic.MessageCreateParamsNonStreaming = {
      model: this.modelName,
      max_tokens: 4096,
      system: this.systemInstruction,
      messages: anthropicMessages,
    };

    // Add thinking configuration if budget is specified
    if (this.thinkingBudget !== undefined) {
      messageParams.thinking = {
        type: 'enabled',
        budget_tokens: this.thinkingBudget,
      };
    }

    // Send message to Anthropic API
    const response = await this.client.messages.create(messageParams);

    // Extract text from response
    const responseText = response.content
      .filter((block) => block.type === 'text')
      .map((block) => ('text' in block ? block.text : ''))
      .join('');

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
 * Anthropic LLM Client implementation
 */
export class AnthropicLLMClient implements ILLMClient {
  private client: Anthropic;
  private modelName: string;
  private apiKey: string;

  constructor(modelName: string, apiKey: string) {
    this.modelName = modelName;
    this.apiKey = apiKey;
    this.client = new Anthropic({ apiKey });
  }

  /**
   * Create client from environment variables
   */
  static fromEnvironment(): AnthropicLLMClient {
    const config = validateAnthropicConfig();
    return new AnthropicLLMClient(config.modelName, config.anthropicApiKey);
  }

  /**
   * Create a chat session
   */
  createChatSession(
    systemInstruction: string,
    history?: Message[],
    thinkingBudget?: number
  ): ILLMChatSession {
    return new AnthropicChatSessionWrapper(
      this.client,
      this.modelName,
      systemInstruction,
      history,
      thinkingBudget
    );
  }

  /**
   * Count tokens in history
   */
  countHistoryTokens(history: Message[]): number {
    // Rough estimation: 1 token ≈ 4 characters
    // For production, you could use @anthropic-ai/tokenizer
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
    return `Preparing Anthropic model ${this.modelName}...`;
  }

  readyForUseMessage(): string {
    const maskedKey = this.apiKey
      ? `${this.apiKey.substring(0, 8)}...${this.apiKey.substring(this.apiKey.length - 4)}`
      : 'NOT SET';
    return `Anthropic ${this.modelName} ready (API Key: ${maskedKey})`;
  }
}
