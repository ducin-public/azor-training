/**
 * OpenRouter configuration validation using Zod
 */

import { z } from 'zod';

/**
 * OpenRouter configuration schema
 */
export const OpenRouterConfigSchema = z.object({
  engine: z.literal('OPENROUTER').default('OPENROUTER'),
  modelName: z.string().min(1, 'Model name is required'),
  openrouterApiKey: z.string().min(1, 'OpenRouter API key is required'),
});

export type OpenRouterConfig = z.infer<typeof OpenRouterConfigSchema>;

/**
 * Validate and parse OpenRouter configuration from environment
 */
export function validateOpenRouterConfig(): OpenRouterConfig {
  const config = {
    engine: 'OPENROUTER' as const,
    modelName: process.env.OPENROUTER_MODEL_NAME || process.env.MODEL_NAME || 'qwen/qwen3.5-9b',
    openrouterApiKey: process.env.OPENROUTER_API_KEY || '',
  };

  return OpenRouterConfigSchema.parse(config);
}
