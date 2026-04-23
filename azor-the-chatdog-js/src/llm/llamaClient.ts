/**
 * Local LLaMA model client using node-llama-cpp v3
 */

import type {
  ILLMClient,
  ILLMChatSession,
  Message,
  LLMResponse,
} from '../types/index.js';
import { validateLlamaConfig } from './llamaValidation.js';

// Dynamically imported types — node-llama-cpp is an optional dependency
type LlamaModel = import('node-llama-cpp').LlamaModel;
type NativeLlamaChatSession = import('node-llama-cpp').LlamaChatSession;
type ChatHistoryItem = import('node-llama-cpp').ChatHistoryItem;

function universalToChatHistory(history: Message[]): ChatHistoryItem[] {
  return history.map((msg) => {
    if (msg.role === 'user') {
      return { type: 'user' as const, text: msg.parts[0]?.text ?? '' };
    }
    return { type: 'model' as const, response: [msg.parts[0]?.text ?? ''] };
  });
}

function chatHistoryToUniversal(chatHistory: ChatHistoryItem[]): Message[] {
  const messages: Message[] = [];
  for (const item of chatHistory) {
    if (item.type === 'user') {
      messages.push({ role: 'user', parts: [{ text: item.text }] });
    } else if (item.type === 'model') {
      const text = item.response
        .filter((r): r is string => typeof r === 'string')
        .join('');
      messages.push({ role: 'model', parts: [{ text }] });
    }
  }
  return messages;
}

/**
 * Wraps a node-llama-cpp LlamaChatSession behind ILLMChatSession.
 * Model + context are initialised asynchronously; sendMessage() awaits the
 * initialisation before forwarding the prompt.
 */
class LlamaChatSessionWrapper implements ILLMChatSession {
  private sessionPromise: Promise<NativeLlamaChatSession>;
  private history: Message[];

  constructor(
    getModel: () => Promise<LlamaModel>,
    contextSize: number,
    systemInstruction: string,
    initialHistory?: Message[]
  ) {
    this.history = initialHistory ? [...initialHistory] : [];
    this.sessionPromise = this._init(
      getModel,
      contextSize,
      systemInstruction,
      this.history
    );
  }

  private async _init(
    getModel: () => Promise<LlamaModel>,
    contextSize: number,
    systemInstruction: string,
    initialHistory: Message[]
  ): Promise<NativeLlamaChatSession> {
    const { LlamaChatSession } = await import('node-llama-cpp');
    const model = await getModel();
    const context = await model.createContext({ contextSize });
    const session = new LlamaChatSession({
      contextSequence: context.getSequence(),
      systemPrompt: systemInstruction,
      autoDisposeSequence: true,
    });

    if (initialHistory.length > 0) {
      session.setChatHistory(universalToChatHistory(initialHistory));
    }

    return session;
  }

  async sendMessage(text: string): Promise<LLMResponse> {
    const session = await this.sessionPromise;
    const responseText = await session.prompt(text, { maxTokens: 4096 });
    this.history = chatHistoryToUniversal(session.getChatHistory());
    return { text: responseText };
  }

  getHistory(): Message[] {
    return this.history;
  }
}

/**
 * LLaMA LLM Client — loads the model once, creates a fresh context per session.
 */
export class LlamaClient implements ILLMClient {
  private modelName: string;
  private modelPath: string;
  private gpuLayers: number;
  private contextSize: number;
  private modelPromise: Promise<LlamaModel> | null = null;

  constructor(
    modelName: string,
    modelPath: string,
    gpuLayers: number,
    contextSize: number
  ) {
    this.modelName = modelName;
    this.modelPath = modelPath;
    this.gpuLayers = gpuLayers;
    this.contextSize = contextSize;
  }

  static fromEnvironment(): LlamaClient {
    const config = validateLlamaConfig();
    return new LlamaClient(
      config.modelName,
      config.llamaModelPath,
      config.llamaGpuLayers,
      config.llamaContextSize
    );
  }

  /**
   * Lazily loads the model the first time it is needed and caches the promise
   * so subsequent sessions reuse the same in-memory model weights.
   */
  private getModel(): Promise<LlamaModel> {
    if (!this.modelPromise) {
      this.modelPromise = (async () => {
        const { getLlama } = await import('node-llama-cpp');
        const llama = await getLlama();
        return llama.loadModel({
          modelPath: this.modelPath,
          gpuLayers: this.gpuLayers,
        });
      })();
    }
    return this.modelPromise;
  }

  createChatSession(
    systemInstruction: string,
    history?: Message[],
    _thinkingBudget?: number
  ): ILLMChatSession {
    return new LlamaChatSessionWrapper(
      () => this.getModel(),
      this.contextSize,
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
    return !!this.modelPath && this.modelPath.length > 0;
  }

  preparingForUseMessage(): string {
    return `Loading LLaMA model from ${this.modelPath}...`;
  }

  readyForUseMessage(): string {
    return `LLaMA ${this.modelName} ready (GPU layers: ${this.gpuLayers}, Context: ${this.contextSize})`;
  }
}
