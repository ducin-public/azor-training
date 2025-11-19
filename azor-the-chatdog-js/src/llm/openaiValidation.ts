/**
 * OpenAI configuration validation using Zod
 */

import { z } from 'zod';

/**
 * OpenAI configuration schema
 */
export const OpenAIConfigSchema = z.object({
  engine: z.literal('OPENAI').default('OPENAI'),
  modelName: z.string().min(1, 'Model name is required'),
  openaiApiKey: z.string().min(1, 'OpenAI API key is required'),
});

export type OpenAIConfig = z.infer<typeof OpenAIConfigSchema>;

/**
 * Validate and parse OpenAI configuration from environment
 */
export function validateOpenAIConfig(): OpenAIConfig {
  const config = {
    engine: 'OPENAI' as const,
    modelName: process.env.OPENAI_MODEL_NAME || process.env.MODEL_NAME || 'gpt-4-turbo',
    openaiApiKey: process.env.OPENAI_API_KEY || '',
  };

  return OpenAIConfigSchema.parse(config);
}
