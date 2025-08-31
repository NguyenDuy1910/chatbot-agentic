export interface Prompt {
  id: string;
  name: string;
  description: string;
  content: string;
  category: PromptCategory;
  tags: string[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  usageCount: number;
}

export type PromptCategory = 
  | 'general'
  | 'coding'
  | 'creative'
  | 'analysis'
  | 'conversation'
  | 'custom';

export interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  template: string;
  variables: PromptVariable[];
  category: PromptCategory;
}

export interface PromptVariable {
  name: string;
  type: 'text' | 'number' | 'select' | 'textarea';
  description: string;
  defaultValue?: string;
  options?: string[]; // for select type
  required: boolean;
}

export interface PromptState {
  prompts: Prompt[];
  templates: PromptTemplate[];
  activePromptId: string | null;
  isLoading: boolean;
  error: string | null;
}
