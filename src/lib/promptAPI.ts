import { Prompt, PromptTemplate } from '@/types/features/prompt';
import { api } from './api';
import { apiConfig } from '@/config/api';

export const promptAPI = {
  // Get all prompts
  async getPrompts(): Promise<Prompt[]> {
    return api.get<Prompt[]>(apiConfig.endpoints.prompts.base);
  },

  // Create new prompt
  async createPrompt(prompt: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt' | 'usageCount'>): Promise<Prompt> {
    return api.post<Prompt>(apiConfig.endpoints.prompts.base, prompt);
  },

  // Update prompt
  async updatePrompt(id: string, prompt: Partial<Prompt>): Promise<Prompt> {
    return api.put<Prompt>(apiConfig.endpoints.prompts.byId(id), prompt);
  },

  // Delete prompt
  async deletePrompt(id: string): Promise<void> {
    await api.delete(apiConfig.endpoints.prompts.byId(id));
  },

  // Get prompt templates
  async getTemplates(): Promise<PromptTemplate[]> {
    return api.get<PromptTemplate[]>(apiConfig.endpoints.prompts.templates);
  },

  // Use prompt (increment usage count)
  async usePrompt(id: string): Promise<void> {
    await api.post(apiConfig.endpoints.prompts.use(id));
  },
};
