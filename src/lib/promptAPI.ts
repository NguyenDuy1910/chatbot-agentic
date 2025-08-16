import { Prompt, PromptTemplate } from '@/types/features/prompt';

const API_BASE_URL = '/api';

export const promptAPI = {
  // Get all prompts
  async getPrompts(): Promise<Prompt[]> {
    const response = await fetch(`${API_BASE_URL}/prompts`);
    if (!response.ok) {
      throw new Error('Failed to fetch prompts');
    }
    return response.json();
  },

  // Create new prompt
  async createPrompt(prompt: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt' | 'usageCount'>): Promise<Prompt> {
    const response = await fetch(`${API_BASE_URL}/prompts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(prompt),
    });

    if (!response.ok) {
      throw new Error('Failed to create prompt');
    }

    return response.json();
  },

  // Update prompt
  async updatePrompt(id: string, prompt: Partial<Prompt>): Promise<Prompt> {
    const response = await fetch(`${API_BASE_URL}/prompts/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(prompt),
    });

    if (!response.ok) {
      throw new Error('Failed to update prompt');
    }

    return response.json();
  },

  // Delete prompt
  async deletePrompt(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/prompts/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete prompt');
    }
  },

  // Get prompt templates
  async getTemplates(): Promise<PromptTemplate[]> {
    const response = await fetch(`${API_BASE_URL}/prompt-templates`);
    if (!response.ok) {
      throw new Error('Failed to fetch templates');
    }
    return response.json();
  },

  // Use prompt (increment usage count)
  async usePrompt(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/prompts/${id}/use`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to update prompt usage');
    }
  },
};
